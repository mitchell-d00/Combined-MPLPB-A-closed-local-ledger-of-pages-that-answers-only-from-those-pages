import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from tools import conversation_router as R, conversation_continuity as C
from tools.ledger_ui import App

class RouterTests(unittest.TestCase):
    def test_proposals_are_pure_and_precede_rendering(self):
        session={'mind':{},'context':None,'log':[]}
        frame=C.prepare('My favorite stone is labradorite',session)
        before=copy.deepcopy(session)
        with patch.object(R.M,'reply',side_effect=AssertionError('rendered during recognition')), patch.object(R.E,'handle',side_effect=AssertionError('read during recognition')):
            plan=R.plan(frame,session,{})
        self.assertEqual(session,before)
        self.assertEqual(plan['phase'],'before_execution')
        self.assertEqual(plan['selected']['handler'],'context')
        self.assertNotIn('answer',plan)
        self.assertFalse(plan['policy']['lexical_match_proves_answer'])

    def test_losing_candidate_never_executes(self):
        with tempfile.TemporaryDirectory() as tmp:
            app=App(topic_base=Path(tmp)/'topics')
            with patch.object(R.PC,'handle',side_effect=AssertionError('losing handler executed')):
                response=app.chat({'corpus':'logic','default_chat':True,'message':'My telescope is blue'})['response']
            self.assertEqual(response['reply_plan']['selected']['handler'],'context')
            self.assertEqual(response['sources'],[])

    def test_compound_memory_reload_and_correction(self):
        for mode in ['chat mode','load all MPLPB']:
            with tempfile.TemporaryDirectory() as tmp:
                base=Path(tmp)/'topics';app=App(topic_base=base)
                sid=app.chat({'corpus':'logic','message':mode})['session']
                turns=[('My pet is Juniper; what is my pet?','Juniper'),
                       ('What is my pet?','Juniper'),
                       ('Actually my pet is Miso; what is my pet?','Miso'),
                       ('What is my pet?','Miso')]
                for q,want in turns:
                    r=app.chat({'corpus':'logic','session':sid,'message':q})['response']
                    self.assertIn(want,r['message']);self.assertEqual(r['sources'],[])
                    self.assertEqual(r['reply_plan']['phase'],'before_execution')
                    if ';' in q:
                        self.assertEqual(r['reply_plan']['selected']['handler'],'compose')
                        self.assertEqual(len(r['claim_units']),2)
                    app=App(topic_base=base)
                self.assertTrue(app.resume_chat({'session':sid})['chain_intact'])

    def test_graph_does_not_read_assistant_as_user(self):
        session={'mind':{},'context':None,'log':[
            {'payload':{'question':'My friend Éloi likes kites','response':{'message':'My friend Fake likes secrets'}}},
            {'payload':{'question':'Éloi likes clay','response':{}}}]}
        graph=R.relationships(session,[])
        self.assertEqual(graph['edges'][0]['object'],'clay')
        self.assertEqual(graph['edges'][0]['authority'],'user_declaration')
        self.assertFalse(graph['source_evidence'])
        self.assertNotIn('Fake',str(graph))

    def test_same_request_same_plan(self):
        s={'mind':{},'context':None,'log':[]}
        def plan():return R.plan(C.prepare('What can you do?',copy.deepcopy(s)),copy.deepcopy(s),{})
        self.assertEqual(plan(),plan())

    def test_literal_and_negation_not_promoted_to_control(self):
        for q in ['say load all MPLPB','do not load all MPLPB','repeat my name is Nobody']:
            s={'mind':{},'context':None,'log':[]}
            p=R.plan(C.prepare(q,s),s,{})
            self.assertNotEqual(p['selected']['intent'],'control')
            self.assertEqual(R.relationships(s,[])['nodes'][0]['label'],'user')

    def test_embedded_words_and_unknown_clauses_do_not_execute(self):
        with tempfile.TemporaryDirectory() as tmp:
            app=App(topic_base=Path(tmp)/'topics')
            r=app.chat({'corpus':'logic','message':'chat mode'});sid=r['session']
            response=app.chat({'corpus':'logic','session':sid,'message':'say how are you'})['response']
            self.assertNotEqual(response['reply_plan']['selected']['handler'],'rules')
            with patch.object(R.CM,'handle',side_effect=AssertionError('partial request executed')):
                response=app.chat({'corpus':'logic','session':sid,'message':'My name is Uma; perform a somersault'})['response']
            self.assertEqual(response['reply_plan']['selected']['handler'],'clarify')
            self.assertEqual(response['sources'],[])
