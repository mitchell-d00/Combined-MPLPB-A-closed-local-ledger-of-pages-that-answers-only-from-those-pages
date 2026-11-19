"""Literal source-location questions prove text presence, never the quoted event."""
import html
from pathlib import Path
import tempfile
import unittest
from mplpb_answers.pipeline import answer_query
from mplpb_combined.ledger import write
from mplpb_combined.reader import PROFILES


class TextLocationTests(unittest.TestCase):
    def answer(self,bodies,question,**kwargs):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            for n,body in enumerate(bodies):
                write(root,doc_id='LETTER-'+str(n),title='Archive',scope='archive',
                      body_html='<pre>'+html.escape(body)+'</pre>',external='no')
            return answer_query(root,question,**kwargs).contract

    def test_location_accepts_only_textual_presence_in_quoted_or_conditional_text(self):
        q='Which document includes the exact wording "if the tide turns"? Find the wording only.'
        result=self.answer(['An illustrative quotation says: "We may depart if the tide turns."'],q)
        self.assertTrue(result['answer_supported'])
        self.assertEqual(result['claims'][0]['support_scope'],'textual_occurrence')
        self.assertFalse(result['claims'][0]['historical_truth_independently_verified'])
        self.assertEqual(result['question'],q)

    def test_wrapped_unicode_words_keep_exact_source_citation(self):
        result=self.answer(['The note says: Élise\r\nheld the basalt chart.'],
                           'What record contains the exact words "Élise held the basalt chart"?')
        self.assertTrue(result['answer_supported']);self.assertIn('Élise\nheld',result['claims'][0]['citations'][0]['quote'])

    def test_word_boundary_absence_and_extra_historical_claim_refuse(self):
        for question in ['Which source contains the exact words "open door"?',
                         'Which source contains the exact words "departure occurred"? Establish completed delivery.',
                         'If authorized, which source contains the exact words "departure occurred"?']:
            with self.subTest(question=question):
                self.assertFalse(self.answer(['The open doorway is mentioned. The phrase departure occurred is quoted.'],question)['answer_supported'])

    def test_two_source_owners_and_profile_restriction_stop(self):
        q='Which source contains the exact words "the tide turns"?'
        self.assertFalse(self.answer(['If the tide turns.','The words the tide turns are copied.'],q)['answer_supported'])
        self.assertFalse(self.answer(['If the tide turns.'],q,profile=PROFILES['external'])['answer_supported'])

    def test_literal_presence_cannot_answer_an_execution_question(self):
        self.assertFalse(self.answer(['A demonstration says: "Quentin Moss sent the basalt chart."'],
                                     'Who sent the basalt chart?')['answer_supported'])

    def test_title_and_over_budget_statement_cannot_supply_a_literal_answer(self):
        q='Which source contains the exact words "the tide turns"?'
        self.assertFalse(self.answer(['The tide turns '+('beside the distant shoreline '*70)+'.'],
                                     q,max_chars=1000)['answer_supported'])
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            write(root,doc_id='LETTER-1',title='the tide turns',scope='archive',body_html='<p>No such wording.</p>')
            self.assertFalse(answer_query(root,q).contract['answer_supported'])

    def test_forged_literal_proposal_cannot_close_a_semantic_question(self):
        from mplpb_answers.documentary_verify import check
        from mplpb_answers.passages import PassageIndex
        from mplpb_answers.body_text import body_text
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);record=write(root,doc_id='LETTER-1',title='Archive',scope='archive',
                                     body_html='<p>A witness alleged that the departure caused the flood.</p>')
            body=body_text(record.body_html)
            proposal={'kind':'literal_location','source_id':record.id,'path':record.path,'hash':record.hash_actual,
                      'start':0,'end':len(body),'quote':body}
            index=PassageIndex(root,'Did the departure cause the flood?',PROFILES['internal'])
            self.assertFalse(check(index,[proposal])['proofs'])
