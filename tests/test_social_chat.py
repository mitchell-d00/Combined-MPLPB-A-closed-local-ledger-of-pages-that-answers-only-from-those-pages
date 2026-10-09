import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from tools.ledger_ui import App
from tools import social_chat as S

class SocialChatTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.base=Path(self.temp.name)/'topics';self.app=App(topic_base=self.base)
    def tearDown(self):self.temp.cleanup()
    def chat(self,message,sid=None,corpus='logic'):
        return self.app.chat({'corpus':corpus,'session':sid,'message':message})
    def test_bad_day_acceptance_and_story_without_any_provider(self):
        with patch.object(self.app,'build_search',side_effect=AssertionError('No network')):
            first=self.chat('Iv had a bad day');sid=first['session']
            self.assertIn('Want to talk',first['response']['message'])
            accepted=self.chat('sure',sid)['response']
            self.assertIn('tell me about it',accepted['message'])
            story=self.chat('My boss yelled at me',sid)['response']
        self.assertIn('frustrating',story['message'])
        self.assertEqual(story['sources'],[]);self.assertEqual(story['authority'],'conversation_structure')
        self.assertFalse(story['response_structure']['factual_claims'])
        self.assertEqual(self.app.sessions[sid]['mind']['notes'],[])
    def test_invitation_and_listening_mode_resume_from_save(self):
        sid=self.chat("I've had a rough day")['session']
        self.app=App(topic_base=self.base)
        self.assertIn('tell me about it',self.chat('okay',sid)['response']['message'])
        self.chat('just listen',sid)
        self.app=App(topic_base=self.base)
        r=self.chat('The bus was late and I got soaked',sid)['response']
        self.assertNotIn('?',r['message']);self.assertEqual(r['response_structure']['stage'],'listen')
    def test_decline_stop_and_subject_change(self):
        sid=self.chat('I had a bad day')['session']
        self.assertEqual(self.chat('not now',sid)['response']['response_structure']['intent'],'social_decline')
        self.assertFalse(self.app.sessions[sid]['mind']['social']['active'])
        self.chat('can we talk',sid)
        r=self.chat('change the subject',sid)['response']
        self.assertEqual(r['response_structure']['intent'],'social_light')
        self.chat('stop chatting',sid)
        self.assertFalse(self.app.sessions[sid]['mind']['social']['active'])
    def test_source_questions_leave_social_flow_and_keep_topic(self):
        sid=self.chat('topic Budget guide')['session']
        self.chat('I had a bad day',sid);self.chat('sure',sid)
        result=self.chat('How big is it?',sid)['response']
        self.assertEqual(result['kind'],'unsupported');self.assertEqual(result['context']['title'],'Budget guide')
        self.assertNotIn('social',self.app.sessions[sid]['mind'])
    def test_literal_topic_offer_takes_priority_over_social_acceptance(self):
        sid=self.chat('I had a bad day')['session']
        offered=self.chat('I was struggling with Budget guide',sid)['response']
        self.assertEqual(offered['response_structure']['intent'],'topic_offer')
        self.assertNotIn('social',self.app.sessions[sid]['mind'])
        accepted=self.chat('sure',sid)['response']
        self.assertEqual(accepted['kind'],'topic');self.assertEqual(accepted['context']['title'],'Budget guide')
    def test_unrelated_turn_expires_invitation(self):
        sid=self.chat('I had a bad day')['session']
        self.chat('hello',sid)
        result=self.chat('sure',sid)['response']
        self.assertNotEqual(result.get('response_structure',{}).get('intent'),'social_accept')
    def test_negation_and_embedded_questions_are_not_emotion_facts(self):
        for text in ("I have not had a bad day",'not a bad day','If I had a bad day','I had a bad day, how big is the Moon?'):
            self.assertIsNone(S.opening(S.key(text)),text)
        state={'social':{'active':True,'stage':'story'}}
        for text in ('Why did my boss yell at me?','Who may operate a kiln?','search Moon','remember my diary','what are you?'):
            self.assertFalse(S.candidate(text,state),text)
        self.assertEqual(S.tone('Nobody yelled and I was not upset'),'neutral')
    def test_good_day_and_replies_do_not_repeat_immediately(self):
        first=self.chat('I had a great day');sid=first['session']
        self.assertIn('good day',first['response']['message'])
        self.chat('yes',sid)
        replies=[self.chat('My friend was happy',sid)['response']['message'] for _ in range(4)]
        self.assertTrue(all(a!=b for a,b in zip(replies,replies[1:])))
    def test_scope_switch_clears_pending_social_invitation(self):
        sid=self.chat('I had a bad day')['session']
        response=self.chat('sure',sid,corpus='canned')['response']
        self.assertNotEqual(response.get('response_structure',{}).get('intent'),'social_accept')
    def test_transcript_is_auditable_not_added_as_ledger_evidence(self):
        first=self.chat('I had a bad day');sid=first['session']
        self.chat('sure',sid)
        log=self.app.export_chat({'session':sid})
        self.assertTrue(log['chain_intact'])
        self.assertEqual(log['turns'][-1]['payload']['social_chat_version'],S.VERSION)
        self.assertEqual(self.app.collections.entries(),{})
