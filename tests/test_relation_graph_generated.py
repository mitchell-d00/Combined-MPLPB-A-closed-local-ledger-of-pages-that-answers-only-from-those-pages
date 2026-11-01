"""Stable generated smoke bench, factual negatives and mutation checks."""
import unittest
from tools.benchmark_relation_graph import run, SEED


class DiverseSmokeBenchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = run()

    def test_unique_fixed_seed_and_twelve_independent_domains(self):
        r = self.report
        self.assertEqual(r['seed'], SEED)
        self.assertEqual(r['domains'], 12)
        self.assertEqual(r['summary']['unique_questions'], 312)
        self.assertEqual(r['summary']['duplicate_questions_skipped'], 0)
        self.assertEqual(len(set(x['id'] for x in r['rows'])), len(r['rows']))
        self.assertEqual(len(set(x['question'].casefold().replace(' ', '')
                                 for x in r['rows'])), len(r['rows']))
        self.assertEqual(r['rows'][0]['id'], 'MPLPB-SM-000001')

    def test_all_relationships_expected_results_and_abstentions(self):
        summary = self.report['summary']
        failures = [r for r in self.report['rows'] if not r['correct']]
        self.assertEqual(summary['failed'], 0, failures[:6])
        self.assertEqual(summary['wrong_returns'], 0)
        self.assertEqual(summary['correct_returns'], 204)
        self.assertEqual(summary['correct_refusals'], 108)
        for category in ('storage', 'responsibility', 'due', 'status',
                         'location', 'contents', 'schedule'):
            self.assertEqual(self.report['categories'][category]['failed'], 0)
            self.assertGreaterEqual(self.report['categories'][category]['questions'], 12)

    def test_source_mutations_and_duplicate_owner_ambiguity(self):
        r = self.report
        failed = [m for m in r['metamorphic'] if not m['correct']]
        self.assertEqual(r['summary']['metamorphic_checks'], 24)
        self.assertEqual(r['summary']['metamorphic_passed'], 24, failed)
        self.assertEqual({p['category'] for p in r['metamorphic']},
                         {'changed_source', 'duplicate_owner'})
        for entry in r['metamorphic']:
            if entry['category'] == 'changed_source':
                self.assertIn('revised', entry['actual']['quote'])
            else:
                self.assertEqual(entry['actual']['kind'], 'ambiguous')


if __name__ == '__main__':
    unittest.main()
