#!/usr/bin/env python3
"""Dispatch exact mp to the protected publisher; never archive or auto-commit."""
import argparse
import fcntl
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
import uuid
from datetime import datetime, timezone

PUBLISHER = Path('/Users/ryanudelhoven/.local/share/codex-publish/codex-git')
ENV = {'PATH': '/usr/bin:/bin', 'HOME': str(Path.home()),
       'GIT_CONFIG_NOSYSTEM': '1', 'GIT_CONFIG_GLOBAL': '/dev/null',
       'GIT_CONFIG_COUNT': '0', 'GIT_NO_REPLACE_OBJECTS': '1',
       'GIT_TERMINAL_PROMPT': '0'}
UUID = re.compile(r'[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}')
BRANCH = re.compile(r'codex/[a-z0-9]+(?:[-/][a-z0-9]+)*')


class NeedsPreparation(ValueError):
    """Expected implementation work, not a failed publication."""


def git(cwd, *args):
    result = subprocess.run(
        ['/usr/bin/git', '-c', 'core.hooksPath=/dev/null',
         '-c', 'core.fsmonitor=false', '-C', str(cwd), *args],
        env=ENV, text=True, capture_output=True, timeout=15,
    )
    if result.returncode:
        raise ValueError('Git inspection failed; check the checkout and branch.')
    return result.stdout.strip()


def identity(cwd, session):
    if not isinstance(cwd, str) or not Path(cwd).is_absolute():
        raise ValueError('The hook needs an absolute working directory.')
    if not isinstance(session, str) or not UUID.fullmatch(session):
        raise ValueError('The hook needs a verified Codex session UUID.')
    repo = Path(git(cwd, 'rev-parse', '--show-toplevel')).resolve()
    branch = git(repo, 'rev-parse', '--abbrev-ref', 'HEAD')
    if not BRANCH.fullmatch(branch):
        raise ValueError('mp needs a checked-out codex/ feature branch; main and detached HEAD are refused.')
    common = Path(git(repo, 'rev-parse', '--path-format=absolute', '--git-common-dir'))
    return repo, branch, common


def publisher(action, repo, branch, session, expected_source=None):
    command = [str(PUBLISHER), action, str(repo), branch, session]
    if expected_source is not None:
        command += ['--expected-source', expected_source]
    result = subprocess.run(
        command,
        env=ENV, text=True, capture_output=True, timeout=180,
    )
    if result.returncode:
        # The protected helper emits bounded diagnostics, not detected secret values.
        detail = (result.stderr or result.stdout).strip()[-700:]
        raise ValueError('Protected publisher stopped: ' + (detail or 'check its result before retrying.'))
    return json.loads(result.stdout)


def snapshot(repo, branch, session):
    if git(repo, 'status', '--porcelain', '--untracked-files=all'):
        raise NeedsPreparation('The task has uncommitted changes.')
    info = publisher('inspect', repo, branch, session)
    if info.get('branch') != branch or info.get('head') != info.get('feature'):
        raise ValueError('The checkout no longer matches the requested feature branch.')
    record = info.get('tracking', {}).get('record') or {}
    if record.get('closed') or not any(
        p.get('source') == 'codex' and p.get('threadId') == session
        and p.get('hostId', 'local') == 'local'
        for p in record.get('participants', [])
    ):
        raise NeedsPreparation('This chat needs branch participation registration.')
    return {'repository': str(repo), 'branch': branch, 'session_id': session,
            'head': info['head'], 'lifecycle_id': record['id']}


def ready_path(common, session):
    return common / 'codex-publish' / ('mp-ready-' + session + '.json')


def request_path(common, session):
    return common / 'codex-publish' / ('mp-request-' + session + '.json')


def write_record(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(value, indent=2) + '\n')
    os.chmod(temporary, 0o600)
    temporary.replace(path)


def request_preparation(event, reason):
    repo, branch, common = identity(event.get('cwd'), event.get('session_id'))
    session = event['session_id']
    request = {'repository': str(repo), 'branch': branch, 'session_id': session,
               'head': git(repo, 'rev-parse', 'HEAD'), 'request_id': str(uuid.uuid4()),
               'requested_at': datetime.now(timezone.utc).isoformat()}
    write_record(request_path(common, session), request)
    context = (
        'The user issued exact mp, authorizing ONE finish-and-publish pass for '
        + json.dumps(str(repo)) + ' on ' + branch + '. Preparation is needed: '
        + str(reason) + ' Review task changes and preserve unrelated work. Reuse '
        'valid checks, run outstanding required gates, fix in-scope failures, and '
        'stage/commit only reviewed task files with a descriptive message. '
        'Register this chat on the branch if needed without claiming historical '
        'creation. Do not ask the user for a separate commit or preparation command. '
        'Stop and report real blockers, ambiguous scope, or denied execution access. '
        'After checks and committing, run python3 ' + shlex.quote(str(Path(__file__).resolve()))
        + ' --complete --cwd ' + shlex.quote(str(repo)) + ' --session ' + session
        + ' --request ' + request['request_id']
        + " --check 'actual successful check command' (repeat --check as needed). "
        'Use normal execution permissions. This records readiness and invokes '
        'protected publication for this request. Do not call raw publication or '
        'retry a partial publication blindly. Report the result and leave the chat '
        'open. This authorization is scoped to this repository/branch and expires '
        'on a new user message or after 30 minutes; it does not authorize other work.'
    )
    return {'hookSpecificOutput': {'hookEventName': 'UserPromptSubmit',
                                  'additionalContext': context}}


def complete(cwd, session, request_id, checks):
    repo, branch, common = identity(cwd, session)
    path = request_path(common, session)
    if not path.exists():
        raise ValueError('No pending mp request; the user must issue mp first.')
    request = json.loads(path.read_text())
    if (not isinstance(request_id, str) or not UUID.fullmatch(request_id)
            or request.get('request_id') != request_id
            or request.get('repository') != str(repo)
            or request.get('branch') != branch
            or request.get('session_id') != session):
        raise ValueError('The pending mp request does not match this chat and branch.')
    age = (datetime.now(timezone.utc) - datetime.fromisoformat(request['requested_at'])).total_seconds()
    if age < 0 or age > 1800:
        path.unlink()
        raise ValueError('The mp request expired; ask the user to issue mp again.')
    # Preparation may add commits, but must not replace the requested branch history.
    git(repo, 'merge-base', '--is-ancestor', request['head'], 'HEAD')
    prepare(cwd, session, checks)
    # A new user message may have arrived while the final snapshot was read.
    if not path.exists() or json.loads(path.read_text()).get('request_id') != request_id:
        raise ValueError('The pending mp request was cancelled or replaced during preparation.')
    path.unlink()
    return {'completed': True, 'message': publish(cwd, session)}


def cancel_pending(event):
    """Any later user message revokes an unfinished preparation request."""
    session, cwd = event.get('session_id'), event.get('cwd')
    if not isinstance(session, str) or not UUID.fullmatch(session) or not isinstance(cwd, str):
        return
    try:
        common = Path(git(cwd, 'rev-parse', '--path-format=absolute', '--git-common-dir'))
        request_path(common, session).unlink(missing_ok=True)
    except (ValueError, OSError, subprocess.SubprocessError):
        pass


def prepare(cwd, session, checks):
    """Record a completed review/check handoff; does not run checks or publish."""
    if not checks or not all(isinstance(c, str) and c.strip() for c in checks):
        raise ValueError('Record the actual successful checks; preparation does not run them.')
    repo, branch, common = identity(cwd, session)
    info = snapshot(repo, branch, session)
    path = ready_path(common, session)
    info.update(checks=checks, prepared_at=datetime.now(timezone.utc).isoformat())
    write_record(path, info)
    return {'ready': True, 'branch': branch, 'head': info['head'], 'record': str(path)}


def publish(cwd, session):
    repo, branch, common = identity(cwd, session)
    directory = common / 'codex-publish'
    directory.mkdir(parents=True, exist_ok=True)
    with (directory / 'mp-command.lock').open('a') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise ValueError('Another mp is running for this repository.')
        # Re-read after locking; another chat may have switched branches.
        current_repo, current_branch, _ = identity(cwd, session)
        if current_repo != repo or current_branch != branch:
            raise ValueError('The checkout changed while mp was starting.')
        current = snapshot(repo, branch, session)
        path = ready_path(common, session)
        if not path.exists():
            raise NeedsPreparation('The task needs final review and a verified-ready record.')
        ready = json.loads(path.read_text())
        if not ready.get('checks') or any(ready.get(k) != v for k, v in current.items()):
            raise NeedsPreparation('Branch, commit, or chat lifecycle changed since verification; prepare again.')
        # Single-use handoff. A partial/failed publication requires deliberate recovery.
        path.unlink()
        result = publisher('publish', repo, branch, session, expected_source=current['head'])
        if result.get('branch') != branch or result.get('source') != current['head'] or result.get('published') != current['head']:
            raise ValueError('Publication receipt differs from the prepared commit; inspect state before retrying.')
        cleanup = result.get('cleanup', [])
        if 'local feature deleted' not in cleanup or any('retained' in step for step in cleanup):
            raise ValueError('Publication returned incomplete cleanup; inspect the protected receipt.')
        publisher('finish', repo, branch, session)
        return 'Merged ' + branch + ' into main, pushed, and cleaned up the branch. Chat remains open.'


def handle(event):
    if not isinstance(event, dict) or event.get('hook_event_name') != 'UserPromptSubmit':
        return None
    prompt = event.get('prompt')
    cancel_pending(event)
    if not isinstance(prompt, str) or prompt.strip() != 'mp':
        return None
    try:
        reason = publish(event.get('cwd'), event.get('session_id'))
    except NeedsPreparation as error:
        try:
            return request_preparation(event, error)
        except (ValueError, OSError, KeyError, TypeError, subprocess.SubprocessError) as failure:
            reason = 'mp could not start preparation: ' + str(failure)[:900]
    except (ValueError, OSError, KeyError, TypeError, subprocess.SubprocessError) as error:
        reason = 'mp stopped: ' + str(error)[:900] + ' No assistant fallback will run; chat remains open.'
    # Ready publication and operational failures are consumed. Only preparation
    # deliberately reaches the model, with a single scoped completion request.
    return {'decision': 'block', 'reason': reason}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--prepare', action='store_true')
    mode.add_argument('--complete', action='store_true')
    parser.add_argument('--cwd')
    parser.add_argument('--session')
    parser.add_argument('--request')
    parser.add_argument('--check', action='append', default=[])
    args = parser.parse_args(argv)
    if args.prepare or args.complete:
        try:
            if args.complete:
                result = complete(args.cwd, args.session, args.request, args.check)
            else:
                result = prepare(args.cwd, args.session, args.check)
            print(json.dumps(result))
        except (ValueError, OSError, KeyError, TypeError, subprocess.SubprocessError) as error:
            parser.exit(1, 'mp handoff stopped: ' + str(error) + '\n')
        return
    try:
        result = handle(json.load(sys.stdin))
    except (ValueError, OSError):
        return
    if result is not None:
        print(json.dumps(result))


if __name__ == '__main__':
    main()
