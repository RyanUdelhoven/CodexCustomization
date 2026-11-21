#!/usr/bin/env python3
"""Play Navi only for permission requests handled by the user, not auto-review."""
import argparse
import json
import os
from pathlib import Path
from secrets import randbelow
import subprocess
import sys


def reverse_lines(path):
    """Read recent transcript records first without loading the transcript."""
    with Path(path).open("rb") as handle:
        position = handle.seek(0, 2)
        pending = b""
        while position:
            size = min(position, 65536)
            position -= size
            handle.seek(position)
            parts = (handle.read(size) + pending).split(b"\n")
            pending = parts[0]
            yield from reversed(parts[1:])
        if pending:
            yield pending


def needs_user(payload):
    """Require affirmative evidence of manual review for this active turn.

    PermissionRequest precedes approval resolution and its permission_mode does
    not identify the reviewer. Use the runtime turn context, never config.toml:
    session overrides can select a different reviewer. Transcript format is not
    a stable API, so missing/changed context stays silent rather than producing
    a misleading alert. This function never returns an approval decision.
    """
    if not isinstance(payload, dict) or payload.get("hook_event_name") != "PermissionRequest":
        return False
    turn_id = payload.get("turn_id")
    path = payload.get("transcript_path")
    if not isinstance(turn_id, str) or not turn_id or not isinstance(path, str) or not path:
        return False
    try:
        for line in reverse_lines(path):
            try:
                record = json.loads(line)
            except (ValueError, UnicodeError):
                continue
            if not isinstance(record, dict) or record.get("type") != "turn_context":
                continue
            context = record.get("payload")
            if not isinstance(context, dict):
                return False
            # Never use an older turn's policy after a session override.
            return (context.get("turn_id") == turn_id
                    and context.get("approvals_reviewer") == "user")
    except (OSError, ValueError):
        return False
    return False


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preview", action="store_true", help="Play a sound without a hook event")
    args = parser.parse_args()
    if not args.preview:
        try:
            payload = json.load(sys.stdin)
        except (ValueError, OSError):
            return
        if not needs_user(payload):
            return
    sounds = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))) / "sounds"
    clips = [(sounds / "navi-hey.mp3", "0.75")]
    if randbelow(6) == 0:
        combined = sounds / "navi-hey-listen-soft.wav"
        if combined.exists():
            clips = [(combined, "0.75")]
        else:
            listen = sounds / "navi-listen.wav"
            if not listen.exists():
                listen = sounds / "navi-listen.mp3"
            clips.append((listen, "0.675"))
    for clip, volume in clips:
        subprocess.run(["/usr/bin/afplay", "--volume", volume, str(clip)], check=True)


if __name__ == "__main__":
    main()
