#!/usr/bin/python3 -I
"""Reviewed installation of fixed script entry points; never allowlist this installer."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import tempfile

ROOT = Path(__file__).resolve().parents[1]
DEST = Path('/Users/ryanudelhoven/.local/share/codex-publish')
YAML_FILES = ('__init__.py', 'composer.py', 'constructor.py', 'cyaml.py',
              'dumper.py', 'emitter.py', 'error.py', 'events.py', 'loader.py',
              'nodes.py', 'parser.py', 'reader.py', 'representer.py',
              'resolver.py', 'scanner.py', 'serializer.py', 'tokens.py')


def isolated(source):
    first, body = source.split(b'\n', 1)
    if first != b'#!/usr/bin/env python3':
        raise ValueError('Source shebang changed; review installer')
    return b'#!/usr/bin/python3 -I\n' + body


def payloads(yaml_source):
    # Read all sources before writing. No imports or execution of source packages.
    validator = isolated((ROOT / 'skills/.system/skill-creator/scripts/quick_validate.py').read_bytes())
    marker = b'\nimport yaml\n'
    if validator.count(marker) != 1:
        raise ValueError('Validator imports changed; review installer')
    validator = validator.replace(marker, b'\nsys.dont_write_bytecode = True\n'
        b'sys.path.insert(0, str(Path(__file__).resolve().parent / "validator-lib"))\n'
        b'import yaml\n', 1)
    files = {'codex-skill-validate': (validator, 0o555),
             'codex-branch-chats': (isolated((ROOT / 'skills/feature-branch/scripts/branch_chats.py').read_bytes()), 0o555),
             # The publisher imports this dependency by its original filename.
             'branch_chats.py': (isolated((ROOT / 'skills/feature-branch/scripts/branch_chats.py').read_bytes()), 0o444)}
    for name in YAML_FILES:
        source = yaml_source / name
        if source.is_symlink() or not source.is_file():
            raise ValueError('Expected regular PyYAML source: ' + name)
        files['validator-lib/yaml/' + name] = (source.read_bytes(), 0o444)
    # License accompanies the existing package; no downloads or package installation.
    license_source = yaml_source.parent / 'pyyaml-6.0.3.dist-info/licenses/LICENSE'
    files['validator-lib/PyYAML-LICENSE'] = (license_source.read_bytes(), 0o444)
    return files


def install(destination, files):
    for name, (content, mode) in files.items():
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.is_symlink():
            raise ValueError('Refusing symlink installation target: ' + str(target))
        descriptor, temporary = tempfile.mkstemp(dir=target.parent, prefix='.install-')
        try:
            with os.fdopen(descriptor, 'wb') as stream:
                stream.write(content)
                stream.flush()
                os.fsync(stream.fileno())
            Path(temporary).chmod(mode)
            os.replace(temporary, target)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)
    return {name: hashlib.sha256(content).hexdigest() for name, (content, _) in files.items()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--yaml-source', required=True, type=Path)
    parser.add_argument('--destination', type=Path, default=DEST,
                        help='Override only for isolated staging/tests')
    args = parser.parse_args()
    print(json.dumps(install(args.destination, payloads(args.yaml_source)), indent=2))


if __name__ == '__main__':
    main()
