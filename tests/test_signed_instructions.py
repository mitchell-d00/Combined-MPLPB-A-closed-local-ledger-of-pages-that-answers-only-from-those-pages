"""Independent wording, source voice, eligibility and budget controls."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from mplpb_answers.pipeline import answer_query
from mplpb_answers import documentary_instruction as instruction
from mplpb_combined.ledger import write, revise, withdraw


QUESTION = 'What task did Irene Salas give the coastal mapping delegation in the letter to Chen?'
DIRECTIVE = 'The task of the coastal mapping delegation is to survey the western inlet before Tuesday.'


class SignedInstructionTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def letter(self, ident='LETTER-1', signer='Irene Salas', recipient='Chen',
               lead='I provide my instructions for the coastal mapping delegation.',
               directive=DIRECTIVE, before='', after='', closing='Yours sincerely,',
               wrapper=None):
        html = ('<p>Dear Director '+recipient+':</p><p>'+lead+'</p>'+before
                +'<p>'+directive+'</p>'+after+'<p>'+closing+'</p><p>'+signer+'</p>')
        if wrapper:html='<'+wrapper+'>'+html+'</'+wrapper+'>'
        return write(self.root,doc_id=ident,title='Retained letter',scope='documentary originals',
                     body_html=html,origin='machine',external='yes')

    def answer(self, question=QUESTION, **kwargs):
        return answer_query(self.root,question,**kwargs).contract

    def withheld(self, out):
        self.assertFalse(out['answer_supported']);self.assertEqual(out['claims'],[])

    def test_separate_wording_preserves_instruction_voice_and_deadline(self):
        self.letter();out=self.answer();self.assertTrue(out['answer_supported'])
        p=out['claims'][0]['proposition']
        self.assertEqual((p['actor'],p['action'],p['source_voice'],p['modality']),
                         ('Irene Salas','instruct','signed_letter_first_person','instruction_only'))
        self.assertFalse(p['time']['completion_established'])
        self.assertEqual(p['time']['source_qualifications'],['before Tuesday'])
        self.assertTrue(any(c['quote']==DIRECTIVE for c in out['claims'][0]['citations']))

    def test_full_name_matches_while_wrong_signer_and_initials_withhold(self):
        root=self.root
        for number,signer in enumerate(['Nora Bell','I. S.']):
            with self.subTest(signer=signer):
                self.root=root/str(number);self.root.mkdir()
                self.letter(signer=signer);self.withheld(self.answer())
        self.root=root

    def test_wrong_addressee_withholds(self):
        self.letter(recipient='Okafor');self.withheld(self.answer())

    def test_quoted_instruction_withholds(self):
        self.letter(directive='“'+DIRECTIVE+'”');self.withheld(self.answer())

    def test_quoted_letter_withholds(self):
        self.letter(wrapper='blockquote');self.withheld(self.answer())

    def test_reported_first_person_cannot_become_signer_voice(self):
        self.letter(lead='A visitor said, “I provide my instructions for the coastal mapping delegation.”')
        self.withheld(self.answer())

    def test_denied_first_person_cannot_become_an_instruction(self):
        self.letter(lead='I deny that I provide my instructions for the coastal mapping delegation.')
        self.withheld(self.answer())

    def test_negation_and_conditions_withhold(self):
        for number,phrase in enumerate(['is not to','is only to','is to survey, provided that access opens,']):
            with self.subTest(phrase=phrase):
                root=self.root;self.root=root/str(number);self.root.mkdir()
                self.letter(directive=DIRECTIVE.replace('is to',phrase));self.withheld(self.answer())
                self.root=root

    def test_compound_question_retains_the_unresolved_obligation(self):
        self.letter()
        first='What transition did Irene Salas intend her approach in the letter to Bell to guide'
        out=self.answer(first+', and what task did she give the coastal mapping delegation in the letter to Chen?')
        self.assertEqual(out['kind'],'partial_answer');self.assertFalse(out['answer_supported'])
        self.assertEqual(out['missing'],[first+'?']);self.assertEqual(len(out['claims']),1)

    def test_unrelated_balanced_quotation_does_not_erase_valid_instruction(self):
        self.letter(after='<p>“Keep a dry notebook.”</p>')
        self.assertTrue(self.answer()['answer_supported'])

    def test_capitalized_institution_name_is_not_a_reporting_verb(self):
        self.letter(lead='I provide my instructions for the coastal mapping delegation of Coastal Reports.')
        self.assertTrue(self.answer()['answer_supported'])

    def test_reporting_verb_as_a_task_object_is_preserved(self):
        text='The task of the coastal mapping delegation is to collect reports before Tuesday.'
        self.letter(directive=text);out=self.answer();self.assertTrue(out['answer_supported'])
        self.assertEqual(out['claims'][0]['proposition']['directive'],text)

    def test_competing_letters_and_surname_ambiguity_withhold(self):
        self.letter();self.letter(ident='LETTER-2',signer='Nora Salas')
        self.assertTrue(self.answer()['answer_supported'])
        self.withheld(self.answer(QUESTION.replace('Irene Salas','Salas')))

    def test_multiple_matching_letters_withhold(self):
        self.letter();self.letter(ident='LETTER-2');self.withheld(self.answer())

    def test_execution_question_is_not_instruction_support(self):
        self.letter();self.withheld(self.answer('What survey did the coastal mapping delegation actually complete?'))

    def test_withdrawal_and_tampering_withhold(self):
        record=self.letter();withdraw(self.root,record.id);self.withheld(self.answer())
        other=self.letter(ident='LETTER-2');path=self.root/other.path
        path.write_text(path.read_text().replace('western inlet','eastern inlet'))
        self.withheld(self.answer())

    def test_passage_budget_and_record_scan_budget_withhold(self):
        self.letter();self.withheld(self.answer(max_passages=1))
        for i in range(8):write(self.root,doc_id='EXTRA-'+str(i),title='Other original',scope='reference',
                                 body='A separate ordinary source.',origin='machine',external='yes')
        out=self.answer();self.withheld(out);self.assertEqual(out['diagnostic']['code'],'reference_scan_budget')

    def test_unit_budget_withholds_without_pruning_other_sources(self):
        self.letter();write(self.root,doc_id='EXTRA-1',title='Many units',scope='reference',
                           body_html=''.join('<p>Unit '+str(i)+' contains a note.</p>' for i in range(1002)),
                           origin='machine',external='yes')
        out=self.answer();self.withheld(out);self.assertEqual(out['diagnostic']['code'],'reference_scan_budget')

    def test_source_state_change_during_verification_discards_all_claims(self):
        self.letter();original=instruction._proof
        def mutate(*args):
            result=original(*args);revise(self.root,'LETTER-1',body='The instruction was revised.')
            return result
        with patch.object(instruction,'_proof',side_effect=mutate):out=self.answer()
        self.withheld(out);self.assertEqual(out['diagnostic']['code'],'source_changed')


if __name__=='__main__':unittest.main()
