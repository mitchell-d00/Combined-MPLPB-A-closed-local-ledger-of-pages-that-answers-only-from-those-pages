"""D6 only compiles independently pinned literal source evidence."""
from html import escape
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from mplpb_answers import d6
from mplpb_combined.ledger import withdraw, write
from test_tools.d6 import evaluate, field, read_field, compare_value


class D6Tests(unittest.TestCase):
    def setUp(self):
        tmp = TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.body = ('Record-ID: ITEM-11\nObservation Date: October 28, 1872\nEarlier Year: 1774\n'
                     'Prior Autumn Year: 1871\nAutumn Weather: crisp\nPrior Autumn Weather: mild')
        self.add('ALMANAC-1', self.body)

    def add(self, identity, body, **kwargs):
        write(self.root, doc_id=identity, title='Fictional almanac', scope='documentary evidence',
              body_html='<pre>' + escape(body) + '</pre>', when='2026-11-22', **kwargs)

    def compile(self, *steps, **kwargs):
        return d6.compile_plan(self.root, {'schema': d6.SCHEMA, 'steps': list(steps)}, **kwargs)

    def test_six_evaluation_families(self):
        outcomes = evaluate(6)
        self.assertEqual(len(outcomes), 15)
        self.assertEqual({row['family'] for row in outcomes},
                         {'read', 'match', 'not_match', 'year_difference', 'if', 'all'})
        self.assertTrue(all(row['passed'] for row in outcomes))

    def test_exact_date_and_comparative_explanation(self):
        plan = self.compile(
            compare_value('Observation Date', 'Oct 28 1872'),
            compare_value('Prior Autumn Weather', 'crisp', 'not_match'),
            {'op': 'year_difference', 'left': field('Earlier Year'), 'right': field('Observation Date')})
        self.assertTrue(plan['answer_supported'])
        self.assertEqual([r['value'] for r in plan['compiled']['steps']], [True, True, 98])
        self.assertFalse(plan['truth_verified'])
        text = d6.render(plan)
        self.assertIn('1872 minus 1774 is 98', text)
        self.assertIn('Observation Date: October 28, 1872', text)
        self.assertIn(plan['evidence'][0]['hash'], text)

    def test_unresolved_or_conflicting_condition_runs_neither_branch(self):
        self.add('ALMANAC-2', self.body.replace('crisp', 'damp'))
        for label in ('Autumn Weather', 'Unknown Weather'):
            with self.subTest(label=label):
                plan = self.compile({'op': 'if', 'when': compare_value(label, 'crisp'),
                                     'then': read_field('Earlier Year'),
                                     'else': read_field('Observation Date')})
                self.assertFalse(plan['answer_supported'])
                self.assertEqual(len(plan['compiled']['steps'][0]['steps']), 1)
                self.assertEqual(plan['evidence'], [])
                self.assertIn('neither branch ran', d6.render(plan))

    def test_partial_date_input_cannot_prove_literal_negation(self):
        plan = self.compile(compare_value('Observation Date', '1872', 'not_match'))
        self.assertFalse(plan['answer_supported'])
        self.assertNotIn('value', plan['compiled']['steps'][0])

    def test_unstructured_prose_cannot_masquerade_as_a_field(self):
        self.add('PROSE-1', 'October 28, 1872 was crisp, unlike the fall of 1871.')
        plan = self.compile(read_field('Observation Date', 'PROSE-1'))
        self.assertFalse(plan['answer_supported'])
        self.assertFalse(plan['evidence'])

    def test_single_span_is_deduplicated_and_combined_budget_is_enforced(self):
        self.assertTrue(self.compile(read_field('Observation Date'), read_field('Observation Date'),
                                     max_passages=1)['answer_supported'])
        plan = self.compile(read_field('Observation Date'), read_field('Earlier Year'), max_passages=1)
        self.assertFalse(plan['answer_supported'])
        self.assertFalse(plan['evidence'])

    def test_mutation_discards_sourced_output(self):
        original = d6.answer_query

        def mutate(*args, **kwargs):
            answer = original(*args, **kwargs)
            withdraw(self.root, 'ALMANAC-1')
            return answer

        with patch.object(d6, 'answer_query', side_effect=mutate):
            plan = self.compile(read_field('Observation Date'))
        self.assertFalse(plan['answer_supported'])
        self.assertFalse(plan['evidence'])
        self.assertIn('changed during the plan', d6.render(plan))

    def test_dead_branch_still_validates_without_reading(self):
        with self.assertRaisesRegex(ValueError, 'unexpected'):
            self.compile({'op': 'if', 'when': compare_value('Autumn Weather', 'crisp'),
                          'then': read_field('Earlier Year'),
                          'else': {'op': 'read', 'record_id': 'X', 'field': 'Y', 'drop': True}})
