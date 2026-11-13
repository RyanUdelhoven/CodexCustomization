# Required merge and push execution rules

These instructions complement the executable `.rules` policy. They do not grant
execution permissions. Apply them to authorized merge/push work in registered
repositories; user requests or applicable standing user instructions supply
publication authorization, not this document.

## Contextual shortcuts

Treat `mp` as “merge push” and `mpa` as “merge push archive” when used
as a direct user instruction about the repository work under discussion.
Match whole tokens, case-insensitively; allow ordinary punctuation and phrasing
such as “please mp”. A standalone shortcut after implementation or verification
is sufficient when the repository and intended branch are clear.

Require both command intent and a clear repository/branch context. Do not trigger
on quoted text, examples, code, filenames, acronym explanations, negated requests,
or unrelated uses such as “What does MPA mean?” A request to define or configure
these shortcuts does not execute them. If a command interpretation is plausible
but the intended action or repository is ambiguous, clarify before mutations.

Both aliases preserve verification, execution permissions, publication, and branch
cleanup requirements. `mpa` directly authorizes archiving the current chat after
successful publication and cleanup, once its work is complete. It needs no
exclusive branch ownership or cross-chat history investigation; never archive
other participants' chats. Failed publication, incomplete cleanup, or unfinished
work keeps the current chat open. An explicit keep-open instruction takes precedence.
`mp` retains conditional automatic archival and its ownership checks; “mp, keep
this chat open” overrides that default. Use post-merge-cleanup for completion.

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

Replace `codex-git` above with its full protected path. `REPOSITORY` may be an absolute checkout path in any current or future project under the user home, with a verified RyanUdelhoven GitHub HTTPS origin; the three legacy aliases also work. Use this path-based workflow across projects, including when older skill text lists only the legacy aliases. For already published branches, use `cleanup REPOSITORY codex/FEATURE VERIFIED_CHAT_UUID` instead of raw branch deletion, then follow the usual archive decision and `finish`. Registry keys, identity
requirements, destination checks, and limitations are in [publish helper](publish-helper.md).
`inspect` returns local scope, worktrees, and participation without refreshing the
remote or changing tracking. It requires a clean checkout and validated config.
`register` records participation without claiming branch creation. Creation records
still follow the feature-branch protocol; failed recording disables automatic archival.

Review the complete scope before publication. Use the inspection's tracking record
instead of direct Python inspection. `publish` registers the integrating chat,
validates the live destination, integrates, verifies publication, and cleans branches.
For explicit `mpa`, verify the current chat identity and use the app archival tool
after successful completion; inspect other chat history only for conditional
automatic archival, not to establish ownership for `mpa`. Run `finish` after the
archive decision and any attempt.
Do not repeat helper mutations manually. Failures require inspecting current state.

## Routine completion path

Reuse the branch, task scope, and verification evidence already established in
this chat. Review only unreviewed changes and run outstanding required checks;
new Git commit identities alone do not invalidate checks on unchanged contents.
Recheck when relevant inputs, environment, scope, or repository policy require it.
Keep the required outgoing-history secret scan at publication.

Use one protected `inspect` result for preflight scope and participation, then
`publish` once. Its receipt establishes publication and cleanup; do not repeat
registration, remote verification, or branch deletion already confirmed there.
Decide archival, attempt it when authorized, then `finish` once. Load recovery
procedures only when the normal path reports a failure or incompatibility.

## Verification and approval boundaries

Run required repository checks inside the sandbox, using existing eligible results
when their inputs and scope still match. Never elevate arbitrary project tests,
build scripts, Python, Node, or shells through a blanket allowance. If required
checks need additional access, explain the specific access and request it normally.
The protected publisher never runs repository verification code.

A routine already-verified registered publication should use only allowed direct
operations. Dirty files, divergence, unsafe configuration, stale verification, or
unverified repositories may stop the workflow. Do not bypass those checks or
disable approvals globally to make the workflow appear successful.

The protected installation and future changes to it require reviewed installation
approval. Restart Codex after policy updates. A CLI rule check predicts policy;
it does not prove the app displayed no approval. Claim that only after observing it.

## Mandatory secret gate

Before publication, run the shared secret checker against every outgoing commit,
not only the final diff or working tree. Require the protected filename policy and
Gitleaks content scan; missing tooling, incomplete history, or scan errors stop
publication. Never bypass a failure with `--no-verify`, scanner exclusions, or an
unreviewed baseline. Safe environment templates still require content scanning.
The protected publisher calls this gate directly because it disables Git hooks.
For ordinary Git workflows, install pre-commit and pre-push hooks as described in
[secret prevention](secret-prevention.md). Do not print detected values. Remove
secrets from all outgoing commits; rotate/revoke any credentials already exposed.
