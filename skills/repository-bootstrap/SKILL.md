---
name: repository-bootstrap
description: Initialize a new local Git repository with an initial commit, then offer GitHub repository creation and verify the first push and connections for future merge/push cycles. Use when asked to create a Git repository for a new project or finish its explicitly requested GitHub setup.
---

# Bootstrap a project repository

Own new-repository initialization and its first GitHub connection. Do not initialize Git merely because an app is being built. Respect explicit local-only requests, existing repositories, and user-selected hosting, account, visibility, or branch names.

## Local repository and initial commit

When asked to make a new Git repository, inspect the intended project root and applicable guidance. Check whether it is already inside a repository or worktree before running initialization; do not accidentally nest repositories or replace existing history, remotes, or configuration. For an existing repository, inspect its state and complete only requested missing setup; do not create another initial commit.

Initialize a genuinely new repository with `main` as its primary branch unless explicitly directed otherwise. This request authorizes one meaningful initial commit on the primary branch: the narrow bootstrap exception to feature-branch's implementation rule. Review project files, ignore generated/runtime/private files, stage only intended files, and run applicable checks and the staged secret gate before committing. If the project is empty, create a useful minimal README for the initial commit rather than an empty commit. Verify author identity; never invent attribution or alter global Git identity. Prepare this minimal baseline before subsequent implementation, which belongs on a feature branch.

Use the installed secret gate and hooks described in [secret prevention](../../rules/secret-prevention.md). Inspect existing hooks and effective configuration first. For a new checkout with no conflicting hooks, set its local `core.hooksPath` to the verified installed protected `git-hooks` directory; do not run the legacy installer that targets three other repositories. Preserve and integrate existing hooks through review. Missing gate tooling or conflicts block the commit/push until resolved; never bypass scanning.

After verifying the initial commit, ask: “Would you like me to create a GitHub repository, connect it, and push this initial commit?” Wait for an affirmative answer before external creation or upload. Respect an earlier explicit GitHub creation request as authorization without asking again. If declined, report local setup and stop external work. Silence is not consent.

## GitHub connection after yes

The affirmative answer authorizes creating the agreed repository, connecting it, and pushing the reviewed initial commit to establish the remote primary branch. It does not authorize publishing later feature work, merging, changing profile settings, or archiving chats. Clarify unresolved repository owner/name and visibility before creation; offer private as the default rather than assume public disclosure. Reuse explicit choices already provided.

Before remote mutation, read [merge/push execution](../../rules/merge-push.md) and [publish helper](../../rules/publish-helper.md). Verify GitHub authentication, intended account, repository permissions, Git transport credentials, and the initial commit author's email attribution. Resolve authentication interactively without printing secrets or adding credentials to remote URLs. Preserve global configuration and avoid broad permission changes.

For Ryan's normal protected workflow, use a literal single origin URL `https://github.com/RyanUdelhoven/NAME.git`, matching fetch and push destinations, and primary/default branch `main`. An explicitly different account, transport, or branch must be respected and its protected-publisher incompatibility reported; do not silently rewrite it or claim `mp` readiness.

Create an empty GitHub repository without generated README, license, or gitignore commits. Inspect a name collision or partially completed setup before retrying; never overwrite, force-push, delete, or silently adopt an existing repository. Add origin only if absent; verify any existing destination before reusing it. Scan all reachable outgoing history with the protected filename and content gate before uploading. A new remote ref requires the full history scan, not just a working-tree scan.

The protected PR publisher needs an existing remote main, so it cannot bootstrap an empty remote. Use an explicitly authorized ordinary first push of the reviewed initial main commit, with upstream tracking and normal execution review; pin the push to the recorded initial commit and do not include feature commits created while awaiting consent; do not use `mp`, fake a feature merge, weaken policy, or install a new protected helper to bypass this prerequisite. Stop if the remote gains unexpected history.

## Verify readiness and hand off

Fetch and verify that local main, origin/main, and GitHub's main ref equal the reviewed initial commit. Verify main tracks origin/main, GitHub's default branch is main, origin/HEAD resolves correctly, and origin has no alternate push destination or URL rewrite. Confirm repository access and that merge commits are enabled for later PR publication. For a newly created repository, enable merge commits if necessary within this requested setup; preserve existing protections and organization policies. Report blocked settings without bypassing reviews or checks.

Confirm the installed publisher advertises the documented PR workflow and can accept this repository's path/account/configuration. Future matching projects need no hardcoded registration or helper source edit. Do not call publication or manufacture a test PR/merge merely to test readiness. Report configuration readiness separately from a future merge cycle that has not run.

If implementation continues, apply [feature-branch](../feature-branch/SKILL.md) from the verified primary tip, including participation and chat naming. Later explicitly requested publication belongs to [post-merge-cleanup](../post-merge-cleanup/SKILL.md) and the `mp` hook. If GitHub setup remains pending, feature work may continue locally; its later commits require their own publication authorization.

Report the local path, initial commit, GitHub URL when created, verified push/tracking/default branch, and any concrete readiness blocker. On failure, inspect actual local and remote state and resume only missing authorized steps. Never claim setup succeeded from a command exit code alone.
