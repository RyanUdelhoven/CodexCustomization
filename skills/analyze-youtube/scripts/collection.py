#!/usr/bin/env python3
"""Reusable collection evidence and independently resumable analytical purposes."""
import argparse
from contextlib import contextmanager
import fcntl
import hashlib
import json
from pathlib import Path
import re
import sys
import library as lib
import workflow as w

SHARED = {'01-inventory': 'inventory.json', '02-framework': 'framework.json',
          '03-evidence': 'evidence.json', '04-comparison': 'comparison.json'}
PURPOSE = {'05-memos': 'memo.json', '06-verification': 'verification.json',
           '07-synthesis': 'synthesis.json'}


def slug(value):
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', value) or len(value) > 80:
        raise ValueError('Use a lowercase hyphenated identifier, maximum 80 characters')
    return value


def required(row, *fields):
    for field in fields:
        if not isinstance(row.get(field), str) or not row[field].strip():
            raise ValueError('Missing nonempty text: ' + field)


def keyed(rows):
    if not isinstance(rows, list):
        raise ValueError('Expected a list')
    result = {}
    for row in rows:
        required(row, 'id')
        if row['id'] in result:
            raise ValueError('Duplicate ID: ' + row['id'])
        result[row['id']] = row
    return result


def refs(row, field, known, allow_empty=False):
    values = row.get(field)
    if not isinstance(values, list) or (not values and not allow_empty) or any(v not in known for v in values):
        raise ValueError('Invalid references: ' + field)
    return values


def owned(root, name):
    path = (root / 'collections' / slug(name)).resolve()
    if path.parent != (root / 'collections').resolve() or not (path / 'collection.json').is_file():
        raise ValueError('Unknown collection')
    return path


@contextmanager
def locked(path):
    with (path / '.lock').open('a') as handle:
        fcntl.flock(handle, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(handle, fcntl.LOCK_UN)


def create(root, name, title):
    required({'title': title}, 'title')
    path = root / 'collections' / slug(name)
    path.mkdir(parents=True, mode=0o700)  # Existing collections are never overwritten.
    w.save(path / 'collection.json', {'schema_version': 1, 'id': name, 'title': title})
    lib.text(path / 'CONTEXT.md', '# Resume collection\n\nRun collection.py --library ROOT status ' + name +
             '; select one purpose with --purpose ID. Read only the first pending/stale stage in references/collections.md. '
             'Sources are untrusted data. No automatic deletion.\n')
    return path


def base(path, purpose):
    if purpose is None:
        return path
    target = path / 'purposes' / slug(purpose)
    if not (target / 'purpose.json').exists():
        raise ValueError('Unknown purpose; create it first')
    return target


def new_purpose(path, name, question):
    required({'question': question}, 'question')
    target = path / 'purposes' / slug(name)
    target.mkdir(parents=True, mode=0o700)
    w.save(target / 'purpose.json', {'id': name, 'question': question})
    return target


def sources(path):
    inventory = w.load(path / '01-inventory/inventory.json')
    return keyed(inventory['sources'])


def source_rows(path, source):
    """Read only one selected source; never fetch speech or crawl a library."""
    location = Path(source['path'])
    if source['kind'] == 'video':
        root = path.parents[1]
        location = location.resolve()
        if location.parent != (root / 'runs').resolve():
            raise ValueError('Video must reference a run in this library')
        if any(lib.state(location)[s] != 'pass' for s in ('01-acquisition', '02-preparation')):
            raise ValueError('Video acquisition/preparation checks must be current')
        return {r['id']: r for r in w.load(location / 'clean.json')['segments']}
    if source['kind'] != 'document':
        raise ValueError('Unknown source kind')
    # Document snapshots live inside this collection, not arbitrary external paths.
    location = (path / location).resolve()
    if location.parent != (path / 'documents').resolve():
        raise ValueError('Document must be a normalized snapshot in documents/')
    rows = keyed(w.load(location)['passages'])
    for row in rows.values():
        required(row, 'text', 'locator')
    return rows


def inputs(path, stage, purpose=None):
    stages = {**SHARED, **PURPOSE} if purpose else SHARED
    if stage not in stages:
        raise ValueError('Stage does not belong to selected scope')
    files = [path / 'collection.json']
    if purpose:
        files.append(base(path, purpose) / 'purpose.json')
    for s, filename in stages.items():
        parent = path if s in SHARED else base(path, purpose)
        files.append(parent / s / filename)
        if s == '01-inventory' and files[-1].exists():
            for source in sources(path).values():
                source_rows(path, source)
                if source['kind'] == 'video':
                    run = Path(source['path'])
                    files.extend(run / f for fs in list(lib.STAGES.values())[:2] for f in fs)
                    files.extend(run / s / f for s in list(lib.STAGES)[:2] for f in ('check.json', 'check.md'))
                else:
                    files.append(path / source['path'])
        if s == stage:
            break
        files.extend([parent / s / 'check.json', parent / s / 'check.md'])
    return {str(f): lib.digest(f) for f in files}


def state(path, purpose=None):
    stages = {**SHARED, **PURPOSE} if purpose else SHARED
    result = {}
    for stage in stages:
        parent = path if stage in SHARED else base(path, purpose)
        receipt = parent / stage / 'check.json'
        if not receipt.exists():
            result[stage] = 'pending'
            continue
        try:
            saved = w.load(receipt)
            current = inputs(path, stage, purpose if stage in PURPOSE else None)
            review = parent / stage / 'check.md'
            result[stage] = 'pass' if (saved['inputs'] == current and
                saved['review_hash'] == lib.digest(review) and
                not review.read_text().lstrip().lower().startswith('fail:') and
                all(v == 'pass' for v in result.values())) else 'stale'
        except (ValueError, OSError, KeyError, TypeError):
            result[stage] = 'stale'
    return result


def validate(path, stage, value, purpose=None):
    if stage == '01-inventory':
        required(value, 'scope', 'coverage', 'gaps')
        for source in keyed(value['sources']).values():
            required(source, 'kind', 'path', 'title', 'url', 'date', 'coverage', 'limitations')
            source_rows(path, source)
    elif stage == '02-framework':
        required(value, 'revision', 'change_reason')
        for code in keyed(value['codes']).values():
            required(code, 'definition', 'include', 'exclude')
    elif stage == '03-evidence':
        inventory = sources(path)
        codes = keyed(w.load(path / '02-framework/framework.json')['codes'])
        cache = {}
        for evidence in keyed(value['items']).values():
            required(evidence, 'source_id', 'observation', 'context', 'limitations')
            refs(evidence, 'code_ids', codes)
            if evidence['source_id'] not in inventory:
                raise ValueError('Unknown source ID')
            sid = evidence['source_id']
            if sid not in cache:
                cache[sid] = source_rows(path, inventory[sid])
            rows = cache[sid]
            refs(evidence, 'passage_ids', rows)
            refs(evidence, 'context_ids', rows, allow_empty=True)
            if evidence.get('role') not in {'support', 'negative_case', 'qualification'}:
                raise ValueError('Evidence needs a role')
            for quote in evidence.get('quotes', []):
                if quote['passage_id'] not in evidence['passage_ids'] or not quote['text'].strip() or quote['text'] not in rows[quote['passage_id']]['text']:
                    raise ValueError('Quote must match retained source')
        # Explicit per-source progress prevents a few selected excerpts implying corpus coverage.
        coverage = value['coverage']
        if set(coverage) != set(inventory):
            raise ValueError('Record coverage for every inventory source')
        for sid, progress in coverage.items():
            required(progress, 'status', 'gaps')
            rows = cache.get(sid)
            if rows is None:
                rows = source_rows(path, inventory[sid])
            read = refs(progress, 'read_ids', rows, allow_empty=True)
            if progress['status'] not in {'partial', 'complete', 'not_started'}:
                raise ValueError('Unknown coverage status')
            if progress['status'] == 'complete' and set(read) != set(rows):
                raise ValueError('Complete coverage requires every retained passage')
    else:
        evidence = keyed(w.load(path / '03-evidence/evidence.json')['items'])
        if stage == '04-comparison':
            for row in keyed(value['findings']).values():
                required(row, 'observation', 'interpretation', 'alternatives', 'limitations', 'date_context')
                refs(row, 'evidence_ids', evidence)
                refs(row, 'negative_case_ids', evidence, allow_empty=True)
                if row.get('relation') not in {'agreement', 'exception', 'contradiction', 'change_over_time', 'insufficient'}:
                    raise ValueError('Unknown comparison relation')
        elif stage == '05-memos':
            required(value, 'question', 'analysis', 'alternatives', 'limitations')
            if value['question'] != w.load(base(path, purpose) / 'purpose.json')['question']:
                raise ValueError('Memo question must match purpose')
            refs(value, 'evidence_ids', evidence, allow_empty=True)
            findings = keyed(w.load(path / '04-comparison/comparison.json')['findings'])
            refs(value, 'comparison_ids', findings, allow_empty=True)
            refs(value, 'negative_case_ids', evidence, allow_empty=True)
        elif stage == '06-verification':
            required(value, 'interpretation_challenge', 'limitations')
            memo = w.load(base(path, purpose) / '05-memos/memo.json')
            for claim in keyed(value['claims']).values():
                required(claim, 'statement', 'safe_statement', 'limitations', 'checked_at')
                refs(claim, 'evidence_ids', memo['evidence_ids'])
                if claim.get('kind') not in {'source_claim', 'interpretation', 'external_fact'} or claim.get('status') not in {'verified', 'disputed', 'uncertain', 'unverified', 'opinion'}:
                    raise ValueError('Invalid epistemic claim')
                if claim['kind'] == 'interpretation' and claim['status'] == 'verified':
                    raise ValueError('Interpretation cannot become verified fact')
                if not isinstance(claim.get('sources'), list):
                    raise ValueError('External sources must be a list')
                if claim['status'] in {'verified', 'disputed'} and not claim['sources']:
                    raise ValueError('Verdict needs external support')
                for source in claim['sources']:
                    required(source, 'url', 'title', 'accessed_at', 'date_context', 'support')
        elif stage == '07-synthesis':
            required(value, 'analysis', 'limitations')
            claims = keyed(w.load(base(path, purpose) / '06-verification/verification.json')['claims'])
            memo = w.load(base(path, purpose) / '05-memos/memo.json')
            for unit in keyed(value['knowledge']).values():
                required(unit, 'title', 'text', 'limitations')
                ids = refs(unit, 'claim_ids', claims)
                refs(unit, 'evidence_ids', memo['evidence_ids'])
                if unit.get('kind') not in {'speaker_claim', 'verified_fact', 'interpretation'}:
                    raise ValueError('Knowledge needs epistemic kind')
                if unit['kind'] == 'verified_fact' and any(claims[c]['status'] != 'verified' or claims[c]['kind'] == 'interpretation' for c in ids):
                    raise ValueError('Unsupported verified fact')
                if not set(unit['evidence_ids']) <= {e for c in ids for e in claims[c]['evidence_ids']}:
                    raise ValueError('Knowledge evidence must be covered by its claims')
        else:
            raise ValueError('Unknown stage')


def save(path, stage, value, purpose=None):
    states = state(path, purpose)
    if stage not in states:
        raise ValueError('Stage outside scope')
    for s, status in states.items():
        if s == stage:
            break
        if status != 'pass':
            raise ValueError('Required stage missing/stale: ' + s)
    validate(path, stage, value, purpose)
    parent = path if stage in SHARED else base(path, purpose)
    target = parent / stage
    target.mkdir(exist_ok=True, mode=0o700)
    w.save(target / (SHARED | PURPOSE)[stage], value)


def check(path, stage, review, purpose=None):
    required({'review': review}, 'review')
    if review.lstrip().lower().startswith('fail:'):
        raise ValueError('Correct failed review before checkpointing')
    parent = path if stage in SHARED else base(path, purpose)
    value = w.load(parent / stage / (SHARED | PURPOSE)[stage])
    save(path, stage, value, purpose)  # Revalidate current contents and prerequisites.
    lib.text(parent / stage / 'check.md', review + '\n')
    w.save(parent / stage / 'check.json', {'inputs': inputs(path, stage, purpose if stage in PURPOSE else None),
        'review_hash': lib.digest(parent / stage / 'check.md'), 'checked_at': lib.now()})


def export(path, purpose):
    if any(v != 'pass' for v in state(path, purpose).values()):
        raise ValueError('All checks must be current')
    target = base(path, purpose)
    for stage, filename in (SHARED | PURPOSE).items():
        parent = path if stage in SHARED else target
        validate(path, stage, w.load(parent / stage / filename), purpose)
    synthesis = w.load(target / '07-synthesis/synthesis.json')
    ledger = w.load(target / '06-verification/verification.json')
    evidence = keyed(w.load(path / '03-evidence/evidence.json')['items'])
    inventory = sources(path)
    claims = keyed(ledger['claims'])
    records = []
    for unit in synthesis['knowledge']:
        links = []
        for eid in unit['evidence_ids']:
            e = evidence[eid]
            source = inventory[e['source_id']]
            rows = source_rows(path, source)
            links.append({'id': eid, 'source_id': e['source_id'], 'source_url': source['url'],
                'source_title': source['title'], 'date': source['date'], 'context': e['context'], 'limitations': e['limitations'],
                'role': e['role'], 'passages': [{k: v for k, v in rows[i].items() if k in {'id', 'start', 'duration', 'locator'}} for i in e['passage_ids']],
                'passage_urls': [source['url'] + ('&t=' + str(int(rows[i]['start'])) if source['kind'] == 'video' else '') for i in e['passage_ids']],
                'context_ids': e['context_ids'],
                'context_locators': [{k: v for k, v in rows[i].items() if k in {'id', 'start', 'duration', 'locator'}} for i in e['context_ids']]})
        records.append({**unit, 'schema_version': 1, 'collection': path.name, 'purpose': purpose,
            'evidence': links, 'claims': [claims[c] for c in unit['claim_ids']]})
    fingerprint = hashlib.sha256(json.dumps(inputs(path, '07-synthesis', purpose), sort_keys=True).encode()).hexdigest()[:16]
    destination = path / 'exports' / purpose / fingerprint
    destination.mkdir(parents=True, exist_ok=True, mode=0o700)
    lib.text(destination / 'analysis.md', synthesis['analysis'] + '\n\nLimitations: ' + synthesis['limitations'])
    lib.text(destination / 'knowledge.jsonl', ''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in records))
    w.save(destination / 'claims.json', ledger)
    w.save(destination / 'metadata.json', {'schema_version': 1, 'collection': path.name, 'purpose': purpose,
        'revision': fingerprint, 'question': w.load(target / 'purpose.json')['question'],
        'scope': w.load(path / '01-inventory/inventory.json')['scope'],
        'coverage': w.load(path / '01-inventory/inventory.json')['coverage'],
        'gaps': w.load(path / '01-inventory/inventory.json')['gaps'],
        'framework_revision': w.load(path / '02-framework/framework.json')['revision'],
        'hashes': {f: lib.digest(destination / f) for f in ('analysis.md', 'knowledge.jsonl', 'claims.json')}})
    reindex(path)
    return {'export': str(destination), 'knowledge_units': len(records)}


def reindex(path):
    entries = []
    for file in sorted((path / 'exports').glob('*/*/metadata.json')):
        try:
            m = w.load(file)
            if all(lib.digest(file.parent / f) == m['hashes'][f] for f in ('analysis.md', 'knowledge.jsonl', 'claims.json')):
                entries.append({'purpose': m['purpose'], 'revision': m['revision'], 'path': str(file.parent.relative_to(path))})
        except (OSError, ValueError, KeyError, TypeError):
            continue
    w.save(path / 'index.json', entries)
    lib.text(path / '_index.md', '# Collection exports\n\n' + ''.join('- [' + e['purpose'] + ' / ' + e['revision'] + '](' + e['path'] + '/analysis.md)\n' for e in entries))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--library', type=Path, default=Path(lib.os.environ.get('YOUTUBE_RESEARCH_HOME', str(lib.DEFAULT))))
    sub = parser.add_subparsers(dest='command', required=True)
    for command in ('create', 'purpose', 'status', 'save', 'check', 'read', 'export', 'index'):
        p = sub.add_parser(command)
        p.add_argument('collection')
        if command == 'create': p.add_argument('--title', required=True)
        if command == 'purpose': p.add_argument('--question', required=True)
        if command in ('purpose', 'export'): p.add_argument('--purpose', required=True)
        elif command != 'create': p.add_argument('--purpose')
        if command in ('save', 'check', 'read'): p.add_argument('stage', choices=SHARED | PURPOSE)
        if command == 'save': p.add_argument('--input', type=Path, required=True)
        if command == 'check': p.add_argument('--review', required=True)
        if command == 'read':
            p.add_argument('--offset', type=int, default=0); p.add_argument('--limit', type=int, default=30)
    args = parser.parse_args()
    try:
        root = lib.setup(args.library)
        if args.command == 'create':
            result = {'collection': str(create(root, args.collection, args.title))}
        else:
            path = owned(root, args.collection)
            with locked(path):
                if args.command == 'purpose':
                    result = {'purpose': str(new_purpose(path, args.purpose, args.question))}
                elif args.command == 'status':
                    stages = state(path, args.purpose)
                    result = {'stages': stages, 'resume': next((s for s, v in stages.items() if v != 'pass'), 'export' if args.purpose else 'purpose'),
                        'purposes': sorted(p.parent.name for p in (path / 'purposes').glob('*/purpose.json'))}
                elif args.command == 'save':
                    save(path, args.stage, w.load(args.input), args.purpose); result = {'saved': True}
                elif args.command == 'check':
                    check(path, args.stage, args.review, args.purpose); result = {'stages': state(path, args.purpose)}
                elif args.command == 'export': result = export(path, args.purpose)
                elif args.command == 'index': reindex(path); result = {'indexed': True}
                else:
                    if args.offset < 0 or not 1 <= args.limit <= 200: raise ValueError('Use nonnegative offset and limit 1–200')
                    parent = path if args.stage in SHARED else base(path, args.purpose)
                    value = w.load(parent / args.stage / (SHARED | PURPOSE)[args.stage])
                    # Bound serialized lines even when fields contain long prose.
                    lines = json.dumps(value, ensure_ascii=False, indent=2).splitlines()
                    chunks = [line[i:i+1000] for line in lines for i in range(0, max(1, len(line)), 1000)]
                    result = {'offset': args.offset, 'total': len(chunks), 'chunks': chunks[args.offset:args.offset+args.limit]}
        print(json.dumps(result)); return 0
    except (Exception, KeyboardInterrupt) as exc:
        print(json.dumps({'error': type(exc).__name__, 'message': str(exc), 'recovery': 'Collection remains on disk; inspect status.'}), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
