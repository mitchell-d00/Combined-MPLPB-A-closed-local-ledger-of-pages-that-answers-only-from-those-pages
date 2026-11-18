"""Stacked-field boundaries must not certify a glued value."""
import tempfile
import unittest
from mplpb_answers.pipeline import answer_query
from mplpb_combined.ledger import write

class StackedFieldSafety(unittest.TestCase):
    def ask(self, body, field='sender'):
        with tempfile.TemporaryDirectory() as root:
            write(root,doc_id='SHIP-7',title='Shipment',scope='SHIP-7 shipment',body=body)
            return answer_query(root, 'What is the '+field+' for record SHIP-7?').contract

    def test_stacked_headers_are_not_supported(self):
        for label in ('Recipient', 'recipient'):
            with self.subTest(label=label):
                c=self.ask('Sender: Boston flour office\n'+label+': Albany depot\nCargo: forty barrels')
                self.assertFalse(c['answer_supported'])
                self.assertEqual(c['diagnostic']['code'],'stacked_field_paragraph')

    def test_separate_paragraphs_and_ordinary_colon_remain_supported(self):
        self.assertEqual(self.ask('Sender: Boston flour office\n\nRecipient: Albany depot')['text'], 'Sender: Boston flour office')
        self.assertTrue(self.ask('Ratio: 3:1 sand to lime', 'ratio')['answer_supported'])
