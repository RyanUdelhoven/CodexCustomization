#!/usr/bin/python3 -I
"""Install reviewed tracker copies; this installer intentionally remains prompted."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'skills/approval-review/scripts'
DESTINATION = Path('/Users/ryanudelhoven/.local/share/codex-publish')


def isolated(content, dependencies=False):
    first, body = content.split(b'\n', 1)
    if first != b'#!/usr/bin/env python3':
        raise ValueError('Source entry point changed; review installer')
    if dependencies:
        marker = b'\nfrom approval_log import '
        if body.count(marker) != 1:
            raise ValueError('Source imports changed; review installer')
        body = body.replace(marker,
                            b'\nsys.dont_write_bytecode = True\n'
                            b'sys.path.insert(0, str(Path(__file__).resolve().parent / "approval-lib"))\n'
                            + marker, 1)
    return b'#!/usr/bin/python3 -I\n' + body


def payloads():
    names = ('approval_log.py', 'approval_tracker.py', 'skill_usage.py')
    for name in names:
        if (SOURCE / name).is_symlink() or not (SOURCE / name).is_file():
            raise ValueError('Expected regular reviewed source')
    recorder = (SOURCE / 'approval_log.py').read_bytes()
    tracker = (SOURCE / 'approval_tracker.py').read_bytes()
    usage = (SOURCE / 'skill_usage.py').read_bytes()
    return {
        'codex-approval-review': (isolated(recorder), 0o555),
        'codex-approval-tracker': (isolated(tracker, True), 0o555),
        'codex-skill-usage': (isolated(usage, True), 0o555),
        'approval-lib/approval_log.py': (recorder, 0o444),
        'approval-lib/skill_usage.py': (usage, 0o444),
    }


def install(destination, files):
    if destination.is_symlink() or (destination / 'approval-lib').is_symlink():
        raise ValueError('Refusing symlink installation directory')
    legacy_ui = destination / 'tracker.html'
    if legacy_ui.is_symlink() or (legacy_ui.exists() and not legacy_ui.is_file()):
        raise ValueError('Refusing unexpected legacy UI path')
    for name, (content, mode) in files.items():
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.is_symlink():
            raise ValueError('Refusing symlink installation target')
        descriptor, temporary = tempfile.mkstemp(dir=target.parent, prefix='.tracker-install-')
        try:
            with os.fdopen(descriptor, 'wb') as handle:
                handle.write(content)
                handle.flush()
                os.fsync(handle.fileno())
            Path(temporary).chmod(mode)
            os.replace(temporary, target)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)
    if legacy_ui.exists():
        legacy_ui.unlink()
    return {name: hashlib.sha256(content).hexdigest() for name, (content, _) in files.items()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--destination', type=Path, default=DESTINATION)
    args = parser.parse_args()
    print(json.dumps(install(args.destination, payloads()), indent=2))


if __name__ == '__main__':
    main()
