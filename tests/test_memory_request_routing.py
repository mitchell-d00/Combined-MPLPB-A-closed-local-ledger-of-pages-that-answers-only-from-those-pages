"""Exercise memory phrasing through the full chat router, not just its parser."""
import tempfile
import unittest
from pathlib import Path
from tools.ledger_ui import App


class MemoryRequestRoutingTests(unittest.TestCase):
    def test_polite_recall_after_correction_and_forgetting(self):
        with tempfile.TemporaryDirectory() as tmp:
            for mode in ['chat mode', 'load MPLPB']:
                app = App(topic_base=Path(tmp)/mode/'topics')
                sid = app.chat({'corpus': 'logic', 'message': mode})['session']
                def ask(q):
                    return app.chat({'corpus': 'logic', 'session': sid, 'message': q})['response']
                ask("My dog's name is Amber")
                ask("Actually, my dog's name is Indigo")
                for q in ["Tell me my dog's name", "Can you tell me my dog's name?",
                          "Could you please tell me my dog's name?", "Please tell me my dog's name"]:
                    with self.subTest(mode=mode, q=q):
                        r = ask(q)
                        self.assertIn('Indigo', r['message'])
                        self.assertNotIn('Amber', r['message'])
                        self.assertEqual(r['authority'], 'user_declaration')
                        self.assertEqual(r['sources'], [])
                        self.assertEqual(r['interpretation']['original'], q)
                ask("forget my dog's name")
                self.assertNotIn('Indigo', ask("Can you tell me my dog's name?")['message'])
                self.assertTrue(app.resume_chat({'session': sid})['chain_intact'])
