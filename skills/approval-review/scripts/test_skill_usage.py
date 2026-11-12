import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from approval_tracker import Tracker
from skill_usage import Usage, counts


class UsageTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.home = Path(self.tmp.name)
        self.usage = Usage(self.home)

    def start(self, skills=('approval-review',), session='session', agent=None):
        return self.usage.start(session, list(skills), self.home, 'Test task', agent)

    def hook(self, kind, **fields):
        payload = dict(hook_event_name=kind, session_id='session', turn_id='turn', model='test-model')
        payload.update(fields)
        self.usage.capture(payload)

    def request(self, usage=None, **fields):
        self.hook('PreModelRequest', **fields)
        self.hook('PostModelRequest', token_usage=usage, status='completed', **fields)

    def test_counts_preserve_subsets_zero_and_missing(self):
        self.assertEqual(counts({'input_tokens': 100, 'cached_input_tokens': 80,
                                 'output_tokens': 20, 'reasoning_output_tokens': 10})['total_tokens'], 120)
        self.assertEqual(counts({'input_tokens': 0, 'output_tokens': 0})['total_tokens'], 0)
        self.assertIsNone(counts({'input_tokens': True, 'output_tokens': -1})['total_tokens'])
        self.assertEqual(counts({'input_tokens_details': {'cached_tokens': 12}})['cached_input_tokens'], 12)
        self.assertTrue(all(v is None for v in counts(None).values()))

    def test_interval_membership_shared_totals_and_approval_links(self):
        self.request({'input_tokens': 999, 'output_tokens': 999})  # Before start: excluded.
        runs = self.start(('approval-review', 'context-audit'))
        self.request({'input_tokens': 100, 'cached_input_tokens': 80, 'output_tokens': 20})
        self.usage.finish([r['id'] for r in runs])
        self.request({'input_tokens': 999, 'output_tokens': 999})  # After finish: excluded.
        data = self.usage.snapshot([dict(id='approval', session_id='session', timestamp=runs[-1]['started_at'])])
        self.assertEqual(data['unique_tokens']['total_tokens'], 120)
        self.assertEqual(data['unique_request_count'], 1)
        for run in data['runs']:
            self.assertEqual(run['tokens']['total_tokens'], 120)
            self.assertEqual(run['shared_request_count'], 1)
            self.assertEqual(run['approval_request_ids'], ['approval'])
            self.assertEqual(run['coverage'], 'observed_requests')

    def test_missing_usage_is_not_zero_and_failed_attempts_count(self):
        run = self.start()[0]
        self.assertIsNone(self.usage.snapshot()['runs'][0]['tokens']['input_tokens'])
        self.request(None)
        self.hook('PreModelRequest')
        self.hook('PostModelRequest', token_usage={'input_tokens': 5, 'output_tokens': 3}, status='failed', error='SECRET')
        measured = self.usage.snapshot()['runs'][0]
        self.assertEqual(measured['tokens']['input_tokens'], 5)
        self.assertEqual(measured['coverage'], 'partial')
        self.assertEqual(measured['reported_requests'], 1)
        self.assertEqual(measured['missing_usage_requests'], 1)
        self.assertNotIn('SECRET', (self.usage.store.root / 'model-usage.jsonl').read_text())
        self.usage.finish([run['id']], abandoned=True)
        self.assertEqual(self.usage.snapshot()['runs'][0]['state'], 'abandoned')

    def test_ambiguous_concurrent_attempts_are_not_paired_by_timestamp(self):
        self.start()
        self.hook('PreModelRequest')
        self.hook('PreModelRequest')
        self.hook('PostModelRequest', token_usage={'input_tokens': 1000, 'output_tokens': 2})
        data = self.usage.snapshot()
        self.assertEqual(data['ambiguous_posts'], 1)
        self.assertIsNone(data['runs'][0]['tokens']['input_tokens'])
        self.assertEqual(data['runs'][0]['missing_usage_requests'], 2)

    def test_supplied_ids_pair_concurrent_requests_and_duplicate_posts(self):
        self.start()
        self.hook('PreModelRequest', request_id='a')
        self.hook('PreModelRequest', request_id='b')
        self.hook('PostModelRequest', request_id='b', token_usage={'input_tokens': 20, 'output_tokens': 3})
        self.hook('PostModelRequest', request_id='a', token_usage={'input_tokens': 10, 'output_tokens': 2})
        self.hook('PostModelRequest', request_id='a', token_usage={'input_tokens': 10, 'output_tokens': 2})
        data = self.usage.snapshot()
        self.assertEqual(data['unique_tokens']['input_tokens'], 30)
        self.assertEqual(data['unique_request_count'], 2)

    def test_agent_session_turn_isolation_and_boundary_crossing(self):
        run = self.start(agent='agent-a')[0]
        self.request({'input_tokens': 999}, agent_id='agent-b')
        self.request({'input_tokens': 999}, session_id='another')
        self.hook('PreModelRequest', agent_id='agent-a')
        self.usage.finish([run['id']])
        self.hook('PostModelRequest', agent_id='agent-a', turn_id='other', token_usage={'input_tokens': 999})
        self.hook('PostModelRequest', agent_id='agent-a', token_usage={'input_tokens': 4, 'output_tokens': 2})
        data = self.usage.snapshot()
        self.assertEqual(data['runs'][0]['request_count'], 1)
        self.assertEqual(data['unique_tokens']['input_tokens'], 4)

    def test_marker_validation_is_atomic_and_private_exports_omit_free_text(self):
        run = self.start(('secret-skill',))[0]
        with self.assertRaises(ValueError):
            self.start(('secret-skill',))
        with self.assertRaises(ValueError):
            self.usage.finish([run['id'], 'missing'])
        self.assertEqual(self.usage.snapshot()['runs'][0]['state'], 'running')
        self.request({'input_tokens': 1, 'output_tokens': 2}, prompt='SECRET')
        exported = Tracker(self.home).snapshot(redacted=True)
        encoded = json.dumps(exported)
        for text in ('secret-skill', 'Test task', str(self.home), 'SECRET', 'test-model'):
            self.assertNotIn(text, encoded)
        for filename in ('model-usage.jsonl', 'skill-runs.json', 'usage-state.json'):
            self.assertEqual((self.usage.store.root / filename).stat().st_mode & 0o777, 0o600)
        self.usage.finish([run['id']])
        self.usage.finish([run['id']])  # Idempotent.

    def test_hook_errors_return_success_without_decisions(self):
        script = Path(__file__).with_name('skill_usage.py')
        for payload in ('not json', '{}'):
            result = subprocess.run([sys.executable, str(script), '--home', str(self.home), 'capture'],
                                    input=payload, text=True, capture_output=True)
            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stdout, '')

    def test_abandoned_late_posts_cannot_be_misattributed_to_a_later_run(self):
        run = self.start()[0]
        self.hook('PreModelRequest')
        self.usage.finish([run['id']], abandoned=True)
        self.start()
        self.request({'input_tokens': 4, 'output_tokens': 2})
        runs = self.usage.snapshot()['runs']
        self.assertIsNone(runs[0]['tokens']['total_tokens'])
        self.assertIsNone(runs[1]['tokens']['total_tokens'])
        self.request({'input_tokens': 50, 'output_tokens': 20})  # Quarantined same turn.
        self.assertIsNone(self.usage.snapshot()['runs'][0]['tokens']['total_tokens'])
        self.request({'input_tokens': 4, 'output_tokens': 2}, turn_id='fresh-turn')
        self.assertEqual(self.usage.snapshot()['runs'][0]['tokens']['total_tokens'], 6)

    def test_unmeasured_request_cannot_supply_a_missing_end_for_a_closed_run(self):
        run = self.start()[0]
        self.hook('PreModelRequest')
        self.usage.finish([run['id']])
        self.request({'input_tokens': 400, 'output_tokens': 200})
        data = self.usage.snapshot()
        self.assertIsNone(data['runs'][0]['tokens']['total_tokens'])
        self.assertEqual(data['unique_request_count'], 1)


if __name__ == '__main__':
    unittest.main()
