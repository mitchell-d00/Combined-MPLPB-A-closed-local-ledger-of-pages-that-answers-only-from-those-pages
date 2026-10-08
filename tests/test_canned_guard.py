import unittest
from mplpb_combined import reader as R


class CannedGuardTests(unittest.TestCase):
    def test_uneven_complete_names_stop_before_majority(self):
        d = {'frog': R.terms('Phrynomedusa vanzolinii'),
             'company': R.terms('Hyundai Engineering and Construction')}
        self.assertEqual(R.decide(set.union(*d.values()), d),
                         (R.AMBIGUOUS, ['frog', 'company'], 'scope'))
        for key, words in d.items():
            self.assertEqual(R.decide(words, d), (R.RETURN, [key], 'scope'))

    def test_complete_names_still_stop_with_extra_unknown_words(self):
        d = {'short': {'frog'}, 'long': {'hyundai', 'engineering', 'construction'}}
        self.assertEqual(R.decide(set.union(*d.values()) | {'zebra', 'unknown'}, d),
                         (R.AMBIGUOUS, ['short', 'long'], 'scope'))

    def test_nested_scopes_preserve_specificity(self):
        d = {'broad': {'kiln'}, 'specific': {'kiln', 'firing'}}
        self.assertEqual(R.decide({'kiln', 'firing'}, d), (R.RETURN, ['specific'], 'scope'))

    def test_duplicate_declarations_remain_ambiguous(self):
        self.assertEqual(R.decide({'cat'}, {'a': {'cat'}, 'b': {'cat'}}),
                         (R.AMBIGUOUS, ['a', 'b'], 'scope'))

    def test_partial_scope_still_uses_majority(self):
        d = {'a': {'alpha', 'beta', 'missing'}, 'b': {'gamma', 'missing'}}
        self.assertEqual(R.decide({'alpha', 'beta', 'gamma'}, d),
                         (R.RETURN, ['a'], 'scope'))

    def test_empty_declarations_do_not_block_prose(self):
        self.assertEqual(R.decide({'zebra'}, {'a': set(), 'b': set()},
                                 {'a': {'zebra'}, 'b': {'cat'}}),
                         (R.RETURN, ['a'], 'prose'))
