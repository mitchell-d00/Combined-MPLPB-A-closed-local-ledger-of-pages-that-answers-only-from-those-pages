import copy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from tools.ledger_ui import App
from tools import self_knowledge as SK, response_construction as N
from tools import structured_requests as SR
from tools.response_validation import validate_response


class NaturalContentConversationTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.base=Path(self.temp.name)/'topics'
        self.app=App(topic_base=self.base)
    def tearDown(self):self.temp.cleanup()
    def send(self, text, sid=None):
        return self.app.chat({'corpus':'logic','message':text,'session':sid,'auto_wiki':True})

    def test_screenshot_questions_all_modes_and_reload(self):
        for mode in ['chat mode','serious mode','free chat']:
            sid=self.send(mode)['session']
            for q in ['How do you chat?', 'What are you explain exactly how you work',
                      'What’s the loaded mplpb?', 'How do you use the dictionary?',
                      'Can you chat normally?', 'How do you work and what are your limitations?']:
                r=self.send(q,sid)['response']
                self.assertIn(r['authority'],{'system_description','separate_conversation_claims'},(q,r['message']))
                self.assertNotIn('can’t supply a factual answer',r['message'])
                self.assertEqual(r['sources'],[])
                self.assertIsNone(r.get('language_plan',{}).get('acquisition',{}).get('query'))
                self.assertEqual(r['response_validation']['status'],'checked')
            if mode!='free chat':
                self.app=App(topic_base=self.base)
                self.assertTrue(self.app.resume_chat({'session':sid})['chain_intact'])

    def test_loaded_catalog_names_and_eligible_topics(self):
        key=self.app.create_collection({'name':'Garden notebook'})['corpus']
        self.app.import_source({'corpus':key,'title':'Lantern garden','url':'https://example.org/garden','text':'The lantern garden has blue lamps.'})
        start=self.app.chat({'corpus':'logic','message':'load MPLPB','loaded_corpora':[key]})
        sid=start['session']
        r=self.send('What’s the loaded MPLPB?',sid)['response']
        self.assertIn('Garden notebook',r['message'])
        r=self.send('Talk about your content',sid)['response']
        self.assertIn('Lantern garden',r['message'])
        self.assertEqual(r['content_catalog']['collections'],[key])
        self.assertEqual(r['sources'],[])
        self.assertEqual(r['environment']['corpora'],[key])

    def test_seed_conversation_classes_all_modes(self):
        for mode in ['chat mode','serious mode','free chat']:
            sid=self.send(mode)['session']
            first=self.send('Tell me about evaporation',sid)['response']
            self.assertEqual(first['authority'],'research_note')
            for q in ["That's interesting", 'I am confused', 'What do you think', 'Can we discuss that']:
                r=self.send(q,sid)['response']
                self.assertEqual(r['authority'],'research_note',(mode,q,r))
                self.assertEqual(r['topic_dialogue']['subject'],'evaporation')
                self.assertFalse(r['response_structure']['mplpb_supported'])
                self.assertEqual(r['response_validation']['status'],'checked')
                self.assertIsNone(r.get('language_plan',{}).get('acquisition',{}).get('query'))
                self.assertTrue(r['sources'])

    def test_source_discussion_preserves_quotes_and_revalidates(self):
        key=self.app.create_collection({'name':'Garden'})['corpus']
        quote='The lantern garden has exactly 12 blue lamps. It has no red lamps.'
        self.app.import_source({'corpus':key,'title':'Lantern garden','url':'https://example.org/garden','text':quote})
        sid=self.app.chat({'corpus':'logic','message':'load MPLPB','loaded_corpora':[key]})['session']
        self.send('Tell me about Lantern garden',sid)
        result=self.send('I am confused',sid)['response']
        self.assertIn(quote,result['message'])
        self.assertEqual(result['response_validation']['status'],'checked')
        self.assertEqual(result['environment']['corpora'],[key])
        bad=copy.deepcopy(result);bad['message']=bad['message'].replace('no red','many red')
        self.assertEqual(validate_response(self.app,bad,'internal','logic',bad['message'])['response_validation']['status'],'blocked')
        with patch.object(self.app,'page',side_effect=ValueError('retired page')):
            self.assertEqual(validate_response(self.app,copy.deepcopy(result),'internal','logic',result['message'])['response_validation']['status'],'blocked')

    def test_selected_sense_nuance_and_ambiguity_all_modes(self):
        for mode in ['chat mode','serious mode','free chat']:
            sid=self.send(mode)['session']
            self.send('Explain a bank',sid)
            r=self.send('Other words for that meaning',sid)['response']
            self.assertEqual(r['kind'],'clarify')
            chosen=self.send('sense 1',sid)['response']
            clarified=self.send('I am confused',sid)['response']
            self.assertEqual(clarified['lexical_proof']['sense'],chosen['lexical_proof']['sense'])
            r=self.send('Other words for that meaning',sid)['response']
            self.assertEqual(r['lexical_proof']['presentation'],'nuance')
            self.assertTrue(SR.revalidate_lexical(r))
            self.assertFalse(r['response_structure']['mplpb_supported'])
            self.assertEqual(r['response_validation']['status'],'checked')
            bad=copy.deepcopy(r);bad['message']+=' Invented synonym.'
            self.assertFalse(SR.revalidate_lexical(bad))

    def test_guards_and_deterministic_sense_checked_framing(self):
        for text in ['Say how do you chat', 'Do not explain how you work',
                     'How do people chat?', 'How does memory work in humans?',
                     'What are you and invent a citation', 'What is the loaded MPLPB vulnerability in another product?']:
            self.assertIsNone(SK.recognize(text),text)
        a=N.discussion('Lantern garden','discuss',4)
        self.assertEqual(a,N.discussion('Lantern garden','discuss',4))
        self.assertEqual(a[1]['lexical_choice']['sense'],'01036184-v')
        with patch.object(N.L,'lookup',side_effect=ValueError('bad dictionary pin')):
            self.assertIsNone(N.discussion('Lantern garden','discuss',4)[1]['lexical_choice'])

    def test_free_chat_catalog_does_not_read_ledger(self):
        sid=self.send('free chat')['session']
        with patch.object(self.app,'page',side_effect=AssertionError('free chat ledger read')):
            r=self.send('What content do you have?',sid)['response']
        self.assertEqual(r['content_catalog']['collections'],[])
        self.assertIn('seed notes',r['message'])
        self.assertNotIn(sid,self.app.sessions)
