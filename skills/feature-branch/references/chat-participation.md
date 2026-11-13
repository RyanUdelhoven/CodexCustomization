# Branch participation records

Use this protocol when creating, reusing, handing off, or integrating a branch. Records preserve provenance; they authorize neither publication nor archival.

Resolve the current chat's exact ID and source from trusted session context or app tools. For Codex, retain a verified host ID when available and use the same identity throughout. Never infer identity from a title. If identity or recording is unavailable, continue authorized work, report the tracking gap.

When installed, run `~/.local/share/codex-publish/codex-branch-chats` directly. Otherwise use `python3 ~/.codex/skills/feature-branch/scripts/branch_chats.py` under normal permissions. Supply `--repo` with the checkout path and `--branch` with the feature branch name. The helper shares records across worktrees through `git rev-parse --git-common-dir`; records stay outside tracked project files. The protected copy uses isolated system Python and fixed, configuration-isolated Git calls. Updating its source requires separately reviewed installation before the installed behavior changes.

Immediately after creating a new branch for this chat, register with:

```sh
~/.local/share/codex-publish/codex-branch-chats register \
  --repo /absolute/repository --branch codex/example \
  --chat-id VERIFIED_CHAT_ID --source codex --created
```

Add `--host-id VERIFIED_HOST_ID` when available for Codex. For the registered local publisher, use `--host-id local` consistently; its integrating identity uses that alias. The updated local tracker normalizes omitted Codex hosts to `local`, including legacy records; this does not equate distinct explicit hosts. Inspection normalizes its returned view without rewriting stored history; registration and closure persist normalization. Until the updated protected tracker is installed, pass `local` explicitly. Use `--source chatgpt` without a host for ChatGPT. Omit `--created` whenever joining or resuming an existing branch, including a separate chat performing only the merge. Registration deduplicates identities and preserves earlier participants. Never claim creation retrospectively to make an existing branch eligible.

Before substantive management in another chat, register that chat too. Management includes implementation, directing branch changes, reviewing changes for integration, and merging/pushing. A passive reference or unrelated read-only lookup does not count. Resuming the same chat does not add another participant. A transferred or forked chat with a different ID does.

For preexisting branches without records, registration marks history incomplete. Preserve that uncertainty. Recreated branch names receive a new lifecycle after the previous one closes; never fabricate creation history or discard earlier participants.

Reuse the protected publisher's preflight and receipt for participation evidence. Do not scan app history for archival eligibility: automatic archival is disabled. Registration confirmed for the same chat and lifecycle need not repeat.

After successful integration, publication, and cleanup, close the branch record once with `close --repo ... --branch ...` or the protected publisher's `finish`. Keep records for provenance. Closure never archives a chat. Report failures; never reopen an old lifecycle merely to satisfy an explicit chat-archival request.

For an authorized merge in a registered local repository, post-merge-cleanup may use the protected publish helper described in [publish helper](../../../rules/publish-helper.md). Its `publish` command registers the integrating chat and returns the participation record; reuse that result. Its `finish` command closes that same lifecycle after successful publication and cleanup. Branch creation still uses the registration protocol above.
