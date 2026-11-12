#!/usr/bin/env python3
"""Observational permission capture and explicit incremental review checkpoints."""
import argparse
import contextlib
import datetime
import fcntl
import hashlib
import json
import os
from pathlib import Path
import sys
import uuid


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def digest(value):
    return hashlib.sha256(value).hexdigest()


class Store:
    def __init__(self, home):
        self.home = Path(home).expanduser().resolve()
        self.root = self.home / '.local' / 'approval-review'

    @contextlib.contextmanager
    def locked(self):
        self.root.mkdir(parents=True, exist_ok=True, mode=0o700)
        os.chmod(self.root, 0o700)
        fd = os.open(self.root / 'lock', os.O_CREAT | os.O_RDWR, 0o600)
        with os.fdopen(fd, 'a') as handle:
            fcntl.flock(handle, fcntl.LOCK_EX)
            yield

    def read(self, name, default):
        path = self.root / name
        return json.loads(path.read_text()) if path.exists() else default

    def write(self, name, value):
        path = self.root / name
        tmp = path.with_name(path.name + '.' + str(uuid.uuid4()) + '.tmp')
        fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, 'w') as handle:
            json.dump(value, handle, indent=2)
            handle.write('\n')
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)

    def policy(self):
        paths = list((self.home / 'rules').glob('*.rules'))
        paths += [self.home / 'config.toml', self.home / 'hooks.json']
        paths += [Path.home() / '.local/share/codex-publish' / name
                  for name in ('codex-git', 'codex-read')] if self.home == Path.home() / '.codex' else []
        hashes = {str(p): digest(p.read_bytes()) if p.exists() else None
                  for p in sorted(paths)}
        return digest(json.dumps(hashes, sort_keys=True).encode())

    def events(self):
        path = self.root / 'events.jsonl'
        if not path.exists():
            return []
        rows = [json.loads(line) for line in path.read_text().splitlines()]
        ids = [r['id'] for r in rows]
        if len(ids) != len(set(ids)):
            raise ValueError('Duplicate event IDs; inspect the log before reviewing')
        return rows

    def pending(self):
        rows = self.events()
        state = self.read('state.json', {})
        cursor = state.get('last_event_id')
        if cursor:
            positions = [i for i, r in enumerate(rows) if r['id'] == cursor]
            if not positions:
                raise ValueError('Checkpoint event missing; inspect log continuity')
            pending = rows[positions[0] + 1:]
        else:
            pending = rows
        return rows, pending, state

    def capture(self, payload):
        if not isinstance(payload, dict) or payload.get('hook_event_name') != 'PermissionRequest':
            raise ValueError('Expected PermissionRequest object')
        fields = ('session_id', 'turn_id', 'tool_use_id', 'cwd', 'transcript_path',
                  'tool_name', 'permission_mode', 'model')
        event = {k: payload[k] for k in fields if isinstance(payload.get(k), str)}
        tool_input = payload.get('tool_input')
        if isinstance(tool_input, dict):
            if payload.get('tool_name') == 'Bash':
                command = tool_input.get('command', tool_input.get('cmd'))
                if isinstance(command, (str, list)):
                    event['command'] = command
            reason = tool_input.get('description') or tool_input.get('justification')
            if isinstance(reason, str):
                event['reason'] = reason
            prefix = tool_input.get('prefix_rule')
            if isinstance(prefix, list) and all(isinstance(x, str) for x in prefix):
                event['requested_prefix'] = prefix
            if isinstance(tool_input.get('workdir'), str):
                event['command_cwd'] = tool_input['workdir']
        event.update(schema_version=2, id=str(uuid.uuid4()), timestamp=now(),
                     observation='permission_request', approval_outcome='unknown')
        with self.locked():
            event['policy_hash'] = self.policy()
            # IDs are optional in PermissionRequest. Deduplicate only when supplied,
            # retaining distinct retries with changed command/input or turn.
            if event.get('session_id') and event.get('tool_use_id'):
                identity = {k: v for k, v in event.items()
                            if k not in ('id', 'timestamp', 'policy_hash')}
                event['delivery_key'] = digest(json.dumps(identity, sort_keys=True).encode())
                if any(r.get('delivery_key') == event['delivery_key'] for r in self.events()):
                    return
            encoded = (json.dumps(event, ensure_ascii=True) + '\n').encode()
            fd = os.open(self.root / 'events.jsonl', os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
            with os.fdopen(fd, 'ab') as handle:
                handle.write(encoded)
                handle.flush()
                os.fsync(handle.fileno())

    def status(self):
        with self.locked():
            rows, pending, state = self.pending()
            policy = self.policy()
            return {'captured_requests': len(rows), 'pending_requests': len(pending),
                    'last_capture': rows[-1]['timestamp'] if rows else None,
                    'checkpoint': state, 'policy_hash': policy,
                    'policy_changed': state.get('policy_hash') != policy,
                    'capture_coverage': 'unknown_until_live_hook_verified',
                    'data_directory': str(self.root)}

    def prepare(self, limit):
        with self.locked():
            _, pending, state = self.pending()
            batch_id = str(uuid.uuid4())
            batch = {'id': batch_id, 'created_at': now(),
                     'previous_cursor': state.get('last_event_id'),
                     'previous_batch_id': state.get('batch_id'),
                     'policy_hash': self.policy(), 'events': pending[:limit],
                     'has_more': len(pending) > limit,
                     'previous_report': state.get('report'),
                     'corrections': str(self.root / 'corrections.md')}
            batch['policy_changed'] = state.get('policy_hash') != batch['policy_hash']
            self.write('batch-' + batch_id + '.json', batch)
            return batch

    def complete(self, batch_id, report):
        batch_id = str(uuid.UUID(batch_id))
        report_path = Path(report)
        if not report_path.is_absolute():
            raise ValueError('Report must be an absolute path')
        report_text = report_path.read_text()
        if not report_text.strip():
            raise ValueError('Review report is empty')
        with self.locked():
            batch = self.read('batch-' + batch_id + '.json', None)
            if batch is None:
                raise ValueError('Unknown batch')
            _, pending, state = self.pending()
            if (state.get('last_event_id') != batch['previous_cursor']
                    or state.get('batch_id') != batch['previous_batch_id']):
                raise ValueError('Another review advanced the cursor; prepare again')
            if self.policy() != batch['policy_hash']:
                raise ValueError('Policy changed; prepare and reassess again')
            events = batch['events']
            if pending[:len(events)] != events:
                raise ValueError('Captured evidence changed; inspect log continuity')
            # Keep the reviewed report durable before advancing the cursor.
            reports = self.root / 'reports'
            reports.mkdir(exist_ok=True, mode=0o700)
            target = reports / (batch_id + '.md')
            fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(fd, 'w') as handle:
                handle.write(report_text)
                handle.flush()
                os.fsync(handle.fileno())
            state = {'last_event_id': events[-1]['id'] if events else batch['previous_cursor'],
                     'policy_hash': batch['policy_hash'], 'reviewed_at': now(),
                     'report': str(target), 'batch_id': batch_id}
            self.write('state.json', state)
            return state


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--home', default=os.environ.get('CODEX_HOME', str(Path.home() / '.codex')))
    sub = parser.add_subparsers(dest='action', required=True)
    sub.add_parser('capture')
    sub.add_parser('status')
    prepare = sub.add_parser('prepare')
    prepare.add_argument('--limit', type=int, default=50, choices=range(1, 201), metavar='1..200')
    complete = sub.add_parser('complete')
    complete.add_argument('--batch', required=True)
    complete.add_argument('--report', required=True)
    args = parser.parse_args()
    store = Store(args.home)
    try:
        if args.action == 'capture':
            # No output and no decision: always defer to normal approval handling.
            store.capture(json.load(sys.stdin))
        elif args.action == 'status':
            print(json.dumps(store.status(), indent=2))
        elif args.action == 'prepare':
            print(json.dumps(store.prepare(args.limit), indent=2))
        else:
            print(json.dumps(store.complete(args.batch, args.report), indent=2))
    except (OSError, ValueError, KeyError, TypeError) as error:
        # Never print payloads or secrets in diagnostics.
        print('approval-review: capture unavailable' if args.action == 'capture'
              else 'approval-review: ' + str(error), file=sys.stderr)
        return 0 if args.action == 'capture' else 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
