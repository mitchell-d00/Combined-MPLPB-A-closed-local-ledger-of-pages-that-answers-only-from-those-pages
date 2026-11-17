"""Closed documentary arrangement references, never completed external acts."""
import html
from pathlib import Path
import tempfile
import unittest

from mplpb_answers.pipeline import answer_query
from mplpb_answers import documentary_verify as kernel
from mplpb_combined.ledger import write
from mplpb_combined.reader import PROFILES

QUESTION = "Who arranged for Iris Vale to receive Nora Reed's atlas, and which dated letter records the arrangement?"
HEADER = 'NORA REED TO IRIS VALE. Haven, March 3rd, 1841.\nMy dear Sir,\n'
STATEMENT = 'I have told Arun Hale to send you by post (if possible) a copy of my atlas.'


class ArrangementCompletionTests(unittest.TestCase):
    def ask(self, body=HEADER+STATEMENT, question=QUESTION, markup=False, **kw):
        with tempfile.TemporaryDirectory() as name:
            root=Path(name)
            write(root, doc_id='LETTER-1', title='Metadata supplies no evidence', scope='archive',
                  body_html=body if markup else '<pre>'+html.escape(body)+'</pre>')
            return answer_query(root, question, **kw).contract

    def test_complete_recorded_request_has_three_independent_witness_spans(self):
        c=self.ask()
        self.assertTrue(c['answer_supported']);self.assertEqual(c['kind'], 'supported_answer')
        p=c['claims'][0]['proposition'];citations=c['claims'][0]['citations']
        self.assertEqual(len(citations),3)
        self.assertEqual(citations[0]['quote'],HEADER.split('\n')[0])
        self.assertEqual(citations[1]['quote'],STATEMENT)
        self.assertEqual(citations[2]['quote'],HEADER+STATEMENT)
        self.assertEqual(p['writer_text'],'NORA REED');self.assertEqual(p['requested_recipient_text'],'IRIS VALE')
        self.assertEqual(p['object_owner_text'],'NORA REED');self.assertEqual(p['condition_text'],'if possible')
        self.assertEqual(p['heading_date_text'],'March 3rd, 1841')
        self.assertEqual(p['date_role'],'letter_heading_date_role_unresolved')
        for flag in ('dispatch_verified','receipt_verified','instruction_event_truth_verified',
                     'actual_arrangement_independently_verified'):self.assertFalse(p[flag])
        self.assertIsNone(p['event_identity']);self.assertFalse(c['verification']['truth_verified'])
        self.assertIn('Actual fulfillment', c['text']);self.assertFalse(c['missing'])
        self.assertTrue(all(g['evidence_claim_indices']==[0] for g in c['documentary_support']['obligations']))

    def test_literal_author_and_recipient_bindings_not_nearby_name_guesses(self):
        for q in (QUESTION.replace('Nora Reed', 'Lena Grey'), QUESTION.replace('Iris Vale','Mira Stone'),
                  QUESTION.replace('atlas','second atlas')):
            with self.subTest(q=q):self.assertFalse(self.ask(question=q)['answer_supported'])
        # A shared surname cannot identify the two local roles.
        q="Who arranged for Vale to receive Vale's atlas, and which dated letter records the arrangement?"
        self.assertFalse(self.ask(body=(HEADER+STATEMENT).replace('NORA REED','NORA VALE'),question=q)['answer_supported'])

    def test_missing_date_names_or_explicit_ownership_cannot_close(self):
        for body in ((HEADER+STATEMENT).replace('March 3rd, 1841.',''), STATEMENT,
                     (HEADER+STATEMENT).replace('my atlas','the atlas')):
            with self.subTest(body=body):self.assertFalse(self.ask(body=body)['answer_supported'])

    def test_instruction_is_not_delivery_execution_acceptance_or_receipt(self):
        for question in (QUESTION+' Did delivery occur?', QUESTION.replace('arranged','actually arranged'),
                         'Was the arrangement carried out?', 'Did Iris Vale receive the atlas?',
                         'Did Arun Hale accept and execute the instruction?'):
            with self.subTest(question=question):
                c=self.ask(question=question)
                self.assertFalse(c['answer_supported'])
                for cl in c['claims']:
                    self.assertFalse(cl.get('proposition',{}).get('receipt_verified',False))
                    self.assertFalse(cl.get('proposition',{}).get('dispatch_verified',False))

    def test_source_plan_negation_or_quotation_does_not_become_arrangement(self):
        for text in (STATEMENT.replace('have told','have not told'), STATEMENT.replace('have told','plan to tell'),
                     'If approved, '+STATEMENT, '"'+STATEMENT+'"'):
            with self.subTest(text=text):self.assertFalse(self.ask(body=HEADER+text)['answer_supported'])
        self.assertFalse(self.ask(body='<blockquote><pre>'+html.escape(HEADER+STATEMENT)+'</pre></blockquote>',markup=True)['answer_supported'])

    def test_complete_letter_context_retains_cancellation_and_resource_limits(self):
        for tail in ('\nI have since canceled that request.', '\nThe instruction was withdrawn.', '\n'+'Additional context. '*300):
            with self.subTest(tail=tail[:50]):self.assertFalse(self.ask(body=HEADER+STATEMENT+tail)['answer_supported'])

    def test_display_budget_cannot_hide_complete_letter_witness(self):
        c=self.ask(max_passages=2)
        self.assertFalse(c['answer_supported'])
        self.assertTrue(c['missing'])
        self.assertTrue(any(g['undisplayed_evidence_count'] for g in c['documentary_support']['obligations']))

    def test_printed_date_changes_in_checked_quote_without_becoming_delivery_date(self):
        c=self.ask(body=(HEADER+STATEMENT).replace('1841','1842'))
        self.assertTrue(c['answer_supported'])
        p=c['claims'][0]['proposition'];self.assertEqual(p['heading_date_text'],'March 3rd, 1842')
        self.assertEqual(p['date_role'],'letter_heading_date_role_unresolved')
        self.assertFalse(p['receipt_verified'])

    def test_generic_nonpossessive_arrangement_question_keeps_prior_partial_boundary(self):
        q='Who arranged for Iris Vale to receive the atlas, and which dated letter records the arrangement?'
        self.assertIsNone(kernel.arrangement_request(q))
        self.assertFalse(self.ask(question=q)['answer_supported'])
