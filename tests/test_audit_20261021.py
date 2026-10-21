"""Audit regressions; synthetic development tests, never held-out scores."""
import json
import tempfile
import unittest
from pathlib import Path
from mplpb_combined import ledger as L
from mplpb_answers.support import supported_answer
from tools.evaluate_audit_20261021 import run

class AuditRegressions(unittest.TestCase):
    def test_new_language_controls(self):
        report = run()
        for row in report['rows']:
            with self.subTest(case=row['name']):
                self.assertTrue(row['passed'], (row['expected'], row['actual'], row['text']))

    def test_corpus_isolation_stale_record_and_lineage_corruption(self):
        with tempfile.TemporaryDirectory() as tmp:
            a, b = Path(tmp)/'a', Path(tmp)/'b'
            a.mkdir(); b.mkdir()
            q = 'When did the Lumen Festival begin?'
            old = L.write(a, title='Lumen Festival', scope='Lumen Festival',
                          body='The Lumen Festival began in 1998.')
            L.write(b, title='Lumen Festival', scope='Lumen Festival',
                    body='The Lumen Festival began in 2001.')
            self.assertIn('1998', supported_answer(a, q).text)
            self.assertIn('2001', supported_answer(b, q).text)
            L.revise(a, old.id, body='The Lumen Festival began in 2003.')
            answer = supported_answer(a, q)
            self.assertEqual(answer.kind, 'return')
            self.assertIn('2003', answer.text)
            self.assertNotIn('1998', answer.text)
            history = L.log_path(a)
            history.write_text(history.read_text().replace('"event": "write"', '"event": "retire"'))
            self.assertNotEqual(supported_answer(a, q).kind, 'return')
            self.assertIn('2001', supported_answer(b, q).text)

    def test_citation_hash_matches_exact_supporting_source(self):
        with tempfile.TemporaryDirectory() as root:
            rec = L.write(root, title='Lumen Festival', scope='Lumen Festival',
                          body='The Lumen Festival began in 1998.')
            result = supported_answer(root, 'When did the Lumen Festival begin?')
            self.assertEqual(result.kind, 'return')
            self.assertEqual(result.record.hash, rec.hash)
            self.assertEqual(result.record.id, rec.id)
            self.assertEqual(result.support['spans'][0]['quote'], result.text)
            file = Path(root)/rec.path
            file.write_text(file.read_text().replace('1998', '2002'))
            result = supported_answer(root, 'When did the Lumen Festival begin?')
            self.assertEqual(result.kind, 'not_in_corpus')
            self.assertEqual(result.citation(), '')
