"""Exercise publication against disposable local repositories; never contact GitHub."""
import contextlib
import io
import json
from pathlib import Path
import runpy
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
MODULE = runpy.run_path(str(ROOT / 'scripts/codex-git'))
Publisher = MODULE['Publisher']
CHAT = '01a1c2cb-b5c9-7ea0-b9ef-b1bfc0e646c0'


def git(*args, cwd=None, check=True):
    return subprocess.run(['/usr/bin/git', *map(str, args)], cwd=cwd, text=True,
                          capture_output=True, check=check).stdout.strip()


class LocalPublisher(Publisher):
    PR_CHECK_ATTEMPTS = 1

    @property
    def remote(self):
        return self.repo.parent / 'remote.git'

    def git(self, *args, check=True):
        # Test-only transport; production has no CLI override for its HTTPS registry.
        args = tuple(str(self.repo.parent / 'remote.git') if arg == 'https://github.com/RyanUdelhoven/Test.git' else arg for arg in args)
        return git('-c', 'core.hooksPath=/dev/null', '-C', self.repo, *args, check=check)


    def contribution_identity(self, source):
        return {'login': 'RyanUdelhoven', 'id': 123}

    def api(self, endpoint, method='GET', **fields):
        self.api_calls = getattr(self, 'api_calls', []) + [(endpoint, method, fields)]
        if endpoint.endswith('/merge'):
            if getattr(self, 'merge_denied', False):
                raise ValueError('simulated merge protection failure')
            assert fields == {'sha': git('rev-parse', 'codex/example', cwd=self.remote), 'merge_method': 'merge'}
            server = self.repo.parent / 'server'
            git('clone', self.remote, server)
            git('config', 'user.name', 'GitHub', cwd=server)
            git('config', 'user.email', 'noreply@github.com', cwd=server)
            git('merge', '--no-ff', fields['sha'], '-m', 'Merge pull request #1', cwd=server)
            git('push', 'origin', 'main', cwd=server)
            return {'merged': True, 'sha': git('rev-parse', 'HEAD', cwd=server)}
        if '/pulls' not in endpoint and '/commits/' not in endpoint:
            return {'default_branch': 'main', 'allow_merge_commit': getattr(self, 'allow_merge_commit', True)}
        pr = {'number': 1, 'html_url': 'https://github.com/RyanUdelhoven/Test/pull/1',
              'head': {'sha': git('rev-parse', 'codex/example', cwd=self.remote),
                       'repo': {'full_name': 'RyanUdelhoven/Test'}},
              'base': {'ref': 'main', 'repo': {'full_name': 'RyanUdelhoven/Test'}},
              'user': {'login': 'RyanUdelhoven'}, 'draft': False}
        if '/commits/' in endpoint:
            return {'author': {'login': getattr(self, 'mapped_author', 'RyanUdelhoven')}}
        if endpoint.endswith('/pulls'):
            if method == 'POST':
                self.pr_exists = True
                return pr
            return [pr] if getattr(self, 'pr_exists', False) else []
        if '/pulls/' in endpoint:
            if getattr(self, 'pr_changed', False):
                pr['head']['sha'] = '0' * 40
            return pr
        return {'default_branch': 'main', 'allow_merge_commit': getattr(self, 'allow_merge_commit', True)}

    def gh(self, *args):
        return json.dumps(getattr(self, 'pr_state', {'mergeStateStatus': 'CLEAN',
            'reviewDecision': '', 'statusCheckRollup': []}))

    def publish_pr(self, branch, source, user):
        # Preserve the real production implementation; only API transport is fake.
        original = self.url
        self.url = 'https://github.com/RyanUdelhoven/Test.git'
        try:
            with patch.object(self, 'remote_tip', side_effect=lambda ref:
                              git('rev-parse', '--verify', ref, cwd=self.remote, check=False) or None):
                return super().publish_pr(branch, source, user)
        finally:
            self.url = original

class PublicationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.remote = self.root / 'remote.git'
        self.repo = self.root / 'checkout'
        git('init', '--bare', '--initial-branch=main', self.remote)
        git('clone', self.remote, self.repo)
        git('config', 'user.name', 'Test', cwd=self.repo)
        git('config', 'user.email', 'test@example.com', cwd=self.repo)
        (self.repo / 'file').write_text('base')
        git('add', '.', cwd=self.repo)
        git('commit', '-m', 'base', cwd=self.repo)
        git('push', 'origin', 'main', cwd=self.repo)
        git('remote', 'set-head', 'origin', '-a', cwd=self.repo)
        git('switch', '-c', 'codex/example', cwd=self.repo)
        (self.repo / 'file').write_text('feature')
        git('commit', '-am', 'feature', cwd=self.repo)
        git('push', 'origin', 'codex/example', cwd=self.repo)
        shutil.copy(ROOT / 'skills/feature-branch/scripts/branch_chats.py', self.root)
        for name in ['secret_check.py', 'secret-policy.toml']:
            shutil.copy(ROOT / 'scripts' / name, self.root)
        shutil.copy(ROOT / 'scripts/mp-command-hook.py', self.root)
        self.old_install = Publisher.tracking.__globals__['INSTALL']
        Publisher.tracking.__globals__['INSTALL'] = self.root
        self.addCleanup(lambda: Publisher.tracking.__globals__.__setitem__('INSTALL', self.old_install))
        self.publisher = LocalPublisher(self.repo, str(self.remote))

    def test_publish_verify_cleanup_and_finish(self):
        tip = git('rev-parse', 'HEAD', cwd=self.repo)
        receipt = self.publisher.publish('codex/example', CHAT)
        self.assertNotEqual(receipt['published'], tip)
        self.assertEqual(receipt['source'], tip)
        self.assertTrue(receipt['source_preserved'])
        self.assertEqual(git('rev-parse', 'main', cwd=self.remote), receipt['published'])
        git('merge-base', '--is-ancestor', tip, 'main', cwd=self.remote)
        self.assertEqual(git('branch', '--show-current', cwd=self.repo), 'main')
        self.assertEqual(git('branch', '--list', 'codex/example', cwd=self.repo), '')
        self.assertEqual(git('branch', '--list', 'codex/example', cwd=self.remote), '')
        self.assertFalse(receipt['tracking']['single_chat_candidate'])
        self.assertTrue(self.publisher.finish('codex/example', CHAT)['closed'])

    def test_one_mp_from_dirty_iteration_through_preparation_to_publication(self):
        hook = runpy.run_path(str(ROOT / 'scripts/mp-command-hook.py'))
        # Ordinary task branches stay local until explicitly requested PR publication.
        git('push', 'origin', ':codex/example', cwd=self.repo)
        self.publisher.register('codex/example', CHAT)
        (self.repo / 'file').write_text('final iteration')
        calls = []
        def protected(action, repo, branch, session, expected_source=None):
            self.assertEqual(Path(repo), self.repo.resolve())
            calls.append(action)
            if action == 'publish':
                return self.publisher.publish(branch, session, expected_source=expected_source)
            return getattr(self.publisher, action)(branch, session)
        with patch.dict(hook['handle'].__globals__, publisher=protected):
            response = hook['handle']({'hook_event_name': 'UserPromptSubmit', 'prompt': 'mp',
                                       'cwd': str(self.repo), 'session_id': CHAT})
            self.assertIn('hookSpecificOutput', response)
            self.assertEqual(calls, [])
            common = self.repo / '.git'
            request_file = hook['request_path'](common, CHAT)
            request = json.loads(request_file.read_text())
            # Simulate the agent's authorized preparation, using real Git/checks.
            git('diff', '--check', cwd=self.repo)
            git('commit', '-am', 'final task iteration', cwd=self.repo)
            expected = git('rev-parse', 'HEAD', cwd=self.repo)
            with patch('runpy.run_path', return_value=hook) as load:
                result = self.publisher.complete('codex/example', CHAT, request['request_id'], ['git diff --check'])
            load.assert_called_once_with(str(self.root / 'mp-command-hook.py'))
        self.assertTrue(result['completed'])
        self.assertEqual(calls, ['inspect', 'inspect', 'publish', 'finish'])
        git('merge-base', '--is-ancestor', expected, 'main', cwd=self.remote)
        self.assertEqual(git('branch', '--show-current', cwd=self.repo), 'main')
        self.assertEqual(git('branch', '--list', 'codex/example', cwd=self.repo), '')
        self.assertFalse(request_file.exists())
        self.assertTrue(self.publisher.tracking('inspect', 'codex/example', CHAT)['record']['closed'])

    def test_complete_refuses_missing_or_symlinked_protected_dependency(self):
        module = self.root / 'mp-command-hook.py'
        module.unlink()
        for symlink in (False, True):
            if symlink:
                module.symlink_to(ROOT / 'scripts/mp-command-hook.py')
            with self.subTest(symlink=symlink), patch('runpy.run_path') as load:
                with self.assertRaisesRegex(ValueError, 'protected mp handoff dependency'):
                    self.publisher.complete('codex/example', CHAT, CHAT, ['checks'])
                load.assert_not_called()

    def test_complete_loads_installed_copy_and_refuses_absent_or_expired_request(self):
        with self.assertRaisesRegex(ValueError, 'No pending mp request'):
            self.publisher.complete('codex/example', CHAT, CHAT, ['checks'])
        path = self.repo / '.git/codex-publish' / ('mp-request-' + CHAT + '.json')
        path.parent.mkdir(parents=True)
        path.write_text(json.dumps({'request_id': CHAT, 'repository': str(self.repo.resolve()),
            'branch': 'codex/example', 'session_id': CHAT, 'requested_at': '2000-01-01T00:00:00+00:00'}))
        with self.assertRaisesRegex(ValueError, 'expired'):
            self.publisher.complete('codex/example', CHAT, CHAT, ['checks are data, not executed'])
        self.assertFalse(path.exists())
        self.assertEqual(git('rev-parse', 'main', cwd=self.repo), git('rev-parse', 'main', cwd=self.remote))

    def test_complete_requires_matching_checkout_and_validated_repository(self):
        git('checkout', 'main', cwd=self.repo)
        with patch('runpy.run_path') as load:
            with self.assertRaisesRegex(ValueError, 'requested feature branch'):
                self.publisher.complete('codex/example', CHAT, CHAT, ['checks'])
            load.assert_not_called()
        git('checkout', 'codex/example', cwd=self.repo)
        (self.repo / 'file').write_text('unreviewed')
        with patch('runpy.run_path') as load:
            with self.assertRaisesRegex(ValueError, 'clean'):
                self.publisher.complete('codex/example', CHAT, CHAT, ['checks'])
            load.assert_not_called()

    def test_complete_cli_rejects_unsafe_argument_variants(self):
        for tail in ([], ['--request', 'bad', '--check', 'checks'],
                     ['--request', CHAT], ['--request', CHAT, '--check', ' '],
                     ['--request', CHAT, '--check', 'checks', '--module', '/tmp/evil.py'],
                     ['--request', CHAT, '--check', 'checks', '--expected-source', 'a' * 40]):
            with self.subTest(tail=tail), contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit):
                    MODULE['main'](['complete', 'customization', 'codex/example', CHAT, *tail])
        for action in ('inspect', 'register', 'publish', 'finish'):
            with self.subTest(action=action), contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit):
                    MODULE['main']([action, 'customization', 'codex/example', CHAT,
                                    '--request', CHAT, '--check', 'checks'])

    def test_creation_without_host_stays_single_chat_after_publish(self):
        subprocess.run(['/usr/bin/python3', str(self.root / 'branch_chats.py'),
            'register', '--repo', str(self.repo), '--branch', 'codex/example',
            '--chat-id', CHAT, '--created'], check=True, capture_output=True)
        receipt = self.publisher.publish('codex/example', CHAT)
        self.assertTrue(receipt['tracking']['single_chat_candidate'])
        self.assertEqual(receipt['tracking']['record']['origin']['hostId'], 'local')
        self.assertTrue(self.publisher.finish('codex/example', CHAT)['closed'])

    def test_inspect_preserves_refs_files_and_tracking(self):
        before = git('show-ref', cwd=self.repo)
        result = self.publisher.inspect('codex/example', CHAT)
        self.assertEqual(result['branch'], 'codex/example')
        self.assertIn('feature', result['commits'])
        self.assertIn('file', result['changes'])
        self.assertEqual(git('show-ref', cwd=self.repo), before)
        self.assertEqual(git('status', '--porcelain', cwd=self.repo), '')
        self.assertFalse((self.repo / '.git/codex-branch-chats').exists())

    def test_register_does_not_claim_creation_or_publish(self):
        before = git('rev-parse', 'main', cwd=self.remote)
        result = self.publisher.register('codex/example', CHAT)
        self.assertFalse(result['single_chat_candidate'])
        self.assertEqual(git('rev-parse', 'main', cwd=self.remote), before)

    def test_push_failure_preserves_feature_and_tracking(self):
        before = git('rev-parse', 'main', cwd=self.remote)
        git('push', 'origin', ':codex/example', cwd=self.repo)
        original = self.publisher.git
        def fail_push(*args, **kwargs):
            if args[0] == 'push':
                raise ValueError('simulated push failure')
            return original(*args, **kwargs)
        with patch.object(self.publisher, 'git', side_effect=fail_push):
            with self.assertRaisesRegex(ValueError, 'simulated push failure'):
                self.publisher.publish('codex/example', CHAT)
        self.assertEqual(git('rev-parse', 'main', cwd=self.remote), before)
        self.assertTrue(git('branch', '--list', 'codex/example', cwd=self.repo))
        record = self.publisher.tracking('inspect', 'codex/example', CHAT)
        self.assertFalse(record['record']['closed'])

    def test_dirty_checkout_never_publishes(self):
        before = git('rev-parse', 'main', cwd=self.remote)
        (self.repo / 'untracked').write_text('keep')
        with self.assertRaisesRegex(ValueError, 'clean'):
            self.publisher.publish('codex/example', CHAT)
        self.assertEqual(git('rev-parse', 'main', cwd=self.remote), before)
        self.assertTrue((self.repo / 'untracked').exists())

    def test_expected_source_mismatch_stops_before_mutation(self):
        before = git('show-ref', cwd=self.repo)
        remote_before = git('show-ref', cwd=self.remote)
        with self.assertRaisesRegex(ValueError, 'verified commit'):
            self.publisher.publish('codex/example', CHAT, expected_source='0' * 40)
        self.assertEqual(git('show-ref', cwd=self.repo), before)
        self.assertEqual(git('show-ref', cwd=self.remote), remote_before)

    def test_expected_source_publishes_the_verified_commit(self):
        tip = git('rev-parse', 'HEAD', cwd=self.repo)
        receipt = self.publisher.publish('codex/example', CHAT, expected_source=tip)
        self.assertNotEqual(receipt['published'], tip)
        self.assertEqual(receipt['source'], tip)
        self.assertTrue(receipt['source_preserved'])

    def test_cleanup_already_published_branch(self):
        git('switch', 'main', cwd=self.repo)
        git('merge', '--ff-only', 'codex/example', cwd=self.repo)
        git('push', 'origin', 'main', cwd=self.repo)
        receipt = self.publisher.cleanup('codex/example', CHAT)
        self.assertIn('local feature deleted', receipt['cleanup'])
        self.assertTrue(self.publisher.finish('codex/example', CHAT)['closed'])

    def test_cleanup_unpublished_branch_preserved(self):
        git('switch', 'main', cwd=self.repo)
        with self.assertRaises(subprocess.CalledProcessError):
            self.publisher.cleanup('codex/example', CHAT)
        self.assertTrue(git('branch', '--list', 'codex/example', cwd=self.repo))

    def test_cleanup_requires_exact_published_main(self):
        git('switch', 'main', cwd=self.repo)
        git('merge', '--ff-only', 'codex/example', cwd=self.repo)
        with self.assertRaisesRegex(ValueError, 'match published main'):
            self.publisher.cleanup('codex/example', CHAT)
        self.assertTrue(git('branch', '--list', 'codex/example', cwd=self.repo))

    def test_cleanup_preserves_worktrees_and_changed_remote_feature(self):
        git('switch', 'main', cwd=self.repo)
        git('merge', '--ff-only', 'codex/example', cwd=self.repo)
        git('push', 'origin', 'main', cwd=self.repo)
        git('worktree', 'add', self.root / 'other', 'codex/example', cwd=self.repo)
        with self.assertRaisesRegex(ValueError, 'another worktree'):
            self.publisher.cleanup('codex/example', CHAT)
        git('worktree', 'remove', self.root / 'other', cwd=self.repo)
        git('push', 'origin', 'main~1:codex/example', '--force', cwd=self.repo)
        receipt = self.publisher.cleanup('codex/example', CHAT)
        self.assertIn('remote feature retained', ' '.join(receipt['cleanup']))
        self.assertTrue(git('branch', '--list', 'codex/example', cwd=self.remote))

    def test_repository_resolution_accepts_future_projects_and_rejects_destinations(self):
        resolver = MODULE['resolve_repository']
        with patch.dict(resolver.__globals__, HOME=self.root):
            git('remote', 'set-url', 'origin', 'https://github.com/RyanUdelhoven/FutureApp.git', cwd=self.repo)
            self.assertEqual(resolver(str(self.repo)), (self.repo.resolve(), 'https://github.com/RyanUdelhoven/FutureApp.git'))
            for url in ['https://github.com/OtherOwner/App.git', 'git@github.com:RyanUdelhoven/App.git',
                        'https://github.com/RyanUdelhoven/App.git/../../Other/App.git']:
                git('remote', 'set-url', 'origin', url, cwd=self.repo)
                with self.assertRaises(ValueError):
                    resolver(str(self.repo))
            with self.assertRaises(ValueError):
                resolver('/tmp/outside-home')

    def test_destination_rewrite_rejected_before_network(self):
        git('config', 'url.https://evil.example/.insteadOf', 'https://github.com/', cwd=self.repo)
        with self.assertRaisesRegex(ValueError, 'rewrites'):
            self.publisher.validate()

    def test_repository_execution_config_rejected(self):
        for key in ['credential.https://github.com/RyanUdelhoven.helper', 'filter.example.smudge']:
            with self.subTest(key=key):
                git('config', key, '!unreviewed-command', cwd=self.repo)
                with self.assertRaisesRegex(ValueError, 'executable config'):
                    self.publisher.validate()
                git('config', '--unset', key, cwd=self.repo)

    def test_divergence_preserves_branches(self):
        git('switch', 'main', cwd=self.repo)
        (self.repo / 'other').write_text('diverged')
        git('add', '.', cwd=self.repo)
        git('commit', '-m', 'other', cwd=self.repo)
        git('push', 'origin', 'main', cwd=self.repo)
        git('switch', 'codex/example', cwd=self.repo)
        with self.assertRaises(subprocess.CalledProcessError):
            self.publisher.publish('codex/example', CHAT)
        self.assertTrue(git('branch', '--list', 'codex/example', cwd=self.repo))

    def test_other_worktree_preserved(self):
        git('worktree', 'add', self.root / 'other', 'main', cwd=self.repo)
        with self.assertRaisesRegex(ValueError, 'another worktree'):
            self.publisher.publish('codex/example', CHAT)

    def test_remote_feature_with_different_tip_retained(self):
        git('push', 'origin', 'main:codex/example', '--force', cwd=self.repo)
        with self.assertRaisesRegex(ValueError, 'Remote feature tip differs'):
            self.publisher.publish('codex/example', CHAT)
        self.assertTrue(git('branch', '--list', 'codex/example', cwd=self.remote))
        self.assertTrue(git('branch', '--list', 'codex/example', cwd=self.repo))

    def test_pending_checks_reviews_and_failures_preserve_branches(self):
        for state in [
            {'mergeStateStatus': 'BLOCKED', 'reviewDecision': 'REVIEW_REQUIRED'},
            {'mergeStateStatus': 'UNKNOWN'},
            {'mergeStateStatus': 'CLEAN', 'statusCheckRollup': [{'status': 'IN_PROGRESS'}]},
            {'mergeStateStatus': 'CLEAN', 'statusCheckRollup': [{'conclusion': 'FAILURE'}]},
        ]:
            self.publisher.pr_state = state
            before = git('rev-parse', 'main', cwd=self.remote)
            with self.assertRaisesRegex(ValueError, 'pending/blocked'):
                self.publisher.publish('codex/example', CHAT)
            self.assertEqual(git('rev-parse', 'main', cwd=self.remote), before)
            self.assertTrue(git('branch', '--list', 'codex/example', cwd=self.repo))
            self.assertTrue(git('branch', '--list', 'codex/example', cwd=self.remote))
        creations = [c for c in self.publisher.api_calls if c[1] == 'POST']
        self.assertEqual(len(creations), 1)

    def test_waits_for_pending_checks_then_merges(self):
        self.publisher.PR_CHECK_ATTEMPTS = 2
        states = [json.dumps({'mergeStateStatus': 'BLOCKED', 'statusCheckRollup': [{'status': 'IN_PROGRESS'}]}),
                  json.dumps({'mergeStateStatus': 'CLEAN', 'statusCheckRollup': [{'conclusion': 'SUCCESS'}]})]
        with patch.object(self.publisher, 'gh', side_effect=states), patch('time.sleep') as sleep:
            receipt = self.publisher.publish('codex/example', CHAT)
        sleep.assert_called_once_with(5)
        self.assertTrue(receipt['source_preserved'])

    def test_mismatched_pr_and_disallowed_merge_preserve_branches(self):
        for attribute, message in [('pr_changed', 'PR identity'),
                                   ('allow_merge_commit', 'must allow merge'),
                                   ('merge_denied', 'protection failure')]:
            setattr(self.publisher, attribute, attribute != 'allow_merge_commit')
            with self.assertRaisesRegex(ValueError, message):
                self.publisher.publish('codex/example', CHAT)
            self.assertTrue(git('branch', '--list', 'codex/example', cwd=self.repo))
            setattr(self.publisher, attribute, attribute == 'allow_merge_commit')

    def test_unattributed_tip_stops_before_pr_creation(self):
        self.publisher.mapped_author = 'someone-else'
        with self.assertRaisesRegex(ValueError, 'not attributed'):
            self.publisher.publish('codex/example', CHAT)
        self.assertFalse(any(c[1] == 'POST' for c in self.publisher.api_calls))

    def test_pr_merge_preserves_all_individual_commits(self):
        (self.repo / 'second').write_text('another meaningful change')
        git('add', '.', cwd=self.repo)
        git('commit', '-m', 'second change', cwd=self.repo)
        git('push', 'origin', 'codex/example', cwd=self.repo)
        outgoing = git('rev-list', 'main..HEAD', cwd=self.repo).splitlines()
        receipt = self.publisher.publish('codex/example', CHAT)
        for commit in outgoing:
            git('merge-base', '--is-ancestor', commit, receipt['published'], cwd=self.repo)
        self.assertEqual(len(git('rev-list', '--parents', '-1', receipt['merge_commit'], cwd=self.repo).split()), 3)

    def test_secret_deleted_in_later_commit_blocks_before_integration(self):
        before = git('rev-parse', 'main', cwd=self.remote)
        (self.repo / '.env').write_text('LOCAL_VALUE=fixture')
        git('add', '.', cwd=self.repo)
        git('commit', '-m', 'accidental environment', cwd=self.repo)
        git('rm', '.env', cwd=self.repo)
        git('commit', '-m', 'delete environment', cwd=self.repo)
        with self.assertRaisesRegex(ValueError, 'filename blocked'):
            self.publisher.publish('codex/example', CHAT)
        self.assertEqual(git('rev-parse', 'main', cwd=self.remote), before)
        self.assertEqual(git('branch', '--show-current', cwd=self.repo), 'codex/example')
        self.assertFalse((self.repo / '.git/codex-branch-chats').exists())

    def test_cli_rejects_extra_flags_main_and_unknown_repositories(self):
        for args in [['publish', 'mynormal', 'main', CHAT],
                     ['publish', 'mynormal', 'codex/example', CHAT, '--force'],
                     ['publish', '/tmp/arbitrary', 'codex/example', CHAT]]:
            with self.subTest(args=args), contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit):
                    MODULE['main'](args)


class IdentityTests(unittest.TestCase):
    def setUp(self):
        self.publisher = Publisher('/tmp', 'https://github.com/RyanUdelhoven/Test.git')

    def test_account_specific_noreply_needs_no_email_scope(self):
        with patch.object(self.publisher, 'git', return_value='123+RyanUdelhoven@users.noreply.github.com'), \
             patch.object(self.publisher, 'api', return_value={'login': 'RyanUdelhoven', 'id': 123}) as api:
            self.publisher.contribution_identity('a' * 40)
        api.assert_called_once_with('user')

    def test_verified_email_and_wrong_account(self):
        with patch.object(self.publisher, 'git', return_value='test@example.com'), \
             patch.object(self.publisher, 'api', side_effect=[{'login': 'RyanUdelhoven', 'id': 123},
                                                            [{'email': 'test@example.com', 'verified': True}]]):
            self.publisher.contribution_identity('a' * 40)
        with patch.object(self.publisher, 'api', return_value={'login': 'Other', 'id': 1}):
            with self.assertRaisesRegex(ValueError, 'RyanUdelhoven GitHub account'):
                self.publisher.contribution_identity('a' * 40)

    def test_unverified_email_is_rejected(self):
        with patch.object(self.publisher, 'git', return_value='test@example.com'), \
             patch.object(self.publisher, 'api', side_effect=[{'login': 'RyanUdelhoven', 'id': 123},
                                                            [{'email': 'test@example.com', 'verified': False}]]):
            with self.assertRaisesRegex(ValueError, 'not verified'):
                self.publisher.contribution_identity('a' * 40)


if __name__ == '__main__':
    unittest.main()
