# Branch participation records

Use this protocol when creating, reusing, handing off, or integrating a branch. Records support an archive decision; they do not prove that unrecorded work never happened.

Resolve the current chat's exact ID and source from trusted session context or app tools. For Codex, retain a verified host ID when available and use the same identity throughout. Never infer identity from a title. If identity or recording is unavailable, continue authorized work, report the tracking gap, and skip automatic archival.

When installed, run `~/.local/share/codex-publish/codex-branch-chats` directly. Otherwise use `python3 ~/.codex/skills/feature-branch/scripts/branch_chats.py` under normal permissions. Supply `--repo` with the checkout path and `--branch` with the feature branch name. The helper shares records across worktrees through `git rev-parse --git-common-dir`; records stay outside tracked project files. The protected copy uses isolated system Python and fixed, configuration-isolated Git calls. Updating its source requires separately reviewed installation before the installed behavior changes.

Immediately after creating a new branch for this chat, register with:

```sh
~/.local/share/codex-publish/codex-branch-chats register \
  --repo /absolute/repository --branch codex/example \
  --chat-id VERIFIED_CHAT_ID --source codex --created
```

Add `--host-id VERIFIED_HOST_ID` when available for Codex. For the registered local publisher, use `--host-id local` consistently; its integrating identity uses that alias. The updated local tracker normalizes omitted Codex hosts to `local`, including legacy records; this does not equate distinct explicit hosts. Inspection normalizes its returned view without rewriting stored history; registration and closure persist normalization. Until the updated protected tracker is installed, pass `local` explicitly. Use `--source chatgpt` without a host for ChatGPT. Omit `--created` whenever joining or resuming an existing branch, including a separate chat performing only the merge. Registration deduplicates identities and preserves earlier participants. Never claim creation retrospectively to make an existing branch eligible.

Before substantive management in another chat, register that chat too. Management includes implementation, directing branch changes, reviewing changes for integration, and merging/pushing. A passive reference or unrelated read-only lookup does not count. Resuming the same chat does not add another participant. A transferred or forked chat with a different ID does.

For preexisting branches without records, registration marks history incomplete. Recreated branch names receive a new lifecycle only after the previous lifecycle is closed; unresolved open records remain a tracking blocker. Distinct clones or hosts do not automatically share records: reconcile participation and history before conditional automatic archival, or skip it. Missing, malformed, inconsistent, or lost records never establish exclusive ownership and do not block explicitly authorized current-chat archival.

Reuse the protected publisher's preflight/receipt for participation evidence. For conditional automatic archival only, `single_chat_candidate` means the record contains one chat and tracked creation; also inspect available app history for credible branch-related chats, using `read_thread` for candidates. Titles alone cannot establish exclusivity. Contradictory or incomplete ownership evidence blocks automatic archival. Explicit `mpa` instead authorizes the verified current chat's archival after successful publication, cleanup, and task completion; it needs no ownership/history investigation. Retain participation records without repeating confirmed registration.

After successful integration and push, record `close --repo ... --branch ...` once the archive decision and any attempted archival have finished. Keep records for audit; do not delete them with the feature branch. If closure fails, report it and keep archival disabled for any later ambiguous reuse. The helper never merges, pushes, deletes branches, or archives chats.

These ownership requirements govern conditional automatic archival, not explicit `mpa` or direct specific-chat requests. Follow post-merge-cleanup's explicit archival guidance for those requests; never reopen a lifecycle, recreate a branch, or fabricate participation to satisfy archival.

For an authorized merge in a registered local repository, post-merge-cleanup may use the protected publish helper described in [publish helper](../../../rules/publish-helper.md). Its `publish` command registers the integrating chat and returns the participation record; reuse that result. Its `finish` command closes that same lifecycle after the archive decision. Branch creation still uses the registration protocol above.
