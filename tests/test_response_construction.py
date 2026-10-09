import unittest
from unittest.mock import patch
from tools import response_construction as N
from tools import social_chat as S


class ResponseConstructionTests(unittest.TestCase):
    def test_replay_and_novel_user_detail(self):
        text = 'My purple bicycle broke beside the bakery'
        a = N.social(text, 'neutral', 4)
        self.assertEqual(a, N.social(text, 'neutral', 4))
        self.assertIn('«'+text+'»', a[0])
        self.assertFalse(a[1]['user_quote_is_evidence'])
        self.assertNotEqual(a[0], N.social('My blue bicycle broke', 'neutral', 4)[0])

    def test_real_wordnet_sense_and_grammar(self):
        results = [N.social('I worked overtime', 'tired', i) for i in range(1, 9)]
        self.assertGreater(len({r[0] for r in results}), 4)
        for body, trace in results:
            self.assertEqual(trace['lexical_choice']['sense'], '00840788-s')
            self.assertIn(trace['lexical_choice']['word'], body)
            self.assertTrue(trace['lexical_choice']['definition'])
            self.assertTrue(body.endswith('?'))

    def test_wrong_sense_or_part_of_speech_is_not_used(self):
        for sense in ({'id':'wrong','part_of_speech':'a','definitions':['x'],'synonyms':['exhausting']},
                      {'id':'00840788-s','part_of_speech':'n','definitions':['x'],'synonyms':['exhausting']}):
            with patch.object(N.L, 'lookup', return_value=([sense], {})):
                body, trace = N.social('overtime', 'tired', 1)
                self.assertIsNone(trace['lexical_choice'])
                self.assertNotIn('exhausting', body)

    def test_missing_reference_degrades_to_neutral_without_network(self):
        with patch.object(N.L, 'lookup', side_effect=ValueError('pin mismatch')):
            body, trace = N.social('A story', 'tired', 1)
        self.assertIsNone(trace['lexical_choice'])
        self.assertIn('I’m following.', body)

    def test_listening_and_negation_do_not_assign_feelings(self):
        body, trace = N.social('I was not upset', S.tone('i was not upset'), 1)
        self.assertIsNone(trace['lexical_choice'])
        body, trace = N.social('I was upset', 'sad', 2, listening=True)
        self.assertNotIn('?', body)
        self.assertIsNone(trace['user_quote'])
        self.assertIsNone(trace['lexical_choice'])

    def test_long_or_markup_disclosures_are_not_repeated_or_truncated(self):
        for message in ('A'*181+' but that never happened', '<script>alert(1)</script>', 'quote «nested»'):
            body, trace = N.social(message, 'neutral', 1)
            self.assertIsNone(trace['user_quote'])
            self.assertNotIn(message, body)

    def test_no_immediate_repeat(self):
        body, _ = N.social('Same story', 'neutral', 1)
        again, _ = N.social('Same story', 'neutral', 1, previous=body)
        self.assertNotEqual(body, again)

    def test_context_wrapping_does_not_generate_facts(self):
        self.assertEqual(N.source_intro('Moon', 'diameter'),
                         'For diameter, the loaded page “Moon” says:')


if __name__ == '__main__':
    unittest.main()
