import tempfile
import unittest
from pathlib import Path
from mplpb_combined.ledger import write
from mplpb_combined.reader import PROFILES
from mplpb_answers.support import supported_answer
from mplpb_answers.practical_evidence import parse


class PracticalEvidenceTests(unittest.TestCase):
    def ask(self, question, body, **kwargs):
        with tempfile.TemporaryDirectory() as root:
            write(root, doc_id='T-0001', title='Reference', scope=question, body=body)
            return supported_answer(root, question, **kwargs)

    def test_variable_values_and_verbatim_spans(self):
        # Changed values exercise relations beyond the frozen corpus values.
        cases = [
            ('How long should I candle the burners?', 'Light both burners on low and candle for 45 minutes.'),
            ('How often should I measure resistance with a multimeter?', 'Measure each circuit with a multimeter once a month and replace the set when resistance has risen by 15 percent.'),
            ('What mesh sieve should I use?', 'Pass twice through a 60 mesh sieve.'),
            ('How many posts per shelf?', 'Four posts per shelf, aligned.'),
            ('How deep should I spread slurry on a plaster batt?', 'Spread the slurry 3 cm deep on a plaster batt and turn it when the underside peels away clean.'),
            ('Which clay is suitable for sculpture?', 'Grey crank, GC, is for sculpture and large slab work and tolerates uneven drying.'),
            ('Which clay for cone 8?', 'Grey stoneware, bag code GS, matures at cone 8 and shrinks ten percent.'),
        ]
        for question, body in cases:
            with self.subTest(question=question):
                answer = self.ask(question, body)
                self.assertEqual(answer.kind, 'return')
                self.assertEqual(answer.text, body)
                self.assertEqual(answer.support['frame']['version'], 'practical-evidence-v1')
                for bad in ('If approved, '+body, 'Perhaps '+body, 'Say '+body, '"'+body+'"', 'Imagine a studio. '+body):
                    self.assertNotEqual(self.ask(question, bad).kind, 'return', bad)

    def test_complete_subject_and_modifier_constraints(self):
        for question in ('How long should I candle the kiln room?',
                         'How long should I candle the burners after repairs?',
                         'What mesh sieve should I not use?',
                         'How many posts per shelf tomorrow?',
                         'Which clay for cone 8 if fired twice?'):
            self.assertIsNone(parse(question))
        self.assertNotEqual(self.ask('Which clay for cone 8?', 'White stoneware, bag code WS, matures at cone 6 and shrinks twelve percent.').kind, 'return')
        self.assertNotEqual(self.ask('What mesh sieve should I use?', 'The sieve is in storage.').kind, 'return')
        self.assertNotEqual(self.ask('How many posts per shelf?', '<h1>Three posts per shelf.</h1>No instruction recorded.').kind, 'return')

    def test_competing_owners_and_denials(self):
        q = 'How many posts per shelf?'
        for body in ('Four posts per shelf. Five posts per shelf.',
                     'Four posts per shelf. Never four posts per shelf.'):
            self.assertEqual(self.ask(q, body).kind, 'ambiguous')
        with tempfile.TemporaryDirectory() as root:
            write(root, doc_id='T-0001', title='Loading', scope='posts shelf', body='Four posts per shelf.')
            write(root, doc_id='T-0002', title='Checklist', scope='posts shelf', body='Four posts per shelf, aligned.')
            self.assertEqual(supported_answer(root, q).kind, 'ambiguous')

    def test_provenance_and_profile_gates(self):
        q = 'What mesh sieve should I use?'
        body = 'Pass twice through an 80 mesh sieve.'
        with tempfile.TemporaryDirectory() as root:
            write(root, doc_id='T-0001', title='Mixing', scope='sieve mesh', body=body, external='no')
            self.assertNotEqual(supported_answer(root, q, PROFILES['external']).kind, 'return')
        with tempfile.TemporaryDirectory() as root:
            write(root, doc_id='T-0001', title='Mixing', scope='mixing', body=body, not_for='sieve')
            self.assertNotEqual(supported_answer(root, q).kind, 'return')
        with tempfile.TemporaryDirectory() as root:
            write(root, doc_id='T-0001', title='Mixing', scope='sieve mesh', body=body)
            page = next(Path(root).glob('*.html'))
            page.write_text(page.read_text().replace('80 mesh', '60 mesh'))
            self.assertNotEqual(supported_answer(root, q).kind, 'return')
