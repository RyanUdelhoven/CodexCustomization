---
name: post-merge-cleanup
description: Finish explicitly requested merge/push work with branch cleanup. Keep chats open; archive only on a separate explicit chat request. The exact mp command authorizes preparation and hook publication; mpa is retired.
---

# Post-merge cleanup

For a direct request to archive a specific chat, use [archival guidance](references/archival.md) directly; no merge, push, or branch-tracking repair is required.

Merge and push only on a separate explicit user request; completing an implementation or skill change does not authorize publication. Standalone `mp` uses the hook: ready work publishes directly; a scoped preparation request reaches the assistant in the same turn. `mpa` is retired. Follow [shortcut interpretation](../../rules/merge-push.md#contextual-shortcuts).

## Routine completion

For a scoped mp preparation request, review task changes, reuse valid checks, run outstanding gates, and commit only reviewed task files. Register missing participation normally. Then invoke `mp-command-hook.py --complete` with the repository, session, request ID, and real successful checks supplied by the hook protocol in [merge/push execution](../../rules/merge-push.md#preparation-within-mp). The handoff prepares and publishes; do not ask the user for another command or independently publish a second time. Stop for real blockers or ambiguous scope, preserve unrelated work, and leave the chat open.

Already-ready mp requests publish directly through the hook. For other explicitly requested publication, reuse one protected inspection/receipt and run only outstanding required gates. Never skip secret scanning or publication checks. Failed publication needs state inspection before recovery.

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

For Ryan's registered `customization`, `mynormal`, and `marketnuance` repositories, prefer the protected executable `/Users/ryanudelhoven/.local/share/codex-publish/codex-git` after explicit merge/push authorization and completed verification. See [publish helper](../../rules/publish-helper.md) for exact arguments and limits. Do not execute the writable source copy as an approved shortcut.

Run `publish REPOSITORY codex/FEATURE VERIFIED_CHAT_UUID` as one direct command. It registers the integrating chat, checks the checkout and destination, fast-forwards main, publishes, verifies the remote commit, and removes only the completed feature branches. Reuse its receipt instead of repeating these mutations or Python tracking calls. It refuses divergence; integrate remote changes on the feature branch and repeat required verification before retrying. Other failures require inspecting the reported current state; never force-push or bypass its checks.

The receipt preserves participation evidence. After successful publication and cleanup, run `finish REPOSITORY codex/FEATURE VERIFIED_CHAT_UUID` once to close that branch lifecycle. This does not archive the chat. Report publication and cleanup once; preserve the branch on incomplete publication or cleanup.

## Chat archival

Never archive automatically after publication, cleanup, or task completion. Use [explicit archival guidance](references/archival.md) only when the user separately asks to archive a specific chat. Do not investigate cross-chat ownership merely to finish Git work.
