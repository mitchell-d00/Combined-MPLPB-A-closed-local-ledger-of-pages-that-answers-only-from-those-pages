"""Document-layout boundaries must not erase source modality or quotation scope."""
import html
from pathlib import Path
import tempfile
import unittest
from mplpb_combined.ledger import write
from mplpb_answers.pipeline import answer_query


class DocumentaryHeaderScopeTests(unittest.TestCase):
    def result(self,subject,question):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            body='From: Selma Birch\nTo: Quentin Moss\nSubject: '+subject+'\nMessage-ID: Q-44\nQuentin Moss sent the basalt chart.'
            write(root,doc_id='LOG-1',title='Archive',scope='archive',body_html='<pre>'+html.escape(body)+'</pre>')
            return answer_query(root,question).contract

    def test_header_scope_survives_sentence_segmentation(self):
        for subject in ['Plan','Proposal','Draft','Conditional scenario','Hypothetical example','Reported instructions']:
            with self.subTest(subject=subject):
                self.assertFalse(self.result(subject,'Who sent the basalt chart?')['answer_supported'])

    def test_neutral_header_preserves_explicit_action_discovery(self):
        self.assertTrue(self.result('Dispatch record','Who sent the basalt chart?')['answer_supported'])

    def test_plan_can_still_supply_literal_words_without_execution(self):
        result=self.result('Plan','Which document contains the exact words "Quentin Moss sent"?')
        self.assertTrue(result['answer_supported'])
        self.assertEqual(result['claims'][0]['support_scope'],'textual_occurrence')

    def test_folded_or_over_budget_headers_do_not_become_action_statements(self):
        bodies=['From: Selma Birch\nTo: Quentin Moss\nSubject: Dispatch\n Quentin Moss sent the basalt chart.',
                '\ufeffFROM: Sélma Birch\r\nTO: Quentin Moss\r\nSUBJECT: PLAN.\r\nQuentin Moss sent the basalt chart.',
                'From: Selma Birch\nTo: Quentin Moss\nX-Context: Plan.\nQuentin Moss sent the basalt chart.',
                'From: Selma Birch\nSubject: Plan.\nQuentin Moss sent the basalt chart.',
                'From: Selma Birch\nTo: Quentin Moss\n'+('Cc: Archive desk\n'*17)+
                'Subject: Plan\nQuentin Moss sent the basalt chart.']
        for body in bodies:
            with self.subTest(body=body),tempfile.TemporaryDirectory() as tmp:
                root=Path(tmp);write(root,doc_id='LOG-1',title='Archive',scope='archive',
                                    body_html='<pre>'+html.escape(body)+'</pre>')
                self.assertFalse(answer_query(root,'Who sent the basalt chart?').contract['answer_supported'])

    def test_explicit_physical_separator_allows_indented_body(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            body='From: Selma Birch\nTo: Quentin Moss\nSubject: Dispatch\n\n    Quentin Moss sent the basalt chart.'
            write(root,doc_id='LOG-1',title='Archive',scope='archive',body_html='<pre>'+html.escape(body)+'</pre>')
            self.assertTrue(answer_query(root,'Who sent the basalt chart?').contract['answer_supported'])

    def test_document_date_labels_are_not_action_counterstatements(self):
        for date_role,past in [('written','wrote'),('sent','sent')]:
            with self.subTest(date_role=date_role),tempfile.TemporaryDirectory() as tmp:
                root=Path(tmp)
                body=('From: Selma Birch\nTo: Quentin Moss\nDate '+date_role+': April 7, 1872\n'
                      'Subject: The basalt chart\n\nQuentin Moss '+past+' the basalt chart.')
                write(root,doc_id='LOG-1',title='Archive',scope='archive',body_html='<pre>'+html.escape(body)+'</pre>')
                self.assertTrue(answer_query(root,'Who '+past+' the basalt chart?').contract['answer_supported'])

    def test_explicit_structural_example_and_plan_layers_block_action_proof(self):
        for before,after in [('<div class="documentation_example"><pre>','</pre></div>'),
                             ('<h2 class="proposed">Text</h2><pre>','</pre>')]:
            with self.subTest(before=before),tempfile.TemporaryDirectory() as tmp:
                root=Path(tmp);body='From: Selma Birch\nTo: Quentin Moss\nSubject: Dispatch\n\nQuentin Moss sent the basalt chart.'
                write(root,doc_id='LOG-1',title='Archive',scope='archive',body_html=before+html.escape(body)+after)
                self.assertFalse(answer_query(root,'Who sent the basalt chart?').contract['answer_supported'])
                self.assertTrue(answer_query(root,'Which source contains the exact words "Quentin Moss sent"?').contract['answer_supported'])

    def test_self_ascribed_plan_scope_is_not_a_bare_word_filter(self):
        bodies=['This is a plan. Quentin Moss sent the basalt chart.',
                'Quentin Moss sent the basalt chart. This is merely a proposal.',
                'What follows is a draft.\n\nQuentin Moss sent the basalt chart.']
        for body in bodies:
            with self.subTest(body=body),tempfile.TemporaryDirectory() as tmp:
                root=Path(tmp);write(root,doc_id='LOG-1',title='Archive',scope='archive',body_html='<pre>'+html.escape(body)+'</pre>')
                self.assertFalse(answer_query(root,'Who sent the basalt chart?').contract['answer_supported'])
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);write(root,doc_id='LOG-1',title='Archive',scope='archive',
                                body_html='<p>The archive retained a proposal. Quentin Moss sent the basalt chart.</p>')
            self.assertTrue(answer_query(root,'Who sent the basalt chart?').contract['answer_supported'])

    def test_markdown_fences_and_quote_continuations_are_not_bare_actions(self):
        for body in ['```text\nNOTE\nQuentin Moss sent the basalt chart.\n```',
                     '~~~text\nNOTE\nQuentin Moss sent the basalt chart.\n~~~',
                     '> A copied statement.\nQuentin Moss sent the basalt chart.']:
            with self.subTest(body=body),tempfile.TemporaryDirectory() as tmp:
                root=Path(tmp);write(root,doc_id='LOG-1',title='Archive',scope='archive',body_html='<pre>'+html.escape(body)+'</pre>')
                self.assertFalse(answer_query(root,'Who sent the basalt chart?').contract['answer_supported'])
                self.assertTrue(answer_query(root,'Which source contains the exact words "Quentin Moss sent"?').contract['answer_supported'])

    def test_header_topic_is_not_a_second_causal_event_appearance(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            body=('From: Selma Birch\nTo: Quentin Moss\nDate written: April 7, 1872\n'
                  'Subject: The dock inspection\n\nThe dock inspection was postponed because of ice.')
            write(root,doc_id='LOG-1',title='Archive',scope='archive',body_html='<pre>'+html.escape(body)+'</pre>')
            self.assertTrue(answer_query(root,'Why was the dock inspection postponed?').contract['answer_supported'])
