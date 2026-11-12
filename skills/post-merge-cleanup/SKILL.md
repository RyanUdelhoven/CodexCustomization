---
name: post-merge-cleanup
description: Finish an authorized merge with branch cleanup and eligible chat archival. Use during merge requests, contextual mp or mpa workflow commands, and post-merge cleanup; preserve branches or chats when explicitly requested. Acronym mentions alone do not trigger execution.
---

# Post-merge cleanup

Recognize `mp` (“merge push”) and `mpa` (“merge push archive”) only as direct workflow instructions in clear repository/branch context. Follow [contextual shortcuts](../../rules/merge-push.md#contextual-shortcuts) for interpretation; quotations, examples, definitions, and unrelated acronym mentions do not authorize execution. Both aliases retain this skill's existing safeguards, including conditional archival eligibility; `mpa` makes the archival request explicit without bypassing those checks.

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

The receipt preserves participation evidence. This skill still owns app-history checks, the archive decision, and the app archival call. A retained remote branch or any incomplete cleanup keeps the chat open. After the decision and any archive attempt, run `finish REPOSITORY codex/FEATURE VERIFIED_CHAT_UUID` to close the recorded lifecycle. Never close it before the archive decision. The helper does not archive chats or authorize publication. For unregistered repositories or incompatible workflows, follow the ordinary steps above and normal execution approvals.

## Archive the completed chat

The ownership and open-lifecycle checks below govern automatic archival and archival requested through `mpa`. A direct request to archive a specific chat (including the current chat) independently authorizes that chat operation, even after a lifecycle has closed. Verify the target, finish any explicitly required prerequisite work, and use the app archival tool; do not require branch tracking repairs or another confirmation. This direct request does not authorize archiving other participants' chats. Do not reinterpret `mpa` alone as an override of its safeguards.

Inspect and retain the participation record before deleting branches.

After a verified merge into the repository's primary/default branch and a successful push of that target to `origin`, archive the originating chat only if one verified chat managed the branch from creation through integration. Determine the primary branch from repository guidance or verified remote metadata; do not assume `main`. Merging into another target or pushing only another remote does not trigger archival. A failed push never triggers archival. Explicit instructions to retain the chat override this preference.

Use the participation protocol above. Require a complete, open lifecycle, one distinct participant matching the recorded origin, and no evidence of other managing chats or missing history. The current integrating chat must match that origin. Verify that the chat's task is complete and no other active branch, unfinished work, or pending request in that chat would be hidden by archival. When merging multiple branches, assess all of them before any archival; if any participating branch has multiple managing chats, archive nothing for that merge workflow.

Use the local tracker's normalized identities: an omitted Codex host and `local` represent the same local host for the same chat ID. Distinct explicit hosts remain distinct. Duplicate alias records alone do not prove multiple managing chats. A previously closed lifecycle remains ineligible for automatic archival; explain that a direct request to archive this chat can proceed independently, rather than implying Git work remains.

When multiple chats managed a branch, archive none of those chats. After the successful push, report: “Multiple chats managed this branch; no chats were archived.” Name or link verified participants when useful. If evidence is incomplete instead, report that ownership could not be verified and no chats were archived; do not claim multiple chats without evidence. Missing tools or tracking never block authorized merge/push or branch cleanup.

Complete branch cleanup and report the merge, push, cleanup outcome, and archive decision before archiving. A material cleanup blocker or unfinished follow-up keeps the chat open. Use the available `set_thread_archived` tool with `archived: true` and the verified originating chat identity; omit the thread ID only when targeting the verified current chat. Preserve its source and any verified Codex host. Inspect the tool result and report archival success only when confirmed. If it fails or is unavailable, keep the chat open and report the limitation. Do not substitute permanent deletion, worktree archival, bulk archival, or a scheduled automation.

Close the participation lifecycle after the decision and any archive attempt, following the protocol. Report the confirmed outcome in the final response. This skill does not authorize bulk stale-branch deletion, unrelated chat archival, or unrelated repository changes.
