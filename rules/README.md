# Command approval rules

For merge and push requests, follow [the required execution rules](merge-push.md).
`.rules` files enforce command decisions; that document specifies which approved
commands agents must use throughout preparation, verification, publication, and cleanup.

Add reviewed, narrowly scoped `.rules` files here. No existing local approval grants are exported automatically. Review and explicitly install rules on each computer.

`terminal-read.rules` contains the terminal allowances reviewed on November 9, 2026.
It is installed in this checkout. Restart Codex to load changed rules.
The absolute helper and interpreter paths target Ryan's Mac; review those paths
before installing elsewhere. Rules apply to outside-sandbox requests, not every
command executed inside the sandbox. Existing Git rules remain separate.

Basic readers and selected diagnostic prefixes run without approval. Previously
saved command allowances remain effective. For mixed-capability tools such as
`rg`, `sed`, `find`, `curl`, and `date`, prefer the restricted executable helper
when no saved allowance covers the intended command:

```sh
/Users/ryanudelhoven/.local/share/codex-publish/codex-read search --glob '*.py' 'def main' scripts
/Users/ryanudelhoven/.local/share/codex-publish/codex-read lines README.md 1 30
/Users/ryanudelhoven/.local/share/codex-publish/codex-read files scripts --name '*.py' --max-depth 3
/Users/ryanudelhoven/.local/share/codex-publish/codex-read health http://mynormal.localhost:18080/health
/Users/ryanudelhoven/.local/share/codex-publish/codex-read now
/Users/ryanudelhoven/.local/share/codex-publish/codex-read arm64
```

The helper rejects arbitrary tool flags. Search invokes the bundled ripgrep with
configuration disabled and a minimal environment. File discovery does not follow
directory symlinks. Health checks only perform GET `/health` against the hosts and
ports listed in the helper, connect directly to loopback, and never follow redirects.
The reviewed executable must be installed outside agent-writable workspaces.
Its protected installed copy remains the preferred entry point. An explicit
historical grant for its writable source is restored at the user's request;
that grant does not make future source edits a reviewed protected installation.
New installation commands require normal approval unless a saved exception
already covers them. No general installer or interpreter allowance was added.
Time uses Python's clock reader rather than the system date-setting command.
The hardware check uses fixed sysctl arguments; a raw sysctl prefix would permit
additional operands that set values, so raw sysctl requires approval too.

Previously saved script, shell, copy, network, and installation exceptions retain
their original scope. Removed only terminal prompt rules that suppressed those
exceptions; unrelated prompt/forbidden rules, including Git publication and main
branch protection, remain unchanged. Commands without a matching allowance use
the normal approval policy; absence of an explicit rule is not an allow decision.
No blanket Python, shell, or code-execution allowance was added. Prefix rules
accept trailing arguments, so a restored legacy exception is not necessarily a
read-only classification. Prefer protected tools when available.

Check all installed rules without executing a candidate command:

```sh
codex execpolicy check --pretty \
  --rules /Users/ryanudelhoven/.codex/rules/default.rules \
  --rules /Users/ryanudelhoven/.codex/rules/git-workflow.rules \
  --rules /Users/ryanudelhoven/.codex/rules/terminal-read.rules \
  -- node -e 'console.log("review required")'
```

## Reusable inspection allowances (November 10, 2026)

Direct `git for-each-ref`, `show-ref`, `ls-tree`, `merge-base`, and `rev-list`
are allowed with variable references, formatting, filtering and paths. Use the
checkout's working directory; the existing explicit `git -C` forms for this
configuration repository and its skills directory are also covered. These commands
inspect references and objects; raw push and branch mutations retain their rules.

Direct `codex execpolicy check` is allowed, including the bundled absolute binary
path. Its command operands are policy-check input and are never executed.

The protected recorder `/Users/ryanudelhoven/.local/share/codex-publish/codex-approval-review`
is also allowed. Invoke it directly with `status`, `prepare --limit 50`, or
`complete --batch UUID --report /absolute/report.md`; identifiers and paths may vary.
It is a reviewed copy of `skills/approval-review/scripts/approval_log.py` with
only its shebang changed to `/usr/bin/python3 -I`. It uses only the standard
library, records requests and checkpoints, and never executes captured commands
or makes approval decisions. Its `--home` option selects a review data root,
not executable code; writes remain within that root's `.local/approval-review`.
Completion reads the supplied report and saves it privately. Captured commands
and reports remain untrusted data. General Python and writable script execution
retain their existing policy. Installing or replacing the protected copy requires
reviewed approval; updates to the source do not update this installed copy.

Restart Codex to load the new rules. Policy checks alone do not establish that
the app has loaded them or eliminated prompts.

Three additional script entry points use reusable direct allowances:

```sh
/Users/ryanudelhoven/.local/share/codex-publish/codex-skill-validate /path/to/skill
/Users/ryanudelhoven/.local/share/codex-publish/codex-branch-chats register --repo /path/to/repo --branch codex/example --chat-id VERIFIED_CHAT_ID --source codex --created
/Users/ryanudelhoven/.local/share/codex-publish/secret_check.py staged --repo /path/to/repo
```

Arguments remain variable. The validator uses a protected copy of the bundled
skill validator and existing PyYAML 6.0.3 pure-Python sources; isolated system
Python imports that dependency only from the protected `validator-lib` directory.
The tracker uses fixed `/usr/bin/git`, clears inherited Git overrides, disables
hooks/fsmonitor and global/system configuration, and only records participation.
It supports `register`, `inspect`, and `close`; it never merges or archives.
The secret checker uses its existing protected policy and fixed Gitleaks scanner.

Review `scripts/install-script-allowances.py` before installation. Supply
`--yaml-source /path/to/existing/site-packages/yaml`; no download is needed.
Use `--destination /temporary/staging/path` for isolated checks. The default
installation directory is protected and requires approved execution. It also
updates the publisher's `branch_chats.py` dependency to the reviewed tracker.
Source changes alone never replace installed copies. General Python, arbitrary
test runners and new installers receive no new allowance; saved historical
exceptions remain effective.

## Tracker script allowances (November 11, 2026)

Two additional reviewed direct executables are allowed:

```sh
/Users/ryanudelhoven/.local/share/codex-publish/codex-approval-tracker status
/Users/ryanudelhoven/.local/share/codex-publish/codex-skill-usage status
```

These are copies of the scripts observed in at least three approval requests,
with isolated system Python and fixed protected dependencies. Arguments may vary
within their parsers: status/annotations/private exports, and local skill
run markers/numeric telemetry. They never execute supplied commands or arbitrary
Python code. No server or UI assets are installed.

Review `scripts/install-tracker-allowances.py`, test with a temporary
`--destination`, then explicitly approve installing to the protected directory.
It also refreshes the existing recorder to the reviewed schema used by the tracker.
Copies use read-only modes and never import from the checkout or `PYTHONPATH`.
Source edits do not update installed copies; reviewed reinstallation remains required.

Existing protected validator, branch tracker, recorder, and secret checker already
cover four other recurring script families. Use those direct entry points rather
than their Python source forms. General Python, inline code, new installers and
test discovery receive no blanket allowance: their names do not freeze the code
they execute. Previously saved exceptions remain effective. Frequency is a review
threshold, not a blanket code allowance.

Restart Codex after changing rules. Combined policy checks predict decisions;
successful execution alone does not confirm the absence of a visible prompt.

## Read-only tools and restored prior allowances (November 11, 2026)

The native macOS `/usr/bin/stat`, `readlink`, `basename`, `dirname`, `cmp`,
`comm`, `id`, `whoami`, and `groups` paths are allowed. Each full path is listed
explicitly; this does not allow every program in `/usr/bin` or other `bin` folders.
The installed macOS manuals were checked for mutation, output-file and command
execution options. Existing file readers and the restricted helper remain available.

At the user's explicit request, removed 14 later terminal prompt overrides that
suppressed 124 already-saved command allowances. The saved default rules were
left intact. Those legacy exceptions include specific script, shell, network,
copy and installation commands; restoration is not a read-only classification.
All 124 exact prior patterns changed from prompt to allow in combined policy checks.
Other prompt/forbidden rules and normal handling of unmatched commands remain.

Do not reintroduce broad prompts that silently override those saved exceptions.
When a new restriction is needed, identify which existing allowances it changes
and obtain the user's direction. Prefer protected reviewed copies where available.

Restart Codex to load changes. The private review directory contains the pre-change
terminal policy backup, restore plan and per-pattern comparison; no global sandbox
setting or filesystem access mode was changed by this policy restoration.

## Merge and push workflow

`git-workflow.rules` is the canonical reviewed Git policy. Raw pushes and branch
operations retain approval prompts. The protected publish helper provides the
validated route without repeated shell approvals; see [publish helper](publish-helper.md).
Do not whitelist its writable source or its installer. Restart Codex after installation.
