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
    def git(self, *args, check=True):
        # Test-only transport; production has no CLI override for its HTTPS registry.
        return git('-c', 'core.hooksPath=/dev/null', '-C', self.repo, *args, check=check)


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
        self.old_install = Publisher.tracking.__globals__['INSTALL']
        Publisher.tracking.__globals__['INSTALL'] = self.root
        self.addCleanup(lambda: Publisher.tracking.__globals__.__setitem__('INSTALL', self.old_install))
        self.publisher = LocalPublisher(self.repo, str(self.remote))

    def test_publish_verify_cleanup_and_finish(self):
        tip = git('rev-parse', 'HEAD', cwd=self.repo)
        receipt = self.publisher.publish('codex/example', CHAT)
        self.assertEqual(receipt['published'], tip)
        self.assertEqual(git('rev-parse', 'main', cwd=self.remote), tip)
        self.assertEqual(git('branch', '--show-current', cwd=self.repo), 'main')
        self.assertEqual(git('branch', '--list', 'codex/example', cwd=self.repo), '')
        self.assertEqual(git('branch', '--list', 'codex/example', cwd=self.remote), '')
        self.assertFalse(receipt['tracking']['single_chat_candidate'])
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
        receipt = self.publisher.publish('codex/example', CHAT)
        self.assertIn('remote feature retained', ' '.join(receipt['cleanup']))
        self.assertTrue(git('branch', '--list', 'codex/example', cwd=self.remote))

    def test_cli_rejects_extra_flags_main_and_unknown_repositories(self):
        for args in [['publish', 'mynormal', 'main', CHAT],
                     ['publish', 'mynormal', 'codex/example', CHAT, '--force'],
                     ['publish', '/tmp/arbitrary', 'codex/example', CHAT]]:
            with self.subTest(args=args), contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit):
                    MODULE['main'](args)


if __name__ == '__main__':
    unittest.main()
