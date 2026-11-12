#!/usr/bin/env python3
"""Play an OoT rupee, replacing it with a pot shatter one time in six."""
import os
from pathlib import Path
from secrets import randbelow
import subprocess


def main():
    sounds = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))) / "sounds"
    pot = randbelow(6) == 0
    clip = sounds / ("oot-pot-shatter.wav" if pot else "oot-rupee.wav")
    subprocess.run(["/usr/bin/afplay", "--volume", "0.675" if pot else "0.30", str(clip)], check=True)


if __name__ == "__main__":
    main()
