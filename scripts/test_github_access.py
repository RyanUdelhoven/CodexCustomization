"""Live-read invariants using local bare remotes; no GitHub writes or network."""
import contextlib
import io
import json
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch

import test_codex_git as support

MODULE, git = support.MODULE, support.git


class RemoteReads(unittest.TestCase):
    setUp = support.PublicationTests.setUp

    def test_reads_allow_dirty_checkout_and_preserve_every_ref_and_user_file(self):
        (self.repo / 'draft').write_text('preserve')
        before = git('show-ref', cwd=self.repo)
        remote = git('show-ref', cwd=self.remote)
        with patch.object(self.publisher, 'publish') as publish, patch.object(self.publisher, 'tracking') as tracking:
            result = self.publisher.remote_read('remote-branches')
            tip = self.publisher.remote_read('remote-tip', 'main')
            publish.assert_not_called()
            tracking.assert_not_called()
        self.assertEqual(result['branches']['main'], tip['tip'])
        self.assertFalse(result['publication'])
        self.assertEqual(result['remote_state'], 'live')
        self.assertEqual(before, git('show-ref', cwd=self.repo))
        self.assertEqual(remote, git('show-ref', cwd=self.remote))
        self.assertEqual((self.repo / 'draft').read_text(), 'preserve')
        self.assertFalse((self.repo / '.git/FETCH_HEAD').exists())

    def test_missing_live_branch_is_not_confused_with_stale_tracking_ref(self):
        cached = git('rev-parse', 'refs/remotes/origin/codex/example', cwd=self.repo)
        git('push', 'origin', ':codex/example', cwd=self.repo)
        git('update-ref', 'refs/remotes/origin/codex/example', cached, cwd=self.repo)
        result = self.publisher.remote_read('remote-tip', 'codex/example')
        self.assertFalse(result['exists'])
        self.assertIsNone(result['tip'])
        self.assertEqual(result['cached_tip'], cached)

    def test_fetch_only_objects_and_fetch_head_without_tracking_or_checkout_changes(self):
        before = git('show-ref', cwd=self.repo)
        remote_before = git('show-ref', cwd=self.remote)
        (self.repo / 'draft').write_text('preserve')
        result = self.publisher.remote_read('fetch-ref', 'main')
        self.assertEqual(result['tip'], git('rev-parse', 'main', cwd=self.remote))
        self.assertEqual(result['tip'], git('rev-parse', 'FETCH_HEAD', cwd=self.repo))
        self.assertEqual(before, git('show-ref', cwd=self.repo))
        self.assertEqual(remote_before, git('show-ref', cwd=self.remote))
        self.assertEqual(git('symbolic-ref', '--short', 'HEAD', cwd=self.repo), 'codex/example')
        self.assertEqual((self.repo / 'draft').read_text(), 'preserve')
        self.assertFalse((self.repo / '.git/codex-publish').exists())

    def test_unsafe_branch_inputs_fail_before_destination_or_network(self):
        for name in ('--upload-pack=evil', 'main:refs/heads/main', 'main~1', 'refs/heads/main',
                     '../main', 'a//b', 'a/.b', 'a/b.lock', 'a/', 'a*', 'a\\b', 'a@{1}', 'a'*241):
            with self.subTest(name=name), patch.object(self.publisher, 'validate_destination') as validate:
                with self.assertRaises(ValueError):
                    self.publisher.remote_read('fetch-ref', name)
                validate.assert_not_called()

    def test_untrusted_destination_config_stops_before_network(self):
        for key, value in [('url.https://evil.example/.insteadOf','https://github.com/'),
                           ('include.path','/tmp/unreviewed-config'),
                           ('http.proxy','https://evil.example'),('http.sslVerify','false'),
                           ('remote.origin.uploadpack','evil'),('credential.helper','!evil'),
                           ('core.alternateRefsCommand','evil')]:
            with self.subTest(key=key):
                git('config', key, value, cwd=self.repo)
                with self.assertRaisesRegex(ValueError, 'manual review'):
                    self.publisher.remote_read('remote-branches')
                git('config', '--unset', key, cwd=self.repo)

    def test_api_read_uses_only_fixed_get_endpoints_and_checks_account(self):
        self.publisher.url = 'https://github.com/RyanUdelhoven/Test.git'
        with patch.object(self.publisher, 'validate_destination'), patch.object(self.publisher, 'api', side_effect=[
                {'login':'RyanUdelhoven'}, {'default_branch':'main'}]) as api:
            result = self.publisher.remote_read('remote-info')
        self.assertEqual(result['account'], 'RyanUdelhoven')
        self.assertEqual([c.args for c in api.call_args_list], [('user',), ('repos/RyanUdelhoven/Test',)])
        with patch.object(self.publisher, 'validate_destination'), patch.object(self.publisher, 'api', return_value={'login':'Other'}) as api:
            with self.assertRaisesRegex(ValueError, 'account'):
                self.publisher.remote_read('remote-info')
            self.assertEqual(api.call_count, 1)

    def test_cli_read_needs_no_feature_or_chat_and_rejects_extra_authority(self):
        main = MODULE['main']
        with patch.dict(main.__globals__, resolve_repository=lambda _: (self.repo, str(self.remote)),
                        Publisher=lambda *_: self.publisher), contextlib.redirect_stdout(io.StringIO()) as out:
            main(['remote-branches', str(self.repo)])
            self.assertFalse(json.loads(out.getvalue())['publication'])
            for args in (['remote-info',str(self.repo),'--method','POST'],
                         ['remote-tip',str(self.repo),'main','--force'],
                         ['fetch-ref',str(self.repo),'main','--request','anything']):
                with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                    main(args)


class ErrorClassification(unittest.TestCase):
    def test_policy_auth_visibility_missing_ref_and_connectivity_stay_distinct(self):
        for message, category in [
            ('Network access to github.com was blocked: domain is not on the allowlist', 'network-policy'),
            ('CONNECT tunnel failed, response 403','network-policy'),
            ('HTTP 401 Bad credentials','authentication'),
            ('Authentication failed','authentication'),
            ("fatal: couldn't find remote ref missing",'missing-ref'),
            ('HTTP 403 Resource not accessible','authorization-or-visibility'),
            ('Repository not found','authorization-or-visibility'),
            ('error connecting to api.github.com','connectivity'),
            ('other failure','operation-failed')]:
            with self.subTest(message=message):
                self.assertEqual(MODULE['failure_kind'](message), category)

    def test_failure_is_classified_without_retries(self):
        run = MODULE['run']
        with patch('subprocess.run', return_value=subprocess.CompletedProcess([],1,'','CONNECT tunnel failed, response 403')) as command:
            with self.assertRaisesRegex(ValueError, r'\[network-policy\]'):
                run(['/usr/bin/git','ls-remote'], Path('/tmp'))
            self.assertEqual(command.call_count,1)


if __name__ == '__main__':
    unittest.main()
