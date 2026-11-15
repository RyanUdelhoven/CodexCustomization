import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parents[1] / 'scripts'))
import library as lib
import workflow as w


class LibraryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.original_root = w.ROOT
        self.addCleanup(setattr, w, 'ROOT', self.original_root)
        self.root = lib.setup(Path(self.temp.name) / 'library')
        self.run = w.create()
        w.save(self.run / 'raw.json', {'video_id': 'dQw4w9WgXcQ', 'source': 'human_captions',
            'segments': [{'id': 0, 'start': 12.5, 'duration': 2, 'text': 'The example is limited.'},
                         {'id': 1, 'start': 20, 'duration': 3, 'text': 'Buy ACME today.'}]})
        w.save(self.run / 'sponsorblock.json', {'status': 'unavailable', 'segments': []})
        w.save(self.run / 'provenance.json', {'source': 'human_captions'})
        (self.run / 'brief.md').write_text('Understand the argument.')

    def prepared(self):
        lib.checkpoint(self.run, '01-acquisition', 'Checked identity and acquisition limitations.')
        w.clean(self.run, {'sponsors': ['ACME'], 'exclusions': []})
        w.save(self.run / 'reading-progress.json', {'read_ids': [0, 1]})
        lib.checkpoint(self.run, '02-preparation', 'Read all speech and reviewed promotional boundaries.')
        w.sections(self.run, [{'id': 's1', 'title': 'Example', 'segment_ids': [0]}])
        w.notes(self.run, [{'section_id': 's1', 'analysis': 'Example includes a qualification.', 'evidence_ids': [0]}])
        lib.checkpoint(self.run, '03-extraction', 'Reviewed example and preserved qualification.')

    def claim(self):
        return {'id': 'c1', 'speaker_claim': 'The example is limited.', 'evidence_ids': [0],
            'status': 'unverified', 'safe_statement': 'Speaker presents a limited example.',
            'checked_at': '2026-11-14', 'limitations': 'No external corroboration.', 'sources': []}

    def unit(self):
        return {'id': 'k1', 'title': 'Limited example', 'kind': 'speaker_claim',
            'text': 'Speaker qualifies the example.', 'evidence_ids': [0], 'claim_ids': ['c1'],
            'limitations': 'Unverified speaker assertion.', 'quotes': [{'segment_id': 0, 'text': 'example is limited'}]}

    def complete(self):
        self.prepared()
        lib.claims(self.run, [self.claim()])
        lib.checkpoint(self.run, '04-verification', 'Ledger records absent corroboration explicitly.')
        lib.synthesis(self.run, '# Analysis\nThe example carries a qualification.', [self.unit()])
        lib.checkpoint(self.run, '05-synthesis', 'Reviewed fidelity, uncertainty and standalone retrieval context.')

    def test_resume_export_evidence_and_private_sources(self):
        self.complete()
        self.assertTrue(all(v == 'pass' for v in lib.state(self.run).values()))
        result = lib.export(self.root, self.run)
        exported = Path(result['export'])
        unit = json.loads((exported / 'knowledge.jsonl').read_text())
        self.assertEqual(unit['evidence'][0]['start'], 12.5)
        self.assertIn('&t=12', unit['evidence'][0]['url'])
        self.assertEqual(unit['claims'][0]['status'], 'unverified')
        self.assertNotIn('ACME', ''.join(p.read_text() for p in exported.iterdir()))
        self.assertFalse((exported / 'raw.json').exists())
        self.assertEqual(len(w.load(self.root / 'index.json')), 1)
        self.assertTrue((self.run / 'raw.json').exists())
        self.assertEqual(lib.export(self.root, self.run)['export'], str(exported))

    def test_changed_inputs_block_export_and_retain_revisions(self):
        self.complete()
        first = Path(lib.export(self.root, self.run)['export'])
        lib.synthesis(self.run, '# Revised\nMore qualified assessment.', [self.unit()])
        self.assertEqual(lib.state(self.run)['05-synthesis'], 'stale')
        with self.assertRaises(ValueError): lib.export(self.root, self.run)
        lib.checkpoint(self.run, '05-synthesis', 'Reviewed the revised assessment.')
        second = Path(lib.export(self.root, self.run)['export'])
        self.assertNotEqual(first, second)
        self.assertTrue((first / 'analysis.md').exists())
        self.assertEqual(len(w.load(self.root / 'index.json')), 2)
        (self.run / 'brief.md').write_text('A different question')
        self.assertTrue(all(v == 'stale' for v in lib.state(self.run).values()))

    def test_fabricated_quotes_and_certainty_rejected(self):
        self.prepared(); lib.claims(self.run, [self.claim()])
        unit = self.unit(); unit['quotes'][0]['text'] = 'The example is unlimited.'
        with self.assertRaises(ValueError): lib.synthesis(self.run, 'Report', [unit])
        unit = self.unit(); unit['kind'] = 'verified_fact'
        with self.assertRaises(ValueError): lib.synthesis(self.run, 'Report', [unit])
        claim = self.claim(); claim['status'] = 'verified'
        with self.assertRaises(ValueError): lib.claims(self.run, [claim])

    def test_missing_stage_read_coverage_and_failure_stop(self):
        with self.assertRaises(ValueError): lib.checkpoint(self.run, '03-extraction', 'reviewed')
        lib.checkpoint(self.run, '01-acquisition', 'reviewed source')
        w.clean(self.run, {'sponsors': ['ACME'], 'exclusions': []})
        w.save(self.run / 'reading-progress.json', {'read_ids': [0]})
        with self.assertRaises(ValueError): lib.checkpoint(self.run, '02-preparation', 'reviewed')
        (self.run / '01-acquisition/check.md').write_text('fail: wrong source\n')
        self.assertEqual(lib.state(self.run)['01-acquisition'], 'stale')

    def test_explicit_storage_and_corrupt_exports_not_indexed(self):
        for bad in (Path.home() / '.codex/private-library', Path.home() / 'Documents/Notes/research'):
            with self.assertRaises(ValueError): lib.setup(bad)
        self.complete(); exported = Path(lib.export(self.root, self.run)['export'])
        (exported / 'analysis.md').write_text('corrupted')
        lib.reindex(self.root)
        self.assertEqual(w.load(self.root / 'index.json'), [])

    def test_cli_checked_pipeline_and_resume(self):
        import contextlib
        import io
        def invoke(*args):
            out = io.StringIO()
            with patch.object(sys, 'argv', ['library.py', '--library', str(self.root), *map(str, args)]), contextlib.redirect_stdout(out):
                code = lib.main()
            self.assertEqual(code, 0)
            return json.loads(out.getvalue())
        self.assertEqual(invoke('status', self.run)['resume'], '01-acquisition')
        invoke('check', self.run, '01-acquisition', '--review', 'Reviewed source and provenance')
        w.save(self.run / 'decision.json', {'sponsors': ['ACME'], 'exclusions': []})
        invoke('clean', self.run, '--input', 'decision.json')
        w.save(self.run / 'reading-progress.json', {'read_ids': [0, 1]})
        invoke('check', self.run, '02-preparation', '--review', 'Read all speech and checked exclusions')
        w.save(self.run / 'outline.json', [{'id': 's1', 'title': 'Example', 'segment_ids': [0]}])
        invoke('sections', self.run, '--input', 'outline.json')
        w.save(self.run / 'notes-input.json', [{'section_id': 's1', 'analysis': 'Limited example.', 'evidence_ids': [0]}])
        invoke('notes', self.run, '--input', 'notes-input.json')
        invoke('check', self.run, '03-extraction', '--review', 'Checked qualification and coverage')
        w.save(self.run / 'claims-input.json', [self.claim()])
        invoke('claims', self.run, '--input', 'claims-input.json')
        invoke('check', self.run, '04-verification', '--review', 'No external confirmation; uncertainty explicit')
        w.save(self.run / 'synthesis-input.json', {'analysis': 'A qualified example.', 'knowledge': [self.unit()]})
        invoke('synthesis', self.run, '--input', 'synthesis-input.json')
        invoke('check', self.run, '05-synthesis', '--review', 'Reviewed fidelity and reusable knowledge')
        self.assertEqual(invoke('verify', self.run)['coverage'], 'complete')
        self.assertEqual(invoke('status', self.run)['resume'], 'export')
        self.assertEqual(invoke('export', self.run)['knowledge_units'], 1)

    def test_acquisition_offline_fixture_and_failure_cleanup(self):
        payload = w.load(self.run / 'raw.json')
        with patch.object(w, 'retrieve', return_value=payload), patch.object(w, 'sponsorblock', return_value={'status': 'absent', 'segments': []}):
            result = w.start('https://youtu.be/dQw4w9WgXcQ', ['en'], 'small')
            self.assertTrue(Path(result['run']).exists())
        self.assertTrue(self.run.exists())


if __name__ == '__main__':
    unittest.main()
