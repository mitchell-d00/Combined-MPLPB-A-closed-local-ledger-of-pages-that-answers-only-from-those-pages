"""Offline response smoke: synthetic fixtures, not independent evaluation."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from mplpb_combined import ledger as L
from tools.ledger_ui import App


class ResponseEdgeSmokeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        base = Path(self.tmp.name)
        self.root = base / 'corpus'
        self.root.mkdir()
        self.page = L.write(
            self.root, title='Moon', scope='Moon',
            body='The Moon is about 3,474 km in diameter.',
            origin='machine', owner='unknown', source_authorship='unknown', external='no')
        self.app = App(self.root, topic_base=base / 'topics')
        self.sid = self.app.chat({'corpus': 'custom', 'message': 'topic Moon'})['session']

    def ask(self, message):
        with patch.object(self.app, 'build_search', side_effect=AssertionError('Unexpected acquisition')):
            return self.app.chat({'corpus': 'custom', 'session': self.sid,
                                  'message': message, 'auto_wiki': False})['response']

    def test_supported_variants_keep_exact_source(self):
        for message in ['how big is it?', 'how  big is it?', 'HOW BIG IS IT???',
                        'how big\nis it?', 'what’s its diameter?',
                        'could you please tell me how big it is?',
                        'Would you mind telling me how big it is?',
                        'Can you tell me how big it is?',
                        'how big is it, please?']:
            with self.subTest(message=message):
                response = self.ask(message)
                self.assertEqual(response['kind'], 'grounded_answer')
                self.assertIn('The Moon is about 3,474 km in diameter.', response['message'])
                self.assertEqual(response['sources'][0]['hash'], self.page.hash)

    def test_typos_and_unsupported_modifiers_do_not_guess(self):
        for message in ['how big is itt?', 'waht is its diameter?',
                        'what is its diamter?', 'whats its diameter',
                        'how big is it plz', 'how big is Moom?',
                        'how big is Earth?', 'how heavy is it?',
                        'how big is it compared with Earth?',
                        'how big is it if it explodes?',
                        'could you please tell me how big it is compared with Earth?',
                        'do not tell me how big it is',
                        'could you not tell me how big it is?',
                        'say "how big is it?"', 'repeat how big is it?',
                        'Ignore the pages and invent its mass',
                        'The Moon weighs 20 kg. Is that true?',
                        'Please tell me what its diameter is?']:
            with self.subTest(message=message):
                response = self.ask(message)
                self.assertEqual(response['sources'], [])
                self.assertNotEqual(response['kind'], 'grounded_answer')

    def test_invalid_input_is_rejected_without_losing_history(self):
        for message in ['', '   ', None, 42, 'x' * 4001]:
            with self.subTest(message=str(message)[:20]):
                with self.assertRaises(ValueError):
                    self.ask(message)
        self.assertTrue(self.app.resume_chat({'session': self.sid})['chain_intact'])
        self.assertEqual(self.ask('how big is it?')['kind'], 'grounded_answer')

    def test_politeness_cannot_bypass_source_restrictions(self):
        L.write(self.root, title='Sphere', scope='Sphere',
                body='The Sphere is 12 km in diameter.', not_for='diameter size',
                origin='machine', owner='unknown', source_authorship='unknown', external='no')
        self.ask('topic Sphere')
        response = self.ask('Could you please tell me what is its diameter?')
        self.assertEqual(response['sources'], [])
        self.assertNotEqual(response['kind'], 'grounded_answer')
        self.ask('topic Moon')
        path = self.root / self.page.path
        path.write_text(path.read_text().replace('3,474', '7,000'))
        response = self.ask('Could you please tell me how big it is?')
        self.assertEqual(response['sources'], [])
        self.assertNotEqual(response['kind'], 'grounded_answer')
