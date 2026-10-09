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
    def test_chat_request_retains_topic_on_reload(self):
        sid=self.chat('just chat')['session']
        r=self.chat('Chat about imaginary umbrella gardens',sid)['response']
        self.assertEqual(r['environment']['mode'],'chat');self.assertEqual(r['environment']['corpora'],[])
        self.assertIn('imaginary umbrella gardens',r['message']);self.assertIn('not MPLPB-supported',r['support_notice'])
        self.app=App(topic_base=self.base)
        if True:
            for q in ['tell me more','what if we lived there?','how big is it?']:
                r=self.chat(q,sid)['response'];self.assertEqual(r['response_structure']['subject'],'imaginary umbrella gardens');self.assertEqual(r['sources'],[])
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

    def test_conversation_keeps_loaded_page_and_factual_gate(self):
        corpus=self.app.create_collection({'name':'Loaded Moon'})['corpus']
        self.app.import_source({'corpus':corpus,'title':'Moon','url':'https://example.org/moon','text':'The Moon is 3474 km in diameter.'})
        def send(msg,sid=None):return self.app.chat({'corpus':corpus,'message':msg,'session':sid,'default_chat':True})
        sid=send('load MPLPB')['session'];send('topic Moon',sid)
        for message in ['hello','I feel happy','say potato','chat about space gardens','tell me more','what if they floated?']:
            r=send(message,sid)['response']
            self.assertEqual(r['environment']['mode'],'focus')
            self.assertEqual(r['environment']['corpora'],[corpus])
            self.assertEqual(r['context']['title'],'Moon')
            self.assertEqual(r['sources'],[])
            self.assertIn('not MPLPB-supported',r['support_notice'])
        self.app=App(topic_base=self.base)
        r=send('how big is it?',sid)['response']
        self.assertEqual(r['kind'],'grounded_answer');self.assertIn('3474',r['message'])
        self.assertTrue(r['sources']);self.assertNotIn('support_notice',r)
        r=send('who owns it?',sid)['response']
        self.assertNotEqual(r.get('response_structure',{}).get('intent'),'casual_idea_exploration')

    def test_polite_topic_requests_read_facts_in_both_modes(self):
        corpus=self.app.create_collection({'name':'Facts'})['corpus']
        for title,body in [('Moon','The Moon is 3474 km in diameter.'),('Banana','Banana is a fruit.')]:
            self.app.import_source({'corpus':corpus,'title':title,'url':'https://example.org/'+title,'text':body})
        for mode in ['just chat','load all MPLPB']:
            sid=self.chat(mode)['session']
            for topic in ['the moon','a banana']:
                r=self.chat('Can you chat about '+topic,sid)['response']
                self.assertTrue(r['sources']);self.assertEqual(r['response_structure']['intent'],'source_exploration')
                self.assertEqual(r['environment']['mode'],'chat' if mode=='just chat' else 'focus')
                more=self.chat('tell me more',sid)['response'];self.assertTrue(more['sources'])
            r=self.chat('Could you please talk about the Moon?',sid)['response'];self.assertIn('3474',r['message'])
            r=self.chat('how big is it?',sid)['response'];self.assertIn('3474',r['message'])

    def test_factual_chat_keeps_collection_citations_with_existing_focus(self):
        keys=[]
        for title,body in [('Moon','The Moon is 3474 km in diameter.'),('Banana','Banana is a fruit.')]:
            key=self.app.create_collection({'name':title+' citations'})['corpus'];keys.append(key)
            self.app.import_source({'corpus':key,'title':title,'url':'https://example.org/'+title,'text':body})
        sid=self.chat('load all MPLPB')['session']
        self.chat('focus '+keys[0]+' :: Moon',sid)
        r=self.chat('Can you chat about a banana',sid)['response']
        self.assertEqual(r['context']['title'],'Moon')
        self.assertTrue(r['sources'])
        self.assertEqual({s['corpus'] for s in r['sources']},{keys[1]})

    def test_screenshot_tell_me_phrasing_and_relevant_buttons(self):
        key=self.app.create_collection({'name':'Moon details'})['corpus']
        self.app.import_source({'corpus':key,'title':'Moon','url':'https://example.org/moon','text':'The Moon is 3474 km in diameter. It orbits Earth.'})
        for mode in ['just chat','load all MPLPB']:
            sid=self.chat(mode)['session']
            r=self.chat('Can you tell me about the moon',sid)['response']
            self.assertTrue(r['sources']);self.assertIn('3474',r['message'])
            self.assertNotIn('Source:',r['message'])
            self.assertTrue(all('moon' in button.lower() for button in r['suggestions']))
            self.assertNotIn('focus canned',str(r['suggestions']))
            r=self.chat('Could you tell me how big it is?',sid)['response']
            self.assertIn('3474',r['message'])
    def test_attribution_only_capture_is_not_a_factual_answer(self):
        key=self.app.create_collection({'name':'Empty capture'})['corpus']
        self.app.import_source({'corpus':key,'title':'EmptyZorb','url':'https://example.org/zorb','text':'EmptyZorb\nSource: https://example.org/zorb License: CC BY-SA 4.0;'})
        r=self.chat('Can you tell me about EmptyZorb')['response']
        self.assertFalse(r['sources'])
        self.assertFalse(r['response_structure']['factual_claims'])

    def test_more_advances_through_source_sentences(self):
        key=self.app.create_collection({'name':'Many facts'})['corpus']
        self.app.import_source({'corpus':key,'title':'Zorb planet','url':'https://example.org/zorb','text':'Zorb is fictional. It has rings. Its rings are blue. It has two moons.'})
        sid=self.chat('Tell me about Zorb planet')['session']
        r=self.chat('Tell me more about Zorb planet',sid)['response']
        self.assertIn('rings are blue',r['message']);self.assertNotIn('Zorb is fictional',r['message'])
        r=self.chat('tell me more',sid)['response']
        self.assertTrue(r['source_exhausted'])
        self.assertFalse(any('tell me more' in s.lower() for s in r['suggestions']))
        self.app.import_source({'corpus':key,'title':'Zorb planet discoveries','url':'https://example.org/new','text':'New telescopes detected mountains.'})
        r=self.chat('tell me more',sid)['response']
        self.assertIn('detected mountains',r['message'])
        self.assertNotIn('Zorb is fictional',r['message'])
