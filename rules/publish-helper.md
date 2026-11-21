# Protected merge and push helper

Follow [merge and push execution rules](merge-push.md) for the entire workflow,
including preflight, search, verification, and native app history operations.

Use `inspect REPOSITORY codex/FEATURE VERIFIED_CHAT_UUID` for local preflight and
tracking inspection. It returns scope and worktrees without network requests or
tracking writes; it validates configuration and requires a clean checkout first.
Use `register` with the same arguments to record participation without claiming
creation. Both operations use the protected tracking dependency, not workspace Python.

Installed executable: `/Users/ryanudelhoven/.local/share/codex-publish/codex-git`.
Reviewed source: `scripts/codex-git`. The installed copy and its tracking dependency
live outside the normal Codex writable workspace. Updating either installed file
requires an approved installation; editing the source alone changes no approved
behavior. This is sandbox protection, not root ownership: do not grant an agent
write access to the installation directory or register it as a writable workspace.
The user's account can still update it intentionally.

The `complete` action also loads the reviewed installed `mp-command-hook.py`
from that same protected directory, never the workspace source. Install that
dependency with mode 444 and the publisher with mode 555 after source review.
Use direct `/usr/bin/install` commands under normal installation review; no
installer or interpreter receives a general allowance. Install the dependency
before the publisher. Keep both copies synchronized after handoff-code changes.

Repository arguments accept an absolute checkout path anywhere under `/Users/ryanudelhoven`, including future projects. The existing `customization`, `mynormal`, and `marketnuance` aliases remain supported. Paths resolve canonically; the checkout must be the repository root. The literal local origin must be a single `https://github.com/RyanUdelhoven/NAME.git` URL. Other owners, SSH URLs, missing origins, rewrites, includes, and alternate push destinations require ordinary review. No project registration or source update is needed for new matching projects.

After reviewing the complete branch scope, running repository gates, and confirming
explicit user merge/push authorization, run exactly:

```sh
/Users/ryanudelhoven/.local/share/codex-publish/codex-git publish customization codex/example VERIFIED_CHAT_UUID
```

Supply the current verified Codex chat UUID. The workflow currently supports local
Codex chats and main as the verified remote default branch. It rejects extra
arguments, unverified repositories, primary-branch deletion, dirty checkouts,
in-progress operations, participating branches in other worktrees, unexpected
origin destinations, URL rewrites/config includes, and repository credential or filter commands. It fetches main directly
from the fixed HTTPS destination and requires local main to be contained in remote
main and remote main to be contained in the verified feature tip. Divergence stops
before publication; update the feature branch and rerun affected checks.

The PR-capable publisher uses fixed `/usr/local/bin/gh` API calls to github.com,
requires the RyanUdelhoven account, and verifies the feature tip's author email. It
scans outgoing history before any feature push. Missing remote feature refs use
an exact absence lease. In a frozen project plan, existing refs may advance only
by an ancestry-proven fast-forward with the exact frozen tip lease; other
differing remote tips are rejected. It
verifies the pushed tip's GitHub attribution, opens or reuses a same-repository PR,
and requires clean mergeability, successful checks, and satisfied reviews. It
merges with `merge_method=merge` pinned to the verified source SHA. It never pushes
main directly, bypasses protections, squashes, or enables auto-merge. It polls pending checks/mergeability for up to 30 seconds. Pending checks
or reviews then stop with the PR URL and retain branches; inspect live state before
recovery. A missing email-read scope can block attribution verification; use a
verified account-specific noreply email or resolve access without rewriting history.

After GitHub confirms the merge, it fetches main, proves both the source and merge
commit remain in published history, and fast-forwards local main to that published
tip. Its receipt records `source`, `published`, `merge_commit`, `pull_request`, and
`source_preserved`. Inspection advertises `publication_workflow=github-pr-merge-v1`;
the mp hook rejects older installed helpers before publication. The mp hook must accept a published merge SHA different from
the feature SHA. Both publisher and hook source changes require coordinated
activation; an old direct-main publisher must not be used for this workflow.

Remote verification must observe the published commit before cleanup.
Remote feature deletion uses
an exact-tip lease to preserve concurrent commits; different feature tips remain
untouched and disable archival. Local cleanup uses `branch -d`. Git hooks and
fsmonitor are disabled, global/system Git configuration is excluded, inherited
Git overrides are removed, and authentication uses the fixed installed GitHub CLI
credential helper. The protected secret checker scans outgoing history before switching main;
missing tooling, detected secrets, or scan errors stop publication. See
[secret prevention](secret-prevention.md). Project verification remains the caller's responsibility;
publication does not run repository scripts or tests.

Output includes publication evidence, cleanup status, and the participation record.
Keep the chat open after publication. Reuse the receipt for publication and cleanup
instead of repeating operations. Close the branch participation lifecycle with:

```sh
/Users/ryanudelhoven/.local/share/codex-publish/codex-git finish customization codex/example VERIFIED_CHAT_UUID
```

A failed operation can leave main advanced or already published. Inspect the state
before retrying; no automatic rollback, reset, or force push occurs. Failed cleanup
preserves tracking history and requires ordinary repair. The helper never archives
chats. Archival requires a separate explicit chat request and uses the app tool; publication never triggers it.

`git-workflow.rules` owns reviewed Git grants, raw push prompts, and main-branch deletion prohibitions.
Historical grants for those same command contexts were removed from the local
`default.rules`; unrelated grants remain. Keep raw commands prompted. The protected
helper has a separate executable allow rule, so these prompts do not match it.
Other command spellings fall back to normal approval policy. Rules govern shell
escalation, not every action executed within a writable sandbox.

Restart Codex after changing rule files. Until then, the running session may retain
old rules. For installation, explicitly approve copying reviewed files into
the protected directory; never whitelist the installer, Python, or a general shell.
Run `python3 -m unittest discover -s scripts -p 'test_*.py'` for regression checks.

For already integrated and published branches, use `cleanup ABSOLUTE_REPOSITORY_PATH codex/FEATURE VERIFIED_CHAT_UUID`. This requires a clean checkout on main, feature ancestry in main, local main matching live origin main, the remote default main, and no feature checkout in another worktree. It removes the verified feature branches and writes the same receipt for `finish`, without merging or pushing main. Changed remote feature tips remain preserved.

## Commit-bound mp hook

The UserPromptSubmit dispatcher now inventories local worktrees and emits a
project request for every exact mp. Before any publication, invoke protected
`plan-project REPOSITORY CHAT_UUID --request REQUEST_UUID` directly; it reads live
heads and finalizes local plus remote branch scope. It neither switches branches
nor pushes. Remote-only histories must be fetched and restored at their frozen
SHA before per-branch completion. Even already-ready work goes through discovery.

After reviewing, committing, and checking each owning branch, invoke
`codex-git complete REPOSITORY FEATURE_BRANCH CHAT_UUID --request REQUEST_UUID`
with `--checks-file /tmp/BRANCH-CHECKS.json`. Reuse the request UUID for remaining
branches, but keep each branch's actual successful check evidence separate. The
protected handoff pins the reviewed source SHA and frozen remote tip. A differing
remote tip stops; a matching existing remote may advance only after ancestry
proves a fast-forward, guarded by its exact-tip lease. Non-fast-forward updates
remain refused. Missing remote branches use the exact absence lease.

The reader accepts only a bounded regular JSON file, refuses symlinks and non-string
entries, and never executes evidence. Legacy repeated `--check` arguments still
accept literal strings, but shell expansion can defeat executable-rule matching.
The MoneyNotes lock failure reproduced with `"$PATH"` in an ignored tracker argument;
the same invocation with literal data succeeded. Use literal command arguments
and a JSON file instead of constructing nested shell quoting.
Other publication actions reject evidence options.
The direct protected entry point lets its existing rule cover Git metadata
writes; Python launching the helper as a subprocess inherits Python's sandbox
instead. Completion records readiness and publishes without another
user command. The request expires after 30 minutes or a later user message; main,
detached HEAD, wrong chat/branch, and rewritten request history are refused.
The Python dispatcher never stages or commits by itself; the authorized assistant
preparation pass owns those judgment-dependent operations. No path archives chats.

`probe REPOSITORY codex/FEATURE CHAT_UUID --checks-file ABSOLUTE_JSON_PATH`
tests nested tracking inspection plus temporary metadata writes and locking.
It creates no request/readiness, performs no network operations, changes no refs
or lifecycle, and removes its scratch directory. Check evidence remains inert.
Use this for live sandbox diagnosis without consuming an mp request or publishing.
The existing helper rule covers the new actions; no new Git permissions or rule
grants are needed. Install the reviewed dispatcher before the reviewed publisher.

## Bounded live reads

The same installed helper provides `remote-branches REPOSITORY`,
`remote-tip REPOSITORY BRANCH`, `remote-info REPOSITORY`, and
`fetch-ref REPOSITORY BRANCH`. See [access recovery](merge-push.md#github-access-recovery-all-git-actions).
Reads share canonical repository/origin validation and the fixed credential helper;
they accept dirty checkouts and do not require origin/HEAD or default main.
`remote-info` permits only fixed GET account/repository calls. Fetch writes only
objects and FETCH_HEAD, leaves cached origin refs unchanged, disables recursive
submodules/auto-maintenance, and accepts no refspec, tag, SHA, or arbitrary options.
Live observations are timestamped snapshots, not guarantees against later changes.

Install the reviewed publisher with mode 555 using a direct `/usr/bin/install`
operation after source review. Preserve the already installed dispatcher and other
dependencies. No executable-policy change is needed where the existing protected
codex-git grant applies; the current session must still demonstrate the new actions.
A managed-policy denial remains a blocker, not permission to bypass that policy.

## Project-wide mp cycle

Exact mp snapshots local non-primary branches/worktrees, then protected live discovery
adds remote-only branches and freezes their exact tips. The agent commits reviewed pending changes on their owning branches. The frozen plan
uses the primary worktree as coordinator and one request UUID across separate
`complete` calls. Each branch retains its own check evidence, verified SHA, PR,
merge commit, receipt, and cleanup. New user input or the 30-minute timeout cancels
remaining authorization; failed/partial publication prevents replay or continuation.
Live remote-only branches are included after exact-tip restoration; later-created branches are excluded. Primary or detached dirty
work must be assigned explicitly before entering the cycle. Linked feature
worktrees may be detached only after committing, cleanliness checks, and idle-work
verification. Required checks run in the normal sandbox, never in this helper.

The publisher accepts bounded literal feature-branch names beyond `codex/` for
existing project branches, while still refusing main/master sources and unsafe
ref syntax. New implementation branches retain the `codex/` naming convention.
After each verified publication/cleanup, origin/main is refreshed to the verified
published SHA with a compare-and-swap before safe local deletion. This cache update
belongs only to authorized publication/cleanup; read actions remain unchanged.
Already-integrated branches receive verified cleanup without duplicate PR creation.

Install both reviewed `mp-command-hook.py` (mode 444) and `codex-git` (mode 555)
before using the project cycle. Preserve the existing executable-policy boundaries.
See [preparation](merge-push.md#preparation-within-mp) for sequencing and stop rules.
