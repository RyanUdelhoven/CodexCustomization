"""Real scanner and Git fixtures; all tokens are deliberately synthetic."""
from pathlib import Path
import runpy
import subprocess
import tempfile
import unittest
from unittest.mock import patch

M = runpy.run_path(str(Path(__file__).with_name('secret_check.py')))
scan = M['scan']


class SecretTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.repo = Path(self.tmp.name)
        self.git('init', '--initial-branch=main')
        self.git('config', 'user.name', 'Test')
        self.git('config', 'user.email', 'test@example.com')
        self.put('readme', 'safe')
        self.commit()
        self.base = self.git('rev-parse', 'HEAD').strip()

    def git(self, *args):
        return subprocess.run(['/usr/bin/git', '-c', 'core.hooksPath=/dev/null', *args],
                              cwd=self.repo, check=True, capture_output=True, text=True).stdout

    def put(self, path, content):
        p = self.repo / path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)
        self.git('add', '--', path)

    def commit(self):
        self.git('commit', '-m', 'fixture')

    def test_nested_environment_and_variants(self):
        for name in ['nested/.env', '.env.local', '.env.production', '.env.example.local']:
            with self.subTest(name=name):
                self.put(name, 'safe-looking=value')
                with self.assertRaisesRegex(ValueError, 'filename blocked'):
                    scan(self.repo, 'staged')
                self.git('reset', '--', name)

    def test_placeholder_template_passes(self):
        self.put('.env.example', 'API_KEY=replace_me')
        scan(self.repo, 'staged')

    def test_content_scanned_in_template_and_other_files(self):
        for name in ['.env.example', 'src/settings.ts']:
            self.put(name, 'token = "ghp_' + 'Ab3dE6gH9jK2mN5pQ8rS1tU4vW7xY0zA3bC6' + '"\n')
            with self.assertRaisesRegex(ValueError, 'Gitleaks'):
                scan(self.repo, 'staged')
            self.git('reset', '--', name)

    def test_index_not_working_copy_is_scanned(self):
        self.put('.env', 'fixture')
        (self.repo / '.env').unlink()
        with self.assertRaisesRegex(ValueError, 'filename blocked'):
            scan(self.repo, 'staged')

    def test_deleted_historical_secret_is_blocked(self):
        self.put('.env', 'fixture')
        self.commit()
        self.git('rm', '.env')
        self.commit()
        with self.assertRaisesRegex(ValueError, 'filename blocked'):
            scan(self.repo, 'range', self.base, 'HEAD')

    def test_deleted_historical_content_secret_is_blocked(self):
        self.put('settings', 'token = "ghp_' + 'Ab3dE6gH9jK2mN5pQ8rS1tU4vW7xY0zA3bC6' + '"\n')
        self.commit()
        self.git('rm', 'settings')
        self.commit()
        with self.assertRaisesRegex(ValueError, 'Gitleaks'):
            scan(self.repo, 'range', self.base, 'HEAD')

    def test_missing_scanner_blocks(self):
        with patch.dict(scan.__globals__, SCANNER=Path('/nonexistent/scanner')):
            with self.assertRaisesRegex(ValueError, 'missing'):
                scan(self.repo, 'staged')

    def test_repository_configuration_and_inline_allow_cannot_bypass(self):
        self.put('.gitleaks.toml', 'title = "disable repository rules"')
        self.put('settings', 'token = "ghp_' + 'Ab3dE6gH9jK2mN5pQ8rS1tU4vW7xY0zA3bC6' + '" # gitleaks:allow\n')
        with self.assertRaisesRegex(ValueError, 'Gitleaks'):
            scan(self.repo, 'staged')

    def test_pre_push_new_branch_checks_history_and_deletions_pass(self):
        self.put('.env', 'fixture')
        self.commit()
        self.git('rm', '.env')
        self.commit()
        tip = self.git('rev-parse', 'HEAD').strip()
        script = str(Path(__file__).with_name('secret_check.py'))
        zeros = '0' * 40
        result = subprocess.run(['/usr/bin/python3', '-I', script, 'pre-push',
                                 '--repo', str(self.repo)],
                                input=f'refs/heads/main {tip} refs/heads/new {zeros}\n',
                                text=True, capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('filename blocked', result.stderr)
        result = subprocess.run(['/usr/bin/python3', '-I', script, 'pre-push',
                                 '--repo', str(self.repo)],
                                input=f'(delete) {zeros} refs/heads/main {tip}\n',
                                text=True, capture_output=True)
        self.assertEqual(result.returncode, 0)

    def test_symlink_is_not_followed(self):
        (self.repo / 'link').symlink_to('/etc/passwd')
        self.git('add', 'link')
        scan(self.repo, 'staged')


if __name__ == '__main__':
    unittest.main()
