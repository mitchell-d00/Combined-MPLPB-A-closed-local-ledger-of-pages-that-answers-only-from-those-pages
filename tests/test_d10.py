"""Exercise ten filled draws and D10's freeze, execution, and scoring boundaries."""
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from test_tools import d10, d10_capture
from test_tools.primary_book_test import read_json, write_json


class D10Tests(unittest.TestCase):
    def setUp(self):
        folder = TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.root = Path(folder.name)
        self.plan = self.root / 'plan.json'
        self.seed = 'd10-paired-controls'
        self.captures = {}
        topics = ('corn', 'river', 'ship', 'bee', 'cat', 'garden', 'train', 'moon', 'book', 'tree')
        for number, topic in enumerate(topics, 1):
            ident = f'D10-{number:02}'
            capture = self.root / ident
            # Those topic words distinguish the source and let the negative
            # quote control vary just the adjacent word order.
            text = f'The town archivist recorded {topic} samples after each seasonal showing. The staff kept the original notes in the reading room.\n'
            d10_capture.freeze(capture, text.encode(), {'kind': 'synthetic_fixture'}, self.seed, None)
            self.captures[ident] = capture
        write_json(self.plan, {'schema': 'mplpb-d10-draw-plan-v1', 'suite': 'exact_anchor', 'seed': self.seed,
                               'draws': [{'id': ident} for ident in self.captures]})

    def prepare(self, captures, token='run'):
        public, private = self.root / f'{token}-inputs', self.root / f'{token}-key'
        d10.prepare(self.plan, captures, public, private)
        return public, private

    def test_full_ten_draws_each_prove_one_quote_and_withhold_one(self):
        inputs, custody = self.prepare(self.captures)
        self.assertFalse((inputs/'key.json').exists())
        self.assertFalse(any(inputs.glob('*.bin')))
        original = d10.run(inputs)
        self.assertEqual(original, d10.run(inputs))
        verdict = d10.score(inputs, original, read_json(custody/'key.json'))
        self.assertEqual(verdict['totals'], {'exact_source_and_quote': 10, 'withheld': 10})
        self.assertEqual(verdict['unfilled'], 0)

    def test_unfilled_draws_remain_visible(self):
        inputs, custody = self.prepare({'D10-01': self.captures['D10-01']})
        verdict = d10.score(inputs, d10.run(inputs), read_json(custody/'key.json'))
        self.assertEqual((verdict['filled'], verdict['unfilled']), (1, 9))
        self.assertEqual(verdict['totals'], {'exact_source_and_quote': 1, 'withheld': 1})

    def test_mutation_does_not_reuse_frozen_checks(self):
        subset = {'D10-01': self.captures['D10-01']}
        inputs, custody = self.prepare(subset)
        report = d10.run(inputs)
        key = read_json(custody/'key.json')
        wrong_key = deepcopy(key)
        wrong_key['cases'][0]['source_id'] = 'D10-10'
        with self.assertRaisesRegex(ValueError, 'frozen packet'):
            d10.score(inputs, report, wrong_key)
        altered = deepcopy(report)
        answer = next(case['answer'] for case in altered['cases'] if case['answer']['answer_supported'])
        answer['claims'][0]['citations'][0]['body_start'] += 1
        verdict = d10.score(inputs, altered, key)
        self.assertEqual(verdict['totals']['invalid_evidence'], 1)
        (inputs/'D10-01.txt').write_text('changed original excerpt')
        with self.assertRaisesRegex(ValueError, 'does not match'):
            d10.run(inputs)
        (subset['D10-01']/'source.bin').write_text('changed raw capture')
        with self.assertRaisesRegex(ValueError, 'failed verification'):
            self.prepare(subset, 'changed')
