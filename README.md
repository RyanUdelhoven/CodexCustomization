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

The attention sound script plays Navi Hey for structured user-question calls and manually reviewed permission requests, with the existing one-in-six Listen variant. The `PreToolUse` matcher covers `request_user_input` and `request_user_input_async`, with or without the `functions.` prefix. A question batch plays once; it does not inspect transcripts or depend on the approval reviewer. Other tools stay silent. When no question tool is available, `python3 scripts/approval-sound.py --question` alerts before a real text question; do not also invoke it for tool-based questions.

`PermissionRequest` also fires for automatic review, before resolution; it is not proof that a person needs to approve. For permission events only, the script reads the latest runtime `turn_context` and checks its turn ID and explicit `user` reviewer. Automatic review and missing, stale, or changed transcript context stay silent. Approval decisions and permission logging remain unchanged. Preview explicitly with `python3 scripts/approval-sound.py --preview`.

Verify sound routing without playing audio: `python3 -B -m unittest discover -s scripts -p 'test_approval_sound.py'`. A question alert observes a tool attempt, not confirmation that its UI opened. The permission guard distinguishes reviewers rather than observing the approval UI. Review/trust the changed hook in Settings > Hooks or `/hooks`, and reload existing sessions if necessary. Some tool paths may opt out of hooks; unit tests do not establish live desktop coverage. See [official hook semantics](https://learn.chatgpt.com/docs/hooks#tool-coverage).

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

## One-command project completion

Submit exact standalone lowercase `mp` to finish every local and live remote feature branch in
this project, including pending work in linked worktrees. The agent reviews and
commits changes on their owning branches, then merges each branch individually
through its own PR, preserving commits and performing verified cleanup. Primary
branches are targets. Include live remote-only branches by restoring their exact
frozen commits locally; later-created branches are excluded. Nothing publishes after
ordinary work or merely because this workflow is configured. Chats stay open;
`mpa` is retired.

The hook freezes branch/worktree scope. The assistant prepares each branch, runs
required checks, and invokes the scoped protected `codex-git complete` handoff for
each one. It brings verified main into subsequent branches when needed and reruns
affected checks. No additional commit or mp commands are needed between branches.
Conflicts trigger investigation and focused user questions before resolution.
Active worktrees, failed checks, changed tips, and unresolved choices stop
publication with a completed/remaining report. See [execution rules](rules/merge-push.md).

Conceptually, each mp cycle follows these steps:

- Freeze local and live remote branch scope; preserve each branch's owning worktree.
- Compare committed tips and pending work with live published main.
- Skip duplicate merges for fully integrated branches.
- Prepare missing work; investigate conflicts and ask about disputed behavior.
- Apply answers, verify the resolved contents, and commit necessary changes.
- Push each verified feature branch and merge its own PR.
- Verify integration in live main, then delete completed local and remote branches.
- Refresh branch inventory and report every remaining open branch, or None.

Conflict questions name the remaining scope and explain that selecting a resolution
continues its requested publication. A reply still cancels the old mp token; an
explicit resolution-and-continuation answer proceeds through the protected
registered workflow with fresh verification and the same frozen branch scope.
Cancelled tokens are never replayed and new branches never join silently.

The assistant stores successful check commands in a temporary JSON array and passes
its literal path through `--checks-file`. This keeps `$PATH`, quotes and redirections
inside inert evidence rather than shell syntax, preserving the protected executable
allowance. `codex-git probe` tests nested metadata access without publication or
readiness; see [the helper contract](rules/publish-helper.md).

Preparation reuses valid checks and preserves unrelated work. Genuine blockers,
ambiguous scope, unassigned main/detached changes, conflicting remote history, or publication
failures stop with an explanation in the app. The protected publisher retains its
secret scans and exact-commit check. An interrupted preparation request expires
on a later message or after 30 minutes; publication failures require state
inspection, not a blind retry.

Review/trust the handler in Settings > Hooks or `/hooks` if the app requests it;
reload if an existing session retains older hooks. This is one-time setup, not a
per-feature step. Internal --prepare remains available for clean preverified
commits, but the user does not need it. Tests use disposable local repositories;
unit/integration results do not establish live desktop hook activation.
