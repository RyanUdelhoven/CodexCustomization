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
BRANCH = re.compile(r'[A-Za-z0-9][A-Za-z0-9._/-]*')


def feature_branch(branch):
    return (isinstance(branch, str) and bool(BRANCH.fullmatch(branch))
            and branch not in ('main', 'master') and not branch.startswith('refs/')
            and len(branch) <= 240 and not any(x in branch for x in ('..', '//'))
            and not branch.endswith('/')
            and all(not p.startswith('.') and not p.endswith(('.', '.lock')) for p in branch.split('/')))



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
    if not feature_branch(branch):
        raise ValueError('mp needs a checked-out feature branch; main and detached HEAD are refused.')
    common = Path(git(repo, 'rev-parse', '--path-format=absolute', '--git-common-dir'))
    return repo, branch, common


def publisher(action, repo, branch, session, expected_source=None, expected_remote=None):
    command = [str(PUBLISHER), action, str(repo), branch, session]
    if expected_source is not None:
        command += ['--expected-source', expected_source]
    if expected_remote is not None:
        command += ['--expected-remote', expected_remote]
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
    if info.get('publication_workflow') != 'github-pr-merge-v1':
        raise ValueError('Installed publisher lacks the PR workflow; install the reviewed publisher before mp.')
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


def project_inventory(cwd, session):
    """Snapshot local branches only. Never switch, commit, fetch, or publish here."""
    if not isinstance(cwd, str) or not Path(cwd).is_absolute() or not isinstance(session, str) or not UUID.fullmatch(session):
        raise ValueError('mp needs an absolute checkout and verified chat UUID.')
    repo = Path(git(cwd, 'rev-parse', '--show-toplevel')).resolve()
    common = Path(git(repo, 'rev-parse', '--path-format=absolute', '--git-common-dir')).resolve()
    worktrees = []
    for block in git(repo, 'worktree', 'list', '--porcelain').split('\n\n'):
        lines = block.splitlines()
        location = next((line[9:] for line in lines if line.startswith('worktree ')), None)
        branch = next((line[18:] for line in lines if line.startswith('branch refs/heads/')), None)
        if location:
            worktrees.append({'path': str(Path(location).resolve()), 'branch': branch})
    coordinator = worktrees[0]['path'] if worktrees else str(repo)
    current = git(repo, 'rev-parse', '--abbrev-ref', 'HEAD')
    if current == 'HEAD' and git(repo, 'status', '--porcelain', '--untracked-files=all'):
        raise ValueError('Detached checkout has changes; assign them to a feature branch before mp.')
    for tree in worktrees:
        if tree['branch'] in ('main', 'master') and git(tree['path'], 'status', '--porcelain', '--untracked-files=all'):
            raise ValueError('Primary checkout has uncommitted changes; assign them to their feature branch before mp.')
    branches = []
    for row in git(repo, 'for-each-ref', '--format=%(refname:short) %(objectname)', 'refs/heads/').splitlines():
        branch, head = row.split()
        if branch in ('main', 'master'):
            continue
        if not feature_branch(branch):
            raise ValueError('Local branch needs manual review before mp: ' + branch)
        checkout = next((t['path'] for t in worktrees if t['branch'] == branch), None)
        branches.append({'branch': branch, 'head': head, 'checkout': checkout, 'status': 'pending'})
    branches.sort(key=lambda item: (item['branch'] != current, item['branch']))
    return {'repository': coordinator, 'common': str(common), 'branches': branches, 'worktrees': worktrees}


def request_project(event, inventory):
    session = event['session_id']
    common = Path(inventory['common'])
    request = dict(inventory, scope='project-all-branches-v2', remote_discovery='pending', session_id=session,
                   request_id=str(uuid.uuid4()), requested_at=datetime.now(timezone.utc).isoformat())
    write_record(request_path(common, session), request)
    context = (
        'Exact mp authorizes the project-wide local AND remote feature-branch cycle, not just the current task. '
        'The initial local branch/worktree plan is ' + json.dumps(inventory) + '. '
        'Review and commit ALL pending project changes in each owning feature checkout; '
        'do not move dirty files between branches or collect every change into the current branch. '
        'Use descriptive separate commits for distinct work. Primary/default branches are targets only. '
        'Before any publication, invoke the installed protected helper directly with literal arguments: '
        + shlex.quote(str(PUBLISHER)) + ' plan-project ' + shlex.quote(inventory['repository'])
        + ' ' + session + ' --request ' + request['request_id'] + '. '
        'This adds live remote-only branches and freezes their exact tips. Use its returned final plan. '
        'Fetch all remote-only heads before any publication. For each remote-only branch, use protected fetch-ref, require the returned SHA to equal '
        'its frozen head, and restore that existing branch locally at that exact SHA. '
        'This restores remote history; it is not creation of a new implementation branch from main. '
        'Branches created after the finalized snapshot are excluded. '
        'Prepare existing linked worktrees first; detach only reviewed clean idle feature worktrees '
        'when needed, and never disrupt active work. Use the primary checkout at '
        + json.dumps(inventory['repository']) + ' as publication coordinator. '
        'Process every listed branch individually, ancestors before dependents. '
        'First compare each source tip with live published main and inspect pending work; '
        'integrated clean branches need verified cleanup only. Before each necessary merge, '
        'bring verified published main into that branch with a normal merge if needed and run '
        'affected required checks. Preserve commits; never squash branches together or force-push. '
        'Register this chat on each branch without claiming creation. Write each branch’s actual '
        'successful check commands as an inert JSON array to a branch-specific /tmp file. '
        'Then invoke the protected executable directly with literal arguments: '
        + shlex.quote(str(PUBLISHER)) + ' complete ' + shlex.quote(inventory['repository'])
        + ' BRANCH ' + session + ' --request ' + request['request_id']
        + ' --checks-file /tmp/BRANCH-CHECKS.json. Substitute one frozen branch and its check file. '
        'Use the returned remaining list; each completion publishes one PR merge and cleans that '
        'branch only. An already-integrated branch needs verified cleanup through the same handoff, '
        'not an empty commit/PR. Do not ask for separate commit or mp commands between branches. '
        'Investigate merge conflicts using the base, both sides, and relevant tests. '
        'Ask focused behavior questions before resolving disputed behavior, state the named '
        'remaining branches will continue publication after a selected resolution, then '
        'apply answers and check the result. Follow '
        'rules/merge-push.md#integration-and-conflict-resolution for deliberate continuation '
        'under the answer if it cancels this token; never replay it. Stop publication for '
        'unresolved choices, failed checks, changed remote tips, pending reviews, ambiguous '
        'ownership, active worktrees, or denied access; report completed and remaining branches. '
        'Never blindly retry a partial publication. New user input cancels the pending plan; it '
        'expires after 30 minutes. Keep chats open. Configuring this behavior does not publish it.'
    )
    return {'hookSpecificOutput': {'hookEventName': 'UserPromptSubmit', 'additionalContext': context}}


def extend_project(cwd, session, request_id, remote_heads):
    """Called only by the installed protected planner after live fixed-origin reads."""
    # Planning is allowed from main; it does not switch branches or fetch objects.
    inventory = project_inventory(cwd, session)
    common = Path(inventory['common'])
    path = request_path(common, session)
    if not path.exists():
        raise ValueError('No pending mp project request.')
    request = json.loads(path.read_text())
    if (request.get('scope') != 'project-all-branches-v2' or request.get('request_id') != request_id
            or request.get('session_id') != session or request.get('repository') != str(Path(cwd).resolve())
            or request.get('common') != str(common)):
        raise ValueError('Pending project request does not match the coordinator and chat.')
    age = (datetime.now(timezone.utc) - datetime.fromisoformat(request['requested_at'])).total_seconds()
    if not 0 <= age <= 1800:
        path.unlink()
        raise ValueError('The mp request expired; issue mp again.')
    if request.get('remote_discovery') == 'complete':
        return request
    if any(item['status'] != 'pending' for item in request['branches']):
        raise ValueError('Cannot change project scope after publication starts.')
    # Refuse unsupported refs before freezing any remote scope or doing mutations.
    for name, tip in remote_heads.items():
        if name not in ('main', 'master') and (not feature_branch(name) or not re.fullmatch(r'[0-9a-f]{40}', tip)):
            raise ValueError('Remote branch needs manual review: ' + name)
    local = {item['branch']: item for item in request['branches']}
    for name, tip in remote_heads.items():
        if name in ('main', 'master'):
            continue
        if name not in local:
            local[name] = {'branch': name, 'head': tip, 'checkout': None,
                           'status': 'pending', 'remote_only': True}
    for name, item in local.items():
        item['remote_tip'] = remote_heads.get(name)
    request['branches'] = list(local.values())
    request['remote_discovery'] = 'complete'
    # New user input during discovery must not recreate a cancelled request.
    if not path.exists() or json.loads(path.read_text()).get('request_id') != request_id:
        raise ValueError('The project request was cancelled during live discovery.')
    write_record(path, request)
    return request


def complete(cwd, session, request_id, checks):
    _, _, common = identity(cwd, session)
    directory = common / 'codex-publish'
    directory.mkdir(parents=True, exist_ok=True)
    with (directory / 'mp-handoff.lock').open('a') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise ValueError('Another mp completion is running for this repository.')
        return _complete(cwd, session, request_id, checks)


def _complete(cwd, session, request_id, checks):
    repo, branch, common = identity(cwd, session)
    path = request_path(common, session)
    if not path.exists():
        raise ValueError('No pending mp request; the user must issue mp first.')
    request = json.loads(path.read_text())
    if (not isinstance(request_id, str) or not UUID.fullmatch(request_id)
            or request.get('request_id') != request_id
            or request.get('repository') != str(repo)
            or (request.get('scope') != 'project-all-branches-v2' and request.get('branch') != branch)
            or request.get('session_id') != session):
        raise ValueError('The pending mp request does not match this chat and branch.')
    age = (datetime.now(timezone.utc) - datetime.fromisoformat(request['requested_at'])).total_seconds()
    if age < 0 or age > 1800:
        path.unlink()
        raise ValueError('The mp request expired; ask the user to issue mp again.')
    project = request.get('scope') == 'project-all-branches-v2'
    entry = None
    if project:
        if request.get('remote_discovery') != 'complete':
            raise ValueError('Complete protected live remote discovery before publishing any branch.')
        if request.get('common') != str(common.resolve()) or any(item['status'] == 'publishing' for item in request['branches']):
            raise ValueError('Project cycle has a partial publication; inspect state and issue a new mp.')
        entry = next((item for item in request['branches'] if item['branch'] == branch), None)
        if entry is None or entry['status'] != 'pending':
            raise ValueError('Branch is not pending in this frozen mp plan.')
        for other in request['branches']:
            if other['status'] != 'pending' or other['branch'] == branch:
                continue
            git(repo, 'cat-file', '-e', other['head'] + '^{commit}')
            if other['head'] != entry['head'] and git(repo, 'rev-list', '--count', entry['head'] + '..' + other['head']) == '0':
                raise ValueError('Publish ancestor branch first: ' + other['branch'])
    # Preparation may add commits, but must not replace the requested branch history.
    git(repo, 'merge-base', '--is-ancestor', entry['head'] if project else request['head'], 'HEAD')
    prepare(cwd, session, checks)
    # A new user message may have arrived while the final snapshot was read.
    if not path.exists() or json.loads(path.read_text()).get('request_id') != request_id:
        raise ValueError('The pending mp request was cancelled or replaced during preparation.')
    if not project:
        path.unlink()
        return {'completed': True, 'message': publish(cwd, session)}
    # Persist single-use state before any network mutation. Failures cannot replay it.
    entry['status'] = 'publishing'
    write_record(path, request)
    message = publish(cwd, session, expected_remote=entry['remote_tip'] or 'absent')
    entry['status'], entry['message'] = 'completed', message
    remaining = [item['branch'] for item in request['branches'] if item['status'] == 'pending']
    if not path.exists() or json.loads(path.read_text()).get('request_id') != request_id:
        return {'completed': True, 'message': message, 'remaining': remaining, 'cancelled': True}
    if remaining:
        write_record(path, request)
    else:
        path.unlink()
    return {'completed': True, 'message': message, 'remaining': remaining, 'project_completed': not remaining}


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


def publish(cwd, session, expected_remote=None):
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
        remote_args = {'expected_remote': expected_remote} if expected_remote is not None else {}
        result = publisher('publish', repo, branch, session, expected_source=current['head'], **remote_args)
        if (result.get('branch') != branch or result.get('source') != current['head']
                or (not result.get('already_integrated') and (not result.get('source_preserved')
                    or not result.get('merge_commit') or not result.get('pull_request')))):
            raise ValueError('Publication receipt differs from the prepared commit; inspect state before retrying.')
        cleanup = result.get('cleanup', [])
        if 'local feature deleted' not in cleanup or any('retained' in step for step in cleanup):
            raise ValueError('Publication returned incomplete cleanup; inspect the protected receipt.')
        publisher('finish', repo, branch, session)
        if result.get('already_integrated'):
            return 'Verified ' + branch + ' was already in published main and cleaned up the branch. Chat remains open.'
        return 'Merged ' + branch + ' through ' + result['pull_request'] + ' into main, preserved commits, and cleaned up the branch. Chat remains open.'


def handle(event):
    if not isinstance(event, dict) or event.get('hook_event_name') != 'UserPromptSubmit':
        return None
    prompt = event.get('prompt')
    cancel_pending(event)
    if not isinstance(prompt, str) or prompt.strip() != 'mp':
        return None
    try:
        inventory = project_inventory(event.get('cwd'), event.get('session_id'))
        return request_project(event, inventory)
    except (ValueError, OSError, KeyError, TypeError, subprocess.SubprocessError) as error:
        reason = 'mp stopped: ' + str(error)[:900] + ' No assistant fallback will run; chat remains open.'
    # Discovery failures are consumed; successful plans reach the assistant.
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
