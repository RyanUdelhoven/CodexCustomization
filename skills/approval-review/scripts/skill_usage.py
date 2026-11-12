#!/usr/bin/env python3
"""Explicit skill intervals and private, per-attempt model usage observations."""
import argparse
import json
import os
from pathlib import Path
import re
import sys
import uuid

from approval_log import Store, now

METRICS = ('input_tokens', 'cached_input_tokens', 'output_tokens',
           'reasoning_output_tokens', 'total_tokens')


def counts(value):
    """Keep only known nonnegative counts. Cached/reasoning are included subsets."""
    value = value if isinstance(value, dict) else {}
    result = {key: value.get(key) if type(value.get(key)) is int and value[key] >= 0 else None
              for key in METRICS}
    for metric, parent, child in (
            ('cached_input_tokens', 'input_tokens_details', 'cached_tokens'),
            ('reasoning_output_tokens', 'output_tokens_details', 'reasoning_tokens')):
        details = value.get(parent)
        item = details.get(child) if isinstance(details, dict) else None
        if result[metric] is None and type(item) is int and item >= 0:
            result[metric] = item
    if result['total_tokens'] is None and all(result[k] is not None for k in ('input_tokens', 'output_tokens')):
        result['total_tokens'] = result['input_tokens'] + result['output_tokens']
    return result


def totals(samples):
    return {key: sum(s[key] for s in samples if s.get(key) is not None)
            if any(s.get(key) is not None for s in samples) else None for key in METRICS}


class Usage:
    def __init__(self, home):
        self.store = Store(home)

    def append(self, event):
        fd = os.open(self.store.root / 'model-usage.jsonl', os.O_CREAT | os.O_APPEND | os.O_WRONLY, 0o600)
        with os.fdopen(fd, 'a') as handle:
            handle.write(json.dumps(event) + '\n')
            handle.flush()
            os.fsync(handle.fileno())

    def start(self, session, skills, cwd, task='', agent=None):
        if not session or not skills or any(not re.fullmatch(r'[A-Za-z0-9_.:/-]{1,160}', s) for s in skills):
            raise ValueError('Provide a session and skill identifiers')
        if len(set(skills)) != len(skills):
            raise ValueError('Duplicate skill identifiers')
        with self.store.locked():
            runs = self.store.read('skill-runs.json', [])
            if any(r['session_id'] == session and r.get('agent_id') == agent and r['skill'] in skills
                   and not r.get('finished_at') for r in runs):
                raise ValueError('Skill already active in this scope; finish or reuse that run')
            added = [dict(id=str(uuid.uuid4()), session_id=session, skill=skill, cwd=str(Path(cwd).resolve()),
                          task_title=task or 'Unknown', agent_id=agent, started_at=now(),
                          finished_at=None, state='running', confidence='explicit_markers') for skill in skills]
            self.store.write('skill-runs.json', runs + added)
            return added

    def finish(self, ids, abandoned=False):
        with self.store.locked():
            runs = self.store.read('skill-runs.json', [])
            if set(ids) - {r['id'] for r in runs}:
                raise ValueError('Unknown run ID; no runs changed')
            for run in runs:
                if run['id'] in ids and not run['finished_at']:
                    run.update(finished_at=now(), state='abandoned' if abandoned else 'finished')
            self.store.write('skill-runs.json', runs)
            return [r for r in runs if r['id'] in ids]

    def capture(self, payload):
        if not isinstance(payload, dict) or payload.get('hook_event_name') not in ('PreModelRequest', 'PostModelRequest'):
            raise ValueError('Expected a model request hook')
        if not all(isinstance(payload.get(k), str) and payload[k] for k in ('session_id', 'turn_id')):
            raise ValueError('Missing session or turn identity')
        event = {k: payload[k] for k in ('session_id', 'turn_id', 'agent_id', 'agent_type', 'model', 'request_id')
                 if isinstance(payload.get(k), str)}
        event.update(timestamp=now(), hook_event_name=payload['hook_event_name'])
        # Separate agent/turn scopes. Never pair concurrent unidentified attempts by time.
        scope = json.dumps([event.get(k) for k in ('session_id', 'turn_id', 'agent_id')])
        with self.store.locked():
            state = self.store.read('usage-state.json', {'pending': {}})
            state['last_hook_at'] = event['timestamp']
            state['hook_events'] = state.get('hook_events', 0) + 1
            pending = state['pending'].setdefault(scope, [])
            if payload['hook_event_name'] == 'PreModelRequest':
                runs = self.store.read('skill-runs.json', [])
                run_ids = [r['id'] for r in runs if r['session_id'] == event['session_id']
                           and not r['finished_at'] and (r.get('agent_id') is None or r['agent_id'] == event.get('agent_id'))]
                if run_ids or pending:
                    request_id = event.get('request_id')
                    if not request_id or not any(p.get('request_id') == request_id for p in pending):
                        event.update(sample_id=str(uuid.uuid4()), run_ids=run_ids)
                        pending.append(event)
                        self.append(event)
            else:
                request_id = event.get('request_id')
                matches = [p for p in pending if p.get('request_id') == request_id] if request_id else pending[:]
                if len(matches) == 1 and (request_id or scope not in state.get('ambiguous_scopes', [])):
                    start = matches[0]
                    pending.remove(start)
                    event.update(sample_id=start['sample_id'], run_ids=start['run_ids'],
                                 token_usage=counts(payload.get('token_usage')),
                                 status=payload.get('status') if payload.get('status') in ('completed', 'failed', 'cancelled') else 'unknown')
                    self.append(event)
                elif matches:
                    # Leave each start without usage rather than manufacture a pairing.
                    # Quarantine this scope for unidentified posts for the rest
                    # of the turn: a later post might belong to any old attempt.
                    state.setdefault('ambiguous_scopes', [])
                    if scope not in state['ambiguous_scopes']:
                        state['ambiguous_scopes'].append(scope)
                    pending[:] = [p for p in pending if p not in matches]
                    state['ambiguous_posts'] = state.get('ambiguous_posts', 0) + 1
            if not pending:
                state['pending'].pop(scope, None)
            self.store.write('usage-state.json', state)

    def snapshot(self, approvals=()):
        with self.store.locked():
            runs = self.store.read('skill-runs.json', [])
            path = self.store.root / 'model-usage.jsonl'
            journal = [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []
            health = self.store.read('usage-state.json', {})
        starts = {r['sample_id']: r for r in journal if r['hook_event_name'] == 'PreModelRequest' and r['run_ids']}
        ends = {r['sample_id']: r for r in journal if r['hook_event_name'] == 'PostModelRequest' and r['sample_id'] in starts}
        by_id = {r['id']: r for r in runs}
        for run in runs:
            selected = [s for s in starts.values() if run['id'] in s['run_ids']]
            observed = [ends[s['sample_id']] for s in selected if s['sample_id'] in ends]
            usage = [s['token_usage'] for s in observed]
            run['tokens'] = totals(usage)
            run['request_count'] = len(selected)
            run['reported_requests'] = sum(u['input_tokens'] is not None and u['output_tokens'] is not None for u in usage)
            run['missing_usage_requests'] = len(selected) - run['reported_requests']
            run['coverage'] = 'no_observed_requests' if not selected else 'partial' if run['missing_usage_requests'] else 'observed_requests'
            run['shared_with'] = sorted({by_id[i]['skill'] for s in selected for i in s['run_ids'] if i != run['id'] and i in by_id})
            run['shared_request_count'] = sum(len(s['run_ids']) > 1 for s in selected)
            run['samples'] = [dict(sample_id=s['sample_id'], started_at=s['timestamp'],
                                   finished_at=ends.get(s['sample_id'], {}).get('timestamp'),
                                   status=ends.get(s['sample_id'], {}).get('status', 'pending_or_unmatched'),
                                   model=s.get('model'), agent_id=s.get('agent_id'),
                                   turn_id=s['turn_id'], run_ids=s['run_ids'],
                                   tokens=ends.get(s['sample_id'], {}).get('token_usage', counts(None))) for s in selected]
            run['approval_request_ids'] = [a['id'] for a in approvals if a.get('session_id') == run['session_id']
                                           and run['started_at'] <= a['timestamp']
                                           and (not run['finished_at'] or a['timestamp'] <= run['finished_at'])]
        return dict(runs=list(reversed(runs)), unique_request_count=len(starts),
                    unique_tokens=totals([s['token_usage'] for s in ends.values()]),
                    last_hook_at=health.get('last_hook_at'), hook_events=health.get('hook_events', 0),
                    ambiguous_posts=health.get('ambiguous_posts', 0),
                    basis='Whole model attempts starting while explicit markers are active; shared totals are not additive. No causal attribution or savings measurement.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--home', default=os.environ.get('CODEX_HOME', str(Path.home() / '.codex')))
    sub = parser.add_subparsers(dest='action', required=True)
    sub.add_parser('capture')
    start = sub.add_parser('start')
    start.add_argument('--session', required=True)
    start.add_argument('--skills', nargs='+', required=True)
    start.add_argument('--cwd', default=os.getcwd())
    start.add_argument('--task', default='')
    start.add_argument('--agent-id')
    finish = sub.add_parser('finish')
    finish.add_argument('--runs', nargs='+', required=True)
    finish.add_argument('--abandoned', action='store_true')
    sub.add_parser('status')
    args = parser.parse_args()
    usage = Usage(args.home)
    try:
        if args.action == 'capture':
            usage.capture(json.load(sys.stdin))
        elif args.action == 'start':
            print(json.dumps(usage.start(args.session, args.skills, args.cwd, args.task, args.agent_id), indent=2))
        elif args.action == 'finish':
            print(json.dumps(usage.finish(args.runs, args.abandoned), indent=2))
        else:
            print(json.dumps(usage.snapshot(), indent=2))
    except (OSError, ValueError, KeyError, TypeError):
        print('skill-usage: capture unavailable' if args.action == 'capture' else 'skill-usage: unavailable; inspect arguments and local storage', file=sys.stderr)
        return 0 if args.action == 'capture' else 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
