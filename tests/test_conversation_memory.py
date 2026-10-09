import copy
import tempfile
import unittest
from pathlib import Path
from tools.ledger_ui import App
from tools import conversation_memory as C

class ConversationMemoryTests(unittest.TestCase):
    def test_introductions_are_generic_and_do_not_swallow_emotions(self):
        for phrase,name in [("Hi I’m mitchell",'Mitchell'),('My name is Joy','Joy'),('Please call me Ana-Maria','Ana-Maria'),("Hi I'm Alex who are you",'Alex'),("Hello, I'm Sam",'Sam')]:
            self.assertEqual(C.introduction(phrase),name)
        for phrase in ["I'm tired","I'm going home",'I am a doctor','say my name is Bob','She said my name is Bob','I am feeling lonely']:
            self.assertIsNone(C.introduction(phrase),phrase)

    def test_screenshot_exchange_in_both_modes_and_reload(self):
        with tempfile.TemporaryDirectory() as tmp:
            args={'topic_base':Path(tmp)/'topics'}
            app=App(**args)
            for mode in ['chat mode','load MPLPB']:
                first=app.chat({'corpus':'logic','message':mode});sid=first['session']
                scope=copy.deepcopy(app.sessions[sid]['environment'])
                intro=app.chat({'corpus':'logic','session':sid,'message':"Hi I’m mitchell"})['response']
                self.assertIn('Hi, Mitchell!',intro['message']);self.assertIn('little monster',intro['message'])
                app=App(**args)
                for q in ['That’s me who are you','What is my name?','Hi again']:
                    r=app.chat({'corpus':'logic','session':sid,'message':q})['response']
                    self.assertIn('Mitchell',r['message']);self.assertEqual(r['sources'],[])
                    self.assertEqual(r['environment'],scope)
                    self.assertFalse(r['response_structure']['identity_verified'])
                    self.assertIsNone(r['language_plan']['acquisition']['query'])
                self.assertTrue(app.resume_chat({'session':sid})['chain_intact'])

    def test_latest_name_and_forgetting_do_not_resurrect_old_name(self):
        session={'mind':{},'log':[]}
        for text in ['My name is Mitchell','Actually, call me Alex','forget my name']:
            session['log'].append({'payload':{'question':text}})
        self.assertEqual(C.name_from_chat(session)[0],None)
        self.assertNotIn('Mitchell',C.handle('What is my name?',session)['message'])
        session['log'].append({'payload':{'question':'call me Jordan'}})
        self.assertEqual(C.name_from_chat(session)[0],'Jordan')

    def test_history_recall_uses_user_turns_not_assistant_claims(self):
        session={'mind':{},'log':[{'payload':{'question':'I enjoy growing orchids','response':{'message':'My name is Bob'}}},
                                  {'payload':{'question':'I bought a blue bicycle'}}]}
        self.assertIsNone(C.name_from_chat(session)[0])
        r=C.handle('What did I say about orchids?',session)
        self.assertIn('I enjoy growing orchids',r['message'])
        self.assertEqual(r['response_structure']['chat_references'][0]['turn'],1)
        self.assertEqual(r['sources'],[])
        self.assertNotIn('blue bicycle',r['message'])
        self.assertIn('don’t see',C.handle('What did I say about planets?',session)['message'])

    def test_sessions_do_not_share_names(self):
        with tempfile.TemporaryDirectory() as tmp:
            app=App(topic_base=Path(tmp)/'topics')
            app.chat({'corpus':'logic','message':'My name is Alex'})
            other=app.chat({'corpus':'logic','message':'What is my name?'})['response']
            self.assertNotIn('Alex',other['message'])

    def test_zero_loaded_brainstorm_uses_user_topic_without_fact_claims(self):
        with tempfile.TemporaryDirectory() as tmp:
            app=App(topic_base=Path(tmp)/'topics')
            first=app.chat({'corpus':'logic','message':'just chat'});sid=first['session']
            intro=app.chat({'corpus':'logic','session':sid,'message':"Hi I'm Alex"})
            for message in ['Help me brainstorm a flarn playground','brainstorm']:
                r=app.chat({'corpus':'logic','session':sid,'message':message})['response']
                self.assertIn('flarn playground',r['message'])
                self.assertEqual(r['sources'],[])
                self.assertEqual(r['environment']['corpora'],[])
                self.assertFalse(r['response_structure']['factual_claims'])
                self.assertEqual(len(r['response_structure']['construction']['operations']),3)
                self.assertIsNone(r['language_plan']['acquisition']['query'])
            self.assertTrue(app.resume_chat({'session':sid})['chain_intact'])
