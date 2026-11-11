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

Basic readers and selected diagnostic prefixes run without approval. Raw `rg`,
`sed`, `find`, `curl`, and `date` require approval outside the sandbox because
prefix matching cannot validate all their arguments. Use the executable helper:

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
Its writable source at `scripts/codex-read` retains an explicit prompt rule,
overriding historical allow grants. Installing or updating the protected copy
requires approval; the rule never approves a general installer or interpreter.
Time uses Python's clock reader rather than the system date-setting command.
The hardware check uses fixed sysctl arguments; a raw sysctl prefix would permit
additional operands that set values, so raw sysctl requires approval too.

Python, Ruby, shell invocations, observed Node execution forms, tests, file
mutations, container execution, service changes, API calls, and extraction require
approval outside the sandbox. Existing grants for these prefixes are overridden
by the more restrictive prompt decision. Other previously approved categories,
including Git and `npm run build`, remain governed by their existing rules.
Unlisted Node scripts and reordered flags receive no new allowance. Prefix rules
are not a complete executable or argument firewall; alternate paths and spellings
may receive no match and fall back to the normal approval policy.

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

## Merge and push workflow

`git-workflow.rules` is the canonical reviewed Git policy. Raw pushes and branch
operations retain approval prompts. The protected publish helper provides the
validated route without repeated shell approvals; see [publish helper](publish-helper.md).
Do not whitelist its writable source or its installer. Restart Codex after installation.
