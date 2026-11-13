"""Exercise dispatch and commit-bound handoff in disposable local repositories."""
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('mp_command_hook', Path(__file__).with_name('mp-command-hook.py'))
hook = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hook)
CHAT = '01a1d2dc-ff1b-78e1-a5b6-ae05ec46a7ae'
OTHER = '01a1d2dc-ff1b-78e1-a5b6-ae05ec46a7a0'


def git(repo, *args):
    return subprocess.run(['/usr/bin/git', '-c', 'core.hooksPath=/dev/null', '-C', str(repo), *args],
                          check=True, text=True, capture_output=True).stdout.strip()


class DispatchTests(unittest.TestCase):
    def test_exact_command_dispatches_using_event_identity(self):
        with patch.object(hook, 'publish', return_value='published') as publish:
            result = hook.handle({'hook_event_name': 'UserPromptSubmit', 'prompt': ' \nmp\t', 'cwd': '/task', 'session_id': CHAT})
        publish.assert_called_once_with('/task', CHAT)
        self.assertEqual(result['decision'], 'block')

    def test_mentions_other_events_and_bad_payloads_do_nothing(self):
        events = [None, [], {}, {'hook_event_name': 'Stop', 'prompt': 'mp'}]
        events += [{'hook_event_name': 'UserPromptSubmit', 'prompt': p} for p in
                   ('mpa', 'MP', 'please mp', '`mp`', 'what is mp?', 'mp; git push', 'mp\nmerge', '', None, 5)]
        with patch.object(hook, 'publish') as publish:
            for event in events:
                with self.subTest(event=event):
                    self.assertIsNone(hook.handle(event))
            publish.assert_not_called()

    def test_failure_is_consumed_without_assistant_fallback(self):
        with patch.object(hook, 'publish', side_effect=ValueError('not ready')) as publish:
            result = hook.handle({'hook_event_name': 'UserPromptSubmit', 'prompt': 'mp'})
        self.assertEqual(result['decision'], 'block')
        self.assertEqual(publish.call_count, 1)
        self.assertIn('not ready', result['reason'])

    def test_json_cli_contract_and_invalid_input(self):
        for value in ('not json', json.dumps({'hook_event_name': 'UserPromptSubmit', 'prompt': 'hello'})):
            with patch('sys.stdin', io.StringIO(value)), patch('sys.stdout', new_callable=io.StringIO) as output, patch.object(hook, 'publish') as publish:
                hook.main([])
                publish.assert_not_called()
                self.assertEqual(output.getvalue(), '')
        with patch('sys.stdin', io.StringIO(json.dumps({'hook_event_name': 'UserPromptSubmit', 'prompt': 'mp'}))), patch('sys.stdout', new_callable=io.StringIO) as output, patch.object(hook, 'publish', return_value='done'):
            hook.main([])
            self.assertEqual(json.loads(output.getvalue())['decision'], 'block')


class HandoffTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name).resolve()
        git(self.repo, 'init', '--initial-branch=main')
        git(self.repo, 'config', 'user.name', 'Test')
        git(self.repo, 'config', 'user.email', 'test@example.com')
        (self.repo / 'file').write_text('base')
        git(self.repo, 'add', 'file')
        git(self.repo, 'commit', '-m', 'base')
        git(self.repo, 'switch', '-c', 'codex/example')
        self.head = git(self.repo, 'rev-parse', 'HEAD')
        self.inspection = {'branch': 'codex/example', 'head': self.head, 'feature': self.head,
                           'tracking': {'record': {'id': 'lifecycle-1', 'closed': False,
                           'participants': [{'source': 'codex', 'hostId': 'local', 'threadId': CHAT}]}}}
        self.calls = []
        self.patcher = patch.object(hook, 'publisher', side_effect=self.publisher)
        self.patcher.start()
        self.addCleanup(self.patcher.stop)

    def publisher(self, action, repo, branch, session, expected_source=None):
        self.calls.append((action, str(repo), branch, session, expected_source))
        if action == 'inspect':
            return self.inspection
        if action == 'publish':
            return {'branch': branch, 'source': self.head, 'published': self.head,
                    'cleanup': ['local feature deleted']}
        return {'closed': True}

    def prepare(self):
        return hook.prepare(str(self.repo), CHAT, ['verified test command'])

    def test_preparation_is_read_only_except_readiness_record(self):
        before = git(self.repo, 'show-ref')
        ready = self.prepare()
        self.assertTrue(Path(ready['record']).exists())
        self.assertEqual(git(self.repo, 'show-ref'), before)
        self.assertEqual([c[0] for c in self.calls], ['inspect'])

    def test_success_uses_git_branch_and_exact_verified_sha(self):
        ready = self.prepare()
        message = hook.publish(str(self.repo), CHAT)
        self.assertIn('codex/example', message)
        self.assertEqual([c[0] for c in self.calls], ['inspect', 'inspect', 'publish', 'finish'])
        self.assertEqual(self.calls[2], ('publish', str(self.repo), 'codex/example', CHAT, self.head))
        self.assertFalse(Path(ready['record']).exists())

    def test_main_detached_and_unregistered_chat_are_refused(self):
        for target in ('main', self.head):
            git(self.repo, 'checkout', target)
            with self.assertRaisesRegex(ValueError, 'feature branch'):
                self.prepare()
        git(self.repo, 'checkout', 'codex/example')
        with self.assertRaises(hook.NeedsPreparation):
            hook.prepare(str(self.repo), OTHER, ['checks'])
        self.assertNotIn('publish', [c[0] for c in self.calls])

    def test_dirty_tree_and_missing_checks_are_refused(self):
        with self.assertRaisesRegex(ValueError, 'successful checks'):
            hook.prepare(str(self.repo), CHAT, [])
        (self.repo / 'untracked').write_text('unreviewed')
        with self.assertRaises(hook.NeedsPreparation):
            self.prepare()
        self.assertEqual(self.calls, [])

    def test_missing_readiness_and_changed_lifecycle_are_refused(self):
        with self.assertRaises(hook.NeedsPreparation):
            hook.publish(str(self.repo), CHAT)
        self.prepare()
        self.inspection['tracking']['record']['id'] = 'new-lifecycle'
        with self.assertRaisesRegex(ValueError, 'changed since verification'):
            hook.publish(str(self.repo), CHAT)
        self.assertNotIn('publish', [c[0] for c in self.calls])

    def test_changed_commit_invalidates_readiness(self):
        self.prepare()
        (self.repo / 'file').write_text('new')
        git(self.repo, 'commit', '-am', 'new commit')
        self.inspection['head'] = self.inspection['feature'] = git(self.repo, 'rev-parse', 'HEAD')
        with self.assertRaisesRegex(ValueError, 'changed since verification'):
            hook.publish(str(self.repo), CHAT)
        self.assertNotIn('publish', [c[0] for c in self.calls])

    def test_publication_failure_consumes_handoff_and_does_not_finish(self):
        ready = self.prepare()
        original = self.publisher
        def fail(action, *args, **kwargs):
            if action == 'publish':
                self.calls.append(('publish',))
                raise ValueError('network stopped')
            return original(action, *args, **kwargs)
        with patch.object(hook, 'publisher', side_effect=fail):
            with self.assertRaisesRegex(ValueError, 'network stopped'):
                hook.publish(str(self.repo), CHAT)
        self.assertFalse(Path(ready['record']).exists())
        self.assertNotIn('finish', [c[0] for c in self.calls])

    def test_lock_prevents_duplicate_publication(self):
        self.prepare()
        path = self.repo / '.git/codex-publish/mp-command.lock'
        with path.open('a') as lock:
            hook.fcntl.flock(lock, hook.fcntl.LOCK_EX | hook.fcntl.LOCK_NB)
            with self.assertRaisesRegex(ValueError, 'Another mp'):
                hook.publish(str(self.repo), CHAT)
        self.assertNotIn('publish', [c[0] for c in self.calls])

    def test_incomplete_cleanup_does_not_finish(self):
        self.prepare()
        original = self.publisher
        def retained(action, *args, **kwargs):
            result = original(action, *args, **kwargs)
            if action == 'publish':
                result['cleanup'].append('remote feature retained')
            return result
        with patch.object(hook, 'publisher', side_effect=retained):
            with self.assertRaisesRegex(ValueError, 'incomplete cleanup'):
                hook.publish(str(self.repo), CHAT)
        self.assertNotIn('finish', [c[0] for c in self.calls])

    def test_dirty_task_requests_preparation_then_completes_without_second_mp(self):
        (self.repo / 'file').write_text('iteration approved by the user')
        event = {'hook_event_name': 'UserPromptSubmit', 'prompt': 'mp',
                 'cwd': str(self.repo), 'session_id': CHAT}
        response = hook.handle(event)
        self.assertNotIn('decision', response)
        self.assertIn('--complete', response['hookSpecificOutput']['additionalContext'])
        path = hook.request_path(self.repo / '.git', CHAT)
        request = json.loads(path.read_text())
        git(self.repo, 'commit', '-am', 'finish feature')
        self.head = git(self.repo, 'rev-parse', 'HEAD')
        self.inspection['head'] = self.inspection['feature'] = self.head
        result = hook.complete(str(self.repo), CHAT, request['request_id'], ['git diff --check'])
        self.assertTrue(result['completed'])
        self.assertFalse(path.exists())
        self.assertEqual([c[0] for c in self.calls], ['inspect', 'inspect', 'publish', 'finish'])
        self.assertEqual(self.calls[-2][-1], self.head)

    def test_missing_readiness_enters_preparation_instead_of_stopping(self):
        result = hook.handle({'hook_event_name': 'UserPromptSubmit', 'prompt': 'mp',
                              'cwd': str(self.repo), 'session_id': CHAT})
        self.assertIn('hookSpecificOutput', result)
        self.assertNotIn('publish', [c[0] for c in self.calls])

    def test_new_message_revokes_pending_request(self):
        event = {'hook_event_name': 'UserPromptSubmit', 'prompt': 'mp',
                 'cwd': str(self.repo), 'session_id': CHAT}
        hook.handle(event)
        path = hook.request_path(self.repo / '.git', CHAT)
        request = json.loads(path.read_text())
        self.assertIsNone(hook.handle(dict(event, prompt='Actually, change the feature first')))
        self.assertFalse(path.exists())
        with self.assertRaisesRegex(ValueError, 'No pending'):
            hook.complete(str(self.repo), CHAT, request['request_id'], ['checks'])
        self.assertNotIn('publish', [c[0] for c in self.calls])

    def test_complete_requires_matching_pending_request(self):
        with self.assertRaisesRegex(ValueError, 'No pending'):
            hook.complete(str(self.repo), CHAT, OTHER, ['checks'])
        event = {'hook_event_name': 'UserPromptSubmit', 'prompt': 'mp',
                 'cwd': str(self.repo), 'session_id': CHAT}
        hook.handle(event)
        with self.assertRaisesRegex(ValueError, 'does not match'):
            hook.complete(str(self.repo), CHAT, OTHER, ['checks'])
        self.assertNotIn('publish', [c[0] for c in self.calls])

    def test_cancellation_during_final_preparation_prevents_publication(self):
        event = {'hook_event_name': 'UserPromptSubmit', 'prompt': 'mp',
                 'cwd': str(self.repo), 'session_id': CHAT}
        hook.handle(event)
        path = hook.request_path(self.repo / '.git', CHAT)
        request = json.loads(path.read_text())
        original = hook.prepare
        def interrupted(*args, **kwargs):
            result = original(*args, **kwargs)
            hook.cancel_pending(event)
            return result
        with patch.object(hook, 'prepare', side_effect=interrupted):
            with self.assertRaisesRegex(ValueError, 'cancelled or replaced'):
                hook.complete(str(self.repo), CHAT, request['request_id'], ['checks'])
        self.assertNotIn('publish', [c[0] for c in self.calls])

    def test_expired_request_is_refused(self):
        hook.handle({'hook_event_name': 'UserPromptSubmit', 'prompt': 'mp',
                     'cwd': str(self.repo), 'session_id': CHAT})
        path = hook.request_path(self.repo / '.git', CHAT)
        request = json.loads(path.read_text())
        request['requested_at'] = '2000-01-01T00:00:00+00:00'
        hook.write_record(path, request)
        with self.assertRaisesRegex(ValueError, 'expired'):
            hook.complete(str(self.repo), CHAT, request['request_id'], ['checks'])
        self.assertFalse(path.exists())
        self.assertNotIn('publish', [c[0] for c in self.calls])

    def test_invalid_event_identity_never_calls_publisher(self):
        for cwd, session in (('relative', CHAT), (str(self.repo), 'bad-session')):
            with self.assertRaises(ValueError):
                hook.publish(cwd, session)
        self.assertEqual(self.calls, [])


if __name__ == '__main__':
    unittest.main()
