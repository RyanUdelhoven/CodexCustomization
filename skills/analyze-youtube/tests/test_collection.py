import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).parents[1] / 'scripts'))
import collection as c
import library as lib
import workflow as w
import test_library


class CollectionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        previous = w.ROOT
        self.addCleanup(setattr, w, 'ROOT', previous)
        self.root = lib.setup(Path(self.tmp.name) / 'library')
        self.path = c.create(self.root, 'examples', 'Examples')
        (self.path / 'documents').mkdir()
        self.doc = self.path / 'documents/example.json'
        w.save(self.doc, {'passages': [{'id': 'p1', 'text': 'A limited example.', 'locator': 'page 1'},
                                     {'id': 'p2', 'text': 'An exception.', 'locator': 'page 2'}]})
        self.inventory = {'scope': 'Two passages', 'coverage': 'One document', 'gaps': 'No video yet',
            'sources': [{'id': 'doc', 'kind': 'document', 'path': 'documents/example.json', 'title': 'Example',
                         'url': 'urn:example:document', 'date': 'unknown', 'coverage': 'Complete supplied text', 'limitations': 'Fixture only'}]}
        self.framework = {'revision': '1', 'change_reason': 'Initial', 'codes': [
            {'id': 'limits', 'definition': 'Qualification', 'include': 'Scope limits', 'exclude': 'Unrelated claims'}]}
        self.evidence = {'items': [{'id': 'e1', 'source_id': 'doc', 'code_ids': ['limits'], 'passage_ids': ['p1'],
            'context_ids': ['p2'], 'observation': 'Example has a limit', 'context': 'Exception follows',
            'role': 'qualification', 'limitations': 'Single example', 'quotes': [{'passage_id': 'p1', 'text': 'limited example'}]}],
            'coverage': {'doc': {'status': 'complete', 'read_ids': ['p1', 'p2'], 'gaps': 'None'}}}
        self.comparison = {'findings': [{'id': 'f1', 'evidence_ids': ['e1'], 'negative_case_ids': [],
            'relation': 'insufficient', 'observation': 'Only one example', 'interpretation': 'Cannot generalize',
            'alternatives': 'Selection bias', 'limitations': 'Small corpus', 'date_context': 'Unknown date'}]}

    def put(self, stage, value, purpose=None):
        c.save(self.path, stage, value, purpose)
        c.check(self.path, stage, 'Reviewed source fidelity, gaps and uncertainty.', purpose)

    def shared(self):
        for stage, value in zip(c.SHARED, [self.inventory, self.framework, self.evidence, self.comparison]):
            self.put(stage, value)

    def purpose(self, name):
        c.new_purpose(self.path, name, 'What are the limits?')
        memo = {'question': 'What are the limits?', 'analysis': 'A limited example', 'evidence_ids': ['e1'],
                'comparison_ids': ['f1'], 'negative_case_ids': [], 'alternatives': 'Sampling', 'limitations': 'One example'}
        self.put('05-memos', memo, name)
        verification = {'interpretation_challenge': 'Selection might hide counterexamples', 'limitations': 'No external checking',
            'claims': [{'id': 'c1', 'statement': 'Example has limits', 'safe_statement': 'Source qualifies example',
            'kind': 'source_claim', 'status': 'unverified', 'evidence_ids': ['e1'], 'sources': [],
            'checked_at': '2026-11-21', 'limitations': 'Unverified'}]}
        self.put('06-verification', verification, name)
        self.synthesis = {'analysis': 'The source qualifies an example.', 'limitations': 'Single document',
            'knowledge': [{'id': 'k1', 'title': 'Limited example', 'text': 'Source qualifies its example.',
            'kind': 'speaker_claim', 'evidence_ids': ['e1'], 'claim_ids': ['c1'], 'limitations': 'Unverified'}]}
        self.put('07-synthesis', self.synthesis, name)

    def test_shared_reuse_independent_purposes_and_revision_retention(self):
        self.shared()
        evidence_hash = lib.digest(self.path / '03-evidence/evidence.json')
        self.purpose('techniques'); self.purpose('history')
        first = Path(c.export(self.path, 'techniques')['export'])
        record = json.loads((first / 'knowledge.jsonl').read_text())
        self.assertEqual(record['evidence'][0]['passages'][0]['locator'], 'page 1')
        self.assertNotIn('limited example.', (first / 'knowledge.jsonl').read_text())
        self.assertEqual(record['claims'][0]['status'], 'unverified')
        self.assertEqual(c.export(self.path, 'techniques')['export'], str(first))
        self.synthesis['analysis'] = 'Revised interpretation.'
        c.save(self.path, '07-synthesis', self.synthesis, 'techniques')
        self.assertEqual(c.state(self.path, 'techniques')['07-synthesis'], 'stale')
        self.assertEqual(c.state(self.path, 'history')['07-synthesis'], 'pass')
        with self.assertRaises(ValueError): c.export(self.path, 'techniques')
        c.check(self.path, '07-synthesis', 'Reviewed changed interpretation', 'techniques')
        second = Path(c.export(self.path, 'techniques')['export'])
        self.assertNotEqual(first, second)
        self.assertTrue(first.exists())
        self.assertEqual(lib.digest(self.path / '03-evidence/evidence.json'), evidence_hash)
        (first / 'analysis.md').write_text('Corrupt')
        c.reindex(self.path)
        self.assertEqual(len(w.load(self.path / 'index.json')), 1)

    def test_source_framework_and_question_invalidation(self):
        self.shared(); self.purpose('history')
        self.framework['revision'] = '2'
        self.put('02-framework', self.framework)
        state = c.state(self.path, 'history')
        self.assertEqual(state['01-inventory'], 'pass')
        self.assertEqual(state['02-framework'], 'pass')
        self.assertTrue(all(state[s] == 'stale' for s in list(state)[2:]))
        self.put('03-evidence', self.evidence); self.put('04-comparison', self.comparison)
        purpose = self.path / 'purposes/history/purpose.json'
        w.save(purpose, {'id': 'history', 'question': 'A different question'})
        self.assertEqual(c.state(self.path)['04-comparison'], 'pass')
        self.assertEqual(c.state(self.path, 'history')['05-memos'], 'stale')
        self.doc.write_text(self.doc.read_text().replace('limited', 'unlimited'))
        self.assertTrue(all(v == 'stale' for v in c.state(self.path, 'history').values()))

    def test_invalid_evidence_coverage_quotes_and_certainty(self):
        self.put('01-inventory', self.inventory); self.put('02-framework', self.framework)
        self.evidence['items'][0]['quotes'][0]['text'] = 'Fabricated'
        with self.assertRaises(ValueError): c.save(self.path, '03-evidence', self.evidence)
        self.evidence['items'][0]['quotes'] = []
        self.evidence['coverage']['doc']['read_ids'] = ['p1']
        with self.assertRaises(ValueError): c.save(self.path, '03-evidence', self.evidence)
        self.evidence['coverage']['doc']['read_ids'].append('p2')
        self.put('03-evidence', self.evidence); self.put('04-comparison', self.comparison)
        self.purpose('history')
        self.synthesis['knowledge'][0]['kind'] = 'verified_fact'
        with self.assertRaises(ValueError): c.save(self.path, '07-synthesis', self.synthesis, 'history')
        (self.path / '04-comparison/check.md').write_text('fail: missed exception')
        with self.assertRaises(ValueError): c.export(self.path, 'history')

    def test_video_reuse_preserves_timestamps_and_rejects_promotions(self):
        fixture = test_library.LibraryTests('test_resume_export_evidence_and_private_sources')
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        fixture.prepared()
        # Use fixture's own library; source belongs to its root.
        self.path = c.create(fixture.root, 'videos', 'Video comparison')
        source = dict(self.inventory['sources'][0], id='video', kind='video', path=str(fixture.run))
        self.inventory['sources'] = [source]
        self.put('01-inventory', self.inventory); self.put('02-framework', self.framework)
        item = self.evidence['items'][0]
        item.update(source_id='video', passage_ids=[0], context_ids=[], quotes=[])
        self.evidence['coverage'] = {'video': {'status': 'complete', 'read_ids': [0], 'gaps': 'None'}}
        self.put('03-evidence', self.evidence); self.put('04-comparison', self.comparison)
        self.purpose('history')
        destination = Path(c.export(self.path, 'history')['export'])
        record = json.loads((destination / 'knowledge.jsonl').read_text())
        self.assertEqual(record['evidence'][0]['passages'][0]['start'], 12.5)
        self.assertTrue(record['evidence'][0]['passage_urls'][0].endswith('&t=12'))
        self.assertNotIn('ACME', ''.join(f.read_text() for f in destination.iterdir()))
        item['passage_ids'] = [1]
        with self.assertRaises(ValueError): c.save(self.path, '03-evidence', self.evidence)
        (fixture.run / 'brief.md').write_text('Changed')
        self.assertEqual(c.state(self.path)['01-inventory'], 'stale')

    def test_cli_resume_bounds_and_safety(self):
        def invoke(*args):
            out = io.StringIO()
            with patch.object(sys, 'argv', ['collection.py', '--library', str(self.root), *map(str, args)]), contextlib.redirect_stdout(out):
                self.assertEqual(c.main(), 0)
            return json.loads(out.getvalue())
        self.assertEqual(invoke('status', 'examples')['resume'], '01-inventory')
        input_file = Path(self.tmp.name) / 'inventory.json'
        w.save(input_file, self.inventory)
        invoke('save', 'examples', '01-inventory', '--input', input_file)
        invoke('check', 'examples', '01-inventory', '--review', 'Reviewed identity, coverage and gaps')
        self.assertEqual(invoke('status', 'examples')['resume'], '02-framework')
        page = invoke('read', 'examples', '01-inventory', '--limit', 2)
        self.assertEqual(len(page['chunks']), 2)
        with self.assertRaises(ValueError): c.create(self.root, '../escape', 'Bad')
        with self.assertRaises(FileExistsError): c.create(self.root, 'examples', 'Duplicate')
        self.inventory['sources'][0]['path'] = '/etc/passwd'
        with self.assertRaises(ValueError): c.save(self.path, '01-inventory', self.inventory)


if __name__ == '__main__': unittest.main()
