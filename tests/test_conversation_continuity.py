import tempfile
import unittest
from pathlib import Path
from tools.ledger_ui import App

class ContinuityTests(unittest.TestCase):
    def test_branch_interruption_other_and_correction(self):
        for mode in ['chat mode','load all MPLPB']:
            with tempfile.TemporaryDirectory() as tmp:
                base=Path(tmp)/'topics';app=App(topic_base=base)
                sid=app.chat({'corpus':'logic','message':mode})['session']
                for q,want in [('Hi I’m Zuri what are you','Zuri'),("What's that",'Do you mean'),('thanks',None),('the other one','Do you mean'),('the second one','chat interface'),('the other one','bounded local collection'),('No I meant little monster','chat interface'),('that','chat interface'),('tell me moer','grammar'),("What's my name",'Zuri')]:
                    r=app.chat({'corpus':'logic','session':sid,'message':q})['response']
                    if want:self.assertIn(want,r['message'])
                    self.assertEqual(r['reply_plan']['sources'],r['sources'])
                    self.assertEqual(r['interpretation']['original'],q)
                    self.assertEqual(r['sources'],[])
                    app=App(topic_base=base)
                self.assertTrue(app.resume_chat({'session':sid})['chain_intact'])

    def test_literal_request_is_not_reinterpreted(self):
        with tempfile.TemporaryDirectory() as tmp:
            a=App(topic_base=Path(tmp)/'topics')
            r=a.chat({'corpus':'logic','message':'say the other one'})['response']
            self.assertEqual(r['interpretation']['resolved'],'say the other one')
