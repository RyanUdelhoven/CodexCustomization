#!/usr/bin/env python3
"""Temporary workspaces for agent-driven YouTube analysis; no external LLM API."""
import argparse
from contextlib import contextmanager
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import signal
import sys
import tempfile
import time
import uuid
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from analyze_youtube import retrieve, video_id

ROOT = Path(tempfile.gettempdir()) / 'codex-youtube-runs'
OWNER = 'analyze-youtube-v1'
TTL = 24 * 60 * 60
ARTIFACTS = {'raw', 'clean', 'exclusions', 'sections', 'section-notes', 'sponsorblock'}


def load(path):
    return json.loads(Path(path).read_text())


def save(path, value):
    path = Path(path)
    temporary = path.with_suffix('.new')
    with temporary.open('w') as stream:
        os.chmod(temporary, 0o600)
        json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
    temporary.replace(path)


def owned(path):
    path = Path(path).absolute()
    if (path.parent != ROOT.absolute() or path.is_symlink()
            or not re.fullmatch(r'run-[a-f0-9]{32}', path.name)):
        raise ValueError('Not a managed YouTube run directory')
    manifest = load(path / 'manifest.json')
    if manifest.get('owner') != OWNER or manifest.get('run') != path.name:
        raise ValueError('Invalid run ownership marker')
    return path


@contextmanager
def locked(path):
    path = owned(path)
    with (path / '.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        os.utime(path / 'manifest.json', None)
        yield path
        if path.exists():
            os.utime(path / 'manifest.json', None)


def prune():
    ROOT.mkdir(mode=0o700, parents=True, exist_ok=True)
    removed = 0
    for candidate in ROOT.glob('run-*'):
        try:
            path = owned(candidate)
            with (path / '.lock').open('a') as lock:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                if time.time() - (path / 'manifest.json').stat().st_mtime > TTL:
                    shutil.rmtree(path)
                    removed += 1
        except (OSError, ValueError, KeyError):
            continue
    return removed


def create():
    ROOT.mkdir(mode=0o700, parents=True, exist_ok=True)
    path = ROOT / ('run-' + uuid.uuid4().hex)
    path.mkdir(mode=0o700)
    save(path / 'manifest.json', {'owner': OWNER, 'run': path.name, 'created': time.time()})
    return path


def sponsorblock(identifier):
    """Read-only, hash-prefix query. Absence/failure never blocks local analysis."""
    prefix = hashlib.sha256(identifier.encode()).hexdigest()[:4]
    url = 'https://sponsor.ajay.app/api/skipSegments/' + prefix + '?' + urlencode({
        'categories': json.dumps(['sponsor', 'selfpromo', 'interaction']), 'service': 'YouTube'})
    try:
        with urlopen(Request(url, headers={'User-Agent': 'Codex-analyze-youtube/1.0'}), timeout=15) as response:
            data = json.load(response)
        segments = []
        for video in data:
            if video['videoID'] != identifier:
                continue
            for entry in video['segments']:
                start, end = entry['segment']
                if (entry.get('actionType') == 'skip' and entry.get('category') in
                        ('sponsor', 'selfpromo', 'interaction') and
                        math.isfinite(start) and math.isfinite(end) and 0 <= start < end):
                    segments.append({'start': start, 'end': end, 'category': entry['category']})
        return {'status': 'ok', 'segments': segments,
                'attribution': 'SponsorBlock community, https://sponsor.ajay.app/'}
    except HTTPError as exc:
        exc.close()
        return {'status': 'absent' if exc.code == 404 else 'unavailable', 'segments': []}
    except (URLError, TimeoutError, OSError, ValueError, KeyError, TypeError):
        return {'status': 'unavailable', 'segments': []}


def start(url, languages, model):
    path = create()
    try:
        with locked(path):
            data = retrieve(video_id(url), languages, model,
                            Path(__file__).resolve().parents[1] / '.runtime' / 'models', audio_parent=path)
            data['segments'] = [dict(row, id=i) for i, row in enumerate(data['segments'])]
            save(path / 'raw.json', data)
            hints = sponsorblock(data['video_id'])
            save(path / 'sponsorblock.json', hints)
            return {'run': str(path), 'segments': len(data['segments']), 'source': data['source'],
                    'sponsorblock_status': hints['status']}
    except BaseException:
        shutil.rmtree(path)
        raise


def require_ids(ids, valid):
    if (not isinstance(ids, list) or any(type(i) is not int for i in ids)
            or len(ids) != len(set(ids)) or not set(ids) <= valid):
        raise ValueError('Segment IDs must be unique integers from the source')


def clean(path, decision):
    raw = load(path / 'raw.json')
    rows = raw['segments']
    valid = {row['id'] for row in rows}
    sponsors = decision['sponsors']
    if not isinstance(sponsors, list) or any(not isinstance(s, str) or not s.strip() for s in sponsors):
        raise ValueError('Sponsors must be a list of nonempty names/aliases')
    exclusions = decision['exclusions']
    reasons = {}
    for entry in exclusions:
        require_ids(entry['segment_ids'], valid)
        if not isinstance(entry['reason'], str) or not entry['reason'].strip():
            raise ValueError('Every exclusion needs a reason')
        for identifier in entry['segment_ids']:
            reasons.setdefault(identifier, []).append(entry['reason'])
    # Strict user preference: remove every mention, including later brief plugs.
    patterns = [re.compile(r'(?<!\w)' + re.escape(s.strip()) + r'(?!\w)', re.I) for s in sponsors]
    for row in rows:
        if any(pattern.search(row['text']) for pattern in patterns):
            reasons.setdefault(row['id'], []).append('sponsor mention')
    kept = [row for row in rows if row['id'] not in reasons]
    save(path / 'exclusions.json', {'sponsors': sponsors, 'exclusions': [
        {'segment_id': row['id'], 'start': row['start'], 'duration': row['duration'],
         'reasons': reasons[row['id']]} for row in rows if row['id'] in reasons]})
    save(path / 'clean.json', {**raw, 'segments': kept})
    # Changing exclusions invalidates dependent analysis rather than silently reusing it.
    for name in ('sections.json', 'section-notes.json'):
        (path / name).unlink(missing_ok=True)
    return {'retained': len(kept), 'excluded': len(rows) - len(kept)}


def sections(path, value):
    rows = load(path / 'clean.json')['segments']
    valid = {row['id'] for row in rows}
    flattened = []
    names = []
    for entry in value:
        if not isinstance(entry['id'], str) or not entry['id'].strip() or not entry['title'].strip():
            raise ValueError('Sections need nonempty IDs and titles')
        require_ids(entry['segment_ids'], valid)
        if not entry['segment_ids']:
            raise ValueError('Sections must contain speech')
        flattened.extend(entry['segment_ids'])
        names.append(entry['id'])
    if len(names) != len(set(names)) or flattened != [row['id'] for row in rows]:
        raise ValueError('Sections must cover retained speech exactly once in original order')
    save(path / 'sections.json', value)
    (path / 'section-notes.json').unlink(missing_ok=True)
    return {'sections': len(value), 'coverage': 'complete'}


def notes(path, value):
    outline = load(path / 'sections.json')
    if [note['section_id'] for note in value] != [section['id'] for section in outline]:
        raise ValueError('One analysis required per section, in order')
    for note, section in zip(value, outline):
        if not isinstance(note['analysis'], str) or not note['analysis'].strip():
            raise ValueError('Each section needs an analysis')
        require_ids(note['evidence_ids'], set(section['segment_ids']))
        if not note['evidence_ids']:
            raise ValueError('Each analysis must cite source evidence')
    save(path / 'section-notes.json', value)
    return {'analyzed_sections': len(value)}


def verify(path):
    raw = load(path / 'raw.json')['segments']
    kept = load(path / 'clean.json')['segments']
    exclusions = load(path / 'exclusions.json')
    excluded = [entry['segment_id'] for entry in exclusions['exclusions']]
    if (len(excluded) != len(set(excluded)) or
            set(excluded) & {row['id'] for row in kept} or
            set(excluded) | {row['id'] for row in kept} != {row['id'] for row in raw}):
        raise ValueError('Exclusion coverage mismatch')
    if kept != [row for row in raw if row['id'] not in set(excluded)]:
        raise ValueError('Clean transcript altered original speech or timestamps')
    outline = load(path / 'sections.json')
    analyses = load(path / 'section-notes.json')
    # Reuse validation without invalidating or rewriting downstream artifacts.
    flattened = [i for section in outline for i in section['segment_ids']]
    if flattened != [row['id'] for row in kept]:
        raise ValueError('Section coverage mismatch')
    if [n['section_id'] for n in analyses] != [s['id'] for s in outline]:
        raise ValueError('Analysis coverage mismatch')
    for note, section in zip(analyses, outline):
        require_ids(note['evidence_ids'], set(section['segment_ids']))
        if not note['analysis'].strip() or not note['evidence_ids']:
            raise ValueError('Missing section analysis or evidence')
    return {'coverage': 'complete', 'retained_segments': len(kept), 'sections': len(outline)}


def read(path, artifact, offset, limit, section):
    value = load(path / (artifact + '.json'))
    if artifact in ('raw', 'clean'):
        rows = value['segments']
        if section:
            outline = load(path / 'sections.json')
            ids = next(s['segment_ids'] for s in outline if s['id'] == section)
            rows = [row for row in rows if row['id'] in set(ids)]
        return {**{k: v for k, v in value.items() if k != 'segments'}, 'offset': offset,
                'total_segments': len(rows), 'segments': rows[offset:offset + limit],
                'complete': offset + limit >= len(rows)}
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    p = commands.add_parser('start'); p.add_argument('url')
    p.add_argument('--languages', nargs='+', default=['en'])
    p.add_argument('--model', choices=['tiny', 'base', 'small', 'medium', 'large-v3'], default='small')
    commands.add_parser('prune')
    for command in ('read', 'clean', 'sections', 'notes', 'verify', 'finish', 'abort'):
        p = commands.add_parser(command); p.add_argument('run')
        if command == 'read':
            p.add_argument('artifact', choices=sorted(ARTIFACTS))
            p.add_argument('--offset', type=int, default=0); p.add_argument('--limit', type=int, default=60)
            p.add_argument('--section')
        if command in ('clean', 'sections', 'notes'):
            p.add_argument('--input', required=True, help='JSON filename within this run directory')
    args = parser.parse_args()
    run = None
    try:
        prune()
        if args.command == 'start':
            result = start(args.url, args.languages, args.model)
        elif args.command == 'prune':
            result = {'pruned': True}
        else:
            run = owned(args.run)
            with locked(run):
                if args.command in ('clean', 'sections', 'notes'):
                    if Path(args.input).name != args.input or not args.input.endswith('.json'):
                        raise ValueError('Input must be a JSON filename inside the run')
                    result = {'clean': clean, 'sections': sections, 'notes': notes}[args.command](run, load(run / args.input))
                elif args.command == 'read':
                    if args.offset < 0 or not 1 <= args.limit <= 200:
                        raise ValueError('Use nonnegative offset and limit from 1 to 200')
                    result = read(run, args.artifact, args.offset, args.limit, args.section)
                elif args.command in ('verify', 'finish'):
                    result = verify(run)
                    if args.command == 'finish':
                        shutil.rmtree(run); result['deleted'] = True
                else:
                    shutil.rmtree(run); result = {'deleted': True}
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except (Exception, KeyboardInterrupt) as exc:
        # Validation errors are recoverable by the agent; abort in its error handler.
        # An explicit interruption is terminal and cleans up this invocation's run.
        if isinstance(exc, KeyboardInterrupt) and run is not None:
            with locked(run):
                shutil.rmtree(run)
        print(json.dumps({'error': type(exc).__name__, 'message': str(exc)}), file=sys.stderr)
        return 130 if isinstance(exc, KeyboardInterrupt) else 1


if __name__ == '__main__':
    def interrupt(signum, frame):
        raise KeyboardInterrupt
    signal.signal(signal.SIGTERM, interrupt)
    sys.exit(main())
