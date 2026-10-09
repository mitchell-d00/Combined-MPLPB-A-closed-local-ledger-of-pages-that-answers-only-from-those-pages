import tempfile
import unittest
from pathlib import Path
from tools.ledger_ui import App
from tools import conversation_memory as CM
from tools import conversation_engine as CE

class NameVariationTests(unittest.TestCase):
    def test_explicit_names_and_initials(self):
        for name in ['A','B','M','Z','Anna','Mitchell','Mary Jane','Jean-Luc',"O'Connor",'José','李明','Happy','Blue']:
            for prefix in ['My name is ', 'Call me ', 'Please call me ']:
                with self.subTest(name=name,prefix=prefix):
                    self.assertEqual(CM.introduction(prefix+name),name)
        for initial in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            self.assertEqual(CE.act('Hi I’m '+initial)['value'],initial)

    def test_states_are_not_names(self):
        for text in ['I am tired','Hi I’m tired','Hi I’m a teacher','I am happy','Hi I’m feeling good']:
            self.assertNotEqual(CE.act(text)['type'],'introduce')

    def test_recall_correction_reload_both_modes(self):
        with tempfile.TemporaryDirectory() as tmp:
            for mode in ['chat mode','load MPLPB']:
                base=Path(tmp)/mode/'topics'
                app=App(topic_base=base)
                sid=app.chat({'corpus':'logic','message':mode})['session']
                for name in ['A','Anna','Jean-Luc','José','李明','Happy']:
                    q=('Hi I’m '+name+' what are you') if name!='Happy' else 'Call me Happy'
                    r=app.chat({'corpus':'logic','session':sid,'message':q})['response']
                    self.assertIn(name,r['message'])
                    app=App(topic_base=base)
                    r=app.chat({'corpus':'logic','session':sid,'message':'What is my name?'})['response']
                    self.assertIn(name,r['message'])
                    self.assertEqual(r['sources'],[])
                self.assertTrue(app.resume_chat({'session':sid})['chain_intact'])
