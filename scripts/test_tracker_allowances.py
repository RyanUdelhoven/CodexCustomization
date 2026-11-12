"""Installed-style tracker tests: reviewed imports, private output, and rejected code flags."""
import json
import os
from pathlib import Path
import runpy
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
INSTALLER = runpy.run_path(str(ROOT / 'scripts/install-tracker-allowances.py'))


class TrackerAllowanceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.destination = self.root / 'protected'
        self.payload = INSTALLER['payloads']()
        INSTALLER['install'](self.destination, self.payload)

    def command(self, name, *args, **kwargs):
        return subprocess.run([str(self.destination / name), *args], capture_output=True,
                              text=True, **kwargs)

    def test_isolated_imports_usage_lifecycle_and_no_code_options(self):
        hostile = self.root / 'hostile'
        hostile.mkdir()
        for name in ('approval_log', 'skill_usage', 'sqlite3', 'json'):
            (hostile / (name + '.py')).write_text('raise RuntimeError("wrong import")')
        env = dict(os.environ, PYTHONPATH=str(hostile), PYTHONHOME='/nonexistent')
        home = self.root / 'data'
        args = ['--home', str(home)]
        result = self.command('codex-skill-usage', *args, 'start', '--session', 'test', '--skills',
                              'approval-review', '--cwd', str(hostile), env=env, cwd=hostile)
        self.assertEqual(result.returncode, 0, result.stderr)
        run_id = json.loads(result.stdout)[0]['id']
        result = self.command('codex-skill-usage', *args, 'finish', '--runs', run_id, env=env, cwd=hostile)
        self.assertEqual(result.returncode, 0, result.stderr)
        result = self.command('codex-approval-tracker', *args, 'status', env=env, cwd=hostile)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['skill_usage']['runs'][0]['state'], 'finished')
        for name in ('codex-approval-tracker', 'codex-skill-usage'):
            result = self.command(name, '-c', 'print("no")', env=env, cwd=hostile)
            self.assertNotEqual(result.returncode, 0)

    def test_review_capture_and_redacted_export(self):
        home = self.root / 'data'
        args = ['--home', str(home)]
        payload = dict(hook_event_name='PermissionRequest', tool_name='Bash', session_id='test',
                       tool_input={'command': 'echo PRIVATE-CONTENT'})
        result = self.command('codex-approval-review', *args, 'capture', input=json.dumps(payload))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, '')
        output = self.root / 'export.json'
        result = self.command('codex-approval-tracker', *args, 'export', '--output', str(output))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn('PRIVATE-CONTENT', output.read_text())
        self.assertEqual(output.stat().st_mode & 0o777, 0o600)
        result = self.command('codex-approval-tracker', *args, 'export', '--output', str(output))
        self.assertNotEqual(result.returncode, 0)
        result = self.command('codex-approval-tracker', 'serve', '--host', '0.0.0.0')
        self.assertNotEqual(result.returncode, 0)

    def test_readonly_dependencies_and_source_changes_do_not_modify_install(self):
        for name, (content, mode) in self.payload.items():
            target = self.destination / name
            self.assertEqual(target.read_bytes(), content)
            self.assertEqual(target.stat().st_mode & 0o777, mode)
        link = self.root / 'link'
        link.symlink_to(self.destination, target_is_directory=True)
        with self.assertRaises(ValueError):
            INSTALLER['install'](link, self.payload)


if __name__ == '__main__':
    unittest.main()
