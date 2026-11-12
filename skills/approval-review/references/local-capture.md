# Local capture and review state

The installed `hooks.json` runs `scripts/approval_log.py capture` on PermissionRequest alongside the existing sound. The recorder reads JSON stdin and appends observational JSONL records, with no stdout or approval decision. It stores exact Bash commands, provided reason, prefix, source IDs, working directory, model, and a user-policy fingerprint; other tool arguments are omitted to avoid indiscriminate document capture. Reliable supplied delivery IDs permit duplicate suppression; requests without them remain separate. Transcript paths are pointers only, never opened by the hook. Unknown fields are ignored. Sensitive values embedded in shell commands may remain in this private log; do not publish it. For the searchable dashboard, annotations, and exports, read [the tracker](tracker.md).

Records use private directories (0700), files (0600), locked appends, and no external services. Errors emit a short stderr diagnostic and return success so logging cannot grant or reject a request. Check errors or missing events explicitly; this is an experiment, not a complete audit boundary. PermissionRequest may precede another hook's automatic decision, and some paths may not invoke it. No PostToolUse hook is installed: execution alone cannot establish manual approval.

## Commands

For incremental review commands, when installed, use `~/.local/share/codex-publish/codex-approval-review` directly.
This reviewed recorder copy uses isolated system Python and needs no wrapper;
replacing it requires reviewed installation. Otherwise use
`python3 ~/.codex/skills/approval-review/scripts/approval_log.py` under normal
permissions. Either entry point accepts:

- `status`: show capture count, checkpoint, policy drift, and last report.
- `prepare --limit 50`: persist a review batch and return new events (maximum 200).
- `complete --batch UUID --report /absolute/report.md`: checkpoint a reviewed batch and save its report privately.

For isolated tests only, `--home /tmp/TEST_HOME` precedes the subcommand. It replaces CODEX_HOME for both data and policy fingerprinting. The hook never accepts command arguments from stdin.

Each batch snapshots its predecessor cursor, event range, and policy hash. Completion checks policy and cursor again under the same lock, copies the nonempty report into `reports/BATCH.md`, and atomically advances state. Concurrent capture after preparation stays pending. If another review completed first, or policy changed, prepare a new batch. Missing cursors or malformed logs stop review instead of skipping history. Never edit the cursor to suppress incidents.

The fingerprint covers user-level `.rules` files, `hooks.json`, `config.toml`, and the installed protected reader/publisher when present. It stores hashes, never configuration contents. Project/managed/server policies and app activation are not fully observable: inspect them separately for affected cases. This fingerprint is a review aid, not proof of loaded policy or authorization.

## Trial operation

Review and trust the new hook through Codex's Review hooks or Settings > Hooks (CLI: `/hooks`). Reload/restart if the running session retains old hooks. Do not edit trust hashes programmatically. Confirm the next naturally occurring permission request appears in `status`; synthetic tests establish recorder behavior only. Then say “review approval friction” to review new incidents. Ordinary tasks only capture requests, without running the skill.

To pause capture, remove only the `approval_log.py capture` handler from `hooks.json`, preserving the sound and other hooks, then reload. Data stays local for inspection. No automation, collector, subscription, or new library is needed.

Sources checked during implementation:

- [Codex hooks](https://learn.chatgpt.com/docs/hooks): stdin format, PermissionRequest behavior, hook trust, and coverage limits.
- [Developer commands](https://learn.chatgpt.com/docs/developer-commands): execpolicy checks.
