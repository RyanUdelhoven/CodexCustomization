---
name: feature-branch
description: Create or reuse a relevant feature branch before changing files in a Git code repository. Apply to implementation, fixes, refactors, tests, configuration, and repository documentation edits; read-only investigation needs no branch.
---

# Work on a feature branch

Before editing repository files, inspect applicable guidance, the current branch, and working-tree state. Never implement changes on `main`, `master`, or the repository's default branch. Read-only investigation may use any branch.

Create a feature branch from the task's intended base before edits. Use `codex/` followed by one to three relevant lowercase, hyphen-separated words, such as `codex/fix-login` or `codex/add-dark-mode`. The namespace does not count toward the three-word limit. Check for collisions; choose another concise relevant name rather than overwriting an existing branch.

Reuse the current feature branch for related follow-up work. Do not rename existing branches solely to satisfy the naming rule. For unrelated work, create a separate feature branch from the appropriate base; use a separate worktree when needed to preserve concurrent or uncommitted work. Detached HEAD requires a feature branch before edits.

Preserve existing changes. Do not reset, discard, automatically stash, or carry unrelated edits into the task's commits. If switching safely requires an unresolved choice about existing work, resolve that choice before editing. Verify the active branch after creation or switching.

This skill owns branch preparation, not implementation, verification, publication, or merging. It does not independently authorize commits, pushes, pull requests, or merges. Follow existing authorization and repository gates for those actions. For an authorized merge, use post-merge-cleanup; switching to the merge target for integration and cleanup is allowed, but subsequent implementation requires a feature branch again.

Report the branch used with the task result. Explicit user instructions may override this preference.
