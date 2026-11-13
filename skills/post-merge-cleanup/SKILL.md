---
name: post-merge-cleanup
description: Finish an authorized merge with branch cleanup and eligible chat archival. Use during merge requests, contextual mp or mpa workflow commands, and post-merge cleanup; preserve branches or chats when explicitly requested. Acronym mentions alone do not trigger execution.
---

# Post-merge cleanup

For a direct request to archive a specific chat, use [archival guidance](references/archival.md) directly; no merge, push, or branch-tracking repair is required.

Recognize `mp` (“merge push”) and `mpa` (“merge push archive”) only as direct workflow instructions in clear repository/branch context. Follow [contextual shortcuts](../../rules/merge-push.md#contextual-shortcuts); mentions and configuration discussions do not execute them. `mpa` directly requests archiving the current chat after successful publication, cleanup, and task completion. It requires no exclusive ownership or cross-chat history investigation. `mp` retains conditional automatic archival. Explicit keep-open instructions take precedence.

## Routine completion

Reuse the known task scope and qualifying verification results. Review only remaining changes and run outstanding required gates. Use one protected preflight inspection and one publication; reuse the receipt for registration, remote verification, and cleanup. For `mpa`, verify the current chat and completion, archive only that chat, then finish the lifecycle. For automatic archival, read the ownership checks in [archival guidance](references/archival.md). Investigate exceptions only when the normal path reports one. Never skip required secret scanning or publication checks.

A merge request automatically authorizes and requires deleting the completed feature branch both locally and on its source remote, if present. Complete cleanup within the merge workflow after verifying successful integration and target publication; do not wait for a separate cleanup request or conversational confirmation. Keep execution permission requirements and explicit requests to retain a branch. If cleanup cannot safely complete, report the retained branch and concrete blocker rather than treating the merge workflow as fully complete.

Feature-branch owns branch preparation before repository edits. Switching to the merge target for authorized integration and cleanup is allowed; create or reuse a feature branch before further implementation.

- Record the feature branch, target branch, source remote, and source tip before merging.
- Register the integrating chat through feature-branch's [participation protocol](../feature-branch/references/chat-participation.md), including merge-only work.
- Let repository guidance and code-change-verification own checks; reuse valid verification results.
- Complete the requested merge and push before cleanup. If pushing was not requested or otherwise authorized, do not infer authorization from this skill; retain the branch until publication is confirmed.
- Verify the target includes the feature work and the push succeeded. For squash or rebase merges, use confirmed merge evidence rather than ancestry alone.
- Switch to the target and delete the completed local feature branch. Prefer `git branch -d`; do not force deletion merely because it reports unmerged work. Only use `-D` when squash/rebase merge evidence proves the branch contains no additional work.
- Delete the corresponding remote feature branch if it exists and belongs to the authorized workflow. Confirm its tip still matches the merged source before deletion; retain it if someone added commits.
- Preserve the default branch, merge target, unrelated branches, unmerged work, and branches checked out in other worktrees. Report a cleanup blocker without disturbing those worktrees.

Before integration, inspect all commits and uncommitted changes in the requested scope. A request to merge a branch covers its unmerged commits unless the user narrows it. Do not silently substitute selected cherry-picks for a branch merge. If inherited work materially expands the understood task, explain the difference and resolve scope before integration. Commit reviewed local edits when the user includes them; preserve anything excluded.

## Registered local publish helper

For Ryan's registered `customization`, `mynormal`, and `marketnuance` repositories, prefer the protected executable `/Users/ryanudelhoven/.local/share/codex-publish/codex-git` after explicit or applicable standing merge/push authorization and completed verification. See [publish helper](../../rules/publish-helper.md) for exact arguments and limits. Do not execute the writable source copy as an approved shortcut.

Run `publish REPOSITORY codex/FEATURE VERIFIED_CHAT_UUID` as one direct command. It registers the integrating chat, checks the checkout and destination, fast-forwards main, publishes, verifies the remote commit, and removes only the completed feature branches. Reuse its receipt instead of repeating these mutations or Python tracking calls. It refuses divergence; integrate remote changes on the feature branch and repeat required verification before retrying. Other failures require inspecting the reported current state; never force-push or bypass its checks.

The receipt preserves participation evidence. This skill owns the archive decision and app archival call; app-history ownership checks apply only to conditional automatic archival. A retained remote branch or incomplete cleanup keeps the chat open. After the decision and any archive attempt, run `finish REPOSITORY codex/FEATURE VERIFIED_CHAT_UUID` once to close the lifecycle. The helper does not archive chats or authorize publication. For unsupported workflows, follow ordinary execution approvals.

## Archive decision and completion

After publication and cleanup, explicit `mpa` follows the current-chat route above; missing or multi-chat participation records do not block that explicit archival. Keep the chat open if its target cannot be verified, work remains, or publication/cleanup failed. Use [archival guidance](references/archival.md) for direct standalone archive requests or conditional automatic archival. Keep-open instructions skip archival investigation. Report merge, publication, cleanup, and the confirmed archive outcome once.
