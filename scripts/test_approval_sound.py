"""Sound routing regressions; never play audio during verification."""
import io
import json
from pathlib import Path
import runpy
import re
import tempfile
import unittest
from unittest.mock import patch

MODULE = runpy.run_path(str(Path(__file__).with_name("approval-sound.py")))


class ApprovalSoundTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.transcript = Path(self.directory.name) / "session.jsonl"
        self.event = {"hook_event_name": "PermissionRequest", "turn_id": "turn-2",
                      "permission_mode": "default", "transcript_path": str(self.transcript)}

    def context(self, reviewer, turn="turn-2"):
        return {"type": "turn_context", "payload": {
            "turn_id": turn, "approvals_reviewer": reviewer}}

    def write_records(self, *records):
        self.transcript.write_text("\n".join(json.dumps(r) for r in records) + "\n")

    def run_hook(self, payload=None, arguments=None):
        with patch("sys.argv", ["approval-sound.py"] + (arguments or [])), \
                patch("sys.stdin", io.StringIO(json.dumps(payload or self.event))), \
                patch("subprocess.run") as play, \
                patch.dict(MODULE["main"].__globals__, {"randbelow": lambda _: 1}):
            MODULE["main"]()
            return play.call_args_list

    def test_auto_review_with_default_permission_mode_is_silent(self):
        self.write_records(self.context("auto_review"))
        self.assertEqual(self.run_hook(), [])

    def test_manual_review_preserves_navi_sound(self):
        self.write_records(self.context("user"))
        calls = self.run_hook()
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0].args[0][:3], ["/usr/bin/afplay", "--volume", "0.75"])
        self.assertTrue(calls[0].args[0][-1].endswith("navi-hey.mp3"))

    def test_session_override_uses_latest_turn_not_global_or_old_policy(self):
        for old, new, expected in [("user", "auto_review", 0), ("auto_review", "user", 1)]:
            with self.subTest(new=new):
                self.write_records(self.context(old, "turn-1"), self.context(new))
                self.assertEqual(len(self.run_hook()), expected)

    def test_stale_or_unknown_context_never_alerts(self):
        for records in [[], [self.context("user", "turn-1")], [self.context("future")],
                        [{"type": "turn_context", "payload": None}]]:
            with self.subTest(records=records):
                self.write_records(*records)
                self.assertEqual(self.run_hook(), [])
        self.transcript.unlink()
        self.assertEqual(self.run_hook(), [])

    def test_invalid_event_never_alerts(self):
        self.write_records(self.context("user"))
        for event in [[], {"hook_event_name": "Stop"},
                      dict(self.event, turn_id=None), dict(self.event, transcript_path=None)]:
            with self.subTest(event=event):
                self.assertFalse(MODULE["needs_user"](event))

    def test_reverse_reader_handles_chunks_and_incomplete_final_record(self):
        self.write_records(self.context("auto_review", "turn-1"), self.context("user"))
        with self.transcript.open("a") as handle:
            handle.write(json.dumps({"type": "response_item", "text": "a" * 150000}))
            handle.write('\n{"unfinished":')
        self.assertEqual(len(self.run_hook()), 1)

    def test_preview_is_explicit_and_does_not_require_transcript(self):
        self.assertEqual(len(self.run_hook(arguments=["--preview"])), 1)

    def test_question_tools_alert_without_permission_review_or_transcript(self):
        for name in MODULE['QUESTION_TOOLS']:
            field = 'title' if name.endswith('_async') else 'question'
            event = {'hook_event_name': 'PreToolUse', 'tool_name': name,
                     'tool_input': {'questions': [{field: 'Which behavior should remain?'}]}}
            with self.subTest(tool=name):
                self.assertEqual(len(self.run_hook(event)), 1)
                event['tool_input'] = json.dumps(event['tool_input'])
                self.assertEqual(len(self.run_hook(event)), 1)

    def test_question_batch_plays_once_and_other_tools_stay_silent(self):
        event = {'hook_event_name': 'PreToolUse', 'tool_name': 'request_user_input_async',
                 'tool_input': {'questions': [{'title': 'First?'}, {'title': 'Second?'}]}}
        self.assertEqual(len(self.run_hook(event)), 1)
        for name in ['Bash', 'exec', 'request_user_input_async_extra', 'mcp__search', None, []]:
            with self.subTest(tool=name):
                self.assertEqual(self.run_hook(dict(event, tool_name=name)), [])
        self.assertEqual(self.run_hook(dict(event, hook_event_name='PostToolUse')), [])

    def test_invalid_question_payloads_stay_silent(self):
        for arguments in [None, 'not JSON', [], {}, {'questions': []},
                          {'questions': [{}]}, {'questions': [{'title': ' '}]},
                          {'questions': [{'title': 'First?'}, None]}]:
            with self.subTest(arguments=arguments):
                event = {'hook_event_name': 'PreToolUse', 'tool_name': 'request_user_input_async',
                         'tool_input': arguments}
                self.assertEqual(self.run_hook(event), [])

    def test_text_question_fallback_is_explicit(self):
        self.assertEqual(len(self.run_hook(arguments=['--question'])), 1)

    def test_registered_question_hook_matches_supported_tools_only(self):
        hooks = json.loads(Path(__file__).resolve().parents[1].joinpath('hooks.json').read_text())
        groups = hooks['hooks']['PreToolUse']
        for name in MODULE['QUESTION_TOOLS']:
            matched = [group for group in groups if re.search(group['matcher'], name)]
            self.assertEqual(len(matched), 1)
            self.assertIn('approval-sound.py', matched[0]['hooks'][0]['command'])
        for name in ['Bash', 'exec_command', 'request_user_input_async_extra']:
            self.assertFalse(any(re.search(group['matcher'], name) for group in groups))

    def test_questions_keep_the_occasional_hey_listen_variant(self):
        with tempfile.TemporaryDirectory() as directory:
            sounds = Path(directory) / 'sounds'
            sounds.mkdir()
            (sounds / 'navi-hey-listen-soft.wav').touch()
            with patch('sys.argv', ['approval-sound.py', '--question']), \
                    patch.dict('os.environ', {'CODEX_HOME': directory}), \
                    patch('subprocess.run') as play, \
                    patch.dict(MODULE['main'].__globals__, {'randbelow': lambda _: 0}):
                MODULE['main']()
            self.assertEqual(len(play.call_args_list), 1)
            self.assertTrue(play.call_args.args[0][-1].endswith('navi-hey-listen-soft.wav'))

    def test_bad_stdin_does_not_fail_hook(self):
        with patch("sys.argv", ["approval-sound.py"]), \
                patch("sys.stdin", io.StringIO("not JSON")), patch("subprocess.run") as play:
            MODULE["main"]()
            play.assert_not_called()


if __name__ == "__main__":
    unittest.main()
