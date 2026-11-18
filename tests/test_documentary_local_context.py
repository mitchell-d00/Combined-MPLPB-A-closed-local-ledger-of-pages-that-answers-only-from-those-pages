"""A local topic witness may support an excerpt, never resolve its referent."""
import tempfile
from pathlib import Path
import unittest
from mplpb_combined.ledger import write
from mplpb_answers.pipeline import answer_query


class LocalContextTests(unittest.TestCase):
    def ask(self,body):
        with tempfile.TemporaryDirectory() as root:
            write(root,doc_id='DOC-1',title='Archive',scope='archive',body=body)
            return answer_query(root,'Who surveyed Cedar Valley?').contract

    def test_context_retains_checked_statement_without_binding_area(self):
        r=self.ask('Mira Vale surveyed the area in 1881. The Cedar Valley archive retains the note.')
        self.assertEqual(r['kind'],'partial_answer');self.assertFalse(r['answer_supported'])
        self.assertEqual(r['claims'][0]['proposition']['actor_text'],'Mira Vale')
        self.assertFalse(r['claims'][0]['proposition']['context_identity_resolved'])
        self.assertTrue(r['claims'][0]['source_support_established'])
        self.assertTrue(any('does not resolve' in q for q in r['claims'][0]['qualifiers']))

    def test_different_paragraph_does_not_bind_or_bridge(self):
        r=self.ask('Mira Vale surveyed the area in 1881.\n\nThe Cedar Valley archive retains an unrelated note.')
        self.assertFalse(r['answer_supported']);self.assertFalse(r['claims'])

    def test_condition_and_quote_prevent_action_certification(self):
        for prefix in ('If approved, ', 'Quoted example: '):
            with self.subTest(prefix=prefix):
                r=self.ask(prefix+'Mira Vale surveyed the area in 1881. The Cedar Valley archive retains the note.')
                self.assertFalse(r['answer_supported']);self.assertFalse(r['claims'])


if __name__=='__main__':unittest.main()
