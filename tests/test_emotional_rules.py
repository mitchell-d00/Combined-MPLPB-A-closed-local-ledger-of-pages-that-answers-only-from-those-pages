import copy
import tempfile
import unittest
from pathlib import Path
from tools import emotional_rules as E
from tools.ledger_ui import App

class EmotionalRulesTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.base=Path(self.temp.name)/'topics';self.app=App(topic_base=self.base)
    def tearDown(self):self.temp.cleanup()
    def chat(self,message,sid=None):
        return self.app.chat({'corpus':'logic','message':message,'session':sid,'default_chat':True})
    def test_explicit_feelings_are_attributed_not_diagnosed(self):
        for word in ('sad','angry','worried','overwhelmed','happy','proud','lonely'):
            r=self.chat('I feel '+word)['response']
            self.assertIn(word,r['message']);self.assertEqual(r['sources'],[])
            self.assertFalse(r['response_structure']['assessment'])
            self.assertEqual(r['determination']['basis'],'conversation')
            self.assertIn('not MPLPB-supported',r['support_notice'])
    def test_negation_and_mixed_feelings(self):
        r=self.chat("I'm not sad")['response']
        self.assertEqual(r['response_structure']['intent'],'casual_emotional_correction')
        self.assertNotIn('you’re feeling sad',r['message'])
        r=self.chat('I feel happy but also nervous')['response']
        self.assertEqual(r['response_structure']['expressed_words'],['happy','nervous'])
    def test_third_party_quotes_hypotheticals_and_questions_are_not_self_reports(self):
        for msg in ('My friend is sad', 'If I am sad', '"I am sad"', 'I am sad, why is the sky blue?', 'I am not sad but happy', 'I am sad or happy'):
            self.assertIsNone(E.feeling(msg),msg)
    def test_listening_survives_reload_without_questions_or_advice(self):
        sid=self.chat('I feel lonely')['session']
        self.chat('just listen',sid)
        self.app=App(topic_base=self.base)
        for message in ('I had a long day','I feel sad'):
            r=self.chat(message,sid)['response']
            self.assertNotIn('?',r['message']);self.assertEqual(r['response_structure']['style'],'listen')
        self.assertEqual(self.app.sessions[sid]['mind']['notes'],[])
        self.assertNotIn('words',self.app.sessions[sid]['mind']['emotional'])
    def test_choice_ideas_and_correction(self):
        sid=self.chat('I feel frustrated')['session']
        r=self.chat('sure',sid)['response'];self.assertIn('listening or ideas',r['message'])
        r=self.chat('ideas',sid)['response'];self.assertEqual(r['response_structure']['style'],'ideas')
        r=self.chat('you got that wrong',sid)['response'];self.assertIn('shouldn’t assume',r['message'])
        self.chat('not now',sid)
        self.assertFalse(self.app.sessions[sid]['mind']['emotional']['active'])
    def test_no_jokes_is_respected_for_echo_and_joke_requests(self):
        sid=self.chat('no jokes')['session']
        self.assertEqual(self.chat('say potato',sid)['response']['message'],'potato')
        self.assertIn('leave jokes out',self.chat('tell me a joke',sid)['response']['message'])
        self.chat('jokes are okay',sid)
        self.assertIn('?',self.chat('say potato',sid)['response']['message'])
    def test_serious_focus_does_not_apply_emotional_response(self):
        sid=self.chat('load MPLPB')['session']
        r=self.chat('I feel sad',sid)['response']
        self.assertEqual(r['determination']['mode'],'focus')
        self.assertNotIn('emotional',r.get('response_structure',{}).get('intent',''))
    def test_same_state_same_response(self):
        state={'emotional':{'active':True,'style':'ask','turn':2,'no_jokes':False}}
        self.assertEqual(E.handle('I feel sad',copy.deepcopy(state)),E.handle('I feel sad',copy.deepcopy(state)))

    def test_listening_preference_before_feeling_is_respected(self):
        sid=self.chat('just listen')['session']
        r=self.chat('I feel sad',sid)['response']
        self.assertNotIn('?',r['message']);self.assertEqual(r['response_structure']['style'],'listen')

    def test_explicit_echo_is_not_swallowed_by_listening(self):
        sid=self.chat('just listen')['session']
        self.assertEqual(self.chat('say exactly potato',sid)['response']['message'],'potato')
        self.assertNotIn('?',self.chat('It has been a long day',sid)['response']['message'])
