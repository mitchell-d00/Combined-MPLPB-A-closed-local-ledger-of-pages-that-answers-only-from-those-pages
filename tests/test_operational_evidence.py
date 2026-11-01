"""Bounded operational sentence relations; never use metadata as answer evidence."""
import tempfile
import unittest
from pathlib import Path

from mplpb_answers.operational_evidence import parse, statement_support, VERSION
from mplpb_answers.support import supported_answer
from mplpb_combined.ledger import write
from mplpb_combined.reader import PROFILES


class OperationalEvidenceTests(unittest.TestCase):
    def ask(self, question, body, **kwargs):
        with tempfile.TemporaryDirectory() as root:
            write(root, doc_id='QA-001', title='Source', scope='reference notes',
                  body=body, **kwargs)
            return supported_answer(root, question)

    def test_changed_conditional_entities_outcomes_and_full_quotes(self):
        cases = (
            ('What does it mean if the guard has gone over?',
             'If the guard has gone over, the load ran hot: shorten the soak next time rather than lowering the set point.'),
            ('What happens if the indicator turns amber?',
             'If the indicator turns amber, the control unit enters inspection mode.'),
            ('What happens if the batch is not sealed?',
             'If the batch is not sealed, reject it without issuing a receipt.'),
        )
        for question, source in cases:
            with self.subTest(question=question):
                answer = self.ask(question, source)
                self.assertEqual(answer.kind, 'return', answer.reason)
                self.assertEqual(answer.text, source)
                self.assertEqual(answer.support['frame']['version'], VERSION)
                self.assertEqual(answer.record.id, 'QA-001')

    def test_separation_lists_generalize_without_inferred_composition(self):
        for question, source in (
            ('Which bodies must be kept in separate buckets?',
             'Keep red and white bodies in separate buckets; a mixed batch cannot be sorted afterwards.'),
            ('Which samples should be kept in separate cabinets?',
             'Store wet and dry samples in separate cabinets.'),
            ('Which documents must be kept in separate folders?',
             'Keep draft and signed documents in separate folders, with a visible revision label.'),
        ):
            with self.subTest(question=question):
                answer = self.ask(question, source)
                self.assertEqual(answer.kind, 'return', answer.reason)
                self.assertEqual(answer.text, source)

    def test_no_subject_or_antecedent_substitution(self):
        cases = (
            ('What happens if the gate is open?', 'If the gate is not open, log a fault.'),
            ('What happens if the batch is not sealed?', 'If the batch is sealed, issue a receipt.'),
            ('What happens if the indicator turns amber?', 'If the indicator turns red, shut down the process.'),
            ('Which bodies must be kept in separate buckets?', 'Keep red and white glazes in separate buckets.'),
            ('Which samples must be kept in separate cabinets?', 'Keep wet and dry samples in separate buckets.'),
            ('What happens if the lock trips?', 'Perhaps if the lock trips, the controller resets.'),
        )
        for question, source in cases:
            with self.subTest(question=question):
                self.assertNotEqual(self.ask(question, source).kind, 'return')

    def test_no_rewrite_of_conditional_or_qualified_question(self):
        for q in (
            'What does it mean if the guard has gone over yesterday?',
            'What happens if the gate is open or shut?',
            'What happens if the gate is open, after repairs?',
            'Which bodies must not be kept in separate buckets?',
            'Which samples must be kept in separate cabinets tomorrow?',
            'Which samples must be kept in separate cabinets except tomorrow?',
        ):
            # The qualified sentence is not licensed by a weaker plain question.
            if parse(q):
                self.assertNotEqual(
                    self.ask(q, 'If the gate is open, notify the operator.').kind,
                    'return')
        self.assertIsNone(parse('Which bodies must not be kept in separate buckets?'))

    def test_page_context_and_heading_are_not_evidence(self):
        q = 'What happens if the batch is unsealed?'
        sentence = 'If the batch is unsealed, reject it without issuing a receipt.'
        for body in (
            '<h1>'+sentence+'</h1><p>No rule is recorded.</p>',
            'Imagine a batch. '+sentence,
            'Suppose this case is fictional. '+sentence,
            '"'+sentence+'"',
            sentence+' Perhaps the batch should be approved.',
        ):
            with self.subTest(body=body):
                self.assertNotEqual(self.ask(q, body).kind, 'return')
        self.assertNotEqual(
            self.ask(q, 'The batch requires inspection.', when_to_use=sentence).kind,
            'return')

    def test_multiple_eligible_sources_are_ambiguous(self):
        q = 'What happens if the alarm is on?'
        for second in ('If the alarm is on, inspect the relay.',
                       'If the alarm is on, shut down the motor.'):
            with tempfile.TemporaryDirectory() as root:
                write(root, doc_id='QA-001', title='One', scope='alarm',
                      body='If the alarm is on, inspect the relay.')
                write(root, doc_id='QA-002', title='Two', scope='alarm', body=second)
                self.assertEqual(supported_answer(root, q).kind, 'ambiguous')

    def test_sealed_delivery_and_exclusions_remain_authoritative(self):
        q = 'What happens if the gate is open?'
        body = 'If the gate is open, request a second inspection.'
        with tempfile.TemporaryDirectory() as root:
            write(root, doc_id='QA-001', title='Private', scope='gate',
                  body=body, external='no')
            self.assertNotEqual(supported_answer(root, q, PROFILES['external']).kind, 'return')
        with tempfile.TemporaryDirectory() as root:
            write(root, doc_id='QA-001', title='Excluded', scope='gate',
                  body=body, not_for='gate')
            self.assertNotEqual(supported_answer(root, q).kind, 'return')
        with tempfile.TemporaryDirectory() as root:
            write(root, doc_id='QA-001', title='Damaged', scope='gate', body=body)
            page = next(Path(root).glob('*.html'))
            page.write_text(page.read_text().replace('second inspection', 'first inspection'))
            self.assertNotEqual(supported_answer(root, q).kind, 'return')

    def test_parsed_frames_do_not_claim_world_truth(self):
        frame = parse('Which documents must be kept in separate folders?')
        self.assertEqual(frame.relation, 'separate_storage')
        self.assertFalse(frame.to_dict()['world_verified'])
        self.assertFalse(frame.to_dict()['execution_verified'])
