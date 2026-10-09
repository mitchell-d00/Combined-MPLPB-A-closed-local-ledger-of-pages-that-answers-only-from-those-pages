import copy
import tempfile
import unittest
from pathlib import Path
from tools import language_planner as P
from tools.ledger_ui import App

class LanguagePlannerTests(unittest.TestCase):
    def test_resolution_and_compound_actions(self):
        plan=P.parse('Can you say hi to the club and tell them about it?',{'idea_chat':{'subject':'Moon'}})
        self.assertEqual(plan['actions'],['greet','overview'])
        self.assertEqual(plan['subject'],'Moon')
        self.assertEqual(plan['reference'],'resolved')
        self.assertEqual(P.parse('tell me about it',{})['reference'],'unresolved')

    def test_immutable_source_payload_and_determinism(self):
        source={'id':'a','hash':'pin','corpus':'one'}
        result={'kind':'federated_answers','sources':[source],'response_structure':{'intent':'source_exploration','subject':'Moon'},'message':'Let’s talk about Moon.\n\nThe Moon is not 10 km wide; this estimate may be incomplete. [1]\n\nWhat part interests you most?'}
        parsed=P.parse('tell me about Moon',{})
        a=P.finish(copy.deepcopy(result),parsed,{},1)
        b=P.finish(copy.deepcopy(result),parsed,{},1)
        self.assertEqual(a,b)
        self.assertIn('The Moon is not 10 km wide; this estimate may be incomplete. [1]',a['message'])
        self.assertEqual(a['sources'],[source])
        self.assertNotEqual(a['message'],P.finish(copy.deepcopy(result),parsed,{},2)['message'])
        self.assertFalse(a['language_plan']['source_paraphrasing'])
        self.assertIn('page says',a['message'])
        self.assertIn('pages say',P.topic_clause('Moon',1,count=2))

    def test_no_remote_query_for_negation_ideas_or_unresolved_reference(self):
        for message in ['tell me about it','Explore an idea about Moon','tell me about Moon without searching','say exactly search Moon']:
            r=P.finish({'message':'Example','kind':'conversation'},P.parse(message,{}),{},1)
            self.assertIsNone(r['language_plan']['acquisition']['query'],message)

    def test_exact_text_proof_and_refusal_preserved(self):
        for kind,text in [('conversation','PoTaTo!'),('relations','A -> B; FACT-1'),('unsupported','No supporting evidence.')]:
            r=P.finish({'kind':kind,'message':text,'response_structure':{'construction':None}},P.parse('say exactly PoTaTo!',{}),{},1)
            self.assertEqual(r['message'],text)
            self.assertFalse(r['language_plan']['surface_changed'])

    def test_all_chat_paths_are_planned_and_saved(self):
        with tempfile.TemporaryDirectory() as tmp:
            app=App(topic_base=Path(tmp)/'topics')
            key=app.create_collection({'name':'Planner'})['corpus']
            app.import_source({'corpus':key,'title':'Moon','url':'https://example.org/moon','text':'The Moon is not 10 km wide.'})
            sid=None
            for message in ['load MPLPB','Tell me about Moon','say exactly Hi!','I feel sad','what are you?','define dog','show loaded MPLPB','Explore an idea about Moon']:
                r=app.chat({'corpus':key,'session':sid,'message':message});sid=r['session']
                self.assertIn('language_plan',r['response'],message)
                self.assertIn('support_label',r['response'])
                if message=='Tell me about Moon':
                    self.assertIn('not 10 km wide',r['response']['message']);self.assertTrue(r['response']['sources'])
                if message=='say exactly Hi!':self.assertEqual(r['response']['message'],'Hi!')
            saved=App(topic_base=Path(tmp)/'topics').resume_chat({'session':sid})
            self.assertTrue(saved['chain_intact'])
            self.assertTrue(all('language_planner_sha256' in t['payload'] for t in saved['turns']))
