import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from tools.ledger_ui import App

class IdeaChatTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.base=Path(self.tmp.name)/'topics';self.app=App(topic_base=self.base)
    def tearDown(self):self.tmp.cleanup()
    def chat(self,text,sid=None):return self.app.chat({'corpus':'logic','message':text,'session':sid,'default_chat':True})
    def test_chat_request_leaves_serious_and_retains_topic_on_reload(self):
        sid=self.chat('load MPLPB')['session']
        r=self.chat('Chat about moons',sid)['response']
        self.assertEqual(r['environment']['mode'],'chat');self.assertEqual(r['environment']['corpora'],[])
        self.assertIn('moons',r['message']);self.assertIn('not MPLPB-supported',r['support_notice'])
        self.app=App(topic_base=self.base)
        if True:
            for q in ['tell me more','what if we lived there?','how big is it?']:
                r=self.chat(q,sid)['response'];self.assertEqual(r['response_structure']['subject'],'moons');self.assertEqual(r['sources'],[])
        self.assertIn('verified answer',r['message'])
    def test_topic_mentions_stay_chat_and_explicit_serious_stays_serious(self):
        sid=self.chat('just chat')['session']
        for q in ['talk about MPLPB','explore an idea about floating gardens']:
            r=self.chat(q,sid)['response'];self.assertEqual(r['environment']['mode'],'chat')
        self.chat('serious mode',sid)
        r=self.chat('what if we lived there?',sid)['response']
        self.assertEqual(r['environment']['mode'],'focus');self.assertNotEqual(r.get('response_structure',{}).get('intent'),'casual_idea_exploration')
    def test_reset_discards_topic(self):
        sid=self.chat('chat about moons')['session'];self.chat('just chat',sid)
        self.assertNotIn('idea_chat',self.app.sessions[sid]['mind'])

    def test_saved_sources_are_available_in_chat_without_loading(self):
        corpus=self.app.create_collection({'name':'Moon source'})['corpus']
        self.app.import_source({'corpus':corpus,'title':'Moon','url':'https://example.org/moon','text':'The Moon is 3474 km in diameter.'})
        sid=self.chat('chat about Moon')['session']
        r=self.chat('how big is it?',sid)['response']
        self.assertEqual(r['environment']['mode'],'chat')
        self.assertEqual(r['environment']['corpora'],[])
        self.assertTrue(r['sources']);self.assertIn('3474',r['message'])
        self.assertIsNone(r['context'])
        self.assertTrue(r['response_structure']['mplpb_supported'])
