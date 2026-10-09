import tempfile
import unittest
from pathlib import Path
from tools import chat_language_graph as G
from tools.ledger_ui import App

class LanguageGraphTests(unittest.TestCase):
    def test_graph_forms(self):
        for edge in G.GRAPH['edges']:
            for alias in G.GRAPH['subjects'][edge['subject']]:
                for form in G.GRAPH['forms']:
                    q='Could you please '+form.replace('{subject}',alias)+'?'
                    self.assertEqual(G.interpret(q)['intent'],edge['intent'],q)
    def test_no_overreach(self):
        for q in ['say loaded mplpb','do not list topics','load all collections','forget my memory','tell me about loaded mplpb and dogs','tell me about dogs','search loaded mplpb','my name is Topics']:
            self.assertIsNone(G.interpret(q),q)
    def test_live_entry_scope_and_followup(self):
        for mode in ['chat mode','load all MPLPB']:
            with tempfile.TemporaryDirectory() as d:
                app=App(topic_base=Path(d)/'topics')
                r=app.chat({'corpus':'logic','message':mode});sid=r['session']
                for q in ['Can you tell me about loaded mplpb','Tell me more about loaded mplpb','Loaded collections']:
                    r=app.chat({'corpus':'logic','session':sid,'message':q})['response']
                    self.assertIn('Loaded MPLPB collections:',r['message'])
                    self.assertIn('none' if mode=='chat mode' else 'logic',r['message'])
                    self.assertEqual(r['sources'],[])
                    self.assertEqual(r['interpretation']['language_graph']['intent'],'inspect_loaded')
    def test_empty_session(self):
        with tempfile.TemporaryDirectory() as d:
            r=App(topic_base=Path(d)/'topics').chat({'corpus':'logic','message':'Can you tell me about loaded mplpb'})['response']
            self.assertIn('collections: none',r['message'])
