# Required merge and push execution rules

These instructions complement the executable `.rules` policy. They do not grant
execution permissions. Apply them to authorized merge/push work in registered
repositories; user requests or applicable standing user instructions supply
publication authorization, not this document.

## Contextual shortcuts

Automatic merge, push, and chat archival are disabled. Completed work stays on
its feature branch until a separate explicit publication request. Merge/push
requests never authorize archiving a chat.

Exact standalone lowercase `mp`, ignoring surrounding whitespace, explicitly
requests finish-and-publish for the current task. It authorizes final review,
outstanding checks, committing reviewed task changes, preparation, merge, push,
and completed-branch cleanup. The user does not issue separate commit/prepare
commands. Mentions, quotes, longer messages, and retired `mpa` do not trigger it.
Configuring the hook is not a request to publish the configuration changes.

The `UserPromptSubmit` hook obtains the checkout from `cwd`, current branch from
Git HEAD, and chat UUID from `session_id`. Ready committed work publishes through
the protected helper. Dirty work, missing/stale readiness, or missing participation
instead creates a scoped pending request and adds preparation instructions to the
same user turn. It does not publish until preparation completes.

## Preparation within mp

On the hook's scoped request, review the current task's full branch changes,
preserve unrelated work, reuse qualifying check results, and run outstanding
required gates. Fix authorized failures and commit only reviewed task files.
Register the managing chat if needed, without fabricating creation history. Stop
for unresolved scope, failed gates, denied execution access, or other concrete
blockers; do not stop merely to ask for another commit/prepare command.

Finish by invoking the existing `scripts/mp-command-hook.py --complete` from the
Codex customization installation, with `--cwd`, `--session`, and the `--request`
identifier supplied by the hook. Pass actual successful check commands through
repeatable `--check` arguments. That handoff records the verified commit and runs
protected publish/finish. It requires the same repository/branch/chat and unchanged
request history; it expires after 30 minutes or a later user message. It runs no
checks itself, so never fabricate results. It does not archive.

The existing `--prepare` mode may still pre-record already-reviewed clean commits,
but is internal and optional; it is not another user step. Changed contents need
affected checks and refreshed readiness. The helper pins publication to the exact
verified SHA. Publication failure consumes readiness; inspect actual state before
recovery. Do not blindly retry or run a second assistant publication workflow.
An unavailable or untrusted hook does not authorize an ad hoc raw-mp fallback.

Separate explicit natural-language merge/push requests retain the protected
workflow below. All paths leave chats open.

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

Replace `codex-git` above with its full protected path. `REPOSITORY` may be an absolute checkout path in any current or future project under the user home, with a verified RyanUdelhoven GitHub HTTPS origin; the three legacy aliases also work. Use this path-based workflow across projects, including when older skill text lists only the legacy aliases. For already published branches, use `cleanup REPOSITORY codex/FEATURE VERIFIED_CHAT_UUID` instead of raw branch deletion, then keep the chat open and run `finish`. Registry keys, identity
requirements, destination checks, and limitations are in [publish helper](publish-helper.md).
`inspect` returns local scope, worktrees, and participation without refreshing the
remote or changing tracking. It requires a clean checkout and validated config.
`register` records participation without claiming branch creation. Creation records
still follow the feature-branch protocol; report tracking gaps without inventing history.

Review the complete scope before publication. Use the inspection's tracking record
instead of direct Python inspection. `publish` registers the integrating chat,
validates the live destination, integrates, verifies publication, and cleans branches.
Keep the chat open after publication and cleanup. Run `finish` to close the branch
participation lifecycle; it does not close the chat. Archival requires a separate
explicit request targeting the chat.
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
Keep the chat open and run `finish` once. Load recovery
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
