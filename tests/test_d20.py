"""Regression controls for the native D20 harness and its scoring boundary."""
from copy import deepcopy
import unittest

from test_tools.d20 import generate, run, score, study


class D20Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixtures, cls.key = generate(20)
        cls.result = run(cls.fixtures)

    def test_seed_and_matched_controls(self):
        self.assertEqual(generate(20), (self.fixtures, self.key))
        self.assertNotEqual(generate(21)[1]['fixtures_sha256'], self.key['fixtures_sha256'])
        cases = self.fixtures['cases']
        self.assertEqual(len(cases), 20)
        for start in range(0, len(cases), 4):
            self.assertEqual(len({case['question'] for case in cases[start:start + 4]}), 1)

    def test_native_controls_and_candidate_boundary(self):
        scored = score(self.result, self.key)
        self.assertEqual(scored['cases'][0]['outcome'], 'supported')
        for observed, outcome in zip(self.result['cases'], scored['cases']):
            self.assertFalse(observed['raw_sorter']['assessment']['answer_supported'])
            if outcome['condition'] != 'unique':
                self.assertEqual(outcome['outcome'], 'withheld', outcome)
            if outcome['condition'] == 'retired':
                self.assertNotIn('PAGE-A', observed['eligible_sources'])

    def test_score_rejects_wrong_batch_and_flags_bad_citation(self):
        with self.assertRaisesRegex(ValueError, 'same D20 fixtures'):
            score(self.result, generate(21)[1])
        edited = deepcopy(self.result)
        edited['cases'][0]['answer']['claims'][0]['citations'][0]['hash'] = 'wrong-hash'
        self.assertEqual(score(edited, self.key)['cases'][0]['outcome'], 'incorrect_support')

    def test_study_groups_every_matched_case(self):
        report = study(1000, 1)
        self.assertEqual(report['base_cases'], 20)
        self.assertEqual(len(report['receipts']), 1)
        groups = report['by_family_and_condition']
        self.assertEqual(len(groups), 5)
        for conditions in groups.values():
            self.assertEqual(len(conditions), 4)
            for evidence in conditions.values():
                self.assertEqual(sum(n for kind, n in evidence.items()
                                     if kind.startswith('diagnostic/')), 1)
