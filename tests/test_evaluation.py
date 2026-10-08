import json
import math
import tempfile
import unittest
from pathlib import Path

from mplpb_combined.baselines import LexicalIndex
from mplpb_combined.evaluate import run
from mplpb_combined import killtest


class TestLexicalBaselines(unittest.TestCase):
    def test_bm25_matches_hand_calculated_score(self):
        index = LexicalIndex({'a': 'alpha alpha beta', 'b': 'beta'})
        expected = math.log(2) * 2 * 2.2 / (2 + 1.2 * (.25 + .75 * 3 / 2))
        self.assertAlmostEqual(dict(index.rank('alpha', 'bm25'))['a'], expected)

    def test_cosine_matches_hand_calculated_score(self):
        index = LexicalIndex({'a': 'alpha beta', 'b': 'beta'})
        weight = 1 + math.log(3 / 2)
        expected = weight / math.sqrt(weight ** 2 + 1)
        self.assertAlmostEqual(dict(index.rank('alpha', 'tfidf'))['a'], expected)

    def test_rare_word_changes_overlap_tie(self):
        index = LexicalIndex({'a': 'common common', 'b': 'rare', 'c': 'common'})
        for method in ('bm25', 'tfidf'):
            self.assertEqual(index.top('common rare', method), 'b')

    def test_empty_and_unknown_queries_refuse_and_ties_are_stable(self):
        for method in ('bm25', 'tfidf'):
            self.assertIsNone(LexicalIndex({}).top('alpha', method))
            index = LexicalIndex({'b': 'alpha', 'a': 'alpha'})
            self.assertIsNone(index.top('unknown', method))
            self.assertIsNone(index.top('', method))
            self.assertEqual(index.top('alpha', method), 'a')


class TestEvaluation(unittest.TestCase):
    def test_shipped_pottery_comparisons_reproduce(self):
        repo = Path(__file__).resolve().parents[1]
        for name in ('probes', 'probes_heldout', 'probes_adjacent'):
            with self.subTest(probes=name):
                shipped = json.loads((repo / 'evaluation' / (name + '_comparison.json')).read_text())
                fresh = killtest.run(repo / 'examples' / 'studio', repo / 'killtest' / (name + '.json'))
                self.assertEqual(fresh['lexical_baselines'], shipped['lexical_baselines'])
                self.assertEqual(fresh['lexical_rows'], shipped['lexical_rows'])

    def test_frozen_multi_domain_results_reproduce(self):
        root = Path(__file__).resolve().parents[1] / 'evaluation'
        fresh = run(root / 'manifest.json')
        shipped = json.loads((root / 'results.json').read_text())
        self.assertEqual(fresh, shipped)
        self.assertFalse(fresh['independence_verified'])
        self.assertEqual(sum(d['n'] for d in fresh['domains']), 36)

    def test_changed_probe_hash_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'probes.json').write_text('{"probes": []}')
            (root / 'manifest.json').write_text(json.dumps({'domains': [
                {'name': 'bad', 'pages': [], 'probes': 'probes.json', 'sha256': 'wrong'}]}))
            with self.assertRaisesRegex(ValueError, 'hash mismatch'):
                run(root / 'manifest.json')
