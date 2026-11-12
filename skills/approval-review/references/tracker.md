# Local approval tracker

## Open and inspect

Run `~/.local/share/codex-publish/codex-approval-tracker serve` when installed. This reviewed isolated executable and its dependencies live outside the writable workspace and have a direct allowance. Otherwise use `python3 ~/.codex/skills/approval-review/scripts/approval_tracker.py serve` under normal permissions, requesting loopback access if blocked. It prints a private tokenized localhost URL on a dynamically allocated port. Open that exact URL and keep its process alive while the dashboard is needed. Use an existing running dashboard rather than spawning duplicates. This is an on-demand local process, not a login service; restart with the same command after it stops. No third-party libraries or paid services are required.

The dashboard refreshes every ten seconds, pausing while details are expanded to preserve reading position; Refresh always reloads. It provides search, project/tool/status/outcome/date filters, sorting, expandable full commands, exact-repeat groups, original-event drilldown, and redacted metadata export. Candidate counts cover the whole group; filters determine which groups appear. Grouping is conservative and never implies an allowance. Missing-command events are not treated as identical commands. Compound commands and quoting remain intact.

`~/.local/share/codex-publish/codex-approval-tracker status` reports counts, last capture, and annotation totals without printing commands. Use the same executable for `label-task`, `annotate`, and `export` in the examples below when installed; source commands remain the prompted fallback. A running dashboard serves the current JSONL and SQLite annotations; the original log remains authoritative. Corrupt logs return an unavailable error rather than silently dropping evidence.

## Enrich and annotate

Task/session IDs come from hook events. Titles are unknown until verified. Use native chat tools for targeted lookups of the sessions being investigated; never scan unrelated history or open transcripts automatically. Save a verified title with:

```text
python3 ~/.codex/skills/approval-review/scripts/approval_tracker.py label-task --session SESSION_ID --title "Verified title" --source "Native chat tool, date or source reference"
```

Project names derive from the recorded working directory and nearest currently existing repository root. The UI exposes that source; directory renames, deleted checkouts, or subdirectory work may limit identification. Legacy events retain missing metadata rather than receiving invented capture-time policy hashes.

Save a complete review annotation with:

```text
python3 ~/.codex/skills/approval-review/scripts/approval_tracker.py annotate --event EVENT_ID --status investigating --notes "Investigate the full compound command"
```

Statuses: `new`, `investigating`, `rule_proposed`, `resolved`, `intentionally_prompted`.
Optional fields: `--outcome`, `--evidence`, `--proposed-rule`, `--verification`.
Outcomes: `unknown`, `human_prompt_confirmed`, `user_approved`, `user_denied`, `automatic_allow`, `automatic_deny`, `execution_confirmed`.

Any confirmed outcome requires a nonempty evidence reference. A later execution result cannot prove user approval. An annotation replaces the current annotation in full; supply every field to retain. Previous versions and title sources remain in SQLite audit history. Annotation status is independent of incremental review checkpoints; neither silently marks the other completed. Proposed-rule text is an investigative note, never installed or executed.

## Exports and privacy

```text
python3 ~/.codex/skills/approval-review/scripts/approval_tracker.py export --output /absolute/new-file.json
```

Exports default to timestamps, event/group IDs, statuses, outcomes, and counts. They omit commands, names, paths, tools, notes, reasons, rules, and other free text rather than guessing which strings contain secrets. Explicit `--include-sensitive` includes full evidence; keep it private. Export files use mode 0600 and refuse overwriting. SQLite lives beside the JSONL under the private data directory, outside Git. The read-only HTTP server binds loopback and requires its random URL token; do not publish that URL or forward its port.

## Capture and coverage

The existing PermissionRequest handler captures supported events without changing decisions. The sound handler remains separate. Shell command, reason, supplied prefix, IDs, working directory, model, and a user-policy fingerprint are recorded when available. Other tools retain metadata, not arbitrary document content. Delivery deduplication requires supplied session/tool IDs plus matching captured input; without reliable IDs, preserve requests separately. Distinct turns or changed input stay distinct.

Check the next naturally occurring request against its recorded session, exact command, and event ID. Synthetic tests establish recorder behavior only. A request observation does not establish a visible human prompt. Some tool paths may omit hooks. Hook trust/activation is managed through Codex Settings > Hooks or `/hooks`; never modify trust hashes or bypass trust review. See [official hook documentation](https://learn.chatgpt.com/docs/hooks).

## Verification

Run `python3 -m unittest discover -s skills/approval-review/scripts -p 'test_approval*.py'` from the customization root. HTTP integration tests require loopback binding. Exercise search, an expanded command, candidate drilldown, and export at the actual printed URL. Keep live capture, backend tests, and browser verification evidence distinct. Ordinary approval requests run capture only; they must not open the dashboard or initiate policy review.
