import concurrent.futures
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from approval_log import Store


SCRIPT = str(Path(__file__).with_name('approval_log.py'))


class ReviewTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.home = Path(self.tmp.name)
        self.store = Store(self.home)

    def capture(self, command='cat a; git branch --show-current'):
        self.store.capture({'hook_event_name': 'PermissionRequest', 'tool_name': 'Bash',
                            'session_id': 'test', 'tool_input': {'command': command}})

    def report(self):
        path = self.home / 'report.md'
        path.write_text('Reviewed; approval and execution outcomes remain unknown.\n')
        return str(path)

    def test_capture_preserves_compound_command_without_claiming_approval(self):
        self.capture()
        event = self.store.events()[0]
        self.assertEqual(event['command'], 'cat a; git branch --show-current')
        self.assertEqual(event['approval_outcome'], 'unknown')
        self.assertEqual(os.stat(self.store.root).st_mode & 0o777, 0o700)
        self.assertEqual(os.stat(self.store.root / 'events.jsonl').st_mode & 0o777, 0o600)

    def test_hook_never_returns_a_decision_even_on_bad_input(self):
        for payload in ('not json', json.dumps({'hook_event_name': 'PermissionRequest',
                                               'tool_name': 'Bash',
                                               'tool_input': {'command': 'echo ok'}})):
            result = subprocess.run([sys.executable, SCRIPT, '--home', str(self.home), 'capture'],
                                    input=payload, text=True, capture_output=True)
            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stdout, '')

    def test_concurrent_append_produces_complete_unique_records(self):
        def write(i):
            payload = json.dumps({'hook_event_name': 'PermissionRequest', 'tool_name': 'Bash',
                                  'tool_input': {'command': str(i)}})
            return subprocess.run([sys.executable, SCRIPT, '--home', str(self.home), 'capture'],
                                  input=payload, text=True, capture_output=True)
        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
            results = list(pool.map(write, range(20)))
        self.assertTrue(all(r.returncode == 0 and not r.stdout for r in results))
        self.assertEqual(len(self.store.events()), 20)

    def test_batch_checkpoint_leaves_new_arrivals_pending(self):
        self.capture('first')
        self.capture('second')
        batch = self.store.prepare(1)
        self.assertTrue(batch['has_more'])
        self.capture('third')
        self.store.complete(batch['id'], self.report())
        pending = self.store.prepare(50)['events']
        self.assertEqual([e['command'] for e in pending], ['second', 'third'])

    def test_changed_policy_refuses_checkpoint(self):
        self.capture()
        batch = self.store.prepare(50)
        (self.home / 'hooks.json').write_text('{}')
        with self.assertRaisesRegex(ValueError, 'Policy changed'):
            self.store.complete(batch['id'], self.report())
        self.assertEqual(self.store.status()['pending_requests'], 1)

    def test_competing_review_refuses_checkpoint(self):
        self.capture()
        first, second = self.store.prepare(50), self.store.prepare(50)
        self.store.complete(first['id'], self.report())
        with self.assertRaisesRegex(ValueError, 'advanced the cursor'):
            self.store.complete(second['id'], self.report())

    def test_corruption_or_missing_cursor_stops_review(self):
        self.capture()
        batch = self.store.prepare(50)
        self.store.complete(batch['id'], self.report())
        (self.store.root / 'events.jsonl').write_text('')
        with self.assertRaisesRegex(ValueError, 'Checkpoint event missing'):
            self.store.prepare(50)

    def test_competing_empty_reviews_cannot_overwrite_checkpoint(self):
        first, second = self.store.prepare(50), self.store.prepare(50)
        self.store.complete(first['id'], self.report())
        with self.assertRaisesRegex(ValueError, 'advanced the cursor'):
            self.store.complete(second['id'], self.report())

    def test_empty_report_cannot_consume_events(self):
        self.capture()
        batch = self.store.prepare(50)
        path = self.home / 'empty.md'
        path.write_text('')
        with self.assertRaisesRegex(ValueError, 'empty'):
            self.store.complete(batch['id'], str(path))
        self.assertEqual(self.store.status()['pending_requests'], 1)

    def test_other_tools_do_not_capture_document_arguments(self):
        self.store.capture({'hook_event_name': 'PermissionRequest', 'tool_name': 'mcp__doc',
                            'tool_input': {'document': 'private content'}})
        self.assertNotIn('private content', json.dumps(self.store.events()))


if __name__ == '__main__':
    unittest.main()
