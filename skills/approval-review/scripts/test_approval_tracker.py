import concurrent.futures
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from urllib.request import urlopen
from urllib.error import HTTPError

from approval_log import Store
from approval_tracker import Tracker

SCRIPT = Path(__file__).with_name('approval_tracker.py')


class TrackerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.home = Path(self.tmp.name)
        self.store, self.tracker = Store(self.home), Tracker(self.home)

    def capture(self, command='cat "a file"; echo "$TOKEN"', **extra):
        payload = dict(hook_event_name='PermissionRequest', tool_name='Bash',
                       cwd=str(self.home), session_id='session', turn_id='turn',
                       tool_input=dict(command=command, justification='Permit this exact command?',
                                       prefix_rule=['cat']))
        payload.update(extra)
        self.store.capture(payload)

    def test_metadata_exact_commands_and_conservative_grouping(self):
        (self.home / '.git').mkdir()
        self.capture()
        self.capture()
        self.capture('cat a')
        data = self.tracker.snapshot()
        self.assertEqual(data['candidates'][0]['count'], 2)
        row = data['rows'][-1]
        self.assertEqual(row['command'], 'cat "a file"; echo "$TOKEN"')
        self.assertEqual(row['reason'], 'Permit this exact command?')
        self.assertEqual(row['requested_prefix'], ['cat'])
        self.assertEqual(row['project_root'], str(self.home))
        self.assertEqual(row['outcome'], 'unknown')
        self.assertEqual(len(row['policy_hash']), 64)

    def test_duplicate_delivery_requires_reliable_id_and_preserves_retries(self):
        self.capture(tool_use_id='call')
        self.capture(tool_use_id='call')
        self.capture(tool_use_id='call', turn_id='retry')
        self.assertEqual(len(self.store.events()), 2)

    def test_missing_commands_do_not_form_false_repeat_groups(self):
        self.capture(tool_input={})
        self.capture(tool_input={})
        data = self.tracker.snapshot()
        self.assertEqual(len(data['candidates']), 2)
        self.assertTrue(all(r['repeat_count'] == 1 for r in data['rows']))

    def test_annotation_audit_evidence_and_task_labels(self):
        self.capture()
        event = self.store.events()[0]
        with self.assertRaises(ValueError):
            self.tracker.annotate(event['id'], 'resolved', 'user_approved', '', '', '', '')
        self.tracker.annotate(event['id'], 'investigating', 'unknown', '', 'review', '', '')
        self.tracker.annotate(event['id'], 'resolved', 'user_approved', 'user turn 12', '', 'cat', 'checked')
        self.tracker.label('session', 'Known title', 'native chat tool')
        row = self.tracker.snapshot()['rows'][0]
        self.assertEqual(row['status'], 'resolved')
        self.assertEqual(row['task_title'], 'Known title')
        self.assertEqual(self.store.events()[0]['approval_outcome'], 'unknown')
        with self.tracker.database() as db:
            self.assertEqual(db.execute('SELECT count(*) FROM audit').fetchone()[0], 3)
        self.assertEqual((self.store.root / 'tracker.sqlite3').stat().st_mode & 0o777, 0o600)

    def test_redaction_omits_all_free_text_and_export_refuses_overwrite(self):
        self.capture('echo credential-SENSITIVE')
        event = self.store.events()[0]
        self.tracker.annotate(event['id'], 'new', 'unknown', '', 'credential-SENSITIVE', '', '')
        data = self.tracker.snapshot(redacted=True)
        self.assertNotIn('SENSITIVE', json.dumps(data))
        self.assertNotIn(str(self.home), json.dumps(data))
        target = self.home / 'export.json'
        command = [sys.executable, str(SCRIPT), '--home', str(self.home), 'export', '--output', str(target)]
        self.assertEqual(subprocess.run(command, capture_output=True).returncode, 0)
        self.assertEqual(target.stat().st_mode & 0o777, 0o600)
        self.assertNotEqual(subprocess.run(command, capture_output=True).returncode, 0)

    def test_http_authorization_refresh_and_no_mutation(self):
        process = subprocess.Popen([sys.executable, str(SCRIPT), '--home', str(self.home), 'serve'],
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        def cleanup():
            process.terminate()
            process.communicate(timeout=5)
        self.addCleanup(cleanup)
        url = process.stdout.readline().strip()
        self.assertTrue(url.startswith('http://127.0.0.1:'))
        base, query = url.split('?', 1)
        with self.assertRaises(HTTPError) as error:
            urlopen(base, timeout=5)
        self.assertEqual(error.exception.code, 403)
        error.exception.close()
        with urlopen(url, timeout=5) as response:
            self.assertIn('Approval tracker', response.read().decode())
            self.assertEqual(response.headers['Cache-Control'], 'no-store')
        def read():
            with urlopen(base + 'data?' + query, timeout=5) as response:
                return json.load(response)
        self.assertEqual(read()['count'], 0)
        self.capture('</script><script>alert(1)</script>')
        self.assertEqual(read()['count'], 1)
        self.assertEqual(read()['rows'][0]['command'], '</script><script>alert(1)</script>')
        (self.store.root / 'events.jsonl').write_text('malformed')
        with self.assertRaises(HTTPError) as error:
            read()
        self.assertEqual(error.exception.code, 503)
        error.exception.close()

    def test_legacy_log_and_concurrent_readers(self):
        self.capture()
        event = self.store.events()[0]
        event.pop('policy_hash')
        (self.store.root / 'events.jsonl').write_text(json.dumps(event) + '\n')
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
            results = list(pool.map(lambda _: self.tracker.snapshot()['count'], range(10)))
        self.assertEqual(results, [1] * 10)


if __name__ == '__main__':
    unittest.main()
