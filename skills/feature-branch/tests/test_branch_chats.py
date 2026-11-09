import json
from pathlib import Path
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor

SCRIPT = str(Path(__file__).resolve().parents[1] / 'scripts' / 'branch_chats.py')

def run(*args):
    return subprocess.check_output(args, text=True, stderr=subprocess.STDOUT).strip()

with tempfile.TemporaryDirectory() as temporary:
    repo = str(Path(temporary) / 'repo')
    run('git', 'init', '-b', 'main', repo)
    run('git', '-C', repo, '-c', 'user.name=Test', '-c', 'user.email=test@example.com', 'commit', '--allow-empty', '-m', 'initial')
    def helper(action, branch='codex/example', chat=None, created=False, checkout=repo):
        args = ['python3', SCRIPT, action, '--repo', checkout, '--branch', branch]
        if chat:
            args += ['--chat-id', chat]
        if created:
            args += ['--created']
        return json.loads(run(*args))
    run('git', '-C', repo, 'branch', 'codex/example')
    assert not helper('inspect')['single_chat_candidate']
    assert helper('register', chat='origin', created=True)['single_chat_candidate']
    assert helper('register', chat='origin')['single_chat_candidate']
    worktree = str(Path(temporary) / 'worktree')
    run('git', '-C', repo, 'worktree', 'add', worktree, 'codex/example')
    assert helper('inspect', checkout=worktree)['single_chat_candidate']
    with ThreadPoolExecutor() as executor:
        list(executor.map(lambda chat: helper('register', chat=chat), ['other', 'third', 'other']))
    record = helper('inspect', checkout=worktree)
    assert not record['single_chat_candidate']
    assert len(record['record']['participants']) == 3
    try:
        helper('register', chat='origin', created=True)
        raise AssertionError('overwrote open lifecycle')
    except subprocess.CalledProcessError:
        pass
    assert not helper('close')['single_chat_candidate']
    assert not helper('register', chat='origin')['single_chat_candidate']
    helper('close')
    assert helper('register', chat='new-origin', created=True)['single_chat_candidate']
    run('git', '-C', repo, 'branch', 'codex/legacy')
    assert not helper('register', branch='codex/legacy', chat='origin')['single_chat_candidate']
    common = Path(run('git', '-C', repo, 'rev-parse', '--path-format=absolute', '--git-common-dir'))
    for record_file in (common / 'codex-branch-chats').glob('*.json'):
        record_file.write_text('invalid json')
    try:
        helper('inspect')
        raise AssertionError('accepted malformed record')
    except subprocess.CalledProcessError as error:
        assert 'skip archival' in error.output
    print('PASS: single chat, duplicate registration, shared worktrees, concurrent participants, open lifecycle protection, closed/reused branch, legacy history, malformed records')
