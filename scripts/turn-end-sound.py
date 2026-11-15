#!/usr/bin/env python3
"""Play completion audio only for a user-facing session's final answer."""
import argparse
import json
import os
from pathlib import Path
from secrets import randbelow
import subprocess
import sys


def is_user_completion(payload):
    """Fail silent for internal review sessions or unverified Stop events.

    Stop is a pre-completion hook, not a post-completion notification. The
    transcript is an unstable runtime interface; require positive evidence
    rather than letting guardian/subagent completions sound like finished work.
    """
    if not isinstance(payload, dict) or payload.get("hook_event_name") != "Stop":
        return False
    session = payload.get("session_id")
    turn = payload.get("turn_id")
    path = payload.get("transcript_path")
    message = payload.get("last_assistant_message")
    if not all(isinstance(value, str) and value for value in (session, turn, path, message)):
        return False
    try:
        with Path(path).open() as handle:
            # Session metadata is the first record. Never guess from a title,
            # permission mode, or model: guardian uses normal models too.
            meta = json.loads(next(handle))
            if not isinstance(meta, dict) or meta.get("type") != "session_meta":
                return False
            info = meta.get("payload")
            if not isinstance(info, dict) or info.get("id") != session:
                return False
            if info.get("source") not in {"cli", "vscode", "exec"}:
                return False
            active_turn = None
            latest = None
            for line in handle:
                record = json.loads(line)
                if not isinstance(record, dict):
                    return False
                item = record.get("payload")
                if not isinstance(item, dict):
                    continue
                if record.get("type") == "turn_context":
                    active_turn = item.get("turn_id")
                    latest = None
                elif record.get("type") == "response_item":
                    latest = item
            if active_turn != turn or not isinstance(latest, dict):
                return False
            return (latest.get("type") == "message"
                    and latest.get("role") == "assistant"
                    and latest.get("phase") == "final_answer")
    except (OSError, ValueError, StopIteration, TypeError):
        return False


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preview", action="store_true")
    args = parser.parse_args()
    if not args.preview:
        try:
            payload = json.load(sys.stdin)
        except (ValueError, OSError):
            return
        if not is_user_completion(payload):
            return
    sounds = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))) / "sounds"
    pot = randbelow(6) == 0
    clip = sounds / ("oot-pot-shatter.wav" if pot else "oot-rupee.wav")
    subprocess.run(["/usr/bin/afplay", "--volume", "0.675" if pot else "0.30", str(clip)], check=True)


if __name__ == "__main__":
    main()
