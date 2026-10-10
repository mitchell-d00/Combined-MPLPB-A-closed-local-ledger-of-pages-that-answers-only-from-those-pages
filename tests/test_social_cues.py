import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from tools.ledger_ui import App
from tools import social_cues as SC


class SocialCueTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name) / 'topics'
        self.app = App(topic_base=self.base)
        self.sid = self.app.chat({'corpus': 'logic', 'message': 'just chat'})['session']

    def chat(self, text):
        return self.app.chat({'corpus': 'logic', 'session': self.sid, 'message': text})['response']

    def test_screenshot_and_common_variants_without_retrieval(self):
        with patch.object(self.app, 'build_search', side_effect=AssertionError('network')):
            for q in ['How are you today', 'How are you doing tonight?', 'How have you been?',
                      'How’s it going?', 'How is your day going?', 'How are you feeling today?']:
                with self.subTest(q=q):
                    r = self.chat(q)
                    self.assertEqual(r['response_structure']['social_cue'], 'wellbeing')
                    self.assertEqual(r['authority'], 'conversation_structure')
                    self.assertEqual(r['sources'], [])
                    self.assertFalse(r['response_structure']['mplpb_supported'])
        self.assertEqual(self.app.collections.entries(), {})

    def test_variation_survives_reload_and_reciprocity(self):
        first = self.chat('How are you today?')['message']
        self.assertIn('I’m functional, thanks!', first)
        self.app = App(topic_base=self.base)
        second = self.chat('and you?')['message']
        third = self.chat('How are you today?')['message']
        self.assertEqual(len({first, second, third}), 3)
        self.assertTrue(self.app.export_chat({'session': self.sid})['chain_intact'])

    def test_followup_requires_recent_social_question(self):
        self.assertIsNone(SC.cue('good thanks', {}))
        self.assertIsNone(SC.cue('and you?', {}))
        self.assertIsNone(SC.cue('serious mode', {'log': [{'payload': {'response': {
            'response_structure': {'acts': ['greet', 'identity']}}}}]}))
        self.chat('How are you today?')
        self.assertEqual(self.chat('good thanks')['response_structure']['social_cue'], 'positive')
        self.chat('How are you today?')
        self.assertEqual(self.chat('could be better')['response_structure']['social_cue'], 'mixed')
        self.chat('What is 2 plus 2?')
        self.assertIsNone(SC.cue('and you?', self.app.sessions[self.sid]))

    def test_compound_greeting_and_ordinary_courtesies(self):
        r = self.chat('Hi! How are you today?')
        self.assertIn('functional', r['message'])
        self.assertEqual(r['sources'], [])
        self.assertEqual(self.chat('not bad')['response_structure']['social_cue'], 'positive')
        for text, kind in [('thanks', 'thanks'), ('good morning', 'greeting'), ('take care', 'farewell')]:
            self.assertEqual(self.chat(text)['response_structure']['social_cue'], kind)

    def test_literals_questions_and_listening_keep_their_handlers(self):
        for q in ['say how are you today', 'How are your pages verified?',
                  'How are you today according to this document?', 'I wonder how are you today']:
            self.assertFalse(SC.wellbeing(q))
            self.assertIsNone(SC.cue(q, {}))
        r = self.chat('say how are you today')
        self.assertNotIn('functional', r['message'])
        self.chat('I had a bad day')
        self.chat('just listen')
        r = self.chat('My boss yelled at me')
        self.assertNotIn('?', r['message'])
        self.assertEqual(r['sources'], [])
        self.assertIsNone(SC.cue('thanks', {'mind': {'social': {'active': True}}}))
