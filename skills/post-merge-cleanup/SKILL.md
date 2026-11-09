---
name: post-merge-cleanup
description: Finish an authorized merge with local and remote branch cleanup, then archive the originating chat after a verified single-chat lifecycle merges into the primary branch and pushes to origin. Use during merge requests and post-merge cleanup; preserve branches or chats when explicitly requested.
---

# Post-merge cleanup

The user prefers deleting completed feature branches after successful merging and pushing. Treat cleanup as part of an authorized merge workflow; do not ask again solely to delete the merged branch. Follow execution permission requirements and explicit requests to retain a branch.

Feature-branch owns branch preparation before repository edits. Switching to the merge target for authorized integration and cleanup is allowed; create or reuse a feature branch before further implementation.

- Record the feature branch, target branch, source remote, and source tip before merging.
- Register the integrating chat through feature-branch's [participation protocol](../feature-branch/references/chat-participation.md), including merge-only work.
- Let repository guidance and code-change-verification own checks; reuse valid verification results.
- Complete the requested merge and push before cleanup. If pushing was not requested or otherwise authorized, do not infer authorization from this skill; retain the branch until publication is confirmed.
- Verify the target includes the feature work and the push succeeded. For squash or rebase merges, use confirmed merge evidence rather than ancestry alone.
- Switch to the target and delete the completed local feature branch. Prefer `git branch -d`; do not force deletion merely because it reports unmerged work. Only use `-D` when squash/rebase merge evidence proves the branch contains no additional work.
- Delete the corresponding remote feature branch if it exists and belongs to the authorized workflow. Confirm its tip still matches the merged source before deletion; retain it if someone added commits.
- Preserve the default branch, merge target, unrelated branches, unmerged work, and branches checked out in other worktrees. Report a cleanup blocker without disturbing those worktrees.

## Archive the completed chat

Inspect and retain the participation record before deleting branches.

After a verified merge into the repository's primary/default branch and a successful push of that target to `origin`, archive the originating chat only if one verified chat managed the branch from creation through integration. Determine the primary branch from repository guidance or verified remote metadata; do not assume `main`. Merging into another target or pushing only another remote does not trigger archival. A failed push never triggers archival. Explicit instructions to retain the chat override this preference.

Use the participation protocol above. Require a complete, open lifecycle, one distinct participant matching the recorded origin, and no evidence of other managing chats or missing history. The current integrating chat must match that origin. Verify that the chat's task is complete and no other active branch, unfinished work, or pending request in that chat would be hidden by archival. When merging multiple branches, assess all of them before any archival; if any participating branch has multiple managing chats, archive nothing for that merge workflow.

When multiple chats managed a branch, archive none of those chats. After the successful push, report: “Multiple chats managed this branch; no chats were archived.” Name or link verified participants when useful. If evidence is incomplete instead, report that ownership could not be verified and no chats were archived; do not claim multiple chats without evidence. Missing tools or tracking never block authorized merge/push or branch cleanup.

Complete branch cleanup and report the merge, push, cleanup outcome, and archive decision before archiving. A material cleanup blocker or unfinished follow-up keeps the chat open. Use the available `set_thread_archived` tool with `archived: true` and the verified originating chat identity; omit the thread ID only when targeting the verified current chat. Preserve its source and any verified Codex host. Inspect the tool result and report archival success only when confirmed. If it fails or is unavailable, keep the chat open and report the limitation. Do not substitute permanent deletion, worktree archival, bulk archival, or a scheduled automation.

Close the participation lifecycle after the decision and any archive attempt, following the protocol. Report the confirmed outcome in the final response. This skill does not authorize bulk stale-branch deletion, unrelated chat archival, or unrelated repository changes.
