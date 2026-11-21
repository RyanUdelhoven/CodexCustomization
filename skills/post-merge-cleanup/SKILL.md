---
name: post-merge-cleanup
description: Publish explicitly requested work through GitHub pull requests, preserve commits, and clean completed branches. Keep chats open; archive only on a separate explicit chat request. The exact mp command authorizes preparation and hook publication; mpa is retired.
---

# Post-merge cleanup

For a direct request to archive a specific chat, use [archival guidance](references/archival.md) directly; no merge, push, or branch-tracking repair is required.

Merge and push only on a separate explicit user request; completing an implementation or skill change does not authorize publication. Standalone `mp` uses the hook: ready work publishes directly; a scoped preparation request reaches the assistant in the same turn. `mpa` is retired. Follow [shortcut interpretation](../../rules/merge-push.md#contextual-shortcuts).

## Routine completion

For a scoped mp preparation request, review task changes, reuse valid checks, run outstanding gates, and commit only reviewed task files. Register missing participation normally. Then invoke the protected `codex-git complete` executable directly with the repository, branch, chat, request ID, and real successful checks supplied by the hook protocol in [merge/push execution](../../rules/merge-push.md#preparation-within-mp). Workspace Python or shell wrappers would prevent its own executable rule from applying to Git metadata writes. The handoff prepares and publishes; do not ask the user for another command or independently publish a second time. Stop for real blockers or ambiguous scope, preserve unrelated work, and leave the chat open.

Already-ready mp requests publish directly through the hook. For other explicitly requested publication, reuse one protected inspection/receipt and run only outstanding required gates. Never skip secret scanning or publication checks. Failed publication needs state inspection before recovery.

For GitHub/network failures, use [shared access recovery](../../rules/merge-push.md#github-access-recovery-all-git-actions). Diagnose policy versus authentication, permissions, and missing refs; prefer protected live reads for inspection. A failed push/merge may already have changed GitHub: inspect live heads and matching PR state before deliberate recovery. Never blindly retry publication, duplicate a PR, or use a read request as mutation authorization. Leases, readiness, and secret gates still apply.

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

For Ryan's verified GitHub HTTPS repositories (absolute paths, including future projects; legacy aliases remain supported), prefer the protected executable `/Users/ryanudelhoven/.local/share/codex-publish/codex-git` after explicit merge/push authorization and completed verification. See [publish helper](../../rules/publish-helper.md) for exact arguments and limits. Do not execute the writable source copy as an approved shortcut.

Run `publish REPOSITORY codex/FEATURE VERIFIED_CHAT_UUID` as one direct command after verifying that the installed publisher supports the PR workflow in [publish helper](../../rules/publish-helper.md). It registers participation, validates the destination and account, scans outgoing history, pushes the exact verified feature tip, opens or reuses a same-repository PR, and merges through GitHub using a merge commit. It verifies feature ancestry in published main, synchronizes local main, and deletes only completed branches. Reuse its receipt; never substitute the legacy direct-main push or repeat successful mutations. An older installed helper requires reviewed installation before use.

Keep the feature branch local until explicit publication authorization. `mp` authorizes pushing it, creating the PR under Ryan's GitHub account, merging, and verified cleanup. Respect explicit narrower destinations and branch-retention requests. Use descriptive commit messages; the helper derives new PR titles and bodies from commit history. If repository templates or custom validation details require a richer description, prepare the matching PR first using an authorized API operation or GitHub CLI with `--body-file`; the publisher reuses it. Preserve meaningful individual commits and accurate attribution; avoid squash merges by default. Confirm Ryan's author email maps to his GitHub account; preserve collaborators' authorship. Never manufacture contributions, rewrite dates, or change account visibility without a separate request. Private contribution counts may require the user to enable their profile setting.

Wait for required checks and approvals. Never self-approve, use admin bypass, disable protection, silently squash, or directly push main when the PR workflow is blocked. Pending checks or missing approvals leave the PR and branches intact. Report the PR URL and blocker; inspect live source, checks, and merge state before deliberate recovery. Reuse an existing matching PR rather than creating duplicates. Repository policies requiring a different merge method need an explicit user decision; preserve branches meanwhile.

The default preserves commits so eligible work reaches the default branch. Deleting merged branch references does not remove those commits or their contribution eligibility. GitHub still determines credit; do not promise counts or immediate graph updates. See [GitHub contribution criteria](https://docs.github.com/en/account-and-profile/reference/profile-contributions-reference).

The receipt preserves participation evidence. After successful publication and cleanup, run `finish REPOSITORY codex/FEATURE VERIFIED_CHAT_UUID` once to close that branch lifecycle. This does not archive the chat. Report publication and cleanup once; preserve the branch on incomplete publication or cleanup.

## Chat archival

Never archive automatically after publication, cleanup, or task completion. Use [explicit archival guidance](references/archival.md) only when the user separately asks to archive a specific chat. Do not investigate cross-chat ownership merely to finish Git work.
