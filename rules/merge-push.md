# Required merge and push execution rules

These instructions complement the executable `.rules` policy. They do not grant
execution permissions. Apply them to authorized merge/push work in registered
repositories; user requests or applicable standing user instructions supply
publication authorization, not this document.

## Contextual shortcuts

Automatic merge, push, and chat archival are disabled. Completed work stays on
its feature branch until a separate explicit publication request. Merge/push
requests never authorize archiving a chat.

Exact standalone lowercase `mp`, ignoring surrounding whitespace, requests the
project-wide local-and-remote-branch finish-and-publish cycle. It authorizes review, required
checks, committing all reviewed pending project changes to their owning feature
branches, individual PR merges, publication, and completed-branch cleanup. It
includes linked worktrees. Primary/default branches are targets only. Before publication, use the protected
`plan-project REPOSITORY CHAT_UUID --request REQUEST_UUID` handoff to add live
remote-only branches and freeze exact remote tips. Fetch all remote-only heads,
compare each returned SHA with that frozen tip, and restore each existing branch
locally at that SHA. These are restorations of existing history, not new
implementation branches from main. Branches created after this final snapshot are
excluded. A remote tip change stops publication. Mentions,
quotes, longer messages, and retired `mpa` do not trigger it. Configuring this
behavior does not publish the configuration or any other pending work.

The hook inventories local branches/worktrees and always requests protected live
remote discovery before any publication, even when the current branch is ready.
The finalized project request freezes both local and remote scope. Review every
listed branch; commit its pending changes in its owning checkout. Preserve other
projects and never carry dirty files across branch switches. Use separate commits
for distinct work. Ambiguous ownership or changes on a primary/detached checkout
need resolution before committing; do not guess their destination.

## Preparation within mp

Prepare checked-out feature worktrees first. Detach a linked feature worktree only
after its changes are committed, it is clean, and it is idle; never disrupt active
work. Use the plan's primary checkout as publication coordinator. Process ancestor
branches before dependent ones. For each branch, bring verified published main
into it with a normal merge if needed, resolve authorized conflicts, and run
required checks for the resulting contents. Preserve existing commits; do not
squash branches together, cherry-pick away scope, rebase shared history, or force-push.
Investigate conflicts and ask the user before choosing disputed behavior; follow
the resolution and continuation workflow below. Stop publication for an unanswered
choice, failed check, active worktree, changed remote tip, pending review,
ambiguous scope, or denied access. Report successes and
remaining branches; never retry a partial publication blindly.

Register this chat on each branch without claiming creation history. Write each
branch's actual successful check commands to a separate inert JSON array in /tmp.
Invoke the protected executable directly with literal arguments for that branch:

`/Users/ryanudelhoven/.local/share/codex-publish/codex-git complete REPOSITORY FEATURE_BRANCH CHAT_UUID --request REQUEST_UUID --checks-file /tmp/BRANCH-CHECKS.json`

Use the coordinator repository and frozen request UUID from the hook. Each
completion verifies the original branch tip remains an ancestor, records the
checked commit/lifecycle, publishes one separate PR, and cleans only that branch.
Use the returned remaining list to continue without another user command. Already
integrated branches go through verified cleanup without an empty commit or PR.
The single-branch handoff remains supported. No helper runs project checks itself.

Project requests are single-use per branch and expire after 30 minutes or a later
user message. Partial publication consumes that branch and blocks continuation
until actual state is inspected and a new valid request exists. New branches never
join an existing plan silently. Keep every chat open.

At the end of every mp cycle, append all remaining open project feature branches
as bullets in the final report, including stopped or partially completed cycles.
Refresh local branch/worktree inventory and live remote heads after processing;
include branches outside the frozen snapshot for reporting only. Deduplicate
matching local/remote branch names, label remote-only branches, and exclude
primary/default merge targets. When none remain, state “Remaining open branches:
None.” If local or live remote discovery fails, report the known branches and
explicitly mark the inventory incomplete rather than claiming none remain.
Whenever listing remaining open branches, append an evidence-based reason to
each branch in fewer than 10 words (nine maximum), excluding the branch name and
labels such as remote-only. State the actual blocker or retention reason; do not
infer it from the branch name. If unverified, use “Reason unknown; investigation
incomplete.” Example: `codex/example — Awaiting explicit publication request.`

Do not invoke completion through workspace Python or another shell wrapper.
Children inherit the caller's sandbox; their own executable rules are not
re-evaluated. Direct invocation with literal arguments uses the protected helper's existing allowance,
including the Git metadata access required by participation and readiness records.
It loads only its reviewed installed `mp-command-hook.py` dependency. Missing
or stale protected installation requires reviewed installation, not a broad
Python allowance or changes to Git directory permissions.

Shell expansion in an argument (for example `"$PATH"` in `--check`) can prevent
the direct executable allowance from matching. The command then runs sandboxed
and nested tracking fails at its protected Git lock. Simple quoting of literal
evidence works, but prefer `--checks-file` for all completion handoffs. The JSON
strings remain inert, including variables, redirections and command substitutions.
Never wrap the invocation in an interpreter or expand its arguments.

For diagnosis without publication, use the same literal invocation with action
`probe` and `--checks-file`, omitting `--request`. It validates the clean checkout,
inspects nested tracking, tests temporary Git metadata writes/locking, and removes
its scratch directory. It creates no readiness or request record, changes no refs
or participation lifecycle, and performs no network operations. A successful probe
verifies access only; it does not authorize publication or establish passed checks.

The existing `--prepare` mode may still pre-record already-reviewed clean commits,
but is internal and optional; it is not another user step. Changed contents need
affected checks and refreshed readiness. The helper pins publication to the exact
verified SHA. Publication failure consumes readiness; inspect actual state before
recovery. Do not blindly retry or run a second assistant publication workflow.
An unavailable or untrusted hook does not authorize an ad hoc raw-mp fallback.

Separate explicit natural-language merge/push requests retain the protected
workflow below. All paths leave chats open.

## Integration and conflict resolution

After live discovery, inspect each frozen branch before scheduling its merge.
Fetch live main with the protected `fetch-ref` when its objects are needed; use
the returned SHA rather than assuming cached origin/main is current. Record
the source tip, live target tip, pending changes, and owning checkout. Classify:

- Integrated tip and clean checkout: verified cleanup only; no empty commit or PR.
- Integrated tip with pending work: review and commit that work before rechecking integration.
- Unintegrated tip: inspect missing commits, merge verified main normally, then validate and publish.

Use `git merge-base --is-ancestor SOURCE_SHA LIVE_MAIN_SHA` as ancestry evidence.
Identical filenames, an empty final diff, or an old branch name do not prove
integration. If prior squash/rebase publication is claimed, corroborate patch
comparisons with the merged PR and target contents; patch equivalence alone does
not prove history preservation or authorize forced deletion. Keep the existing
protected publisher's ancestry and exact-tip requirements.

When a merge conflicts, inspect the merge base, both sides, relevant callers,
tests, and superseding instructions. Explain each meaningful behavior choice in
plain language, with a recommended combined result when compatible. Bundle
related questions through the structured question tool; ask about behavior,
data, or scope rather than asking the user to edit Git markers or blindly choose
“ours”/“theirs”. Include the affected remaining branch names and state that an
answer selecting a resolution will continue their already-requested publication.
Reuse applicable answers already given; ask again only for a new material choice.
Continue independent read-only investigation while waiting, and leave dependent
resolution/publication pending. Do not require another mp merely to ask questions.

Apply the user's answers to the conflicted files and coordinated callers/tests.
Preserve unrelated work and meaningful commits; do not drop a branch's scope to
make the merge clean. Inspect the resolved diff, remove every conflict marker,
run affected checks against the final contents, and commit the resolution only
when appropriate. Recheck integration after new work is committed and after
earlier branch publication advances main. Publish only missing work through the
protected PR flow: push the verified feature tip, merge the PR, verify the source
in live published main, synchronize local main, then delete the verified branch.
Already-integrated branches use protected cleanup instead.

### Continue after conflict answers

User messages still cancel pending mp tokens, and their 30-minute expiry remains.
Do not resurrect, edit, or replay a cancelled/consumed request. If the conflict
question explicitly offered resolution followed by publication of the named
remaining branches, an answer selecting that option supplies a new explicit
natural-language continuation request for that same scope. Use the registered
protected `inspect`/`publish` or `cleanup`/`finish` workflow under that answer;
this is deliberate continuation, not a retry of a failed publication. Retain
the original frozen branch list and remote tips in the handoff. Revalidate live
state, original-tip ancestry, ownership, resolved contents, and successful checks;
pass the verified `--expected-source` and original `--expected-remote` SHA or
`absent` to protected publish. Exclude new branches, stop if a frozen remote tip
changed, and inspect receipts to skip branches already published. A stopped,
ambiguous, or scope-changing reply is not continuation authorization. Failed or
partial publication retains its existing no-blind-retry recovery requirements.

At completion, verify local heads, linked worktrees, and live remote heads again.
Prune stale remote-tracking references only after live absence is established,
so deleted branch names do not linger in the branch chooser. Preserve main,
unmerged or changed work, and explicit retention requests. Report completed work,
real blockers, and every remaining open project feature branch as bullets.

## Remote feature branches

Keep implementation branches local until explicit publication authorization,
unless earlier review, backup, or collaboration needs a remote branch. Default
`mp` publication pushes the exact verified feature tip, opens or reuses a GitHub
pull request under Ryan's account, and merges into main using a merge commit.
Preserve meaningful individual commits and accurate authorship. Verify account
and author-email attribution. Never manufacture commits or backdate work.
Respect narrower explicit push destinations and branch-retention requests.

Wait for checks and approvals; preserve the PR and branches on pending or failed
checks, missing reviews, incompatible merge policies, or changed source tips.
Never bypass protections, silently squash, or fall back to pushing main directly.
Verify the PR merge and feature ancestry in published main before synchronizing
local main and deleting completed branches. Branch deletion preserves merged
history and contribution eligibility. Private-profile visibility changes require
a separate user request. GitHub determines contribution eligibility and counts.

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

## GitHub access recovery (all Git actions)

When an ordinary Git/gh operation fails, classify the actual error before recovery.
An allowlist denial or CONNECT/proxy 403 is a network-policy block, not evidence of
expired credentials. HTTP 401/authentication failures need credential repair;
HTTP 403/404 or repository-not-found can mean permissions or private visibility.
A missing remote ref is not an access failure. Generic connection failures do not
prove any one cause. Never print tokens or reset authentication speculatively.

Use the installed protected helper directly with literal arguments for bounded
live reads, including dirty checkouts and future matching repositories:

```text
codex-git remote-branches ABSOLUTE_REPOSITORY_PATH
codex-git remote-tip ABSOLUTE_REPOSITORY_PATH main
codex-git remote-info ABSOLUTE_REPOSITORY_PATH
codex-git fetch-ref ABSOLUTE_REPOSITORY_PATH main
```

Replace `codex-git` with `/Users/ryanudelhoven/.local/share/codex-publish/codex-git`.
`remote-branches` lists live heads. `remote-tip` returns live existence/tip and a
separately labeled cached tip; absence never authorizes deletion. `remote-info`
checks the fixed GitHub account and repository API using GET only. `fetch-ref`
downloads one literal branch into objects and FETCH_HEAD; it never updates tracking
refs, switches branches, or merges. Use its returned full SHA for inspection and
branch bases; `origin/main` can remain stale. Fetch has local effects and needs an
actual fetch/inspection requirement; a branch-list request needs only a read.
No action accepts arbitrary URLs, Git arguments, API endpoints, or publication flags.
No branch participation/chat ID is required for these non-publication actions.

Attempt the matching protected read once after an ordinary access failure. If it
also fails, stop and report the classified error; request sanctioned operation
access where available. Do not remove proxies, disable TLS, broaden shell/Python
allowances, change managed network policy, or repeat commands blindly. If the
installed helper lacks the action, review/install the source first; never run the
writable source as a protected workaround. The installation is machine-local and
must be repeated on a new machine; it cannot guarantee future policy grants.

For an authorized mutation, retain the existing publish/complete/cleanup flow and
all leases, secret gates, and readiness checks. A failed mutation may already have
pushed or merged: inspect local state and live heads, then inspect the matching PR
through an authorized API/UI before deliberate recovery. Read actions never grant
publication or authorize retrying a consumed mp request. Never publish to test access.

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
validates the live destination, publishes through a PR merge commit, verifies source ancestry in published main, and cleans branches.
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
