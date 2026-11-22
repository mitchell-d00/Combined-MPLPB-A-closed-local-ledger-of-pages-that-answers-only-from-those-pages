"""D12 paired controls and historical trace classification."""
import unittest

from test_tools.d12 import generate, trace_history


class D12Tests(unittest.TestCase):
    def test_paired_classes_report_first_unresolved_step(self):
        rows = {row['class']: row for row in generate(93)}
        self.assertEqual(len(rows), 12)
        self.assertTrue(all(row['passed'] for row in rows.values()))
        self.assertFalse(any(row['unexpected_completion'] for row in rows.values()))
        self.assertEqual(rows['nearby_year']['expected'], ['resolved', False])
        self.assertEqual(rows['unknown_condition']['first_unresolved']['path'], ['all', 'if', 'match', 'read'])
        self.assertEqual(rows['insufficient_evidence_budget']['first_unresolved']['path'], ['all'])
        self.assertIsNone(rows['reversed_operands']['first_unresolved'])

    def test_trace_keeps_conflicts_and_draft_coverage_separate_from_truth(self):
        def original(ident, kind, anchors, visible):
            return {'id': ident, 'question': ident, 'native_kind': kind, 'native_diagnostic': 'test',
                    'anchors': anchors, 'baseline_anchors': 0, 'graph_anchors': visible}

        result = trace_history({'originals': {}, 'cases': [
            original('missing', 'abstain', 2, 1),
            original('visible', 'partial_answer', 2, 2),
            original('conflict', 'conflict', 1, 1),
            original('supported', 'supported_answer', 1, 0),
            original('unreviewed', 'abstain', 0, 0),
        ]}, {'cases': [], 'declared_fields_in_imports': {}})
        self.assertEqual([row['signal'] for row in result['rows']], [
            'inspect_passage_discovery', 'inspect_proof_after_discovery', 'inspect_conflict',
            'native_full_support', 'reference_needed',
        ])
        self.assertTrue(all(row['independent_truth_review'] is None for row in result['rows']))
