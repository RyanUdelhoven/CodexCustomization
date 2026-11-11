# Secret prevention

The shared gate is `scripts/secret_check.py`; protected installation lives beside
`codex-git`. It uses free, locally installed Gitleaks (tested with 8.30.1), a fixed
policy extending its default rules, and independent forbidden filename checks.
No source or credentials are uploaded. Repository scanner settings, ignore files,
inline allow comments, and inherited Gitleaks environment settings cannot disable
this scan. Output never includes detected values.

## Coverage

- Pre-commit scans the complete index, including safe environment templates.
- Pre-push scans every outgoing commit snapshot, not merely the final diff.
- New remote refs scan all reachable history; unknown remote objects stop the push.
- The publisher scans the live remote-main-to-source range before local integration.
- `.env` and `.env.*` files are blocked at any directory depth.
- Exact example/sample/template/dist suffixes permit templates, subject to content scanning.
- Common credential files, private-key filenames, and key containers are blocked.
- Missing tooling, shallow history, submodules, or scanner errors stop the gate.

The scanner checks each distinct blob, including symlink text without following it.
It decodes up to three layers of encoding and archives. Pattern detection is not
proof that content contains no secrets; encrypted data and unsupported formats
still need review. Filename policy is intentionally conservative: public `.key`
files or non-secret `.npmrc` files require a reviewed policy change, not a bypass.
Full snapshot scanning can flag pre-existing secrets and can take time in large
histories. No repository-controlled baselines or allowlists are accepted.

## Installation and use

Install Gitleaks through Homebrew: `brew install gitleaks`. Review and install
`codex-git`, `secret_check.py`, `secret-policy.toml`, and the two Git hooks in the
protected directory. Use `scripts/install-secret-gate.py` for the bounded local
installation after approval. It checks existing hook configurations and refuses
to overwrite unrelated hooks; it does not modify global Git configuration.
It installs hooks only in the three registered repositories, including their
shared worktree configuration. Preserve existing hooks by integrating them after
review rather than silently replacing them.

Manual checks from a checkout:

```sh
/Users/ryanudelhoven/.local/share/codex-publish/secret_check.py staged
/Users/ryanudelhoven/.local/share/codex-publish/secret_check.py range --base origin/main --tip HEAD
```

Invoke the installed executable directly to use its reusable allowance. Its shebang
already selects isolated system Python. Repository paths and revisions may vary;
general Python execution and the writable source copy retain normal permissions.

Local hooks can be bypassed or removed. The protected publisher independently
runs the check with hooks disabled. Other Git clients and machines require hook
installation; enable hosting push protection separately where available. CI is
additional detection after upload, not a substitute for preventing disclosure.
No hosting settings are changed by this installation.

## Handling a failure

Do not print credential values or paste them into chats. Investigate locally with
Gitleaks redaction enabled. Move runtime values into ignored local configuration;
keep only placeholder templates tracked. Verify ignoring with `git check-ignore`;
ignore rules do not untrack files. Remove affected files/values from every
outgoing commit, then rerun the same gate. Do not rewrite published history
without authorization. Revoke/rotate exposed credentials; deletion alone is not
remediation. A false positive requires a reviewed central policy adjustment.

## Maintenance

Run `python3 -m unittest discover -s scripts -p 'test_*.py'` after changes.
Test fixtures use synthetic tokens and disposable repositories. Updating tracked
source does not update the protected installation; reinstall reviewed changes.
Keep scanner updates current and rerun integration tests after upgrades.

Sources: [Gitleaks](https://github.com/gitleaks/gitleaks),
[Git hooks](https://git-scm.com/docs/githooks),
[OWASP secrets management](https://owasp.github.io/DevSecOpsGuideline/2-Process/2-2-Develop/2-2-1-Pre-commit/2-2-1-2-Secrets-Management/).
