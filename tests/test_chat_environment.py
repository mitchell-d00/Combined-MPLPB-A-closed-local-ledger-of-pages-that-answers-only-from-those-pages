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

    def test_mode_switch_restores_selected_scope_after_reload(self):
        sid=self.chat('load MPLPB',loaded_corpora=[self.a,self.b])['session']
        r=self.chat('switch to chat mode',sid)['response']
        self.assertEqual(r['environment']['corpora'],[])
        self.app=App(topic_base=self.base)
        r=self.chat('switch to serious mode',sid)['response']
        self.assertEqual(r['environment']['corpora'],[self.a,self.b])
        self.assertTrue(self.app.resume_chat({'session':sid})['chain_intact'])

    def test_greeting_plus_topic_reads_local_sources_without_changing_scope(self):
        sid=self.chat('load MPLPB',loaded_corpora=[self.a])['session']
        r=self.chat('Could you say hi to the astronomy club and tell them about Moon?',sid)['response']
        self.assertTrue(r['message'].startswith('Hello to the astronomy club!'))
        self.assertIn('10 km',r['message']);self.assertNotIn('20 km',r['message'])
        self.assertEqual(r['environment']['corpora'],[self.a])
        self.assertEqual({s['corpus'] for s in r['sources']},{self.a})
        self.assertFalse(r['composition']['sent_externally'])
        r=self.chat('Explore an idea about Moon',sid)['response']
        self.assertEqual(r['sources'],[])
        self.assertEqual(r['environment']['corpora'],[self.a])
        self.assertFalse(r['response_structure']['factual_claims'])

    def test_audience_introduction_composes_acts_in_both_modes(self):
        for mode in ['chat mode','load all MPLPB']:
            sid=self.chat(mode)['session']
            expected=self.app.sessions[sid]['environment'].copy()
            for phrase in ['say hi to the OpenAI forum and tell them what you are',
                           'Could you say hello to my friends and introduce yourself?',
                           'introduce yourself to our reading group']:
                r=self.chat(phrase,sid)['response']
                self.assertEqual(r['response_structure']['acts'],['greeting','system_description'])
                self.assertIn('explicit rules',r['message'])
                self.assertFalse(r['response_structure']['sent_externally'])
                self.assertEqual(r['sources'],[])
                self.assertEqual(r['environment'],expected)
            r=self.chat('say exactly hi to my friends and introduce yourself',sid)['response']
            self.assertEqual(r['message'],'hi to my friends and introduce yourself')
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

    def test_dictionary_topic_conversation_in_both_modes(self):
        for mode in ['chat mode','load MPLPB']:
            sid=self.chat(mode,loaded_corpora=[self.a])['session']
            before=self.app.sessions[sid]['environment'].copy()
            for q in ['Tell me about serendipity', 'What is serendipity?']:
                r=self.chat(q,sid)['response']
                self.assertEqual(r['authority'],'lexical_reference')
                self.assertEqual(r['support_label'],'Dictionary reference')
                self.assertTrue(r['sources'])
                self.assertEqual(r['environment'],before)
                self.assertNotIn('0 MPLPB loaded',r['message'])
            self.assertTrue(self.app.resume_chat({'session':sid})['chain_intact'])

    def test_saved_reference_answer_is_tagged_without_loading_it(self):
        self.app.import_source({'corpus':self.b,'title':'Zorblax','url':'https://example.org/zorblax','text':'Zorblax is a synthetic blue crystal. Zorblax glows in this fictional fixture.'})
        sid=self.chat('load MPLPB',loaded_corpora=[self.a])['session']
        for q in ['What is a Zorblax?', 'Can you tell me about Zorblax?']:
            r=self.chat(q,sid)['response']
            self.assertIn('synthetic blue crystal',r['message'])
            self.assertEqual(r['source_scope'],'saved_reference_outside_loaded_scope')
            self.assertEqual(r['support_label'],'Saved reference · outside loaded scope')
            self.assertEqual({s['corpus'] for s in r['sources']},{self.b})
            self.assertEqual(r['environment']['corpora'],[self.a])
        self.assertTrue(self.app.resume_chat({'session':sid})['chain_intact'])

    def test_numbered_excerpts_match_displayed_source_pages(self):
        self.app.import_source({'corpus':self.a,'title':'Moon context','url':'https://example.org/context',
                                'text':'Moon context includes the Moon and other satellites.'})
        sid=self.chat('load MPLPB',loaded_corpora=[self.a])['session']
        result=self.chat('Tell me about the Moon',sid)['response']
        self.assertTrue(result['scope_results'])
        self.assertEqual(len(result['sources']),len(result['scope_results']))
        for source,item in zip(result['sources'],result['scope_results']):
            self.assertEqual(source['path'],item['response']['context']['path'])
            self.assertEqual(source['hash'],item['response']['context']['hash'])

    def test_incidental_mentions_do_not_supply_topic_overviews(self):
        self.app.import_source({'corpus':self.a,'title':'Arcade history','url':'https://example.org/arcades',
                                'text':'Video games are electronic entertainment. Veloria has many arcades.'})
        sid=self.chat('load MPLPB',loaded_corpora=[self.a])['session']
        result=self.chat('Cool, tell me about Veloria',sid)['response']
        self.assertEqual(result['sources'],[])
        self.assertNotIn('Video games are',result['message'])
        self.app.import_source({'corpus':self.b,'title':'Country introduction','url':'https://example.org/country',
                                'text':'Veloria is a fictional country. It has many arcades.'})
        sid=self.chat('load MPLPB',loaded_corpora=[self.b])['session']
        result=self.chat('Cool, tell me about Veloria',sid)['response']
        self.assertIn('Veloria is a fictional country',result['message'])
        self.assertTrue(result['sources'])
