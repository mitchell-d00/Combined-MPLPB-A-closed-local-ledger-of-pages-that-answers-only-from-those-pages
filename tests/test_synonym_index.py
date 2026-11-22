"""Controls for scoped lookup and independent verification after selector review."""
import unittest

from test_tools.synonym_index import SynonymIndex
from test_tools.synonym_index_study import study


class SynonymIndexTests(unittest.TestCase):
    def test_collection_scope_and_whole_words(self):
        catalog = {'schema': 'mplpb-synonym-index-v1', 'collections': {
            'home': {'records': {'CAT-1': ['cat care']}, 'fields': {'Intake Date': ['date received']}},
            'water': {'records': {'TANK-1': ['cat care']}, 'fields': {'Observation Time': ['at what time']}},
        }}
        index = SynonymIndex(catalog)
        self.assertEqual(index.lookup('home', 'CAT CARE: what date received?')['status'], 'candidate')
        self.assertEqual(index.lookup('water', 'CAT CARE: what date received?')['status'], 'incomplete')
        self.assertEqual(index.lookup('home', 'bobcat care date received?')['records'], {})

    def test_competing_record_and_field_labels_are_retained(self):
        catalog = {'schema': 'mplpb-synonym-index-v1', 'collections': {
            'records': {'records': {'FILE-1': ['shift log'], 'FILE-2': ['shift log']},
                        'fields': {'Arrival Time': ['clock reading'], 'Departure Time': ['clock reading']}},
        }}
        output = SynonymIndex(catalog).lookup('records', 'What clock reading is in the shift log?')
        self.assertEqual(output['status'], 'ambiguous')
        self.assertEqual(list(output['records']), ['FILE-1', 'FILE-2'])
        self.assertEqual(list(output['fields']), ['Arrival Time', 'Departure Time'])
        self.assertNotIn('answer_supported', output)

    def test_reviewed_choices_use_native_proof_and_qualified_cases_only_lookup(self):
        result = study()
        for arm in ('original', 'alternative'):
            self.assertEqual(result['totals'][arm]['lookup_candidate'], 8)
            self.assertEqual(result['totals'][arm]['reviewed_exact_supported'], 8)
        for row in result['cases']:
            if row['arm'] == 'extra_obligation':
                self.assertIsNone(row['reviewed_proof'])
                self.assertNotIn('native_verified', row)
