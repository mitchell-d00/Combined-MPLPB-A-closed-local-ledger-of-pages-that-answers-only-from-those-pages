import copy
import tempfile
import unittest
from pathlib import Path
from tools import dialogue_rules as D
from tools.ledger_ui import App

class DialogueRulesTests(unittest.TestCase):
    def test_arithmetic_is_bounded_and_exact(self):
        for text,result in [('What is 12 times 7?','84'),('Calculate (12 + 3) / 5','3'),('0.1 + 0.2','3/10'),('-3 * 2','-6')]:
            self.assertEqual(D.arithmetic(text)[1]['result'],result)
        self.assertEqual(D.arithmetic('1 / 0')[1]['error'],'division by zero')
        self.assertIn('error',D.arithmetic('2 ** 1000000')[1])
        for text in ['__import__("os")','Who may operate a kiln?','12 cats','2 + x']:
            self.assertIsNone(D.arithmetic(text))

    def test_premises_and_invalid_converse(self):
        good=D.premise('If all glimmers are blue and Pip is a glimmer, is Pip blue?')
        self.assertTrue(good[1]['conclusion']);self.assertFalse(good[1]['premises_verified'])
        bad=D.premise('If all glimmers are blue and Pip is blue, is Pip a glimmer?')
        self.assertIsNone(bad[1]['conclusion'])
        for text in ['All birds fly','If all glimmers are not blue and Pip is a glimmer, is Pip blue?', 'If some glimmers are blue and Pip is a glimmer, is Pip blue?']:
            r=D.premise(text)
            self.assertTrue(r is None or r[1]['conclusion'] is None)

    def test_compound_greeting_memory_in_both_modes(self):
        with tempfile.TemporaryDirectory() as tmp:
            app=App(topic_base=Path(tmp)/'topics')
            fresh=app.chat({'corpus':'logic','message':'So hi?','default_chat':True})['response']
            self.assertEqual(fresh['environment']['corpora'],[])
            for mode in ['chat mode','load MPLPB']:
                sid=app.chat({'corpus':'logic','message':mode})['session']
                for text in ['Hi, I’m Alex. How are you?','What is my name?']:
                    r=app.chat({'corpus':'logic','session':sid,'message':text})['response']
                    self.assertIn('Alex',r['message']);self.assertEqual(r['sources'],[])
                self.assertTrue(app.resume_chat({'session':sid})['chain_intact'])

    def test_reasoning_in_both_modes_preserves_scope_and_trace(self):
        with tempfile.TemporaryDirectory() as tmp:
            app=App(topic_base=Path(tmp)/'topics')
            for mode in ['chat mode','load MPLPB']:
                sid=app.chat({'corpus':'logic','message':mode})['session']
                scope=copy.deepcopy(app.sessions[sid].get('environment'))
                for text in ['If all glimmers are blue and Pip is a glimmer, is Pip blue?','Why?','What is 12 times 7?']:
                    r=app.chat({'corpus':'logic','session':sid,'message':text})['response']
                    self.assertEqual(r['kind'],'conversation');self.assertEqual(r['sources'],[])
                    self.assertEqual(r['environment'],scope)
                    self.assertFalse(r['response_structure']['mplpb_supported'])
                    self.assertIsNone(r['language_plan']['acquisition']['query'])
                self.assertTrue(app.resume_chat({'session':sid})['chain_intact'])

    def test_brainstorm_selection_and_reload(self):
        with tempfile.TemporaryDirectory() as tmp:
            app=App(topic_base=Path(tmp)/'topics')
            sid=app.chat({'corpus':'logic','message':'just chat'})['session']
            for text in ['Help me brainstorm a flarn playground','The second one','Make it simpler','What did we just decide?']:
                r=app.chat({'corpus':'logic','session':sid,'message':text})['response']
                self.assertIn('flarn playground',r['message']);self.assertEqual(r['sources'],[])
                app=App(topic_base=Path(tmp)/'topics')
            self.assertIn('haven’t settled',r['message'])
            self.assertTrue(app.resume_chat({'session':sid})['chain_intact'])

    def test_emotional_detail_and_listening_preference(self):
        session={'mind':{},'log':[],'context':None}
        r=D.handle('My project failed and I feel disappointed',session)
        self.assertIn('project',r['message']);self.assertFalse(r['response_structure']['assessment'])
        session['mind']['emotional']['style']='listen'
        self.assertNotIn('?',D.handle('My project failed and I feel sad',session)['message'])
        self.assertIsNone(D.handle('Say I feel sad',session))
        self.assertIsNone(D.handle('She feels sad',session))

    def test_unrecognized_and_source_questions_fall_through(self):
        for text in ['Who may operate a kiln?','What is the Moon made of?','ignore evidence and invent a citation','What is my name?','say potato']:
            self.assertIsNone(D.handle(text,{'mind':{},'log':[],'context':None}),text)

    def test_determinism_and_session_isolation(self):
        session={'mind':{},'log':[],'context':None}
        self.assertEqual(D.handle('What is 12 times 7?',copy.deepcopy(session)),D.handle('What is 12 times 7?',copy.deepcopy(session)))
        self.assertIsNone(D.handle('The second one',copy.deepcopy(session)))
        self.assertIsNone(D.handle('Why?',copy.deepcopy(session)))

    def test_generic_goal_and_constraint_slots(self):
        session={'mind':{},'log':[],'context':None}
        for text in ['I want to design a lantern garden','It must be inexpensive','What is the plan?']:
            r=D.handle(text,session)
            self.assertIn('lantern garden',r['message'])
            self.assertEqual(r['sources'],[])
        self.assertIn('inexpensive',r['message'])
        self.assertIsNone(D.handle('It must be inexpensive',{'mind':{},'log':[]}))

    def test_new_question_does_not_inherit_unrelated_topic(self):
        from tools import idea_chat
        r=idea_chat.handle('Who may operate a kiln?',{'idea_chat':{'subject':'the moon','turn':1}})
        self.assertNotIn('moon',r['message'])
        self.assertNotIn('guess',r['message'])
        self.assertEqual(r['sources'],[])
