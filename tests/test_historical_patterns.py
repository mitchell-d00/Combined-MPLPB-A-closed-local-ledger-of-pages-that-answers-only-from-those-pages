"""Check the historical follow-up study's scoring and cohort accounting."""
import unittest

from test_tools.historical_patterns import ARMS, compare, measured


class HistoricalPatternTests(unittest.TestCase):
    def test_passage_visibility_and_cited_support_are_separate(self):
        anchor = {'source_id': 'ORIGINAL-1', 'quote': 'prior public release'}
        group = {'anchors': [anchor]}
        answer = {'kind': 'partial_answer', 'diagnostic': {'code': 'partial'},
                  'answer_supported': False,
                  'claims': [{'citations': [{'source_id': 'ORIGINAL-1',
                                            'quote': 'prior public\nrelease'}]}]}
        probe = {'passages': [{'source_id': 'ORIGINAL-2', 'text': 'prior public release'}]}
        row = measured(group, 'direct', answer, probe)
        self.assertEqual(row['citation_anchors_visible'], 1)
        self.assertEqual(row['probe_anchors_visible'], 0)
        self.assertEqual(row['observation'], 'withheld_full_support')

    def test_boundary_support_requires_review(self):
        answer = {'kind': 'supported_answer', 'diagnostic': {'code': 'support'},
                  'answer_supported': True, 'claims': []}
        row = measured({'anchors': [{'source_id': 'A', 'quote': 'evidence'}]},
                       'boundary', answer, {'passages': []})
        self.assertEqual(row['observation'], 'support_flag_review_required')

    def test_pair_counts_keep_quote_controls_separate(self):
        rows = [{'group': 'sample', 'arm': arm,
                 'observation': ('supported_with_all_anchors' if arm in ('quote', 'direct')
                                 else 'withheld_full_support')} for arm in ARMS]
        arms, pairs = compare(rows)
        self.assertEqual(pairs, {'direct_no_paraphrase': 1})
        self.assertEqual(arms['quote'], {'supported_with_all_anchors': 1})
