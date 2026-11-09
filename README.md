# Codex customizations

Personal Codex skills, working instructions, portable approval hooks, and configuration examples.

## Layout

- `<skill-name>/`: installed custom skills and their supporting files.
- `customizations/instructions/AGENTS.md`: reusable user-level working instructions.
- `customizations/hooks.json`: portable Navi approval sound hook.
- `customizations/config.example.toml`: selected preferences without local runtime state.
- `customizations/scripts/`: optional setup helpers.
- `customizations/sounds/`: audio sources and download instructions.
- `customizations/rules/`, `examples/`, `templates/`: reviewed customization sources.

The checkout currently lives at `~/.codex/skills`, so existing skills stay installed without relocation. Do not move skill folders into a nested `skills/` directory here.

## Install on another computer

Clone this repository into an empty `~/.codex/skills` directory. If that directory already exists, preserve it and copy only the desired skill folders instead.

Review `customizations/instructions/AGENTS.md` before merging it into `~/.codex/AGENTS.md`. Merge selected settings from `customizations/config.example.toml` into your own configuration.

Download optional sounds:

```sh
python3 customizations/scripts/download-sounds.py
```

Review and merge `customizations/hooks.json` into `~/.codex/hooks.json`; preserve existing hooks. Enable or trust hooks through your Codex installation as required. The hook uses `CODEX_HOME`, falling back to `~/.codex`. Changing hook commands may require renewed trust. Playback uses macOS `afplay`.

To select Metal Gear Solid, replace `navi-hey.mp3` with `metal-gear-solid-alert.mp3` in your local hook. This repository does not change active local hooks automatically.

Install command approval rules only after reviewing each grant. Configure MCP services locally; generated computer-use paths and authentication are intentionally omitted.

## Maintenance and privacy

Edit custom skills in this checkout, follow the repository skill-review instructions, review changes, commit, and push to `origin`.

Changes to live `~/.codex/hooks.json`, `AGENTS.md`, or configuration do not automatically update the reviewed repository copies. Export only sanitized changes into `customizations/`.

The root ignore file allows only named skill folders and reviewed customization sources. Add an explicit allowlist entry when introducing a new skill. Authentication, chat history, application databases, caches, plugin packages, local approval grants, and game audio are excluded. Never copy the entire live `.codex` directory into this repository. Inspect staged changes before publishing; ignore rules do not remove tracked files or historical commits.
