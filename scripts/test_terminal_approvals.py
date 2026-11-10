"""Regression checks for the restricted reader and installed command rules."""
import contextlib
import io
import json
from pathlib import Path
import runpy
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
READER = runpy.run_path(str(ROOT / "scripts/codex-read"))
MAIN = READER["main"]
CODEX = "/Applications/ChatGPT.app/Contents/Resources/codex-cli/CodexCLI.app/Contents/MacOS/codex"


class RestrictedReaderTests(unittest.TestCase):
    def test_rejects_execution_and_write_flags(self):
        for arguments in [
            ["search", "--pre", "sh", "pattern", "."],
            ["search", "--hostname-bin", "sh", "pattern", "."],
            ["lines", "--in-place", "file", "1", "2"],
            ["files", ".", "-delete"],
            ["files", ".", "-exec", "sh"],
            ["now", "--set", "tomorrow"],
            ["health", "--upload-file", "file"],
        ]:
            with self.subTest(arguments=arguments), contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit):
                    MAIN(arguments)

    def test_search_ignores_environment_and_treats_pattern_as_data(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample.txt"
            path.write_text("--pre=malicious\n")
            with patch.dict("os.environ", {"RG_CONFIG_PATH": "/bad-config"}), patch("subprocess.run") as run:
                run.return_value.returncode = 0
                self.assertEqual(MAIN(["search", "--", "--pre=malicious", str(path)]), 0)
                args, kwargs = run.call_args
                self.assertIn("--no-config", args[0])
                self.assertEqual(args[0][-4:], ["--regexp", "--pre=malicious", "--", str(path.resolve())])
                self.assertEqual(kwargs["env"], {"PATH": "/usr/bin:/bin"})

    def test_lines_and_discovery_preserve_files_and_skip_symlink_contents(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "sample.txt"
            source.write_text("first\nsecond\nthird\n")
            nested = root / "nested"
            nested.mkdir()
            (nested / "deep.txt").write_text("keep")
            (root / "link").symlink_to(nested, target_is_directory=True)
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(MAIN(["lines", str(source), "2", "2"]), 0)
            self.assertEqual(output.getvalue(), "2: second\n")
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(MAIN(["files", str(root), "--name", "*.txt", "--max-depth", "1"]), 0)
            self.assertEqual(output.getvalue(), str(source.resolve()) + "\n")
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                MAIN(["files", str(root), "--name", "*.txt", "--max-depth", "3"])
            self.assertNotIn("/link/", output.getvalue())
            self.assertEqual(source.read_text(), "first\nsecond\nthird\n")

    def test_health_rejects_external_and_nonhealth_targets_before_connecting(self):
        for url in ["http://example.com:18080/health", "https://mynormal.localhost:18080/health",
                    "http://mynormal.localhost:18080/api/delete", "http://localhost:9999/health",
                    "http://user@localhost:3000/health", "http://localhost:3000/health?delete=1"]:
            with self.subTest(url=url), patch("http.client.HTTPConnection") as connection:
                with self.assertRaises(ValueError):
                    READER["health_target"](url)
                connection.assert_not_called()

    def test_health_uses_loopback_and_does_not_follow_redirects(self):
        with patch("http.client.HTTPConnection") as connect, contextlib.redirect_stdout(io.StringIO()):
            response = connect.return_value.getresponse.return_value
            response.status = 302
            response.read.return_value = b"redirect"
            self.assertEqual(READER["health"]("http://mynormal.localhost:18080/health"), 1)
            connect.assert_called_once_with("127.0.0.1", 18080, timeout=10)
            connect.return_value.request.assert_called_once_with(
                "GET", "/health", headers={"Host": "mynormal.localhost:18080"})


class InstalledPolicyTests(unittest.TestCase):
    def test_allowances_and_guardrails_against_combined_rules(self):
        # Evaluate every configured prefix against ALL installed rules, including old grants.
        rules = []
        definitions = []
        namespace = {"prefix_rule": lambda **rule: definitions.append(rule)}
        exec((ROOT / "rules/terminal-read.rules").read_text(), namespace)
        for path in sorted((ROOT / "rules").glob("*.rules")):
            rules.extend(["--rules", str(path)])
        cases = [(rule["pattern"], rule["decision"]) for rule in definitions]
        cases.extend([
            (["/usr/bin/install", "-m", "555", str(ROOT / "scripts/codex-git"),
              "/Users/ryanudelhoven/.local/share/codex-publish/codex-git"], "prompt"),
            (["git", "push", "origin", "main"], "prompt"),
            (["git", "push", "origin", "main", "--force"], "prompt"),
            (["git", "-C", str(ROOT), "push", "origin", "main"], "prompt"),
            (["git", "branch", "-d", "main"], "forbidden"),
            (["/Users/ryanudelhoven/.local/share/codex-publish/codex-git", "publish",
              "mynormal", "codex/example", "invalid-id", "--force"], "allow"),
            (["git", "remote", "remove", "origin"], "forbidden"),
            (["node", "-e", "require('fs').writeFileSync('/tmp/never-run', '')"], "prompt"),
            (["sed", "-n", "1p;w /tmp/never-run", "README.md"], "prompt"),
            (["rg", "--pre=sh", "pattern", "."], "prompt"),
            (["find", ".", "-delete"], "prompt"),
            (["curl", "-fsS", "http://marketnuance.localhost:18080/", "--upload-file", "secret"], "prompt"),
            (["date", "110912002026"], "prompt"),
            (["/usr/sbin/sysctl", "-n", "hw.optional.arm64", "kern.maxfiles=99999"], "prompt"),
            ([str(ROOT / "scripts/codex-read"), "now"], "prompt"),
            (["/Users/ryanudelhoven/.local/share/codex-publish/codex-read", "now"], "allow"),
            (["git", "branch", "--show-current"], "prompt"),
            (["git", "rev-parse", "--abbrev-ref", "HEAD"], "allow"),
        ])
        for command, expected in cases:
            with self.subTest(command=command):
                result = subprocess.run([CODEX, "execpolicy", "check", *rules, "--", *command],
                                        check=True, capture_output=True, text=True)
                self.assertEqual(json.loads(result.stdout)["decision"], expected)

    def test_merge_preflight_and_lifecycle_commands(self):
        rules = [item for path in sorted((ROOT / 'rules').glob('*.rules'))
                 for item in ('--rules', str(path))]
        protected = '/Users/ryanudelhoven/.local/share/codex-publish/'
        commands = [
            ['cat', 'skills/post-merge-cleanup/SKILL.md', 'rules/merge-push.md'],
            ['git', 'status', '--short'],
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            ['git', 'log', '--oneline', 'main..HEAD'],
            ['git', 'diff', '--stat', 'main..HEAD'],
            [protected + 'codex-read', 'search', 'merge', 'skills'],
            [protected + 'codex-read', 'lines', 'README.md', '1', '30'],
            [protected + 'codex-read', 'files', 'scripts'],
        ]
        commands += [[protected + 'codex-git', action, 'customization',
                      'codex/example', '00000000-0000-0000-0000-000000000000']
                     for action in ['inspect', 'register', 'publish', 'finish']]
        for command in commands:
            with self.subTest(command=command):
                output = subprocess.check_output(
                    [CODEX, 'execpolicy', 'check', *rules, '--', *command], text=True)
                self.assertEqual(json.loads(output)['decision'], 'allow')


if __name__ == "__main__":
    unittest.main()
