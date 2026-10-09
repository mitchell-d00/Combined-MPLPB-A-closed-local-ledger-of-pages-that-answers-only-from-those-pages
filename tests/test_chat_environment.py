import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from tools.ledger_ui import App

class ChatEnvironmentTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.base=Path(self.temp.name)/'topics';self.app=App(topic_base=self.base)
        self.a=self.app.create_collection({'name':'Moon A'})['corpus']
        self.b=self.app.create_collection({'name':'Moon B'})['corpus']
        for key,size in [(self.a,'10'),(self.b,'20')]:
            self.app.import_source({'corpus':key,'title':'Moon','url':'https://example.org/moon','text':'The Moon is '+size+' km in diameter.'})
    def tearDown(self):self.temp.cleanup()
    def chat(self,msg,sid=None,**extra):
        return self.app.chat({'corpus':self.a,'message':msg,'session':sid,**extra})
    def test_empty_chat_answers_self_question_without_accessing_sources(self):
        sid=self.chat('just chat')['session']
        with patch.object(self.app,'root',side_effect=AssertionError('No ledger read')):
            r=self.chat('How do you think?',sid)['response']
        self.assertIn('explicit rules',r['message']);self.assertEqual(r['sources'],[])
        self.assertEqual(r['environment']['corpora'],[])
        self.assertEqual(self.chat('What is happiness?',sid)['response']['authority'],'lexical_reference')
    def test_selected_scope_and_duplicate_titles(self):
        sid=self.chat('load MPLPB',loaded_corpora=[self.a,self.b])['session']
        r=self.chat('topic Moon',sid)['response']
        self.assertIsNone(r['context']);self.assertEqual(len(r['suggestions']),2)
        r=self.chat('focus '+self.b+' :: Moon',sid)['response']
        self.assertEqual(r['source_corpus'],self.b)
        r=self.chat('how big is it?',sid)['response']
        self.assertIn('20 km',r['message']);self.assertNotIn('10 km',r['message'])
        self.assertEqual(r['sources'][0]['corpus'],self.b)
    def test_all_mode_snapshot_and_federated_conflicts(self):
        sid=self.chat('load all MPLPB')['session']
        self.assertEqual(set(self.app.sessions[sid]['environment']['corpora']),set(self.app.roots()))
        # Narrow the experiment to its synthetic fixtures.
        self.chat('load MPLPB',sid,loaded_corpora=[self.a,self.b])
        r=self.chat('how big is Moon?',sid)['response']
        self.assertEqual(r['kind'],'conflict');self.assertEqual(len(r['scope_results']),2)
        self.assertEqual({s['corpus'] for s in r['sources']},{self.a,self.b})
        self.assertIsNone(r['context'])
    def test_empty_selection_and_reload(self):
        sid=self.chat('load MPLPB',loaded_corpora=[self.a,self.b])['session']
        self.chat('focus '+self.a+' :: Moon',sid)
        self.app=App(topic_base=self.base)
        self.assertIn('10 km',self.chat('how big is it?',sid)['response']['message'])
        self.chat('load MPLPB',sid,loaded_corpora=[])
        self.app=App(topic_base=self.base)
        r=self.chat('how big is it?',sid)['response']
        self.assertEqual(r['environment']['mode'],'chat');self.assertEqual(r['sources'],[])
        self.assertIsNone(r['context'])
    def test_out_of_scope_selection_and_invalid_scope(self):
        sid=self.chat('load MPLPB',loaded_corpora=[self.a])['session']
        r=self.chat('focus '+self.b+' :: Moon',sid)['response']
        self.assertIsNone(r['context']);self.assertEqual(r['sources'],[])
        for keys in ([self.a,self.a],['missing'],42):
            with self.assertRaises(ValueError):self.chat('load MPLPB',sid,loaded_corpora=keys)
        self.assertEqual(self.app.sessions[sid]['environment']['corpora'],[self.a])
    def test_deleted_collection_does_not_reuse_focused_evidence(self):
        sid=self.chat('load MPLPB',loaded_corpora=[self.a,self.b])['session']
        self.chat('focus '+self.b+' :: Moon',sid)
        self.app.reset_collection({'corpus':self.b})
        r=self.chat('how big is it?',sid)['response']
        self.assertIsNone(r['context']);self.assertEqual(r['sources'],[])
        self.assertTrue(r['blocked_collections'])
    def test_profile_checks_are_per_collection(self):
        sid=self.chat('load MPLPB',loaded_corpora=['canned',self.a])['session']
        r=self.chat('show my MPLPB',sid,profile='external')['response']
        self.assertFalse(any(p['corpus']=='canned' and p['title']=='Phrynomedusa vanzolinii' for p in r['scope_pages']))
    def test_general_world_question_never_invents_an_answer(self):
        sid=self.chat('just chat')['session']
        r=self.chat('Who will win the next election?',sid)['response']
        self.assertEqual(r['kind'],'conversation');self.assertEqual(r['sources'],[])
        self.assertNotIn('source_offer',r)
        self.assertIsNone(r['context'])

    def test_relation_premises_do_not_chain_across_collections(self):
        for key,title,body in [(self.a,'Dogs','Fact: Fido | instance_of | Mammal'),
                               (self.b,'Mammals','Fact: Mammal | subclass_of | Animal')]:
            self.app.import_source({'corpus':key,'title':title,'url':'https://example.org/facts','text':body})
        sid=self.chat('load MPLPB',loaded_corpora=[self.a,self.b])['session']
        r=self.chat('relate Fido -> Animal',sid)['response']
        self.assertEqual(len(r['scope_results']),2)
        self.assertTrue(all(x['response']['kind']=='unknown_relation' for x in r['scope_results']))

    def test_changed_source_pin_requires_reselection(self):
        sid=self.chat('load MPLPB',loaded_corpora=[self.a])['session']
        self.chat('topic Moon',sid)
        self.app.import_source({'corpus':self.a,'title':'Moon','url':'https://example.org/moon','text':'The Moon is 99 km in diameter.'})
        r=self.chat('how big is it?',sid)['response']
        self.assertIsNone(r['context']);self.assertEqual(r['sources'],[])
        self.assertNotIn('99 km',r['message'])

    def test_named_overview_keeps_both_source_versions(self):
        sid=self.chat('load MPLPB',loaded_corpora=[self.a,self.b])['session']
        r=self.chat('what is Moon?',sid)['response']
        self.assertEqual(len(r['scope_results']),2)
        self.assertIn('10 km',r['message']);self.assertIn('20 km',r['message'])
        self.assertEqual({s['corpus'] for s in r['sources']},{self.a,self.b})
