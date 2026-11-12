# Approval record commands

Use `~/.local/share/codex-publish/codex-approval-tracker` directly when installed. Otherwise use `python3 ~/.codex/skills/approval-review/scripts/approval_tracker.py` under normal permissions. There is no dashboard or server.

## Read and review

`status` prints compact counts, last capture, review statuses and token-accounting metadata. It omits full commands and request samples. Use `codex-approval-review prepare --limit 50` for incremental approval investigation; status and exports do not consume a review batch.

`export --output /absolute/new-file.json` writes redacted metadata. Add `--include-sensitive` to inspect full evidence privately when the user's question calls for it. Filter the exported records to answer the user's prompt, retaining event IDs and exact commands. Exports contain exact-repeat groups, task labels, review annotations, skill runs and token samples. Missing commands are not grouped as identical requests. Never execute captured commands to discover effects or infer safety from frequency.

The authoritative JSONL, SQLite annotations and skill-run journals remain under `$CODEX_HOME/.local/approval-review`, defaulting to `~/.codex/.local/approval-review`. Do not commit them. Corrupt logs stop inspection rather than silently dropping evidence. Exports use mode 0600, refuse overwriting, and omit free text unless explicitly requested through --include-sensitive.

## Update review metadata

`label-task --session SESSION_ID --title "Verified title" --source "Evidence reference"` saves a verified task label. Use native chat tools for targeted identity lookup; never scan unrelated history or transcripts automatically. Missing metadata stays unknown. Project labels derive from recorded working directories and currently existing repository roots; exports expose the source and its limitations.

`annotate --event EVENT_ID --status investigating --notes "Investigate the full command"` replaces the complete current annotation and preserves previous versions in audit history. Include every field to retain. Optional fields: `--outcome`, `--evidence`, `--proposed-rule`, `--verification`.

Statuses: new, investigating, rule_proposed, resolved, intentionally_prompted.
Outcomes: unknown, human_prompt_confirmed, user_approved, user_denied, automatic_allow, automatic_deny, execution_confirmed. Confirmed outcomes require an evidence reference. Later execution does not prove human approval. Annotation status and incremental review checkpoints are independent. Displaying, exporting, or annotating records does not itself authorize rule changes. A requested approval review implements suitable allowances by default under SKILL.md; an explicitly review-only request leaves proposals as notes. Rule updates require combined-policy checks and workflow verification.

## Capture and verification

PermissionRequest records supported request metadata without changing decisions. Keep the sound handler separate. Preserve shell commands, provided reasons/prefixes, IDs, working directories, model and user-policy fingerprints. Omit arbitrary non-shell tool arguments. Deduplicate only reliable matching supplied delivery IDs. Transcript paths remain pointers. Legacy missing fields remain unknown.

Run `python3 -m unittest discover -s skills/approval-review/scripts -p 'test_*.py'`. Verify capture, exports, annotations, token intervals and rejection of the removed serve command. Natural request observations verify live capture separately from tests; they do not prove a human saw a prompt. Hook trust belongs to Codex Settings > Hooks or /hooks; never edit trust hashes. See https://learn.chatgpt.com/docs/hooks.
