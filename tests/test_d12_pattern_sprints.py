"""Paired controls for the bounded excerpt patterns."""
import json
from html import escape
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from mplpb_answers import bounded_records
from mplpb_answers.body_text import body_text
from mplpb_answers.pipeline import answer_query
from mplpb_combined.ledger import withdraw, write
from mplpb_combined.reader import PROFILES


FIXTURE = Path(__file__).resolve().parents[1] / 'evaluation/d12/pattern-sprints/expanded.json'


class PatternSprintTests(unittest.TestCase):
    def check_family(self, family):
        cases = json.loads(FIXTURE.read_bytes())[family]
        for case in cases:
            with self.subTest(case=case['id']), TemporaryDirectory() as root:
                records = {}
                for number, body in enumerate(case['bodies'], 1):
                    record = write(root, title=f'Source {number}', scope='Documentary material',
                                   doc_id=f'REC-{number}', when='2026-11-23',
                                   body_html='<pre>' + escape(body) + '</pre>')
                    records[record.id] = body_text(record.body_html)
                answer = answer_query(root, case['question'], PROFILES['internal'],
                                      max_passages=case.get('max_passages', 12)).contract
                self.assertEqual(answer['kind'], case['kind'], answer['diagnostic'])
                self.assertEqual(answer['answer_supported'], case['kind'] == 'supported_answer')
                if case['kind'] == 'abstain':
                    self.assertEqual(answer['claims'], [])
                for required in case.get('quote', []):
                    self.assertTrue(any(required in cite['quote'] for claim in answer['claims']
                                        for cite in claim['citations']), answer['text'])
                if 'missing' in case:
                    self.assertIn(case['missing'], ' '.join(answer['missing']))
                for claim in answer['claims']:
                    for cite in claim['citations']:
                        body = records[cite['source_id']]
                        self.assertEqual(body[cite['body_start']:cite['body_end']], cite['quote'])
                self.assertFalse(answer['verification']['truth_verified'])

    def test_stage_and_outcome(self):
        self.check_family('stage_and_outcome')

    def test_inventory_row(self):
        self.check_family('inventory_row')

    def test_conditions(self):
        self.check_family('conditions')

    def test_causal_boundary(self):
        self.check_family('causal_boundary')


    def test_recheck_clears_excerpts_on_source_withdrawal(self):
        with TemporaryDirectory() as root:
            record = write(root, title='Inventory', scope='Documentary material', doc_id='REC-1',
                           body_html='<pre>Entry 02 | Switch Lantern | Quantity: 4</pre>')
            original = bounded_records.verify

            def change(index, **kwargs):
                answer = original(index, **kwargs)
                if kwargs.get('excerpts'):
                    withdraw(root, record.id)
                return answer

            with patch.object(bounded_records, 'verify', side_effect=change):
                answer = answer_query(root, 'What values are recorded for this item?', PROFILES['internal']).contract
            self.assertEqual(answer['diagnostic']['code'], 'source_changed')
            self.assertEqual(answer['claims'], [])

    def test_quoted_row_is_not_a_source_statement(self):
        with TemporaryDirectory() as root:
            write(root, title='Inventory', scope='Documentary material',
                  body_html='<blockquote>Entry 02 | Switch Lantern | Quantity: 4</blockquote>')
            answer = answer_query(root, 'What values are recorded for this item?', PROFILES['internal']).contract
            self.assertEqual(answer['kind'], 'abstain')
            self.assertEqual(answer['claims'], [])
