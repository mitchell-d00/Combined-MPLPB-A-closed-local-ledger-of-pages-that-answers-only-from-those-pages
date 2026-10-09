import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from tools.ledger_ui import App
from tools import casual_reasoning as D

class CasualReasoningTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.base=Path(self.temp.name)/'topics';self.app=App(topic_base=self.base)
    def tearDown(self):self.temp.cleanup()
    def chat(self,message,sid=None):
        return self.app.chat({'corpus':'logic','message':message,'session':sid,'default_chat':True})
    def test_screenshot_conversation_without_pressing_just_chat(self):
        sid=None
        for message,intent in [("I'm bored",'casual_ideas'),('So you arnt an ai?','casual_identity'),('What are you','casual_identity'),('What are the rules','casual_rules'),('So hi?','casual_greeting')]:
            result=self.chat(message,sid);sid=result['session'];r=result['response']
            self.assertEqual(r['response_structure']['intent'],intent)
            self.assertEqual(r['environment']['mode'],'chat');self.assertEqual(r['sources'],[])
            self.assertEqual(r['support_notice'],D.NOTICE);self.assertNotIn('source_offer',r)
            self.assertFalse(r['response_structure']['mplpb_supported'])
    def test_old_save_migrates_without_reset_or_source_read(self):
        sid=self.app.chat({'corpus':'logic','message':'remember I like books'})['session']
        self.assertNotIn('environment',self.app.sessions[sid])
        before=len(self.app.sessions[sid]['log'])
        self.app=App(topic_base=self.base)
        with patch.object(self.app,'root',side_effect=AssertionError('No ledger read')):
            r=self.chat('So you arnt an ai?',sid)['response']
        self.assertEqual(r['environment']['corpora'],[])
        self.assertEqual(len(self.app.sessions[sid]['log']),before+1)
        self.assertEqual(self.app.sessions[sid]['mind']['notes'],['I like books'])
    def test_followup_survives_reload_and_expires_after_unrelated_turn(self):
        sid=self.chat('So you arnt an ai?')['session']
        self.app=App(topic_base=self.base)
        r=self.chat('how?',sid)['response']
        self.assertEqual(r['response_structure']['intent'],'casual_construction')
        r=self.chat('tell me more',sid)['response']
        self.assertEqual(r['response_structure']['intent'],'casual_rules')
        self.chat('My bike has a blue basket',sid)
        r=self.chat('why?',sid)['response']
        self.assertNotEqual(r.get('response_structure',{}).get('intent'),'casual_rules')
    def test_negation_typo_variants_and_embedded_questions(self):
        for q in ("So you're not an AI?",'You arent an llm right?','Are you an AI?','What are your rules?','Well, hello?'):
            self.assertIsNotNone(D.respond(q,{}),q)
        for q in ('So hi, who won the election?','What are the rules for kiln operation?','Are you an AI that can diagnose my illness?'):
            self.assertIsNone(D.respond(q,{}),q)
    def test_deterministic_replay_and_labeled_fiction(self):
        memory={'chat_discourse':{'turn':4,'topic':'identity'}}
        self.assertEqual(D.respond('tell me more',copy.deepcopy(memory)),D.respond('tell me more',copy.deepcopy(memory)))
        r=self.chat('tell me a story')['response']
        self.assertIn('made-up story',r['message']);self.assertEqual(r['sources'],[])
        self.assertEqual(r['support_notice'],D.NOTICE)
    def test_focus_cannot_be_bypassed_by_casual_question(self):
        sid=self.chat('load MPLPB')['session']
        self.chat('topic Budget guide',sid)
        r=self.chat('So you arnt an ai?',sid)['response']
        self.assertEqual(r['environment']['mode'],'focus')
        self.assertEqual(r['kind'],'conversation');self.assertIn('support_notice',r)
        self.assertEqual(r['context']['title'],'Budget guide')
    def test_dictionary_retains_its_own_reference_authority(self):
        sid=self.chat('So hi?')['session']
        r=self.chat('define dog',sid)['response']
        self.assertEqual(r['authority'],'lexical_reference');self.assertTrue(r['sources'])
        self.assertNotIn('support_notice',r)
    def test_invitation_acceptance_is_not_swallowed_by_help(self):
        sid=self.chat('I had a bad day')['session']
        self.assertEqual(self.chat('okay',sid)['response']['response_structure']['intent'],'social_accept')

    def test_playful_echo_and_saved_followup(self):
        r=self.chat('say potato');sid=r['session']
        self.assertTrue(r['response']['message'].startswith('potato'))
        self.assertIn('?',r['response']['message'])
        self.assertEqual(r['response']['support_notice'],D.NOTICE)
        self.app=App(topic_base=self.base)
        self.assertEqual(self.chat('again',sid)['response']['message'],'potato')
        self.assertIn('Fair enough',self.chat('just because',sid)['response']['message'])
    def test_echo_preserves_case_and_exact_requests(self):
        for prompt,expected in [('say exactly PoTaTo!','PoTaTo!'),('repeat after me: Hello there','Hello there'),('say only banana','banana')]:
            r=self.chat(prompt)['response']
            self.assertEqual(r['message'],expected);self.assertEqual(r['sources'],[])
        self.assertTrue(self.chat('Could you say potato?')['response']['message'].startswith('potato'))
    def test_echo_is_text_not_a_command_or_evidence(self):
        with patch.object(self.app,'build_search',side_effect=AssertionError('No network')):
            r=self.chat('say exactly search Moon')['response']
        self.assertEqual(r['message'],'search Moon');self.assertFalse(r['response_structure']['execute_text'])
        self.assertEqual(r['sources'],[])
        r=self.chat('say '+'x'*301)['response']
        self.assertIn('300 characters',r['message'])
