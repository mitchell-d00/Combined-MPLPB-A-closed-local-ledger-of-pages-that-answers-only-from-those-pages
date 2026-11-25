"""A non-authoritative derived hint cannot veto a checked original statement."""
from pathlib import Path
import tempfile
import unittest
from mplpb_combined.ledger import write
from mplpb_answers.pipeline import answer_query

class SourceClaimAuthorityTests(unittest.TestCase):
    def test_derived_counter_hint_cannot_remove_original_support(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);q='What intention does the record attribute to Leah Ward concerning the signal basin?'
            original=write(root,doc_id='ORIGINAL',title='Original',scope='archive',origin='machine',external='yes',when='2026-11-25T00:00Z',body_html='<p>Leah Ward intended to inspect the signal basin.</p>')
            self.assertTrue(answer_query(root,q).contract['answer_supported'])
            write(root,doc_id='DERIVED',title='Derived review hint',scope='archive',origin='machine',external='yes',when='2026-11-25T00:00Z',derived_from=[original.id+'@'+original.hash_actual],body_html='<p>Leah Ward did not intend to inspect the signal basin.</p>')
            result=answer_query(root,q).contract
            self.assertTrue(result['answer_supported'])
            self.assertTrue(all(c['source_id']=='ORIGINAL' for claim in result['claims'] for c in claim['citations']))

if __name__=='__main__':unittest.main()
