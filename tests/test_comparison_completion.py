"""Complete source-comparison obligations; no historical authenticity claim."""
import html
from pathlib import Path
import tempfile
import unittest
from mplpb_combined.ledger import write
from mplpb_combined.reader import PROFILES
from mplpb_answers.pipeline import answer_query


class ComparisonCompletionTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
        self.question="Compare the opening rule claim in Iris Vale's rough draft and the final Harbor Charter transcript. What wording changed and what remained?"

    def record(self,id,frame,text,**kw):
        return write(self.root,doc_id=id,title='Untrusted routing title',scope='archive',body_html='<p>'+html.escape(frame)+'</p><p>'+html.escape(text)+'</p>',**kw)

    def pair(self,**kw):
        self.record('DRAFT',"(This is Professor Clara Reed's reconstruction of Iris Vale's \"original Rough draught\" of the Harbor Charter before it was revised by the council.)",'We hold these rules to be fair and binding.')
        return self.record('TRANSCRIPT','Note: The following text is a transcription of the copper engraving of the parchment Harbor Charter. The spelling and punctuation reflect the original.','We hold these rules to be clear and binding.',**kw)

    def test_complete_comparison_checks_roles_target_and_both_operations(self):
        self.pair();r=answer_query(self.root,self.question).contract
        self.assertEqual(r['kind'],'supported_answer');self.assertTrue(r['answer_supported'])
        self.assertFalse(r['missing']);self.assertIn('fair',r['text']);self.assertIn('clear',r['text'])
        self.assertIn('and binding.',r['text']);self.assertFalse(r['verification']['truth_verified'])
        p=r['claims'][0];self.assertTrue(p['proposition']['question_obligations_verified']);self.assertEqual(len(p['citations']),4)
        self.assertFalse(p['historical_truth_independently_verified'])

    def test_missing_documentary_framing_does_not_complete(self):
        self.record('A','Archive record.','We hold these rules to be fair and binding.')
        self.record('B','Archive record.','We hold these rules to be clear and binding.')
        self.assertFalse(answer_query(self.root,self.question).contract['answer_supported'])

    def test_different_work_reference_does_not_complete(self):
        r=self.pair();p=self.root/r.path
        # A properly sealed alternate source, not source corruption, supplies a
        # different named work. Existing source remains a distinct appearance.
        self.record('OTHER','Note: The following text is a transcription of the copper engraving of the Harbor Ledger.','We hold these rules to be clear and binding.')
        q=self.question.replace('Harbor Charter','Harbor Ledger')
        self.assertFalse(answer_query(self.root,q).contract['answer_supported'])

    def test_ambiguous_transcriptions_do_not_choose_a_winner(self):
        self.pair();self.record('ANOTHER','Note: The following text is a transcription of the stone engraving of the parchment Harbor Charter.','We hold these rules to be firm and binding.')
        self.assertFalse(answer_query(self.root,self.question).contract['answer_supported'])

    def test_request_for_motive_is_not_answered_by_word_differences(self):
        self.pair();r=answer_query(self.root,self.question+' Why did the council change it?').contract
        self.assertFalse(r['answer_supported']);self.assertTrue(r['missing'])

    def test_wrong_author_cannot_be_resolved_by_proximity(self):
        self.pair();q=self.question.replace('Iris Vale','Orin Hale')
        self.assertFalse(answer_query(self.root,q).contract['answer_supported'])

    def test_restricted_transcription_cannot_complete(self):
        self.pair(external='no');r=answer_query(self.root,self.question,profile=PROFILES['external']).contract
        self.assertFalse(r['answer_supported'])

    def test_display_budget_must_include_identity_witnesses(self):
        self.pair();r=answer_query(self.root,self.question,max_passages=3).contract
        self.assertFalse(r['answer_supported']);self.assertTrue(r['missing'])

    def test_unrelated_topic_does_not_complete_by_shared_wording(self):
        self.pair();q=self.question.replace('rule claim','ship claim')
        self.assertFalse(answer_query(self.root,q).contract['answer_supported'])

    def test_different_question_wording_uses_same_evidence_rule(self):
        self.pair();q="How does the first rule statement in Iris Vale's rough draft differ from the Harbor Charter transcript? What wording is shared?"
        self.assertTrue(answer_query(self.root,q).contract['answer_supported'])

    def test_qualified_framing_is_not_an_identity_witness(self):
        self.record('DRAFT',"(This is perhaps a reconstruction of Iris Vale's \"original Rough draught\" of the Harbor Charter before it was revised by the council.)",'We hold these rules to be fair and binding.')
        self.record('TRANSCRIPT','Note: The following text is a transcription of the copper engraving of the parchment Harbor Charter.','We hold these rules to be clear and binding.')
        self.assertFalse(answer_query(self.root,self.question).contract['answer_supported'])

    def test_titles_cannot_replace_body_role_evidence(self):
        write(self.root,doc_id='A',title="Iris Vale's rough draft",scope='Harbor Charter',body='We hold these rules to be fair and binding.')
        write(self.root,doc_id='B',title='Final Harbor Charter transcript',scope='Harbor Charter',body='We hold these rules to be clear and binding.')
        self.assertFalse(answer_query(self.root,self.question).contract['answer_supported'])

    def test_quoted_role_declaration_does_not_complete(self):
        self.pair()
        write(self.root,doc_id='QUOTED',title='Another account',scope='archive',body_html='<blockquote><p>Note: The following text is a transcription of the copper engraving of the parchment Harbor Charter.</p></blockquote><p>We hold these rules to be firm and binding.</p>')
        # Quoted source-declaration text cannot introduce another positive role
        # witness or establish its author's actual document classification.
        r=answer_query(self.root,self.question).contract
        self.assertTrue(r['answer_supported']);self.assertEqual({s['id'] for s in r['sources']},{'DRAFT','TRANSCRIPT'})

    def test_source_mutation_discards_completed_answer(self):
        from unittest.mock import patch
        from mplpb_answers import documentary_verify
        record=self.pair();original=documentary_verify.check
        def mutate(*args,**kw):
            result=original(*args,**kw);p=self.root/record.path;p.write_text(p.read_text().replace('Harbor Charter','Harbor Ledger'));return result
        with patch('mplpb_answers.documentary.kernel.check',side_effect=mutate):r=answer_query(self.root,self.question).contract
        self.assertEqual(r['kind'],'abstain');self.assertFalse(r['answer_supported']);self.assertFalse(r['claims'])

    def test_wrapped_plaintext_paragraphs_preserve_completion_and_offsets(self):
        left="(This is Professor Clara Reed's reconstruction of Iris Vale's \"original Rough draught\" of the Harbor Charter before it was revised by the council.)\n\nWe hold these rules to be fair\nand binding."
        right='Note: The following text is a transcription of the copper engraving of the parchment Harbor Charter.\n\nWe hold these rules to be clear\nand binding.'
        write(self.root,doc_id='A',title='Raw record',scope='archive',body_html='<pre>'+html.escape(left)+'</pre>')
        write(self.root,doc_id='B',title='Raw record',scope='archive',body_html='<pre>'+html.escape(right)+'</pre>')
        r=answer_query(self.root,self.question).contract;self.assertTrue(r['answer_supported'])
        self.assertTrue(any('\n' in c['quote'] for c in r['claims'][0]['citations']))

    def test_question_closure_does_not_silently_drop_extra_obligations(self):
        from mplpb_answers.documentary_verify import comparison_request
        for suffix in [' Who changed it?',' Why?',' 1776',' What wording changed in 1776?',' What wording changed if approved?']:
            with self.subTest(suffix=suffix):self.assertIsNone(comparison_request(self.question+suffix))

    def test_admission_metadata_does_not_supply_the_topic(self):
        from mplpb_answers.source_units import comparison_units
        rec=write(self.root,doc_id='CAPTURE',title='Archive',scope='archive',body_html='<pre>Original source text.\n\nSource capture: {&quot;title&quot;:&quot;rules&quot;}</pre>')
        self.assertFalse(any(q.startswith('Source capture:') for a,b,q in comparison_units(rec)))

    def test_plan_heading_does_not_become_a_document_identity_witness(self):
        self.record('TRANSCRIPT','Note: The following text is a transcription of the copper engraving of the parchment Harbor Charter.','We hold these rules to be clear and binding.')
        frame="(This is Professor Clara Reed's reconstruction of Iris Vale's \"original Rough draught\" of the Harbor Charter before it was revised by the council.)"
        write(self.root,doc_id='DRAFT',title='Draft',scope='archive',body_html='<h2>Plan</h2><p>'+html.escape(frame)+'</p><p>We hold these rules to be fair and binding.</p>')
        self.assertFalse(answer_query(self.root,self.question).contract['answer_supported'])
