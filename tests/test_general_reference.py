import tempfile
import unittest
from pathlib import Path
from tools.ledger_ui import App
from tools import general_reference as G

class GeneralReferenceTests(unittest.TestCase):
    def test_reference_boundaries_and_followup(self):
        s={'environment':{'mode':'chat','corpora':[]},'mind':{},'context':None}
        for row in G.records():
            r=G.handle('Tell me about '+row['topic'],s)
            self.assertEqual(r['authority'],'research_note')
            self.assertFalse(r['response_structure']['mplpb_supported'])
            self.assertTrue(r['sources'][0]['url'].startswith('https://'))
            self.assertIn(row['facts'][1],G.handle('tell me more',s)['message'])
        self.assertIsNone(G.handle('How much does evaporation cost?',s))
        s['environment']['mode']='focus'
        self.assertIsNone(G.handle('Tell me about evaporation',s))

    def test_help_and_topics_in_both_modes(self):
        with tempfile.TemporaryDirectory() as tmp:
            a=App(topic_base=Path(tmp)/'topics')
            for mode in ['chat mode','load all MPLPB']:
                sid=a.chat({'corpus':'logic','message':mode})['session']
                for q,want in [('how do I search?','search dogs'),('List topics','Available topics'),("What’s your molpb",'bounded local collection')]:
                    r=a.chat({'corpus':'logic','session':sid,'message':q})['response']
                    self.assertIn(want,r['message'])

    def test_chat_reference_route(self):
        with tempfile.TemporaryDirectory() as tmp:
            a=App(topic_base=Path(tmp)/'topics')
            sid=a.chat({'corpus':'logic','message':'chat mode'})['session']
            r=a.chat({'corpus':'logic','session':sid,'message':'Tell me about evaporation'})['response']
            self.assertEqual(r['authority'],'research_note')
            self.assertIsNone(r['language_plan']['acquisition']['query'])
