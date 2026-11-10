# Required merge and push execution rules

These instructions complement the executable `.rules` policy. They do not grant
execution permissions. Apply them to authorized merge/push work in registered
repositories; user requests or applicable standing user instructions supply
publication authorization, not this document.

## Remote feature branches

Keep implementation branches local unless the user requests a remote branch or
the authorized task needs one for review, backup, or collaboration. A required
push does not by itself require creating a remote feature branch; follow the
authorized destination and lifecycle. Existing remote branches remain valid.

A request to merge a feature branch also authorizes and requires automatic
removal of that completed feature branch locally and on its source remote, if
present. Do not wait for a separate cleanup request or conversational confirmation.
Perform cleanup after verifying successful integration and target publication;
if publication is not authorized or cannot be verified, retain the branches and
report cleanup as pending. This does not independently authorize a target push.
Confirm the remote feature tip still matches the merged source; use the protected publisher's
exact-tip lease in registered workflows. Preserve primary/default branches,
merge targets, unrelated or unmerged work, changed remote tips, and explicitly
retained branches. Keep raw `git push` commands, including remote deletion,
prompted; do not broadly allow deletion of every non-primary branch.

## Preparation and inspection

- Read documents with separate direct `cat`, `head`, or `tail` calls.
- Use `git rev-parse --abbrev-ref HEAD`, never raw `git branch` for inspection.
- Use the protected reader below for search, numbered ranges, discovery, and time.
- Avoid explicit shell wrappers, assignments, substitutions, redirects, and wildcard expansion.
- Do not combine reads with prompted operations in one shell command.

Use `workdir` for the checkout and `login: false` when calling `exec_command`.
Independent reads may share one orchestration call but remain separate commands.

Protected reader: `/Users/ryanudelhoven/.local/share/codex-publish/codex-read`.
Its supported operations and arguments match [reader documentation](README.md).
Never execute an allowlisted writable source copy instead of the protected install.

## Registered workflow

Use `/Users/ryanudelhoven/.local/share/codex-publish/codex-git` directly:

```text
codex-git inspect REPOSITORY codex/FEATURE VERIFIED_CHAT_UUID
codex-git register REPOSITORY codex/FEATURE VERIFIED_CHAT_UUID
codex-git publish REPOSITORY codex/FEATURE VERIFIED_CHAT_UUID
codex-git finish REPOSITORY codex/FEATURE VERIFIED_CHAT_UUID
```

Replace `codex-git` above with its full protected path. Registry keys, identity
requirements, destination checks, and limitations are in [publish helper](publish-helper.md).
`inspect` returns local scope, worktrees, and participation without refreshing the
remote or changing tracking. It requires a clean checkout and validated config.
`register` records participation without claiming branch creation. Creation records
still follow the feature-branch protocol; failed recording disables automatic archival.

Review the complete scope before publication. Use the inspection's tracking record
instead of direct Python inspection. `publish` registers the integrating chat,
validates the live destination, integrates, verifies publication, and cleans branches.
Use native app tools for history and archival. Run `finish` after that decision.
Do not repeat helper mutations manually. Failures require inspecting current state.

## Verification and approval boundaries

Run required repository checks inside the sandbox, using existing eligible results
when their inputs and scope still match. Never elevate arbitrary project tests,
build scripts, Python, Node, or shells through a blanket allowance. If required
checks need additional access, explain the specific access and request it normally.
The protected publisher never runs repository verification code.

A routine already-verified registered publication should use only allowed direct
operations. Dirty files, divergence, unsafe configuration, stale verification, or
unregistered repositories may stop the workflow. Do not bypass those checks or
disable approvals globally to make the workflow appear successful.

The protected installation and future changes to it require reviewed installation
approval. Restart Codex after policy updates. A CLI rule check predicts policy;
it does not prove the app displayed no approval. Claim that only after observing it.
