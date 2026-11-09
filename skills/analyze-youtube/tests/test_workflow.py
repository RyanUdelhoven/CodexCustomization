import contextlib
import fcntl
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import time
import unittest
from unittest.mock import patch
from urllib.error import HTTPError, URLError

sys.path.insert(0, str(Path(__file__).parents[1] / 'scripts'))
import workflow as w

ID = 'dQw4w9WgXcQ'


class WorkspaceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root_patch = patch.object(w, 'ROOT', Path(self.temp.name) / 'runs')
        self.root_patch.start()
        self.addCleanup(self.root_patch.stop)

    def fixture(self):
        run = w.create()
        texts = ['The problem is wasted time.', 'Thanks to ACME for sponsoring.',
                 'Use my link for a discount.', 'Back to the solution.',
                 'Acme also made this example.', 'The conclusion follows.']
        w.save(run / 'raw.json', {'video_id': ID, 'source': 'human_captions', 'segments': [
            {'id': i, 'start': i * 10, 'duration': 3, 'text': text} for i, text in enumerate(texts)]})
        return run

    def prepare(self, run):
        w.clean(run, {'sponsors': ['Acme'], 'exclusions': [
            {'segment_ids': [1, 2], 'reason': 'paid promotion'}]})
        outline = [{'id': 's1', 'title': 'Problem', 'segment_ids': [0]},
                   {'id': 's2', 'title': 'Solution', 'segment_ids': [3, 5]}]
        w.sections(run, outline)
        w.notes(run, [{'section_id': 's1', 'analysis': 'Problem definition.', 'evidence_ids': [0]},
                      {'section_id': 's2', 'analysis': 'Solution and conclusion.', 'evidence_ids': [3, 5]}])

    def invoke(self, *args):
        out = io.StringIO()
        with patch.object(sys, 'argv', ['workflow.py', *map(str, args)]), contextlib.redirect_stdout(out):
            code = w.main()
        return code, json.loads(out.getvalue()) if out.getvalue() else None

    def test_strict_mentions_raw_unchanged_and_exact_timestamps(self):
        run = self.fixture()
        original = (run / 'raw.json').read_bytes()
        self.prepare(run)
        self.assertEqual((run / 'raw.json').read_bytes(), original)
        kept = w.load(run / 'clean.json')['segments']
        self.assertEqual([r['id'] for r in kept], [0, 3, 5])
        self.assertEqual([r['start'] for r in kept], [0, 30, 50])
        self.assertEqual(w.verify(run)['coverage'], 'complete')
        w.clean(run, {'sponsors': [], 'exclusions': []})
        self.assertEqual(w.load(run / 'clean.json'), w.load(run / 'raw.json'))
        self.assertFalse((run / 'sections.json').exists())
        self.assertFalse((run / 'section-notes.json').exists())

    def test_reject_missing_duplicate_and_reordered_coverage(self):
        run = self.fixture()
        w.clean(run, {'sponsors': [], 'exclusions': []})
        for ids in ([0, 1], [0, 1, 1, 2, 3, 4, 5], [1, 0, 2, 3, 4, 5]):
            with self.assertRaises(ValueError):
                w.sections(run, [{'id': 's1', 'title': 'x', 'segment_ids': ids}])
        self.prepare(run)
        with self.assertRaises(ValueError):
            w.notes(run, [{'section_id': 's1', 'analysis': 'x', 'evidence_ids': [3]},
                          {'section_id': 's2', 'analysis': 'x', 'evidence_ids': [5]}])

    def test_finish_deletes_all_files_and_abort_needs_no_analysis(self):
        run = self.fixture(); self.prepare(run)
        (run / 'decision-input.json').write_text('sensitive input')
        self.assertEqual(self.invoke('finish', run)[0], 0)
        self.assertFalse(run.exists())
        run = self.fixture()
        self.assertEqual(self.invoke('abort', run)[0], 0)
        self.assertFalse(run.exists())

    def test_finish_refuses_incomplete_analysis_then_abort(self):
        run = self.fixture()
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(self.invoke('finish', run)[0], 1)
        self.assertTrue(run.exists())
        self.invoke('abort', run)
        self.assertFalse(run.exists())

    def test_expiry_preserves_recent_locked_and_unowned_directories(self):
        old = self.fixture(); recent = self.fixture(); busy = self.fixture()
        unknown = w.ROOT / ('run-' + 'a' * 32); unknown.mkdir()
        (unknown / 'manifest.json').write_text('{}')
        for run in (old, busy):
            os.utime(run / 'manifest.json', (time.time() - w.TTL - 1,) * 2)
        with (busy / '.lock').open('a') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            self.assertEqual(w.prune(), 1)
            self.assertTrue(busy.exists())
        self.assertFalse(old.exists())
        self.assertTrue(recent.exists()); self.assertTrue(unknown.exists())
        with w.locked(busy):
            pass
        self.assertEqual(w.prune(), 0)

    def test_arbitrary_path_and_symlink_not_owned(self):
        run = self.fixture()
        outside = Path(self.temp.name) / 'outside'; outside.mkdir()
        with self.assertRaises(ValueError): w.owned(outside)
        link = w.ROOT / ('run-' + 'b' * 32); link.symlink_to(run, target_is_directory=True)
        with self.assertRaises(ValueError): w.owned(link)
        self.assertEqual(w.prune(), 0)
        self.assertTrue(run.exists())
        self.assertEqual(run.stat().st_mode & 0o777, 0o700)
        self.assertEqual((run / 'raw.json').stat().st_mode & 0o777, 0o600)

    def test_sponsorblock_absence_failure_and_hash_filter(self):
        with patch.object(w, 'urlopen', side_effect=HTTPError('url', 404, 'absent', {}, None)):
            self.assertEqual(w.sponsorblock(ID)['status'], 'absent')
        with patch.object(w, 'urlopen', side_effect=URLError('offline')):
            self.assertEqual(w.sponsorblock(ID)['status'], 'unavailable')
        payload = [{'videoID': ID, 'segments': [{'segment': [10, 20], 'category': 'sponsor', 'actionType': 'skip'}]},
                   {'videoID': 'another', 'segments': [{'segment': [0, 999], 'category': 'sponsor', 'actionType': 'skip'}]}]
        with patch.object(w, 'urlopen', return_value=io.StringIO(json.dumps(payload))) as request:
            self.assertEqual(w.sponsorblock(ID)['segments'], [{'start': 10, 'end': 20, 'category': 'sponsor'}])
            self.assertNotIn(ID, request.call_args.args[0].full_url)

    def test_start_success_and_failure_cleanup_and_audio_parent(self):
        with patch.object(w, 'retrieve', return_value={'video_id': ID, 'source': 'human_captions', 'segments': []}) as retrieve, \
                patch.object(w, 'sponsorblock', return_value={'status': 'unavailable', 'segments': []}):
            result = w.start('https://youtu.be/' + ID, ['en'], 'small')
            run = Path(result['run'])
            self.assertEqual(retrieve.call_args.kwargs['audio_parent'], run)
            self.assertTrue((run / 'raw.json').exists())
            self.invoke('abort', run)
        for error in (RuntimeError('retrieval failed'), KeyboardInterrupt()):
            with patch.object(w, 'retrieve', side_effect=error):
                with self.assertRaises(type(error)):
                    w.start('https://youtu.be/' + ID, ['en'], 'small')
            self.assertEqual(list(w.ROOT.iterdir()), [])

    def test_empty_content_and_paged_section_reads(self):
        run = self.fixture(); self.prepare(run)
        page = w.read(run, 'clean', 1, 1, 's2')
        self.assertEqual([r['id'] for r in page['segments']], [5])
        self.assertTrue(page['complete'])
        w.clean(run, {'sponsors': [], 'exclusions': [{'segment_ids': list(range(6)), 'reason': 'all promotional'}]})
        w.sections(run, []); w.notes(run, [])
        self.assertEqual(w.verify(run)['retained_segments'], 0)


if __name__ == '__main__':
    unittest.main()
