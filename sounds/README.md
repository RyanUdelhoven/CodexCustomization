# Optional notification sounds

Audio stays local; run `python3 scripts/download-sounds.py` to download the clips into `$CODEX_HOME/sounds` (default `~/.codex/sounds`). This does not change the active hook.

- Navi Hey: https://www.myinstants.com/en/instant/navi-hey/
- Navi Listen: https://www.myinstants.com/en/instant/navi-listen-soundtrack5-84910/
- Metal Gear Solid alert: https://www.myinstants.com/en/instant/metal-gear-solid-alert/

The game audio belongs to its respective rights holders and is not included in this repository.

The attention hook plays Hey for structured user-question calls and manually
reviewed permission requests. Automatic permission review stays silent. It
independently has a one-in-six chance of playing Listen after Hey finishes.
Questions use `PreToolUse` matching `request_user_input` or
`request_user_input_async` (including the `functions.` prefix), once per batch.
They do not depend on transcript context or approval-review settings. If no
question tool is available, invoke `scripts/approval-sound.py --question` before
the real text question; do not duplicate a structured tool's alert.
When a local trimmed `navi-listen.wav` exists, the hook uses it instead of the MP3.
The hook chooses all clips before playback. When local `navi-hey-listen-soft.wav` exists, it plays that combined recording for the one-in-six outcome, avoiding a process restart between words. This version reduces only Listen's samples by 10%. Hey plays at 75%; standalone Listen plays at 67.5%.

The `Stop` hook plays `oot-rupee.wav` for a user-facing final answer, replacing it with
`oot-pot-shatter.wav` on an independent one-in-six random roll. Rupee plays at 30%
volume; pot shatter plays at 67.5%. This leaves the computer-use `notify` command intact.
The script requires matching session and turn IDs, a recognized user-facing
session source, and a latest assistant response with `phase: final_answer`.
Internal guardian approval reviews and other subagents stay silent, as do
intermediate messages, pending tool calls, and missing or changed transcript
context. Transcript format is not a stable API, so unknown formats stay silent.
`Stop` runs before the runtime commits completion; another Stop hook can still
request continuation. This filter does not claim to observe the desktop's idle UI.
Preview explicitly with `python3 scripts/turn-end-sound.py --preview`.
Verify routing without audio with
`python3 -B -m unittest discover -s scripts -p 'test_*sound.py'`.
Restart the desktop app if the hook has not loaded in an existing session.

OoT clips come from https://noproblo.dayjo.org/zeldasounds/oot/:
`OOT_Get_Rupee.wav` and `OOT_Pot_Shatter.wav`.

The earlier `mp` sound-only experiment used `metal-gear-solid-alert.mp3` at 75%
volume. The current mp handler performs protected publication instead; it does
not play that clip. The local audio remains available for other explicit uses.
