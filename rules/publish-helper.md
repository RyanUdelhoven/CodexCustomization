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

Repository arguments accept an absolute checkout path anywhere under `/Users/ryanudelhoven`, including future projects. The existing `customization`, `mynormal`, and `marketnuance` aliases remain supported. Paths resolve canonically; the checkout must be the repository root. The literal local origin must be a single `https://github.com/RyanUdelhoven/NAME.git` URL. Other owners, SSH URLs, missing origins, rewrites, includes, and alternate push destinations require ordinary review. No project registration or source update is needed for new matching projects.

After reviewing the complete branch scope, running repository gates, and confirming
explicit or applicable standing user merge/push authorization, run exactly:

```sh
/Users/ryanudelhoven/.local/share/codex-publish/codex-git publish customization codex/example VERIFIED_CHAT_UUID
```

Supply the current verified Codex chat UUID. The workflow currently supports local
Codex chats and main as the verified remote default branch. It rejects extra
arguments, arbitrary repositories, primary-branch deletion, dirty checkouts,
in-progress operations, participating branches in other worktrees, unexpected
origin destinations, URL rewrites/config includes, and repository credential or filter commands. It fetches main directly
from the fixed HTTPS destination, requires local main to be contained in remote
main and remote main to be contained in the feature tip, and fast-forwards main.
Divergence stops before switching branches; update the feature branch normally
and rerun the relevant checks. Non-fast-forward merge workflows retain normal
approval requirements.

Pushes use explicit main-to-main refspecs, with no force. Remote verification
must observe the published commit before cleanup. Remote feature deletion uses
an exact-tip lease to preserve concurrent commits; different feature tips remain
untouched and disable archival. Local cleanup uses `branch -d`. Git hooks and
fsmonitor are disabled, global/system Git configuration is excluded, inherited
Git overrides are removed, and authentication uses the fixed installed GitHub CLI
credential helper. The protected secret checker scans outgoing history before switching main;
missing tooling, detected secrets, or scan errors stop publication. See
[secret prevention](secret-prevention.md). Project verification remains the caller's responsibility;
publication does not run repository scripts or tests.

Output includes publication evidence, cleanup status, and the participation record.
The app workflow makes the archive decision. Explicit `mpa` verifies and archives
only the current completed chat without an ownership/history investigation;
conditional automatic archival retains those checks. Reuse the receipt for
publication and cleanup instead of repeating its operations. After the decision
and any archive attempt, close the same lifecycle:

```sh
/Users/ryanudelhoven/.local/share/codex-publish/codex-git finish customization codex/example VERIFIED_CHAT_UUID
```

A failed operation can leave main advanced or already published. Inspect the state
before retrying; no automatic rollback, reset, or force push occurs. Failed cleanup
preserves tracking history and requires ordinary repair. The helper never archives
chats. Archival uses the app tool after successful publication and cleanup.

`git-workflow.rules` owns reviewed Git grants and raw push/branch prompts.
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
