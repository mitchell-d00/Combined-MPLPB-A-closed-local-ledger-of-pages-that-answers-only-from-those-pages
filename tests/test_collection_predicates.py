"""Source-bound selection distinguishes explicit modifiers and missing fields."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from mplpb_answers.pipeline import answer_query
from mplpb_answers import collection_fields
from mplpb_combined.ledger import write
from mplpb_combined.reader import PROFILES


class CollectionPredicatesTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)

    def add(self, identifier, *fields, **metadata):
        return write(self.root, doc_id=identifier, title=identifier, scope=identifier,
                     body='\n\n'.join(fields), **metadata)

    def test_no_cook_requires_explicit_same_record_fields(self):
        self.add('CARD-0001', 'Ingredients: 40 g sorrel, 20 g peas',
                 'Occasion: Picnic', 'Preparation: No cook')
        self.add('CARD-0002', 'Ingredients: 30 g sorrel', 'Occasion: Picnic',
                 'Preparation: Cook on stovetop')
        self.add('CARD-0003', 'Ingredients: 20 g sorrel', 'Occasion: Reunion',
                 'Preparation: No cooking')
        result = answer_query(self.root, 'Which sorrel recipes for picnics need no cooking?').contract
        self.assertTrue(result['answer_supported'])
        self.assertEqual([s['id'] for s in result['sources']], ['CARD-0001'])
        self.assertEqual(len(result['claims'][0]['citations']), 3)

    def test_absence_is_explicit_and_missing_remains_unresolved(self):
        self.add('CARD-0001', 'Water: 0 ml')
        self.add('CARD-0002', 'Water: 200 ml')
        self.add('CARD-0003', 'Preparation: No cook')
        result = answer_query(self.root, 'Which recipes use no water?').contract
        self.assertFalse(result['answer_supported'])
        self.assertEqual(result['kind'], 'partial_answer')
        self.assertEqual([s['id'] for s in result['sources']], ['CARD-0001'])
        self.assertEqual(result['collection_filter']['unresolved_records'], 1)

    def test_later_field_mentions_and_qualified_values_do_not_prove_a_match(self):
        self.add('CARD-0001', 'Preparation: No cook if chilled')
        self.add('CARD-0002', 'Preparation: No cook', 'Example follows.', 'Preparation: Bake')
        self.add('CARD-0003', 'Preparation: No-cook')
        result = answer_query(self.root, 'Which records where Preparation is no cook?').contract
        self.assertEqual(result['kind'], 'partial_answer')
        self.assertEqual([s['id'] for s in result['sources']], ['CARD-0003'])
        self.assertEqual(result['collection_filter']['unresolved_records'], 2)

    def test_profile_and_not_for_apply_before_scanning_without_lexical_matches(self):
        self.add('CARD-0001', 'Preparation: No cook', not_for='preparation')
        self.add('CARD-0002', 'Preparation: No cook')
        self.add('CARD-0003', 'Body contains no declared field.')
        question = 'Which records where Preparation is no cook?'
        result = answer_query(self.root, question).contract
        self.assertEqual(result['collection_filter']['evaluated_records'], 2)
        self.assertEqual([s['id'] for s in result['sources']], ['CARD-0002'])
        self.assertEqual(result['collection_filter']['unresolved_records'], 1)
        external = answer_query(self.root, question, PROFILES['external']).contract
        self.assertEqual(external['diagnostic']['code'], 'collection_profile_unavailable')
        self.assertFalse(external['claims'])

    def test_evidence_and_scan_budgets_withhold_completion(self):
        for n in range(2):
            self.add(f'CARD-{n:04d}', 'Preparation: No cook')
        question = 'Which records where Preparation is no cook?'
        budget = answer_query(self.root, question, max_passages=1).contract
        self.assertEqual(budget['kind'], 'partial_answer')
        self.assertFalse(budget['collection_filter']['complete'])
        with patch.object(collection_fields, 'MAX_RECORDS', 1):
            budget = answer_query(self.root, question).contract
        self.assertEqual(budget['diagnostic']['code'], 'collection_scan_budget')
        self.assertFalse(budget['claims'])

    def test_source_change_discards_claims_and_completion(self):
        self.add('CARD-0001', 'Preparation: No cook')
        original = collection_fields.verify

        def change(*args):
            checked = original(*args)
            self.add('CARD-0002', 'Preparation: Bake')
            return checked

        with patch.object(collection_fields, 'verify', side_effect=change):
            result = answer_query(self.root, 'Which records where Preparation is no cook?').contract
        self.assertEqual(result['diagnostic']['code'], 'source_changed')
        self.assertFalse(result['claims'])
        self.assertNotIn('collection_filter', result)
