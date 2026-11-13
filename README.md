# CodexCustomization

The [CodexCustomization repository](https://github.com/RyanUdelhoven/CodexCustomization) is rooted locally at `~/.codex/`. It tracks reviewed customization files using a default-deny allowlist.

## Tracked files

- `skills/<name>/`: custom skills and their supporting files.
- `skills/AGENTS.md`: skill maintenance and synchronization instructions.
- `AGENTS.md`: user-level working instructions.
- `hooks.json`: local permission-request capture and portable Navi approval sound.
- `config.example.toml`: sanitized preference template.
- `scripts/`: optional sound download helper.
- `sounds/README.md`: audio sources; actual game audio stays local.
- `rules/README.md`: guidance; local command grants stay private.
- `examples/`, `templates/`: sanitized reusable customization sources.

Authentication, live `config.toml`, hook trust state, chat history, application databases, caches, managed skills, plugins, and computer-specific runtime files remain ignored. Add explicit allowlist entries for new skills and reviewed rules. Ignore rules do not erase historical commits.

## Setup

Clone into an empty Codex home directory only. If `~/.codex` already exists, clone elsewhere and review and merge desired files; preserve existing configuration and authentication.

Merge selected settings from `config.example.toml` into local `config.toml`. Review `AGENTS.md` and `hooks.json` before installing. The approval hook uses `CODEX_HOME`, falling back to `~/.codex`, and macOS `afplay`. Changed commands may require renewed hook trust in Codex.

Download optional sounds without changing the hook:

```sh
python3 scripts/download-sounds.py
```

The approval sound script always plays Navi Hey, then has an independent one-in-six chance of playing Listen. To use Metal Gear Solid instead, replace the sound command in `hooks.json` with `/usr/bin/afplay` and the path to `metal-gear-solid-alert.mp3`.

The [approval-review skill](skills/approval-review/SKILL.md) records permission
requests locally without changing approval decisions. Review and trust the new
handler in Codex's Review hooks or Settings > Hooks, then reload if needed.
Confirm capture after a naturally occurring request; synthetic tests do not prove
the app loaded the hook. Say “review approval friction” to investigate new events.
Private incidents, corrections, and checkpoints stay in
`$CODEX_HOME/.local/approval-review` (default `~/.codex/.local/approval-review`),
outside tracked files. Remove only its capture handler to pause collection.

## Maintenance

Run Git commands from `~/.codex`. Follow `skills/AGENTS.md` for skill changes. Review staged content before committing and pushing. Never add ignored runtime files with `git add -f`.

## One-command feature completion

Open a project chat, describe the feature, and iterate in that chat. When happy,
submit exact standalone lowercase `mp` (surrounding whitespace allowed). That one
command authorizes final task review, outstanding checks, committing the reviewed
task files, merge, push, and completed-branch cleanup. The chat stays open for you
to archive. `mpa` is retired. Nothing publishes automatically after normal work.

The hook reads its `cwd` and `session_id`, gets the current branch from Git, and
checks this chat's branch participation. Already-ready work publishes directly.
Work needing preparation reaches the assistant in the same turn with a scoped
request. The assistant completes checks, commits only task files, and uses the
supplied --complete handoff to record the verified SHA and publish. You do not
run terminal commands, request a separate commit, or prepare records yourself.

Preparation reuses valid checks and preserves unrelated work. Genuine blockers,
ambiguous scope, main/detached HEAD, conflicting remote history, or publication
failures stop with an explanation in the app. The protected publisher retains its
secret scans and exact-commit check. An interrupted preparation request expires
on a later message or after 30 minutes; publication failures require state
inspection, not a blind retry.

Review/trust the handler in Settings > Hooks or `/hooks` if the app requests it;
reload if an existing session retains older hooks. This is one-time setup, not a
per-feature step. Internal --prepare remains available for clean preverified
commits, but the user does not need it. Tests use disposable local repositories;
unit/integration results do not establish live desktop hook activation.
