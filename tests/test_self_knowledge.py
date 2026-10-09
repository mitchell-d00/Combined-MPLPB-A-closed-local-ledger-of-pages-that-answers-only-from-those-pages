import tempfile
import unittest
from pathlib import Path
from tools import self_knowledge as S
from tools.ledger_ui import App

class SelfKnowledgeTests(unittest.TestCase):
    def test_documentation_matches_runtime_model(self):
        self.assertEqual(Path('docs/SYSTEM_GUIDE.md').read_text(),S.documentation())

    def test_self_questions_work_in_both_modes_without_source_claims(self):
        with tempfile.TemporaryDirectory() as tmp:
            app=App(topic_base=Path(tmp)/'topics')
            for mode in ['chat mode','load MPLPB']:
                first=app.chat({'corpus':'logic','message':mode});sid=first['session']
                scope=first['response']['environment']
                for q in sorted(set().union(*S.ALIASES.values())):
                    r=app.chat({'corpus':'logic','session':sid,'message':q})['response']
                    self.assertEqual(r['support_label'],'System description',q)
                    self.assertEqual(r['sources'],[])
                    self.assertEqual(r['environment'],scope)
                    self.assertIsNone(r['language_plan']['acquisition']['query'])
                self.assertTrue(app.resume_chat({'session':sid})['chain_intact'])

    def test_current_state_is_observed_not_invented(self):
        session={'environment':{'mode':'focus','corpora':['one','two']},'context':{'title':'Moon'},'mind':{'idea_chat':{'subject':'Rocks'}}}
        r=S.handle('What do you have loaded?',session)
        self.assertIn('one, two',r['message']);self.assertIn('Moon',r['message']);self.assertIn('Rocks',r['message'])
        self.assertEqual(r['self_knowledge']['snapshot']['mode'],'focus')
        self.assertEqual(r['context'],session['context'])

    def test_self_routes_do_not_capture_world_questions(self):
        for q in ['What can dogs do?','Explain Moon','How does memory work in humans?']:
            self.assertIsNone(S.handle(q,{'mind':{}}))
        self.assertIsNotNone(S.handle('Could you please explain your modes?',{'mind':{}}))

    def test_definition_phrasings_and_concept_slots(self):
        for q in ['What is a MPLPB', "What's an MPLPB?", 'Could you please tell me about the MPLPB?',
                  'Help me understand Combined MPLPB', 'Give me an overview of your memory']:
            r=S.handle(q,{'mind':{}})
            self.assertIsNotNone(r,q)
            self.assertEqual(r['authority'],'system_description')
        self.assertIsNone(S.handle('What is a MPLPB vulnerability in another product?',{'mind':{}}))
