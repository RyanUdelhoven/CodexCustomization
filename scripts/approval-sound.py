#!/usr/bin/env python3
"""Play Navi Hey, followed by Listen on one in six approval triggers."""
import os
from pathlib import Path
from secrets import randbelow
import subprocess


def main():
    sounds = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))) / "sounds"
    clips = [sounds / "navi-hey.mp3"]
    if randbelow(6) == 0:
        combined = sounds / "navi-hey-listen.wav"
        if combined.exists():
            clips = [combined]
        else:
            listen = sounds / "navi-listen.wav"
            if not listen.exists():
                listen = sounds / "navi-listen.mp3"
            clips.append(listen)
    for clip in clips:
        subprocess.run(["/usr/bin/afplay", "--volume", "0.25", str(clip)], check=True)


if __name__ == "__main__":
    main()
