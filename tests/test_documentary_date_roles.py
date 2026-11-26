"""Shared source-bound date roles, independently worded from retained old packets."""
import html
from pathlib import Path
import tempfile
import unittest
from mplpb_combined.ledger import write, withdraw
from mplpb_answers.pipeline import answer_query

class DocumentaryDateRoleTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
        self.question='Distinguish the reported sending date and the writing date for the island circular.'
        self.body='On July 9, 1903, Lena Ortiz sent the island circular. This record was written on July 12, 1903.'
    def add(self,body=None,ident='ORIGINAL'):
        return write(self.root,doc_id=ident,title='Document',scope='archive',body_html='<pre>'+html.escape(body or self.body)+'</pre>')
    def ask(self,q=None):return answer_query(self.root,q or self.question).contract
    def test_roles_do_not_become_event_or_transmission_from_writing(self):
        self.add();a=self.ask();self.assertTrue(a['answer_supported'])
        p=a['claims'][0]['proposition'];self.assertEqual(p['verified_question'],self.question)
        w=next(v for v in p['date_links'] if v['requested_role']=='writing')
        for name in ('sending_established','receipt_established','event_occurrence_established'):self.assertIs(w[name],False)
    def test_year_is_not_borrowed(self):
        self.add(self.body.replace('July 12, 1903','July 12'));a=self.ask();self.assertTrue(a['answer_supported'])
        w=next(v for v in a['claims'][0]['proposition']['date_links'] if v['requested_role']=='writing');self.assertIsNone(w['year']);self.assertEqual(w['date_text'],'July 12')
    def test_missing_writing_does_not_turn_review_into_writing(self):
        self.add(self.body.replace('This record was written','This page was last reviewed'));self.assertFalse(self.ask()['answer_supported'])
    def test_conflicting_writing_dates_do_not_complete(self):
        self.add(self.body+' This record was written on July 13, 1903.');self.assertFalse(self.ask()['answer_supported'])
    def test_explicit_denial_is_counterevidence(self):
        self.add(self.body+' This record was not written on July 12, 1903.');self.assertFalse(self.ask()['answer_supported'])
    def test_extra_obligations_survive(self):
        self.add()
        for tail in (' and establish actual receipt.',' before the vessel arrived.',' unless the circular was withdrawn.'):
            with self.subTest(tail=tail):self.assertFalse(self.ask(self.question.rstrip('.')+tail)['answer_supported'])
    def test_withdrawal_changes_current_eligibility(self):
        self.add();self.assertTrue(self.ask()['answer_supported']);withdraw(self.root,'ORIGINAL');self.assertFalse(self.ask()['answer_supported'])
    def test_wrapping_preserves_witness_bytes(self):
        self.add(self.body.replace('Lena Ortiz sent','Lena Ortiz\nsent').replace('record was','record\nwas').replace('July 12, 1903','July 12,\n1903'))
        a=self.ask();self.assertTrue(a['answer_supported']);w=next(v for v in a['claims'][0]['proposition']['date_links'] if v['requested_role']=='writing');self.assertEqual(w['date_text'],'July 12,\n1903')

if __name__=='__main__':unittest.main()
