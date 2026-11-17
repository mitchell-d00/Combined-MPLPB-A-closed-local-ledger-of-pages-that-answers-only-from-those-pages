import unittest
from tools.historical_targets import proportion,protocol


class HistoricalTargetTests(unittest.TestCase):
    def test_zero_observations_remain_unknown(self):
        p=proportion(0,0);self.assertIsNone(p['estimate']);self.assertIsNone(p['wilson_95'])

    def test_zero_errors_still_has_statistical_uncertainty(self):
        p=proportion(0,200);self.assertGreater(p['wilson_95'][1],0);self.assertLess(p['wilson_95'][1],.03)

    def test_known_proportion_interval_contains_estimate(self):
        p=proportion(160,200);self.assertEqual(p['estimate'],.8)
        self.assertLess(p['wilson_95'][0],.8);self.assertGreater(p['wilson_95'][1],.8)

    def test_invalid_counts_rejected(self):
        for pair in [(1,0),(-1,20),(True,2),(1.2,4)]:
            with self.assertRaises(ValueError):proportion(*pair)

    def test_protocol_never_claims_independent_results(self):
        p=protocol();self.assertEqual(p['status'],'NOT RUN');self.assertEqual(p['targets']['minimum_questions'],200)
        self.assertTrue(all(x is None for x in p['metrics'].values()))
