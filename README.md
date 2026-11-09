# CodexCustomization

The [CodexCustomization repository](https://github.com/RyanUdelhoven/CodexCustomization) is rooted locally at `~/.codex/`. It tracks reviewed customization files using a default-deny allowlist.

## Tracked files

- `skills/<name>/`: custom skills and their supporting files.
- `skills/AGENTS.md`: skill maintenance and synchronization instructions.
- `AGENTS.md`: user-level working instructions.
- `hooks.json`: portable Navi approval sound hook.
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

To use Metal Gear Solid, replace `navi-hey.mp3` with `metal-gear-solid-alert.mp3` in `hooks.json`.

## Maintenance

Run Git commands from `~/.codex`. Follow `skills/AGENTS.md` for skill changes. Review staged content before committing and pushing. Never add ignored runtime files with `git add -f`.
