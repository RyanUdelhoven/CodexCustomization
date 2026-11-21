"""Project mp scope, per-branch handoffs, and partial-failure behavior without GitHub."""
import json
from pathlib import Path
import unittest
from unittest.mock import patch
import test_mp_command_hook as support

hook, git, CHAT = support.hook, support.git, support.CHAT


class ProjectCycleTests(unittest.TestCase):
    setUp = support.HandoffTests.setUp

    def publisher(self, action, repo, branch, session, expected_source=None, expected_remote=None):
        self.calls.append((action, str(repo), branch, session, expected_source))
        if action == 'inspect':
            head = git(repo, 'rev-parse', 'HEAD')
            return {'publication_workflow': 'github-pr-merge-v1', 'branch': branch,
                    'head': head, 'feature': git(repo, 'rev-parse', 'refs/heads/' + branch),
                    'tracking': {'record': {'id': branch, 'closed': False,
                         'participants': [{'source': 'codex','hostId':'local','threadId':CHAT}]}}}
        if action == 'publish':
            git(repo, 'switch', 'main')
            git(repo, 'merge', '--no-ff', branch, '-m', 'Merge ' + branch)
            git(repo, 'branch', '-d', branch)
            return {'branch':branch,'source':expected_source,'published':git(repo,'rev-parse','HEAD'),
                    'source_preserved':True,'merge_commit':git(repo,'rev-parse','HEAD'),
                    'pull_request':'https://github.com/RyanUdelhoven/Test/pull/' + str(len(self.calls)),
                    'cleanup':['local feature deleted']}
        return {'closed':True}

    def add_second(self):
        (self.repo/'first').write_text('first feature')
        git(self.repo,'add','first');git(self.repo,'commit','-m','first feature')
        git(self.repo,'switch','-c','feature/second','main')
        (self.repo/'second').write_text('second feature')
        git(self.repo,'add','second');git(self.repo,'commit','-m','second feature')
        git(self.repo,'switch','codex/example')

    def request(self, remote_heads=None):
        event={'hook_event_name':'UserPromptSubmit','prompt':'mp','cwd':str(self.repo),'session_id':CHAT}
        response=hook.handle(event)
        path=hook.request_path(self.repo/'.git',CHAT)
        request=json.loads(path.read_text())
        request=hook.extend_project(str(self.repo),CHAT,request['request_id'],remote_heads or {})
        return event,response,path,request

    def test_every_local_branch_gets_separate_verified_completion_and_pr(self):
        self.add_second()
        _,response,path,request=self.request()
        self.assertIn('project-wide',response['hookSpecificOutput']['additionalContext'])
        self.assertEqual({r['branch'] for r in request['branches']},{'codex/example','feature/second'})
        self.assertFalse(any(c[0]=='publish' for c in self.calls))
        first=git(self.repo,'rev-parse','HEAD')
        result=hook.complete(str(self.repo),CHAT,request['request_id'],['first checks'])
        self.assertEqual(result['remaining'],['feature/second'])
        self.assertTrue(path.exists())
        git(self.repo,'switch','feature/second');git(self.repo,'merge','main','-m','Bring in verified main')
        second=git(self.repo,'rev-parse','HEAD')
        result=hook.complete(str(self.repo),CHAT,request['request_id'],['second checks'])
        self.assertTrue(result['project_completed'])
        self.assertFalse(path.exists())
        published=[c for c in self.calls if c[0]=='publish']
        self.assertEqual([(c[2],c[4]) for c in published],[('codex/example',first),('feature/second',second)])
        self.assertEqual(len([c for c in self.calls if c[0]=='finish']),2)
        git(self.repo,'merge-base','--is-ancestor',first,'main')
        git(self.repo,'merge-base','--is-ancestor',second,'main')

    def test_mp_from_main_ignores_stale_remote_tracking_refs_before_live_discovery(self):
        self.add_second();git(self.repo,'switch','main')
        git(self.repo,'update-ref','refs/remotes/origin/remote-only','HEAD')
        _,_,_,request=self.request()
        self.assertEqual({r['branch'] for r in request['branches']},{'codex/example','feature/second'})
        self.assertFalse(any(c[0]=='publish' for c in self.calls))

    def test_new_branch_cannot_join_existing_frozen_authorization(self):
        self.add_second();_,_,_,request=self.request()
        git(self.repo,'switch','-c','feature/unlisted')
        with self.assertRaisesRegex(ValueError,'not pending'):
            hook.complete(str(self.repo),CHAT,request['request_id'],['checks'])
        self.assertFalse(any(c[0]=='publish' for c in self.calls))

    def test_partial_failure_consumes_branch_and_prevents_retry_or_continuation(self):
        self.add_second();_,_,path,request=self.request()
        original=self.publisher
        def failing(action,*args,**kwargs):
            if action=='publish':raise ValueError('simulated partial network failure')
            return original(action,*args,**kwargs)
        with patch.object(hook,'publisher',side_effect=failing):
            with self.assertRaisesRegex(ValueError,'partial network'):
                hook.complete(str(self.repo),CHAT,request['request_id'],['checks'])
        self.assertEqual(json.loads(path.read_text())['branches'][0]['status'],'publishing')
        with self.assertRaisesRegex(ValueError,'partial publication'):
            hook.complete(str(self.repo),CHAT,request['request_id'],['checks'])

    def test_new_user_message_cancels_all_remaining_branches(self):
        self.add_second();event,_,path,request=self.request()
        hook.complete(str(self.repo),CHAT,request['request_id'],['checks'])
        hook.handle(dict(event,prompt='stop and change the design'))
        git(self.repo,'switch','feature/second')
        with self.assertRaisesRegex(ValueError,'No pending'):
            hook.complete(str(self.repo),CHAT,request['request_id'],['checks'])
        self.assertFalse(path.exists())
        self.assertEqual(len([c for c in self.calls if c[0]=='publish']),1)

    def test_dirty_linked_worktree_is_inventoried_without_moving_changes(self):
        self.add_second();other=self.repo/'linked'
        git(self.repo,'worktree','add',str(other),'feature/second')
        (other/'pending').write_text('belongs to second')
        # Ignore the fixture worktree folder in the coordinator's status.
        (self.repo/'.git/info/exclude').write_text('/linked/\n')
        refs=git(self.repo,'show-ref')
        inventory=hook.project_inventory(str(other),CHAT)
        entry=next(x for x in inventory['branches'] if x['branch']=='feature/second')
        self.assertEqual(entry['checkout'],str(other))
        self.assertEqual(inventory['repository'],str(self.repo))
        self.assertEqual((other/'pending').read_text(),'belongs to second')
        self.assertEqual(git(self.repo,'show-ref'),refs)

    def test_dirty_primary_checkout_is_a_real_blocker_not_silently_committed(self):
        self.add_second();git(self.repo,'switch','main');(self.repo/'file').write_text('unassigned')
        with self.assertRaisesRegex(ValueError,'Primary checkout'):
            hook.project_inventory(str(self.repo),CHAT)
        self.assertEqual((self.repo/'file').read_text(),'unassigned')

    def test_live_remote_only_branch_is_frozen_then_restored_at_exact_tip(self):
        git(self.repo,'switch','-c','feature/remote-only','main')
        (self.repo/'remote-file').write_text('remote history')
        git(self.repo,'add','remote-file');git(self.repo,'commit','-m','remote feature')
        tip=git(self.repo,'rev-parse','HEAD')
        git(self.repo,'switch','codex/example');git(self.repo,'branch','-D','feature/remote-only')
        _,_,path,request=self.request({'main':self.head,'feature/remote-only':tip})
        remote=next(x for x in request['branches'] if x['branch']=='feature/remote-only')
        self.assertTrue(remote['remote_only'])
        self.assertEqual(remote['head'],tip)
        self.assertEqual(remote['remote_tip'],tip)
        # Discovery never creates local refs or publishes anything.
        refs=git(self.repo,'for-each-ref','--format=%(refname)','refs/heads/')
        self.assertNotIn('refs/heads/feature/remote-only',refs)
        self.assertFalse(any(c[0]=='publish' for c in self.calls))
        again=hook.extend_project(str(self.repo),CHAT,request['request_id'],{'feature/new':'a'*40})
        self.assertEqual(again['branches'],request['branches'])
        hook.complete(str(self.repo),CHAT,request['request_id'],['local checks'])
        git(self.repo,'switch','-c','feature/remote-only',tip)
        git(self.repo,'merge','main','-m','Bring in verified main')
        result=hook.complete(str(self.repo),CHAT,request['request_id'],['remote branch checks'])
        self.assertTrue(result['project_completed'])

    def test_local_only_inventory_cannot_publish_before_live_remote_discovery(self):
        event={'hook_event_name':'UserPromptSubmit','prompt':'mp','cwd':str(self.repo),'session_id':CHAT}
        hook.handle(event)
        path=hook.request_path(self.repo/'.git',CHAT)
        request=json.loads(path.read_text())
        with self.assertRaisesRegex(ValueError,'live remote discovery'):
            hook.complete(str(self.repo),CHAT,request['request_id'],['checks'])
        self.assertFalse(any(c[0]=='publish' for c in self.calls))

    def test_dependent_branch_cannot_publish_before_its_pending_ancestor(self):
        (self.repo/'first').write_text('first')
        git(self.repo,'add','first');git(self.repo,'commit','-m','ancestor')
        git(self.repo,'switch','-c','feature/dependent')
        (self.repo/'second').write_text('second')
        git(self.repo,'add','second');git(self.repo,'commit','-m','dependent')
        _,_,_,request=self.request()
        with self.assertRaisesRegex(ValueError,'ancestor branch first'):
            hook.complete(str(self.repo),CHAT,request['request_id'],['checks'])
        self.assertFalse(any(c[0]=='publish' for c in self.calls))


if __name__=='__main__':unittest.main()
