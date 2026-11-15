"""Completion routing tests; playback is always mocked."""
import io
import json
from pathlib import Path
import runpy
import tempfile
import unittest
from unittest.mock import patch

MODULE = runpy.run_path(str(Path(__file__).with_name("turn-end-sound.py")))


class CompletionSoundTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / "session.jsonl"
        self.event = dict(hook_event_name="Stop", session_id="session", turn_id="turn",
                          transcript_path=str(self.path), last_assistant_message="Done")

    def transcript(self, source="vscode", phase="final_answer", turn="turn", extra=()):
        records = [dict(type="session_meta", payload=dict(id="session", source=source)),
                   dict(type="turn_context", payload=dict(turn_id=turn)),
                   dict(type="response_item", payload=dict(type="message", role="assistant",
                                                          phase=phase)), *extra]
        self.path.write_text("".join(json.dumps(r) + "\n" for r in records))

    def play(self, event=None, roll=1, arguments=()):
        with patch("sys.argv", ["turn-end-sound.py", *arguments]), \
                patch("sys.stdin", io.StringIO(json.dumps(self.event if event is None else event))), \
                patch("subprocess.run") as player, \
                patch.dict(MODULE["main"].__globals__, {"randbelow": lambda _: roll}):
            MODULE["main"]()
            return player.call_args_list

    def test_user_final_answer_preserves_both_clips_and_volumes(self):
        for source in ("vscode", "cli", "exec"):
            self.transcript(source=source)
            for roll, clip, volume in [(1, "oot-rupee.wav", "0.30"),
                                       (0, "oot-pot-shatter.wav", "0.675")]:
                with self.subTest(source=source, roll=roll):
                    calls = self.play(roll=roll)
                    self.assertEqual(len(calls), 1)
                    self.assertEqual(calls[0].args[0][:3], ["/usr/bin/afplay", "--volume", volume])
                    self.assertTrue(calls[0].args[0][-1].endswith(clip))

    def test_guardian_and_other_subagents_stay_silent(self):
        for source in [{"subagent": {"other": "guardian"}}, {"subagent": "thread_spawn"},
                       "unknown", None]:
            self.transcript(source=source)
            self.assertEqual(self.play(), [])

    def test_intermediate_message_and_pending_tool_stay_silent(self):
        for phase in ("commentary", None):
            self.transcript(phase=phase)
            self.assertEqual(self.play(), [])
        self.transcript(extra=[dict(type="response_item", payload=dict(type="function_call"))])
        self.assertEqual(self.play(), [])

    def test_missing_stale_and_malformed_context_stay_silent(self):
        self.assertEqual(self.play(), [])
        self.transcript(turn="old")
        self.assertEqual(self.play(), [])
        self.transcript()
        for event in [[], {}, dict(self.event, session_id="other"),
                      dict(self.event, hook_event_name="SubagentStop"),
                      dict(self.event, last_assistant_message=None)]:
            self.assertEqual(self.play(event), [])
        with self.path.open("a") as handle:
            handle.write('{"unfinished":')
        self.assertEqual(self.play(), [])

    def test_continued_stop_can_still_finish(self):
        self.transcript()
        self.assertEqual(len(self.play(dict(self.event, stop_hook_active=True))), 1)

    def test_preview_requires_explicit_flag(self):
        self.assertEqual(len(self.play(arguments=["--preview"])), 1)

    def test_bad_stdin_is_silent(self):
        with patch("sys.argv", ["turn-end-sound.py"]), \
                patch("sys.stdin", io.StringIO("bad JSON")), patch("subprocess.run") as player:
            MODULE["main"]()
            player.assert_not_called()


if __name__ == "__main__":
    unittest.main()
