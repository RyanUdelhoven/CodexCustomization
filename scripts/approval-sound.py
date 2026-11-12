#!/usr/bin/env python3
"""Play Navi Hey, followed by Listen on one in six approval triggers."""
import os
from pathlib import Path
from secrets import randbelow
import subprocess


def main():
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
