"""D8 controls for lookup, source-local proof and answer assembly."""
from html import escape
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from mplpb_answers.advanced import advanced_query
from mplpb_answers.body_text import body_text
from mplpb_answers.pipeline import answer_query
from mplpb_combined.ledger import Ledger, write
from mplpb_combined.reader import PROFILES, answer


class D8OwnerBoundaries(unittest.TestCase):
    field = 'What is the kettle color?'
    pair = 'Compare shelf code for record ARCH-A and record ARCH-B'

    def setUp(self):
        temp = TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)

    def page(self, identity, body, scope='kettle color', **options):
        return write(self.root, doc_id=identity, title='Register', scope=scope,
                     body_html='<pre>' + escape(body) + '</pre>', **options)

    def ask(self, question=None, **options):
        return answer_query(self.root, question or self.field, PROFILES['internal'], **options).contract

    def readback(self, result):
        records = {record.path: record for record in Ledger(self.root).servable()}
        citations = [cite for claim in result['claims'] for cite in claim['citations']]
        for cite in citations:
            record = records[cite['path']]
            self.assertEqual((cite['source_id'], cite['hash']), (record.id, record.hash_actual))
            self.assertEqual(body_text(record.body_html)[cite['body_start']:cite['body_end']], cite['quote'])
        return {cite['source_id'] for cite in citations}

    def test_zero_owners_withholds(self):
        self.assertFalse(self.ask()['answer_supported'])
        self.assertEqual(self.ask()['claims'], [])

    def test_one_complete_owner_returns_its_own_proof(self):
        self.page('ARCH-A', 'The kettle color is blue.')
        result = self.ask()
        self.assertTrue(result['answer_supported'])
        self.assertEqual(self.readback(result), {'ARCH-A'})

    def test_competing_owners_keep_attributed_witnesses(self):
        self.page('ARCH-A', 'The kettle color is blue.')
        self.page('ARCH-B', 'The kettle color is red.')
        self.assertEqual(answer(self.root, self.field).kind, 'ambiguous')
        result = self.ask()
        self.assertEqual(result['kind'], 'conflict')
        self.assertFalse(result['answer_supported'])
        self.assertEqual(self.readback(result), {'ARCH-A', 'ARCH-B'})
        self.assertIn('ARCH-A: The kettle color is blue.', result['text'])
        self.assertIn('ARCH-B: The kettle color is red.', result['text'])
        self.assertEqual(result['verification']['semantic'], 'bounded_competing_source_statements')
        self.assertEqual(advanced_query(self.root, self.field)['strict'], result)

    def test_agreeing_owners_stay_separate(self):
        self.page('ARCH-A', 'The kettle color is blue.')
        self.page('ARCH-B', 'The kettle color is blue.')
        result = self.ask()
        self.assertFalse(result['answer_supported'])
        self.assertEqual(self.readback(result), {'ARCH-A', 'ARCH-B'})
        self.assertEqual(result['verification']['semantic'], 'bounded_parallel_source_statements')

    def test_conflict_budget_cannot_leave_a_single_apparent_winner(self):
        self.page('ARCH-A', 'The kettle color is blue.')
        self.page('ARCH-B', 'The kettle color is red.')
        result = self.ask(max_passages=1)
        self.assertEqual(result['diagnostic']['code'], 'contradictory_passages_pruned')
        self.assertEqual(result['claims'], [])
        self.assertFalse(result['answer_supported'])

    def test_lexical_owners_are_inspectable_without_claims(self):
        self.page('ARCH-A', 'A filing note.', scope='archive routing')
        self.page('ARCH-B', 'A different filing note.', scope='archive routing')
        result = self.ask('Explain archive routing')
        self.assertFalse(result['answer_supported'])
        self.assertEqual(result['claims'], [])
        self.assertEqual({item['id'] for item in result['retrieval']['ownership_candidates']},
                         {'ARCH-A', 'ARCH-B'})

    def test_explicit_pair_can_complete_both_independent_obligations(self):
        self.page('ARCH-A', 'Shelf Code: R42', scope='archive')
        self.page('ARCH-B', 'Shelf Code: A17', scope='archive')
        result = self.ask(self.pair)
        self.assertTrue(result['answer_supported'], result['diagnostic'])
        self.assertEqual(self.readback(result), {'ARCH-A', 'ARCH-B'})
        self.assertEqual([part['record_id'] for part in result['question_parts']], ['ARCH-A', 'ARCH-B'])
        self.assertFalse(self.ask(self.pair + ' before the revision')['answer_supported'])
        self.assertFalse(self.ask(self.pair, max_passages=1)['answer_supported'])
        self.page('ARCH-C', 'Shelf Code: B11\nShelf Code: B12', scope='archive')
        conflict = self.ask(self.pair.replace('ARCH-B', 'ARCH-C'))
        self.assertEqual(conflict['kind'], 'conflict')
        self.assertFalse(conflict['answer_supported'])
        self.assertEqual(self.readback(conflict), {'ARCH-A', 'ARCH-C'})
        self.assertIn('B11', conflict['text'])
        self.assertIn('B12', conflict['text'])
        limited = self.ask(self.pair.replace('ARCH-B', 'ARCH-C'), max_passages=2)
        self.assertEqual(limited['kind'], 'conflict')
        self.assertEqual(self.readback(limited), {'ARCH-A'})

    def test_missing_restricted_or_conditional_side_stays_unresolved(self):
        self.page('ARCH-A', 'Shelf Code: R42', scope='archive')
        for selector in ('ARCH-MISSING', 'ARCH-B', 'ARCH-C'):
            with self.subTest(selector=selector):
                if selector == 'ARCH-B':
                    self.page(selector, 'Shelf Code: SECRET', scope='archive', not_for='shelf')
                if selector == 'ARCH-C':
                    self.page(selector, 'Proposed Shelf Code: SECRET', scope='archive')
                result = self.ask(self.pair.replace('ARCH-B', selector))
                self.assertEqual(result['kind'], 'partial_answer')
                self.assertFalse(result['answer_supported'])
                self.assertNotIn('SECRET', result['text'])
                self.assertEqual(self.readback(result), {'ARCH-A'})
