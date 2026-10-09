import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from tools.ledger_ui import App
from tools import deterministic_mind as M

class TutorTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.base=Path(self.temp.name)/'topics';self.app=App(topic_base=self.base)
    def tearDown(self):self.temp.cleanup()
    def chat(self,message,sid=None,corpus='logic'):
        return self.app.chat({'corpus':corpus,'message':message,'session':sid})

    def test_guide_steps_resume_and_stop_without_resetting_notes(self):
        first=self.chat('topic Dungeons and Dragons');sid=first['session']
        self.chat('remember my research',sid)
        guide=self.chat('Guide me',sid)
        self.assertEqual(guide['response']['guide']['step'],1)
        self.assertEqual(self.chat('next step',sid)['response']['guide']['step'],2)
        chosen=self.chat('dinosaurs',sid)
        self.assertIn('search dinosaurs',chosen['response']['suggestions'])
        self.assertEqual(self.app.collections.entries(),{})
        self.app=App(topic_base=self.base)
        self.assertEqual(self.chat('continue guide',sid)['response']['guide']['step'],3)
        self.assertEqual(self.chat('previous step',sid)['response']['guide']['step'],2)
        stop=self.chat('stop guide',sid)
        self.assertEqual(stop['mind']['notes'],['my research'])
        self.assertEqual(stop['response']['context'],first['response']['context'])
        self.assertFalse(self.app.sessions[sid]['mind']['guide']['active'])

    def test_ask_help_works_with_blocked_source_but_factual_query_still_stops(self):
        key=self.app.create_collection({'name':'Blocked'})['corpus']
        self.app.import_source({'corpus':key,'title':'Fossils','url':'https://example.org/fossils','text':'Fossils show ancient life.'})
        entry=self.app.collections.entries()[key]['captures'][0]
        (self.app.collections.path(key)/'captures'/entry['id']/'source.bin').write_bytes(b'tampered')
        result=self.app.query({'corpus':key,'question':'How do I clear mplpb some or all?'})
        self.assertEqual(result['reader']['kind'],'help')
        self.assertEqual(result['gate']['sources'],[])
        self.assertIn('Clear selected MPLPBs',result['help']['message'])
        self.assertIn(key,self.app.collections.entries())
        with self.assertRaises(ValueError):self.app.query({'corpus':key,'question':'Fossils'})

    def test_natural_help_does_not_claim_semantic_world_answers(self):
        for question in ('How can I remove all my collections?','Please explain how to use this app','Where do I export my chat?'):
            self.assertIsNotNone(M.help_reply(question,None),question)
        for question in ('How does it clear water?','How do I save a dog from drowning?','Who built the first computer?'):
            self.assertIsNone(M.help_reply(question,None),question)

    def test_collection_presentation_has_exact_topic_choices(self):
        result=self.chat('Show my MPLPB')['response']
        self.assertEqual(result['kind'],'collection')
        self.assertIn('Dungeons and Dragons',result['message'])
        self.assertIn('topic Dungeons and Dragons',result['suggestions'])
        self.assertEqual(result['authority'],'local_inventory')

    def test_learning_request_offers_choices_without_remote_action(self):
        with patch.object(self.app,'prepare_search',side_effect=AssertionError('No automatic crawl')):
            result=self.chat('I want to learn about fossils')['response']
        self.assertEqual(result['kind'],'help')
        self.assertIn('search fossils',result['suggestions'])
        self.assertEqual(self.app.collections.entries(),{})
        self.assertEqual(result['sources'],[])

    def test_natural_summary_alias_preserves_source_pins_and_trace(self):
        first=self.chat('topic Dungeons and Dragons')
        answer=self.chat('Can you summarize this?',first['session'])['response']
        self.assertEqual(answer['kind'],'summary')
        self.assertEqual(answer['sources'][0],first['response']['context'])
        self.assertTrue(any(isinstance(r,dict) and r.get('rule')=='PHRASE-1' for r in answer['reasoning']))

    def test_topic_conversation_has_no_facts_and_retains_selected_topic(self):
        first=self.chat('topic Dungeons and Dragons');sid=first['session']
        with patch.object(self.app,'build_search',side_effect=AssertionError('No conversation crawl')):
            answer=self.chat("Let's talk about it",sid)['response']
        self.assertEqual(answer['kind'],'conversation')
        self.assertEqual(answer['sources'],[])
        self.assertEqual(answer['context'],first['response']['context'])
        self.assertFalse(answer['response_structure']['factual_claims'])
        self.assertIn('Dungeons and Dragons',answer['message'])
        self.assertIn('summarize it',answer['suggestions'])
        summary=self.chat('summarize it',sid)['response']
        self.assertTrue(summary['sources'])

    def test_conversation_style_survives_reload_and_confusion_without_topic(self):
        first=self.chat('Give me more detail');sid=first['session']
        self.app=App(topic_base=self.base)
        answer=self.chat("I'm confused",sid)['response']
        self.assertEqual(answer['response_structure']['style'],'detailed')
        self.assertIsNone(answer['response_structure']['topic'])
        self.assertIn('guide me',answer['suggestions'])
        self.assertEqual(self.chat('keep it short',sid)['response']['response_structure']['style'],'brief')

    def test_world_questions_do_not_become_conversation(self):
        from tools import chat_tutor as T
        for question in ('Why did dinosaurs go extinct?','What do you think caused extinction?','How do fossils form?'):
            self.assertIsNone(T.conversation(question,None,{}))
