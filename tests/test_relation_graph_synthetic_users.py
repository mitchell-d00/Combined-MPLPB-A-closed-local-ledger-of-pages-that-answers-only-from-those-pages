"""Independent-scripted personas exercise the full source ledger, not just regexes."""
import unittest
from tools.simulate_relation_graph_users import run


class SyntheticUserGraphTests(unittest.TestCase):
    def test_all_six_personas_preserve_expected_evidence_and_refusal(self):
        report = run()
        self.assertEqual(report['personas'], 6)
        self.assertEqual(report['metrics']['questions'], 36)
        bad = [r for r in report['rows'] if not r['correct']]
        self.assertEqual(bad, [], bad)
        self.assertEqual(report['metrics']['wrong_returns'], 0)

    def test_condition_and_relation_graph_have_pinned_source_quotes(self):
        report = run()
        for row in report['rows']:
            if row['kind'] == 'return':
                self.assertTrue(row['source_hash'].startswith('sha256:'))
                self.assertEqual(row['quote'], row['expected_quote'])
                self.assertTrue(row['source_id'])
        graph_results = [r for r in report['rows'] if r['graph_version']]
        self.assertGreaterEqual(len(graph_results), 3)

if __name__ == '__main__':
    unittest.main()
