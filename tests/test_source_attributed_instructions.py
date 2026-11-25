"""Permanent attribution, reporting-layer, state and budget preservation controls."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from mplpb_answers.pipeline import answer_query
from mplpb_answers import attributed_instruction as rule
from mplpb_combined.ledger import write, revise, withdraw

Q = 'According to the report, what did Selma Duarte instruct the coastal survey crew to do?'
TASK = 'Chart the western inlet before Monday'
STATEMENT = 'Selma Duarte instructed the coastal survey crew: “'+TASK+'.”'


class SourceAttributionTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def source(self, statement=STATEMENT, ident='SOURCE-1', frame='report', before='', after='', wrapper=''):
        if frame == 'letter':
            parts = ['Dear Director Leon Kato:', statement, 'Respectfully,', 'Selma Duarte']
        elif frame == 'minutes':
            parts = ['Meeting minutes.', 'Recorded by Tomas Ivers.', statement]
        else:
            parts = ['Report.', 'Written by Tomas Ivers.', statement]
        html = before+''.join('<p>'+p+'</p>' for p in parts)+after
        if wrapper:
            html='<'+wrapper+'>'+html+'</'+wrapper+'>'
        return write(self.root, doc_id=ident, title='Attribution source', scope='documentary originals',
                     body_html=html, origin='machine', external='yes')

    def ask(self, question=Q, **kwargs):
        return answer_query(self.root, question, **kwargs).contract

    def withheld(self, answer):
        self.assertFalse(answer['answer_supported']); self.assertEqual(answer['claims'], [])

    def test_report_preserves_speaker_distinct_from_writer(self):
        self.source(); out=self.ask(); self.assertTrue(out['answer_supported'])
        p=out['claims'][0]['proposition']
        self.assertEqual(p['actor'],'Selma Duarte'); self.assertEqual(p['writer'],'Tomas Ivers')
        self.assertEqual(p['source_voice'],'report_attributes_quotation')
        self.assertEqual(p['modality'],'instruction_only'); self.assertFalse(p['completion_established'])
        self.assertTrue(any(c['quote']==STATEMENT for c in out['claims'][0]['citations']))
        self.withheld(self.ask(Q.replace('Selma Duarte','Tomas Ivers')))

    def test_minutes_use_the_named_instructor(self):
        self.source('Selma Duarte ordered the coastal survey crew to chart the western inlet before Monday.',frame='minutes')
        out=self.ask(Q.replace('report','minutes')); self.assertTrue(out['answer_supported'])
        self.assertEqual(out['claims'][0]['proposition']['source_voice'],'minutes_attributes_instruction')

    def test_signed_letter_first_person_binds_full_signature(self):
        self.source('I instruct the coastal survey crew to chart the western inlet before Monday.',frame='letter')
        out=self.ask(Q.replace('report','letter')); self.assertTrue(out['answer_supported'])
        self.assertEqual(out['claims'][0]['proposition']['source_voice'],'signed_letter_first_person')

    def test_letter_can_attribute_a_quotation_to_someone_else(self):
        self.source(STATEMENT.replace('Selma Duarte','Oskar Velas'),frame='letter')
        q=Q.replace('report','letter'); self.withheld(self.ask(q))
        out=self.ask(q.replace('Selma Duarte','Oskar Velas')); self.assertTrue(out['answer_supported'])
        self.assertEqual(out['claims'][0]['proposition']['writer'],'Selma Duarte')

    def test_completion_question_withholds_despite_instruction(self):
        self.source(); self.withheld(self.ask('According to the report, did the coastal survey crew complete the task instructed by Selma Duarte?'))

    def test_passive_keeps_actor_and_recipient_roles(self):
        self.source('The coastal survey crew was instructed by Selma Duarte to chart the western inlet before Monday.',frame='minutes')
        self.assertTrue(self.ask(Q.replace('report','minutes'))['answer_supported'])

    def test_passive_first_person_uses_signed_letter_only(self):
        self.source('The coastal survey crew is instructed by me to chart the western inlet before Monday.',frame='letter')
        self.assertTrue(self.ask(Q.replace('report','letter'))['answer_supported'])

    def test_postposed_quote_keeps_named_speaker(self):
        self.source('“'+TASK+',” Selma Duarte directed the coastal survey crew.')
        self.assertTrue(self.ask()['answer_supported'])

    def test_report_first_person_has_no_signature_binding(self):
        self.source('I instruct the coastal survey crew to chart the western inlet before Monday.')
        self.withheld(self.ask())

    def test_initials_and_pronouns_do_not_supply_identity(self):
        for actor in ['S. D.','She','The director']:
            with self.subTest(actor=actor):
                old=self.root
                with TemporaryDirectory() as folder:
                    self.root=Path(folder)
                    self.source(STATEMENT.replace('Selma Duarte',actor)); self.withheld(self.ask())
                self.root=old

    def test_unsupported_outer_reporting_layer_withholds(self):
        self.source('Tomas Ivers reports that '+STATEMENT); self.withheld(self.ask())

    def test_unattributed_bare_quotation_withholds(self):
        self.source('“'+TASK+'.”'); self.withheld(self.ask())

    def test_negation_and_conditions_in_instruction_withhold(self):
        for text in [STATEMENT.replace('instructed','did not instruct'),
                                      STATEMENT.replace('instructed','allegedly instructed'),
                                      STATEMENT.replace('before Monday','if access opens')]:
            with self.subTest(text=text):
                old=self.root
                with TemporaryDirectory() as folder:
                    self.root=Path(folder); self.source(text); self.withheld(self.ask())
                self.root=old

    def test_separate_conditional_governor_cannot_be_discarded(self):
        self.source('<p>If the harbor closes:</p><p>'+STATEMENT); self.withheld(self.ask())

    def test_quoted_or_hypothetical_document_withholds(self):
        self.source(wrapper='blockquote'); self.withheld(self.ask())

    def test_title_does_not_supply_body_writer(self):
        write(self.root,doc_id='SOURCE-1',title='Report written by Tomas Ivers',scope='report',body_html='<p>'+STATEMENT+'</p>')
        self.withheld(self.ask())

    def test_wrong_requested_source_form_withholds(self):
        self.source(); self.withheld(self.ask(Q.replace('report','minutes')))

    def test_multiple_sources_do_not_select_one(self):
        self.source(); self.source(ident='SOURCE-2'); self.withheld(self.ask())

    def test_unframed_competing_instruction_is_not_pruned(self):
        self.source()
        write(self.root,doc_id='SOURCE-2',title='Another report',scope='documentary originals',
              body_html='<p>'+STATEMENT.replace('western','eastern')+'</p>')
        self.withheld(self.ask())

    def test_two_tasks_for_actor_do_not_collapse_to_one(self):
        self.source(after='<p>'+STATEMENT.replace('western','eastern')+'</p>'); self.withheld(self.ask())

    def test_withdrawal_withholds(self):
        self.source(); withdraw(self.root,'SOURCE-1'); self.withheld(self.ask())

    def test_final_mutation_discards_witnesses(self):
        self.source(); original=rule._proof
        def mutate(*args):
            result=original(*args); revise(self.root,'SOURCE-1',body='Revised source.'); return result
        with patch.object(rule,'_proof',side_effect=mutate): out=self.ask()
        self.withheld(out); self.assertEqual(out['diagnostic']['code'],'source_changed')

    def test_output_and_passage_budgets_withhold(self):
        self.source()
        self.withheld(self.ask(max_passages=1))
        with self.assertRaises(ValueError): self.ask(max_chars=200)

    def test_native_output_character_budget_withholds(self):
        from mplpb_answers.passages import PassageIndex
        from mplpb_combined.reader import PROFILES
        self.source(); index=PassageIndex(self.root,Q,PROFILES['internal'])
        result=rule.verify(index,12,100)
        self.assertEqual(result,('abstain','reader_budget_exceeded',{}))

    def test_record_budget_withholds_without_pruning(self):
        self.source()
        for i in range(8):
            write(self.root,doc_id='EXTRA-'+str(i),title='Note',scope='evidence',body_html='<p>A separate note.</p>')
        out=self.ask(); self.withheld(out); self.assertEqual(out['diagnostic']['code'],'reference_scan_budget')

    def test_scan_characters_budget_withholds(self):
        self.source(); write(self.root,doc_id='EXTRA-1',title='Long note',scope='evidence',body_html='<p>'+'x '*100001+'</p>')
        out=self.ask(); self.withheld(out); self.assertEqual(out['diagnostic']['code'],'reference_scan_budget')

    def test_scan_units_budget_withholds(self):
        self.source(); write(self.root,doc_id='EXTRA-1',title='Many notes',scope='evidence',body_html=''.join('<p>Note '+str(i)+'.</p>' for i in range(1001)))
        out=self.ask(); self.withheld(out); self.assertEqual(out['diagnostic']['code'],'reference_scan_budget')

    def test_task_phrase_limit_is_not_expanded(self):
        self.source(STATEMENT.replace(TASK,'Chart '+('x'*601)))
        self.withheld(self.ask())


if __name__=='__main__': unittest.main()
