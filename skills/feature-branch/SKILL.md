---
name: feature-branch
description: Create or reuse a relevant feature branch before repository edits, name the originating chat, and record participating chats for branch provenance. Apply to implementation, fixes, refactors, tests, configuration, and repository documentation edits. Read-only investigation needs no branch.
---

# Work on a feature branch

Before editing repository files, inspect applicable guidance, the current branch, and working-tree state. Never implement changes on `main`, `master`, or the repository's default branch. Read-only investigation may use any branch.

When the user requests code changes, automatically create or switch to the relevant feature branch in the user’s working checkout before editing. Treat the request as authorization to switch branches; do not ask for routine confirmation. Keep that checkout on the task branch while implementing so the user can continually inspect and verify updates. Announce the active branch after verifying it.

Always create new feature branches from the repository's primary branch (`main`), including work that depends on another feature branch. Refresh the primary branch's remote reference when available and verify the chosen primary-branch tip before creation. Pass that verified base explicitly to branch or worktree creation; never rely on the current HEAD or use another feature branch as the base. If dependencies remain unmerged, keep the new branch based on the primary branch and resolve the dependency separately. If the repository uses a different primary-branch name, verify and use that branch instead. Immediately after creation, verify that the new branch points to the chosen primary-branch tip and has no inherited feature commits before editing. Use `codex/` followed by one to three relevant lowercase, hyphen-separated words, such as `codex/fix-login` or `codex/add-dark-mode`. The namespace does not count toward the three-word limit. Check for collisions; choose another concise relevant name rather than overwriting an existing branch.

Reuse the current feature branch for related follow-up work. Do not rename existing branches solely to satisfy the naming rule. For unrelated work, create a separate feature branch from the verified primary-branch tip; use a separate worktree only when needed to preserve concurrent or uncommitted work, with the primary-branch base supplied explicitly. If isolation is necessary, identify its path and branch so the user can inspect the actual changes; do not silently leave the user inspecting another checkout. Detached HEAD requires a feature branch from the verified primary-branch tip before edits.

Preserve existing changes. Do not reset, discard, automatically stash, or carry unrelated edits into the task's commits. If switching safely requires an unresolved choice about existing work, resolve that choice before editing. Verify the active branch after creation or switching.

When creating a new task branch, apply [chat naming](references/chat-title.md) once. Reusing that branch for a correction does not repeat renaming, remote-base discovery, creation proof, or participation registration already confirmed for this chat and lifecycle. Check current branch and worktree safety before edits; re-register only for a new chat or lifecycle, or recovery from a failed registration.

When creating or managing a branch, follow [chat participation](references/chat-participation.md) to register the current chat before substantive work unless its registration is already confirmed for this lifecycle. Record creation only for a branch actually created in this chat. Reuse the same record across worktrees and register each additional managing chat. Tracking failures do not block authorized implementation; report gaps without inventing creation history. Records never authorize publication or archival.

Keep feature branches local unless the user requests a remote branch or the authorized task needs one for review, backup, or collaboration. Do not create a remote feature branch merely because a workflow requires publication; follow its authorized destination and lifecycle. Preserve existing remote branches until their authorized cleanup conditions hold.

This skill owns branch preparation, the associated chat title, and participation recording, not implementation, verification, publication, merging, or archival. It does not independently authorize commits, pushes, pull requests, or merges. Follow explicit or standing user authorization and repository gates for those actions. For an authorized merge, use post-merge-cleanup; switching to the merge target for integration and cleanup is allowed, but subsequent implementation requires a feature branch again.

Report the branch used with the task result. Explicit user instructions may override this preference.
