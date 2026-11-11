# Optional approval sounds

Audio stays local; run `python3 scripts/download-sounds.py` to download the clips into `$CODEX_HOME/sounds` (default `~/.codex/sounds`). This does not change the active hook.

- Navi Hey: https://www.myinstants.com/en/instant/navi-hey/
- Navi Listen: https://www.myinstants.com/en/instant/navi-listen-soundtrack5-84910/
- Metal Gear Solid alert: https://www.myinstants.com/en/instant/metal-gear-solid-alert/

The game audio belongs to its respective rights holders and is not included in this repository.

The approval hook always plays Hey, then independently has a one-in-six chance of playing Listen after Hey finishes.
When a local trimmed `navi-listen.wav` exists, the hook uses it instead of the MP3.
The hook chooses all clips before playback. When local `navi-hey-listen.wav` exists, it plays that combined recording for the one-in-six outcome, avoiding a process restart between words.
