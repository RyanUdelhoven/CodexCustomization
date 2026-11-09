---
name: feature-branch
description: Create or reuse a relevant feature branch before repository edits, name the originating chat, and track participating chats for post-merge archival. Apply to implementation, fixes, refactors, tests, configuration, and repository documentation edits. Read-only investigation needs no branch.
---

# Work on a feature branch

Before editing repository files, inspect applicable guidance, the current branch, and working-tree state. Never implement changes on `main`, `master`, or the repository's default branch. Read-only investigation may use any branch.

When the user requests code changes, automatically create or switch to the relevant feature branch in the user’s working checkout before editing. Treat the request as authorization to switch branches; do not ask for routine confirmation. Keep that checkout on the task branch while implementing so the user can continually inspect and verify updates. Announce the active branch after verifying it.

Create a feature branch from the task's intended base before edits. For unrelated new work, resolve the repository's primary branch and refresh its remote reference when available; branch from that base, not the currently checked-out feature branch. Use another feature branch as a base only when the task intentionally depends on it. Inspect the commits ahead of the base to catch inherited work before editing. Use `codex/` followed by one to three relevant lowercase, hyphen-separated words, such as `codex/fix-login` or `codex/add-dark-mode`. The namespace does not count toward the three-word limit. Check for collisions; choose another concise relevant name rather than overwriting an existing branch.

Reuse the current feature branch for related follow-up work. Do not rename existing branches solely to satisfy the naming rule. For unrelated work, create a separate feature branch from the appropriate base; use a separate worktree only when needed to preserve concurrent or uncommitted work. If isolation is necessary, identify its path and branch so the user can inspect the actual changes; do not silently leave the user inspecting another checkout. Detached HEAD requires a feature branch before edits.

Preserve existing changes. Do not reset, discard, automatically stash, or carry unrelated edits into the task's commits. If switching safely requires an unresolved choice about existing work, resolve that choice before editing. Verify the active branch after creation or switching.

When creating a feature branch for the current chat's task, rename that chat to the exact branch name with only the leading `codex/` removed. Preserve hyphens: `codex/fix-login` becomes `fix-login`. Keep renamed ChatGPT conversation and Codex chat titles to four words or fewer. If a branch-derived title exceeds this limit, shorten the chat title while preserving its subject; leave the branch name unchanged. Use the available `set_thread_title` tool; omit the thread ID to target the calling chat, or use a verified target and its source when required. Do not rename other chats or rename the chat to the merge target during cleanup. Apply an explicit user title override when provided. If renaming is unavailable or fails, continue the repository task and report the limitation without claiming success.

When creating or managing a branch, follow [chat participation](references/chat-participation.md) to register the current chat before substantive work. Record creation only for a branch actually created in this chat. Reuse the same record across worktrees and register each additional managing chat. Tracking failures do not block authorized implementation, but they disable automatic archival. An existing branch without creation records remains ineligible.

This skill owns branch preparation, the associated chat title, and participation recording, not implementation, verification, publication, merging, or archival. It does not independently authorize commits, pushes, pull requests, or merges. Follow existing authorization and repository gates for those actions. For an authorized merge, use post-merge-cleanup; switching to the merge target for integration and cleanup is allowed, but subsequent implementation requires a feature branch again.

Report the branch used with the task result. Explicit user instructions may override this preference.
