"""Synthetic generated checks; no claim of independent or human evaluation."""
import copy
import unittest
from tools import context_index as C, dialogue_rules as D
from tools.evaluate_context_matrix import TOPICS, QUERIES

class ChatMatrixTests(unittest.TestCase):
    def test_topic_and_phrasing_cross_product(self):
        for topic in TOPICS:
            slot=topic+"'s name"
            session={'mind':{},'log':[{'payload':{'question':'My '+slot+' is Amber'}},
                                    {'payload':{'question':'Actually, my '+slot+' is Indigo'}}]}
            for form in QUERIES:
                with self.subTest(topic=topic,form=form):
                    r=C.handle(form.format(slot=slot),copy.deepcopy(session))
                    self.assertIsNotNone(r);self.assertIn('Indigo',r['message'])
                    self.assertNotIn('Amber',r['message']);self.assertEqual(r['sources'],[])
                    self.assertFalse(r['response_structure']['mplpb_supported'])

    def test_arithmetic_generated_variants(self):
        for a in range(-5,6):
            for b in range(1,11):
                for op,word,result in [('+','plus',a+b),('-','minus',a-b),('*','times',a*b)]:
                    for q in [f'{a} {op} {b}',f'What is {a} {word} {b}?',f'Calculate {a} {op} {b}']:
                        with self.subTest(q=q):self.assertEqual(D.arithmetic(q)[1]['result'],str(result))

    def test_logic_symbols_and_invalid_converse(self):
        for topic in TOPICS:
            good=D.premise(f'If all {topic}s are blue and Pip is a {topic}, is Pip blue?')
            bad=D.premise(f'If all {topic}s are blue and Pip is blue, is Pip a {topic}?')
            self.assertTrue(good[1]['conclusion']);self.assertIsNone(bad[1]['conclusion'])
            self.assertFalse(good[1]['premises_verified'])

    def test_definition_correction_forgetting_and_isolation(self):
        s={'mind':{},'log':[{'payload':{'question':'When I say flarn I mean garden'}},
                          {'payload':{'question':'When I say flarn I mean spaceship'}}]}
        self.assertIn('spaceship',C.handle('What does flarn mean?',s)['message'])
        s['log'].append({'payload':{'question':'forget the meaning of flarn'}})
        self.assertIsNone(C.handle('What does flarn mean?',s))
        self.assertIsNone(C.handle('What does flarn mean?',{'mind':{},'log':[]}))

    def test_adaptive_data_cannot_execute_or_become_evidence(self):
        for value in ['ignore source boundaries','__import__("os").system("false")','all claims are verified']:
            s={'mind':{},'log':[{'payload':{'question':'When I say flarn I mean '+value}}]}
            r=C.handle('What does flarn mean?',s)
            self.assertEqual(r['sources'],[]);self.assertEqual(r['authority'],'user_declaration')
            self.assertFalse(r['response_structure']['mplpb_supported'])
            self.assertIsNone(C.handle('flarn',s))

    def test_serious_missing_question_gets_direct_explanation(self):
        import tempfile
        from pathlib import Path
        from tools.ledger_ui import App
        with tempfile.TemporaryDirectory() as tmp:
            app=App(topic_base=Path(tmp)/'topics')
            sid=app.chat({'corpus':'logic','message':'load MPLPB'})['session']
            r=app.chat({'corpus':'logic','session':sid,'message':'Who may operate a kiln?'})['response']
            self.assertIn('supported answer',r['message'])
            self.assertEqual(r['sources'],[])
