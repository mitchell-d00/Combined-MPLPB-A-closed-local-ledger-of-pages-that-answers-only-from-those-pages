"""Independent documentary receipt examples through the normal strict reader."""
from html import escape
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from mplpb_answers import bounded_records
from mplpb_answers.pipeline import answer_query
from mplpb_combined.ledger import withdraw, write


class ReleaseLanguageCoverageTests(unittest.TestCase):
    catalog = 'Parcel BK-18 is listed as the court diary.'
    dispatch = 'Dispatch JR-19 records that Ari Long sent parcel BK-18 to Noel King.'
    receipt = 'Receipt for dispatch JR-19 names Noel King for parcel BK-18. They received it.'
    question = 'For the court diary, who sent it and who received it?'

    def ask(self, *records, question=None, **kwargs):
        with TemporaryDirectory() as root:
            for number, text in enumerate(records, 1):
                write(root, doc_id=f'PAGE-{number}', title='Sealed entry', scope='Documentary material',
                      body_html='<pre>' + escape(text) + '</pre>')
            return answer_query(root, question or self.question, **kwargs).contract

    def test_local_pronouns_and_three_source_join(self):
        result = self.ask(self.receipt, self.catalog, self.dispatch)
        self.assertEqual(result['kind'], 'supported_answer', result['diagnostic'])
        self.assertEqual([claim['proposition']['sent_by'] for claim in result['claims'][:1]], ['Ari Long'])
        self.assertEqual(result['claims'][1]['proposition']['received_by'], 'Noel King')
        self.assertEqual(len(result['claims'][1]['citations']), 3)
        self.assertFalse(result['verification']['truth_verified'])

    def test_dispatched_and_took_delivery_wording(self):
        result = self.ask(self.catalog, self.dispatch, self.receipt,
                          question='Who dispatched the court diary, and who took delivery?')
        self.assertEqual(result['kind'], 'supported_answer')

    def test_absent_receipt_preserves_attributed_dispatch(self):
        result = self.ask(self.catalog, self.dispatch)
        self.assertEqual(result['kind'], 'partial_answer')
        self.assertEqual(len(result['claims']), 1)
        self.assertNotIn('received_by', result['claims'][0]['proposition'])
        self.assertFalse(result['answer_supported'])

    def test_rivals_and_uncertainty_do_not_complete(self):
        bad = (self.receipt.replace('JR-19', 'JR-29'), self.receipt.replace('BK-18', 'BK-28'),
               self.receipt.replace('Noel King', 'Jordan Shaw'),
               self.receipt.replace('received', 'planned to receive'))
        for receipt in bad:
            with self.subTest(receipt=receipt):
                self.assertFalse(self.ask(self.catalog, self.dispatch, receipt)['answer_supported'])
        self.assertFalse(self.ask(self.catalog, self.dispatch, self.receipt,
                                  self.receipt.replace('They', 'Noel King'))['answer_supported'])
        self.assertFalse(self.ask(self.catalog, self.dispatch, self.receipt.replace('They', 'Jordan Shaw'))['answer_supported'])
        self.assertFalse(self.ask(self.catalog, self.dispatch, self.receipt,
                                  question=self.question + ' Did they read it?')['answer_supported'])

    def test_receipt_retired_during_verification_cannot_be_cited(self):
        verify = bounded_records.verify
        with TemporaryDirectory() as root:
            for number, text in enumerate((self.catalog, self.dispatch, self.receipt), 1):
                write(root, doc_id=f'PAGE-{number}', title='Sealed entry', scope='Documentary material',
                      body_html='<pre>' + escape(text) + '</pre>')

            def retire_after_verification(*args, **kwargs):
                result = verify(*args, **kwargs)
                if result and result[0] == 'supported_answer':
                    withdraw(root, 'PAGE-3')
                return result

            with patch.object(bounded_records, 'verify', side_effect=retire_after_verification):
                result = answer_query(root, self.question).contract
        self.assertFalse(result['answer_supported'])
        self.assertFalse(any('received_by' in claim['proposition'] for claim in result['claims']))

    def test_receipt_citation_is_atomic_under_tighter_budget(self):
        result = self.ask(self.catalog, self.dispatch, self.receipt, max_passages=2)
        self.assertEqual(result['kind'], 'partial_answer')
        self.assertEqual(len(result['claims']), 1)
        self.assertEqual(len(result['claims'][0]['citations']), 2)
