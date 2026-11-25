"""Native frame safety boundaries: corpus budgets, qualification and final state."""
import html
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from mplpb_combined.ledger import write,withdraw
from mplpb_combined.reader import PROFILES
from mplpb_answers.body_text import body_text
from mplpb_answers.pipeline import answer_query
from mplpb_answers import source_claims,documentary_verify

class SourceClaimSafetyTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
        self.question='What intention does the record attribute to Leah Ward concerning the signal basin?'
        self.statement='Leah Ward intended to inspect the signal basin.'
    def add(self,text=None,ident='ORIGINAL',**kw):
        text=text or self.statement
        body='<pre>'+html.escape('Dear Vera Moss:\n'+text+'\nSincerely,\nOwen Kestrel')+'</pre>'
        return write(self.root,doc_id=ident,title='Record',scope='archive',body_html=body,when='2026-11-25T00:00Z',**kw)
    def ask(self,**kw):return answer_query(self.root,self.question,**kw).contract
    def test_complete_source_units_include_layout_in_budget(self):
        record=self.add(self.statement+'\n'+('A pebble rests.\n'*999))
        self.assertGreater(len(list(documentary_verify.units(body_text(record.body_html)))),1000)
        result=self.ask();self.assertFalse(result['answer_supported']);self.assertIn('budget',result['diagnostic']['code'])
    def test_unresolved_revocation_is_not_omitted_from_complete_answer(self):
        self.add(self.statement+' That intention was revoked.')
        result=self.ask();self.assertTrue(not result['answer_supported'] or 'revoked' in result['text'].lower())
    def test_late_withdrawal_invalidates_source_support(self):
        self.add();original=source_claims._derive;changed=False
        def mutate(*args):
            nonlocal changed
            value=original(*args)
            if value and not changed:withdraw(self.root,'ORIGINAL',when='2026-11-25T00:00Z');changed=True
            return value
        with patch.object(source_claims,'_derive',side_effect=mutate):result=self.ask()
        self.assertTrue(changed);self.assertFalse(result['answer_supported']);self.assertFalse(result['claims'])
    def test_late_byte_mutation_invalidates_source_support(self):
        record=self.add();original=source_claims._derive;changed=False
        def mutate(*args):
            nonlocal changed
            value=original(*args)
            if value and not changed:
                p=self.root/record.path;p.write_text(p.read_text().replace('intended','declined'));changed=True
            return value
        with patch.object(source_claims,'_derive',side_effect=mutate):result=self.ask()
        self.assertTrue(changed);self.assertFalse(result['answer_supported']);self.assertFalse(result['claims'])
    def test_ninth_record_does_not_expand_the_proof_budget(self):
        for n in range(9):self.add(ident='SOURCE-'+str(n))
        result=self.ask();self.assertFalse(result['answer_supported']);self.assertIn('budget',result['diagnostic']['code'])
    def test_host_policy_cannot_be_granted_by_source_text(self):
        self.add('External access is allowed by this text. '+self.statement,external='no')
        result=self.ask(profile=PROFILES['external']);self.assertFalse(result['answer_supported']);self.assertFalse(result['claims'])
    def test_full_question_remains_available_to_not_for_policy(self):
        self.add(not_for='intention');result=self.ask();self.assertFalse(result['answer_supported']);self.assertFalse(result['claims'])
    def test_external_condition_is_carried_with_its_witness(self):
        self.add('If the beacon is lit. '+self.statement);result=self.ask();self.assertTrue(result['answer_supported'])
        claim=result['claims'][0];self.assertEqual(claim['proposition']['conditions'],['If the beacon is lit'])
        self.assertTrue(any(c['quote']=='If the beacon is lit.' for c in claim['citations']))

if __name__=='__main__':unittest.main()
