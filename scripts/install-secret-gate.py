#!/usr/bin/python3 -I
"""Reviewed installation only; never allowlist this writable installer."""
import os
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
DEST = Path('/Users/ryanudelhoven/.local/share/codex-publish')
REPOS = [Path('/Users/ryanudelhoven/.codex'),
         Path('/Users/ryanudelhoven/development/projects/MyNormal'),
         Path('/Users/ryanudelhoven/development/projects/MarketNuance')]
HOOKS = DEST / 'git-hooks'


def git(repo, *args):
    return subprocess.run(['/usr/bin/git', '-C', str(repo), *args], check=True,
                          capture_output=True, text=True).stdout.strip()


def main():
    if not Path('/usr/local/bin/gitleaks').is_file():
        raise SystemExit('Install Gitleaks first')
    # Validate every checkout before writing any files/configuration.
    for repo in REPOS:
        current = subprocess.run(['/usr/bin/git', '-C', str(repo), 'config',
                                  '--get-all', 'core.hooksPath'], capture_output=True, text=True)
        if current.returncode not in (0, 1):
            raise SystemExit('Cannot inspect hook configuration: ' + str(repo))
        if current.stdout.strip() not in ('', str(HOOKS)):
            raise SystemExit('Existing hooksPath needs reviewed integration: ' + str(repo))
        common = Path(git(repo, 'rev-parse', '--path-format=absolute', '--git-common-dir'))
        existing_hooks = common / 'hooks'
        for existing in existing_hooks.iterdir() if existing_hooks.exists() else []:
            if not existing.name.endswith('.sample') and existing.is_file() and os.access(existing, os.X_OK):
                raise SystemExit('Existing executable hook needs reviewed integration: ' + str(existing))
    DEST.mkdir(parents=True, exist_ok=True)
    HOOKS.mkdir(exist_ok=True)
    # Replace read-only installed files atomically; dependencies precede publisher.
    files = [(ROOT / 'scripts' / name, DEST / name)
             for name in ['secret-policy.toml', 'secret_check.py', 'codex-git']]
    files += [(ROOT / 'scripts/git-hooks' / name, HOOKS / name)
              for name in ['pre-commit', 'pre-push']]
    for source, destination in files:
        fd, temporary = tempfile.mkstemp(dir=destination.parent, prefix='.install-')
        try:
            with os.fdopen(fd, 'wb') as stream:
                stream.write(source.read_bytes())
            Path(temporary).chmod(0o444 if destination.suffix == '.toml' else 0o555)
            os.replace(temporary, destination)
        finally:
            Path(temporary).unlink(missing_ok=True)
    for repo in REPOS:
        git(repo, 'config', '--local', 'core.hooksPath', str(HOOKS))
    print('Installed protected publisher, secret checker, policy, and hooks in three registered repositories')


if __name__ == '__main__':
    main()
