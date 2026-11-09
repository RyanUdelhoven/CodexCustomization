---
name: post-merge-cleanup
description: Finish an authorized Git branch merge by deleting the merged feature branch locally and remotely when applicable. Use during merge requests and post-merge cleanup; preserve branches when explicitly requested.
---

# Post-merge cleanup

The user prefers deleting completed feature branches after successful merging and pushing. Treat cleanup as part of an authorized merge workflow; do not ask again solely to delete the merged branch. Follow execution permission requirements and explicit requests to retain a branch.

Feature-branch owns branch preparation before repository edits. Switching to the merge target for authorized integration and cleanup is allowed; create or reuse a feature branch before further implementation.

- Record the feature branch, target branch, source remote, and source tip before merging.
- Let repository guidance and code-change-verification own checks; reuse valid verification results.
- Complete the requested merge and push before cleanup. If pushing was not requested or otherwise authorized, do not infer authorization from this skill; retain the branch until publication is confirmed.
- Verify the target includes the feature work and the push succeeded. For squash or rebase merges, use confirmed merge evidence rather than ancestry alone.
- Switch to the target and delete the completed local feature branch. Prefer `git branch -d`; do not force deletion merely because it reports unmerged work. Only use `-D` when squash/rebase merge evidence proves the branch contains no additional work.
- Delete the corresponding remote feature branch if it exists and belongs to the authorized workflow. Confirm its tip still matches the merged source before deletion; retain it if someone added commits.
- Preserve the default branch, merge target, unrelated branches, unmerged work, and branches checked out in other worktrees. Report a cleanup blocker without disturbing those worktrees.

Report the merge/push outcome and local/remote branch cleanup. This skill does not authorize bulk stale-branch deletion or unrelated repository changes.
