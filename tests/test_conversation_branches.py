import tempfile
import unittest
from pathlib import Path
from tools.ledger_ui import App
from tools import conversation_branches as B

class ConversationBranchTests(unittest.TestCase):
    def test_screenshot_both_modes_reload_and_choice(self):
        with tempfile.TemporaryDirectory() as tmp:
            for mode in ['chat mode','load MPLPB']:
                base=Path(tmp)/mode/'topics';app=App(topic_base=base)
                sid=app.chat({'corpus':'logic','message':mode})['session']
                for q,want in [('Hi I’m Anna','Anna'),('What’s that?','Do you mean MPLPB or little monster?'),('MPLPB','bounded local collection'),('What is it?','bounded local collection'),('No little monster what is it','chat interface')]:
                    r=app.chat({'corpus':'logic','session':sid,'message':q})['response']
                    self.assertIn(want,r['message']);self.assertEqual(r['sources'],[])
                    self.assertIsNone(r['language_plan']['acquisition']['query'])
                    app=App(topic_base=base)
                self.assertTrue(app.resume_chat({'session':sid})['chain_intact'])
                self.assertEqual(r['conversation_branch']['selected']['id'],'monster')

    def test_explicit_correction_without_pending(self):
        r=B.handle('No mplpb what is it',{'mind':{},'log':[]})
        self.assertIn('bounded local collection',r['message'])
        self.assertNotIn('no mplpb what',r['message'])

    def test_pending_ordinal_and_ambiguous_yes(self):
        s={'mind':{'conversation_branches':{'pending':[{'id':'mplpb','label':'MPLPB','kind':'system'},{'id':'monster','label':'little monster','kind':'system'}]}},'log':[]}
        self.assertIn('Do you mean',B.handle('yes',s)['message'])
        self.assertEqual(B.handle('the second one',s)['conversation_branch']['selected']['id'],'monster')
        self.assertIsNone(B.handle('Tell me about dogs',s))
        self.assertNotIn('active',s['mind']['conversation_branches'])

    def test_generic_candidates_preserve_source_result(self):
        s={'mind':{'idea_chat':{'subject':'Dogs'}},'context':{'title':'Moon'},'log':[{'payload':{'response':{'context':{'title':'Moon'}}}}]}
        r=B.handle("What's that?",s)
        self.assertEqual(r['suggestions'],['Moon','Dogs'])
        pin={'path':'dogs.html','hash':'abc'}
        r=B.handle('Dogs',s,lambda q:{'message':'A quoted fact.','sources':[pin],'context':None,'authority':'source'})
        self.assertEqual(r['sources'],[pin]);self.assertEqual(r['authority'],'source')
        self.assertEqual(s['context'],{'title':'Moon'})
