# Protected merge and push helper

Installed executable: `/Users/ryanudelhoven/.local/share/codex-publish/codex-git`.
Reviewed source: `scripts/codex-git`. The installed copy and its tracking dependency
live outside the normal Codex writable workspace. Updating either installed file
requires an approved installation; editing the source alone changes no approved
behavior. This is sandbox protection, not root ownership: do not grant an agent
write access to the installation directory or register it as a writable workspace.
The user's account can still update it intentionally.

The registry is embedded in the installed helper:

| Key | Checkout | Expected GitHub repository |
| --- | --- | --- |
| customization | `/Users/ryanudelhoven/.codex` | RyanUdelhoven/CodexCustomization |
| mynormal | `/Users/ryanudelhoven/development/projects/MyNormal` | RyanUdelhoven/MyNormal |
| marketnuance | `/Users/ryanudelhoven/development/projects/MarketNuance` | RyanUdelhoven/MarketNuance |

After reviewing the complete branch scope, running repository gates, and receiving
merge/push authorization, run exactly:

```sh
/Users/ryanudelhoven/.local/share/codex-publish/codex-git publish customization codex/example VERIFIED_CHAT_UUID
```

Supply the current verified Codex chat UUID. The workflow currently supports local
Codex chats and main as the verified remote default branch. It rejects extra
arguments, arbitrary repositories, primary-branch deletion, dirty checkouts,
in-progress operations, participating branches in other worktrees, unexpected
origin destinations, and URL rewrites/config includes. It fetches main directly
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
credential helper. Project verification remains the caller's responsibility;
publication does not run repository scripts or tests.

Output includes publication evidence, cleanup status, and the participation record.
The app workflow checks chat history and makes the archive decision. After that
decision and any archive attempt, close the same lifecycle:

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
old rules. For installation, explicitly approve copying both reviewed files into
the protected directory; never whitelist the installer, Python, or a general shell.
Run `python3 -m unittest discover -s scripts -p 'test_*.py'` for regression checks.
