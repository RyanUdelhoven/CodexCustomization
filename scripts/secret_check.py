#!/usr/bin/python3 -I
"""Shared fail-closed staged and outgoing-history secret gate. Never prints content."""
import argparse
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

SCANNER = Path('/usr/local/bin/gitleaks')
POLICY = Path(__file__).resolve().with_name('secret-policy.toml')
ENV = {'PATH': '/usr/bin:/bin', 'HOME': '/var/empty', 'GIT_CONFIG_NOSYSTEM': '1',
       'GIT_CONFIG_GLOBAL': '/dev/null', 'GIT_NO_REPLACE_OBJECTS': '1',
       'GIT_CONFIG_COUNT': '0', 'GIT_TERMINAL_PROMPT': '0'}


def git(repo, *args):
    result = subprocess.run(['/usr/bin/git', '-c', 'core.hooksPath=/dev/null',
                             '-c', 'core.fsmonitor=false', '-C', str(repo), *args],
                            env=ENV, capture_output=True)
    if result.returncode:
        raise ValueError('Cannot inspect Git objects; secret check stopped')
    return result.stdout


def forbidden(path):
    parts = path.lower().split('/')
    name = parts[-1]
    # Exact template suffixes only; their contents are still scanned.
    template = bool(re.fullmatch(r'\.env(?:\.[a-z0-9_-]+)*\.(example|sample|template|dist)', name))
    return ((name == '.env' or name.startswith('.env.')) and not template
            or name in {'id_rsa', 'id_dsa', 'id_ecdsa', 'id_ed25519', '.netrc', '.npmrc',
                        'credentials', 'credentials.json', 'service-account.json'}
            or name.endswith(('.p12', '.pfx', '.key', '.keystore'))
            or '.aws' in parts and name in {'config', 'credentials'})


def scan(repo, mode, base=None, tip=None):
    repo = Path(repo).resolve()
    if not SCANNER.is_file() or not POLICY.is_file():
        raise ValueError('Required Gitleaks scanner or protected policy missing; install before retrying')
    if git(repo, 'rev-parse', '--is-shallow-repository').strip() == b'true':
        raise ValueError('Shallow history cannot establish complete secret coverage')
    if mode == 'staged':
        trees = [None]  # Read index directly; no Git metadata writes or locks.
    else:
        # Resolve objects, not user-controlled revision expressions/options.
        tip = git(repo, 'rev-parse', '--verify', tip + '^{commit}').decode().strip()
        base = git(repo, 'rev-parse', '--verify', base + '^{commit}').decode().strip() if base else None
        trees = git(repo, 'rev-list', tip, *(['^' + base] if base else [])).decode().splitlines()
        trees.append(tip)  # Existing tracked secret files also block publication.
    seen = set()
    with tempfile.TemporaryDirectory(prefix='secret-check-') as temporary:
        for tree in dict.fromkeys(trees):
            rows = git(repo, 'ls-files', '--stage', '-z').split(b'\0') if tree is None else git(repo, 'ls-tree', '-r', '-z', tree).split(b'\0')
            for row in filter(None, rows):
                metadata, raw_path = row.split(b'\t', 1)
                if tree is None:
                    permissions, oid, stage = metadata.split()
                    if stage != b'0':
                        raise ValueError('Resolve index conflicts before secret checking')
                    kind = b'commit' if permissions == b'160000' else b'blob'
                else:
                    permissions, kind, oid = metadata.split()
                path = raw_path.decode('utf-8', 'surrogateescape')
                if forbidden(path):
                    raise ValueError('Secret-bearing filename blocked: ' + repr(path) + '; use an ignored local file and safe template')
                if kind != b'blob':
                    raise ValueError('Submodule content requires separate secret review: ' + repr(path))
                if oid in seen:
                    continue
                seen.add(oid)
                # Neutral names avoid path traversal, symlinks, ignored directories,
                # and scanner extension exclusions. Scan every historical blob.
                Path(temporary, oid.decode() + '.txt').write_bytes(git(repo, 'cat-file', 'blob', oid.decode()))
        result = subprocess.run([str(SCANNER), 'dir', temporary, '--config', str(POLICY),
                                 '--redact=100', '--no-banner', '--ignore-gitleaks-allow',
                                 '--gitleaks-ignore-path', '/dev/null', '--exit-code', '1',
                                 '--max-decode-depth', '3', '--max-archive-depth', '3'],
                                env=ENV, capture_output=True)
        if result.returncode:
            # Suppress raw scanner output: it may contain secret-bearing context.
            raise ValueError('Gitleaks found a secret or could not complete; publication blocked. Investigate locally with redacted output.')
    return len(seen)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['staged', 'range', 'pre-push'])
    parser.add_argument('--repo', default='.')
    parser.add_argument('--base')
    parser.add_argument('--tip', default='HEAD')
    args = parser.parse_args()
    if args.mode == 'pre-push':
        for row in sys.stdin:
            local_ref, local, remote_ref, remote = row.split()
            if set(local) == {'0'}:
                continue  # Deletion transfers no new content.
            # Unknown/new destinations require full reachable history, never an
            # assumption that locally remembered remote refs are trustworthy.
            scan(args.repo, 'range', None if set(remote) == {'0'} else remote, local)
    else:
        scan(args.repo, args.mode, args.base, args.tip)
    print('Secret check passed')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError) as error:
        sys.exit('Secret check stopped: ' + str(error))
