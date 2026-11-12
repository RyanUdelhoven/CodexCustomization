#!/usr/bin/env python3
"""Private approval dashboard and evidence-backed annotations; standard library only."""
import argparse
import contextlib
from collections import Counter, defaultdict
import datetime
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import secrets
import sqlite3
import sys
from urllib.parse import urlsplit, parse_qs

from approval_log import Store, now

STATUSES = ('new', 'investigating', 'rule_proposed', 'resolved', 'intentionally_prompted')
OUTCOMES = ('unknown', 'human_prompt_confirmed', 'user_approved', 'user_denied',
            'automatic_allow', 'automatic_deny', 'execution_confirmed')


class Tracker:
    def __init__(self, home):
        self.store = Store(home)

    @contextlib.contextmanager
    def database(self):
        path = self.store.root / 'tracker.sqlite3'
        fd = os.open(path, os.O_CREAT | os.O_RDWR, 0o600)
        os.close(fd)
        os.chmod(path, 0o600)
        db = sqlite3.connect(path)
        db.row_factory = sqlite3.Row
        db.execute('CREATE TABLE IF NOT EXISTS annotations '
                   '(event_id TEXT PRIMARY KEY, status TEXT, outcome TEXT, evidence TEXT, '
                   'notes TEXT, proposed_rule TEXT, verification TEXT, updated_at TEXT)')
        db.execute('CREATE TABLE IF NOT EXISTS tasks '
                   '(session_id TEXT PRIMARY KEY, title TEXT, source TEXT)')
        db.execute('CREATE TABLE IF NOT EXISTS audit '
                   '(changed_at TEXT, kind TEXT, identity TEXT, value TEXT)')
        try:
            with db:
                yield db
        finally:
            db.close()

    def annotate(self, event_id, status, outcome, evidence, notes, proposed_rule, verification):
        if outcome != 'unknown' and not evidence.strip():
            raise ValueError('A confirmed outcome requires an evidence reference')
        with self.store.locked():
            if event_id not in {e['id'] for e in self.store.events()}:
                raise ValueError('Unknown event ID')
            value = (event_id, status, outcome, evidence, notes, proposed_rule, verification, now())
            with self.database() as db:
                db.execute('INSERT OR REPLACE INTO annotations VALUES (?,?,?,?,?,?,?,?)', value)
                db.execute('INSERT INTO audit VALUES (?,?,?,?)',
                           (now(), 'annotation', event_id, json.dumps(value)))

    def label(self, session_id, title, source):
        with self.store.locked():
            if session_id not in {e.get('session_id') for e in self.store.events()}:
                raise ValueError('Unknown session ID')
            with self.database() as db:
                db.execute('INSERT OR REPLACE INTO tasks VALUES (?,?,?)', (session_id, title, source))
                db.execute('INSERT INTO audit VALUES (?,?,?,?)',
                           (now(), 'task_label', session_id, json.dumps([title, source])))

    def snapshot(self, redacted=False):
        with self.store.locked():
            events = self.store.events()
            with self.database() as db:
                annotations = {r['event_id']: dict(r) for r in db.execute('SELECT * FROM annotations')}
                tasks = {r['session_id']: dict(r) for r in db.execute('SELECT * FROM tasks')}
        rows, groups = [], defaultdict(list)
        for event in events:
            row = dict(event)
            row.update(annotations.get(row['id'], {}))
            row.setdefault('status', 'new')
            row.setdefault('outcome', row.get('approval_outcome', 'unknown'))
            task = tasks.get(row.get('session_id'), {})
            row['task_title'] = task.get('title', 'Unknown')
            row['task_title_source'] = task.get('source', 'unavailable')
            cwd = row.get('command_cwd') or row.get('cwd')
            # Filesystem discovery occurs on demand, never in the capture hook.
            root = None
            if cwd and Path(cwd).is_absolute():
                path = Path(cwd)
                root = next((p for p in (path, *path.parents) if (p / '.git').exists()), None)
            row['project_root'] = str(root) if root else None
            row['project'] = root.name if root else (Path(cwd).name if cwd else 'Unknown')
            row['project_source'] = 'repository_root' if root else 'working_directory' if cwd else 'unavailable'
            command = row.get('command')
            command_text = command if isinstance(command, str) else json.dumps(command) if command else ''
            row['command_text'] = command_text
            # Exact repeats are deliberately conservative: argument/quote differences
            # can change capabilities. Prefix-based groups are labeled separately.
            key = json.dumps([row.get('tool_name'), command, row['id'] if command is None else None], sort_keys=True)
            row['group_id'] = hashlib.sha256(key.encode()).hexdigest()[:16]
            groups[row['group_id']].append(row)
            rows.append(row)
        candidates = []
        for key, members in groups.items():
            count = len(members)
            for row in members:
                row['repeat_count'] = count
            candidates.append({'group_id': key, 'command': members[0]['command_text'],
                               'tool': members[0].get('tool_name', 'Unknown'),
                               'count': count, 'projects': sorted({r['project'] for r in members}),
                               'event_ids': [r['id'] for r in members],
                               'proposed_rules': sorted({r['proposed_rule'] for r in members if r.get('proposed_rule')}),
                               'grouping': 'exact command; no inferred allowance'})
        candidates.sort(key=lambda g: (-g['count'], -len(g['projects']), g['group_id']))
        snapshot = {'generated_at': now(), 'count': len(rows),
                    'last_capture': rows[-1]['timestamp'] if rows else None,
                    'coverage': 'Hook observations only; live activation and human prompts require independent verification.',
                    'rows': list(reversed(rows)), 'candidates': candidates,
                    'statuses': dict(Counter(r['status'] for r in rows))}
        if redacted:
            # Allowlist export fields rather than guessing where credentials appear.
            # Exclude project/task names, paths, commands, prefix rules and all free text.
            snapshot['rows'] = [{k: r.get(k) for k in ('id', 'timestamp', 'status', 'outcome',
                                                       'group_id', 'repeat_count')} for r in snapshot['rows']]
            snapshot['candidates'] = [{k: g[k] for k in ('group_id', 'count', 'event_ids')}
                                      for g in candidates]
            snapshot['redacted'] = True
        return snapshot


def serve(tracker, port):
    token = secrets.token_urlsafe(24)
    page = Path(__file__).with_name('tracker.html').read_bytes()

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass  # Do not write tokens or captured commands into HTTP access logs.

        def do_GET(self):
            parsed = urlsplit(self.path)
            if parse_qs(parsed.query).get('token') != [token]:
                self.send_error(403)
                return
            try:
                if parsed.path == '/':
                    body, mime = page, 'text/html; charset=utf-8'
                elif parsed.path in ('/data', '/export'):
                    body = json.dumps(tracker.snapshot(redacted=parsed.path == '/export')).encode()
                    mime = 'application/json'
                else:
                    self.send_error(404)
                    return
            except (OSError, ValueError, sqlite3.Error, KeyError, TypeError):
                self.send_error(503, 'Tracker unavailable; inspect local log integrity and storage')
                return
            self.send_response(200)
            self.send_header('Content-Type', mime)
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('Referrer-Policy', 'no-referrer')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('Content-Security-Policy', "default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; connect-src 'self'; base-uri 'none'; frame-ancestors 'none'")
            self.end_headers()
            self.wfile.write(body)

    server = ThreadingHTTPServer(('127.0.0.1', port), Handler)
    print(f'http://127.0.0.1:{server.server_port}/?token={token}', flush=True)
    try:
        server.serve_forever()
    finally:
        server.server_close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--home', default=os.environ.get('CODEX_HOME', str(Path.home() / '.codex')))
    sub = parser.add_subparsers(dest='action', required=True)
    view = sub.add_parser('serve')
    view.add_argument('--port', type=int, default=0)
    sub.add_parser('status')
    export = sub.add_parser('export')
    export.add_argument('--output', required=True)
    export.add_argument('--include-sensitive', action='store_true')
    annotation = sub.add_parser('annotate', description='Replace the complete annotation; prior versions remain in audit history.')
    annotation.add_argument('--event', required=True)
    annotation.add_argument('--status', choices=STATUSES, required=True)
    annotation.add_argument('--outcome', choices=OUTCOMES, default='unknown')
    for field in ('evidence', 'notes', 'proposed-rule', 'verification'):
        annotation.add_argument('--' + field, default='')
    label = sub.add_parser('label-task')
    for field in ('session', 'title', 'source'):
        label.add_argument('--' + field, required=True)
    args = parser.parse_args()
    tracker = Tracker(args.home)
    try:
        if args.action == 'serve':
            serve(tracker, args.port)
        elif args.action == 'annotate':
            tracker.annotate(args.event, args.status, args.outcome, args.evidence, args.notes,
                             args.proposed_rule, args.verification)
            print('Annotation saved; original evidence retained.')
        elif args.action == 'label-task':
            tracker.label(args.session, args.title, args.source)
            print('Task label saved with source.')
        elif args.action == 'export':
            data = tracker.snapshot(redacted=not args.include_sensitive)
            # Refuse overwriting; exports are private even with a permissive umask.
            fd = os.open(Path(args.output).expanduser(), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            with os.fdopen(fd, 'w') as handle:
                json.dump(data, handle, indent=2)
            print('Export saved.')
        else:
            data = tracker.snapshot()
            print(json.dumps({k: v for k, v in data.items() if k not in ('rows', 'candidates')}, indent=2))
    except (OSError, ValueError, sqlite3.Error, KeyError, TypeError):
        print('approval-tracker: unavailable; inspect arguments, log integrity and storage locally', file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == '__main__':
    sys.exit(main())
