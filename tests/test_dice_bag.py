"""Dice Bag custody and blind replay checks with a mocked live download."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from test_tools.dice_bag import json_bytes, prepare, put, read, run, score


class DiceBagTests(unittest.TestCase):
    def test_key_is_separate_and_scope_controls_stay_lookup_only(self):
        feature = {'id': 'sample1', 'properties': {'place': 'Silver Bay', 'mag': 5.1,
                                                  'type': 'earthquake'},
                   'geometry': {'coordinates': [10, 20, 30]}}
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            inputs, custody = root / 'operator', root / 'custodian'
            with patch('test_tools.dice_bag.fetch', return_value=json_bytes({'features': [feature]})):
                prepare(inputs, custody, '42', 2)
            self.assertEqual(sorted(p.name for p in inputs.iterdir()), ['packet.json', 'seal.json'])
            packet = read(inputs / 'packet.json')
            self.assertEqual(packet['draw_counts'], {'filled': 1, 'unfilled': 1})
            self.assertTrue(all(set(case) == {'id', 'question'} for case in packet['cases']))
            report = root / 'run.json'
            put(report, run(inputs))
            result = score(inputs, report, custody / 'key.json')
            self.assertEqual(result['summary']['direct']['baseline_exact_supported'], 1)
            self.assertEqual(result['summary']['natural']['confirmed_proof_exact_supported'], 1)
            self.assertEqual(result['summary']['unlisted_wording']['lookup_incomplete'], 1)
            self.assertEqual(result['summary']['qualified']['lookup_candidate'], 1)
            self.assertTrue(all(row['confirmed_proof'] is None for row in result['cases']
                                if row['family'] in {'missing', 'qualified', 'ambiguous'}))
            key = custody / 'key.json'
            key.write_text(json.dumps(read(key)))
            with self.assertRaisesRegex(ValueError, 'frozen'):
                score(inputs, report, key)

    def test_operator_cannot_accidentally_nest_the_custodian(self):
        with TemporaryDirectory() as tmp:
            inputs = Path(tmp) / 'operator'
            with self.assertRaisesRegex(ValueError, 'separate'):
                prepare(inputs, inputs / 'custodian', '42', 1)
