"""Exercise installed-style scripts against hostile inputs and environment overrides."""
import json
import os
from pathlib import Path
import runpy
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
INSTALLER = runpy.run_path(str(ROOT / 'scripts/install-script-allowances.py'))
YAML = ROOT / 'skills/analyze-youtube/.runtime/venv/lib/python3.12/site-packages/yaml'


class ScriptAllowanceTests(unittest.TestCase):
    def test_legacy_aliases_normalize_without_losing_history_or_remote_hosts(self):
        module = runpy.run_path(str(ROOT / 'skills/feature-branch/scripts/branch_chats.py'))
        origin = {'source': 'codex', 'hostId': '', 'threadId': 'origin'}
        record = {'id': 'lifecycle', 'creationTip': 'tip', 'origin': origin,
            'trackedFromCreation': True, 'closed': True,
            'participants': [origin, dict(origin, hostId='local'),
                dict(origin, hostId='remote-host'),
                {'source': 'chatgpt', 'hostId': '', 'threadId': 'origin'}]}
        module['validate_record'](record)
        module['normalize_record'](record)
        module['validate_record'](record)
        self.assertEqual(len(record['participants']), 3)
        self.assertEqual(record['origin']['hostId'], 'local')
        self.assertEqual(record['id'], 'lifecycle')
        self.assertEqual(record['creationTip'], 'tip')
        self.assertTrue(record['closed'])
        self.assertTrue(record['trackedFromCreation'])

    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        cls.root = Path(cls.temporary.name)
        cls.install = cls.root / 'install'
        cls.files = INSTALLER['payloads'](YAML)
        INSTALLER['install'](cls.install, cls.files)

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def test_validator_ignores_local_modules_and_rejects_executable_yaml(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            marker = directory / 'executed'
            (directory / 'yaml.py').write_text('raise RuntimeError("local module imported")')
            skill = directory / 'skill'
            skill.mkdir()
            (skill / 'SKILL.md').write_text('---\nname: example\ndescription: Example\n---\n# Skill\n')
            env = dict(os.environ, PYTHONPATH=str(directory), PYTHONHOME='/nonexistent')
            command = [str(self.install / 'codex-skill-validate'), str(skill)]
            result = subprocess.run(command, cwd=directory, env=env, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            (skill / 'SKILL.md').write_text(
                '---\nname: !!python/object/apply:os.system ["touch ' + str(marker) + '"]\n'
                'description: Example\n---\n')
            result = subprocess.run(command, cwd=directory, env=env, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(marker.exists())
            result = subprocess.run(command + ['-c', 'print(1)'], capture_output=True)
            self.assertNotEqual(result.returncode, 0)

    def test_tracker_ignores_git_environment_and_path_and_preserves_lifecycle(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            repo = directory / 'repo'
            def git(*args):
                return subprocess.check_output(['/usr/bin/git', '-c', 'core.hooksPath=/dev/null',
                    '-C', str(repo), *args], text=True).strip()
            repo.mkdir()
            git('init', '-b', 'main')
            git('-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.com',
                'commit', '--allow-empty', '-m', 'initial')
            git('branch', 'codex/example')
            marker = directory / 'wrong-git'
            fake = directory / 'git'
            fake.write_text('#!/bin/sh\ntouch "' + str(marker) + '"\nexit 1\n')
            fake.chmod(0o755)
            env = dict(os.environ, PATH=str(directory), GIT_DIR='/nonexistent',
                GIT_CONFIG_COUNT='1', GIT_CONFIG_KEY_0='core.fsmonitor', GIT_CONFIG_VALUE_0=str(fake))
            command = [str(self.install / 'codex-branch-chats')]
            arguments = ['--repo', str(repo), '--branch', 'codex/example']
            def tracker(action, *extra):
                result = subprocess.run(command + [action] + arguments + list(extra),
                    env=env, capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                return json.loads(result.stdout)
            self.assertTrue(tracker('register', '--chat-id', 'origin', '--created')['single_chat_candidate'])
            same = tracker('register', '--chat-id', 'origin', '--host-id', 'local')
            self.assertTrue(same['single_chat_candidate'])
            self.assertEqual(len(same['record']['participants']), 1)
            self.assertTrue(tracker('inspect')['single_chat_candidate'])
            self.assertFalse(tracker('register', '--chat-id', 'origin', '--host-id', 'remote-host')['single_chat_candidate'])
            self.assertFalse(tracker('register', '--chat-id', 'another-chat')['single_chat_candidate'])
            self.assertFalse(tracker('close')['single_chat_candidate'])
            self.assertFalse(marker.exists())
            self.assertEqual(git('rev-parse', '--abbrev-ref', 'HEAD'), 'main')
            result = subprocess.run(command + ['inspect'] + arguments + ['--exec', str(fake)], capture_output=True)
            self.assertNotEqual(result.returncode, 0)

    def test_installed_payloads_are_readonly_and_match_reviewed_bytes(self):
        for name, (content, mode) in self.files.items():
            with self.subTest(name=name):
                path = self.install / name
                self.assertEqual(path.read_bytes(), content)
                self.assertEqual(path.stat().st_mode & 0o777, mode)
        self.assertEqual((self.install / 'codex-branch-chats').read_bytes(),
                         (self.install / 'branch_chats.py').read_bytes())


if __name__ == '__main__':
    unittest.main()
