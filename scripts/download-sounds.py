#!/usr/bin/env python3
"""Download optional sounds without overwriting existing files or changing hooks."""
import os
from pathlib import Path
from urllib.request import urlopen

SOUNDS = {
    "oot-rupee.wav": "https://noproblo.dayjo.org/zeldasounds/OOT/OOT_Get_Rupee.wav",
    "oot-pot-shatter.wav": "https://noproblo.dayjo.org/zeldasounds/OOT/OOT_Pot_Shatter.wav",
    "navi-hey.mp3": "https://www.myinstants.com/media/sounds/oot_navi_hey1.mp3",
    "navi-listen.mp3": "https://www.myinstants.com/media/sounds/navi-listen-soundtrack5.mp3",
    "metal-gear-solid-alert.mp3": "https://www.myinstants.com/media/sounds/tindeck_1.mp3",
}

def main():
    destination = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))) / "sounds"
    destination.mkdir(parents=True, exist_ok=True)
    for name, url in SOUNDS.items():
        target = destination / name
        if target.exists():
            print(f"Already exists: {target}")
            continue
        with urlopen(url, timeout=30) as response:
            data = response.read(5_000_001)
        is_wav = data.startswith(b"RIFF") and data[8:12] == b"WAVE"
        if not data or len(data) > 5_000_000 or not (is_wav or data.startswith(b"ID3") or data[0] == 0xFF):
            raise ValueError(f"Unexpected audio response: {url}")
        with target.open("xb") as output:
            output.write(data)
        print(f"Saved: {target}")

if __name__ == "__main__":
    main()
