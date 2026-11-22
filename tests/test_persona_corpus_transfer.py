"""Replay the synthetic persona panel and protect its scoring boundaries."""
import unittest

from test_tools.persona_corpus_transfer import classify, run


class PersonaCorpusTransferTests(unittest.TestCase):
    def test_real_reader_replay(self):
        report = run()
        self.assertEqual(len(report['collections']), 8)
        self.assertEqual(report['by_family']['bounded_field']['exact_supported'], 8)
        self.assertEqual(report['by_family']['scope_overreach']['withheld'], 8)
        self.assertEqual(report['by_family']['absent_fact']['withheld'], 8)
        self.assertEqual(sum(report['by_family']['record_description_instead_of_id'].values()), 8)

    def test_scorer_flags_offer_of_support_on_withhold_control(self):
        self.assertEqual(classify({'expected': 'withhold'}, {'answer_supported': True}, {}),
                         'unexpected_support')
        self.assertEqual(classify({'expected': 'withhold'},
                                  {'answer_supported': False, 'kind': 'partial_answer'}, {}),
                         'review_partial')
