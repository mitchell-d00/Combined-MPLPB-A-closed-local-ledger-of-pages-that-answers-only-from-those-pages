"""Author-written boundary checks, not independently reviewed historical accuracy."""
import html
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from mplpb_answers.pipeline import answer_query, refusal_category
from mplpb_combined.ledger import write


class AnswerBoundaryTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        clock = patch.dict(os.environ, {'MPLPB_NOW': '2026-11-17T00:00Z'})
        clock.start()
        self.addCleanup(clock.stop)

    def page(self, ident='SRC-1', body='Record-ID: CASE-1\nOwner: Alice', **kw):
        return write(self.root, doc_id=ident, title='Witness', scope='archive record owner location',
                     body_html='<pre>'+html.escape(body)+'</pre>', **kw)

    def ask(self, **kw):
        return answer_query(self.root, 'What is Owner for record CASE-1?', **kw).contract

    def test_coherent_original_is_supported_but_never_outside_world_truth(self):
        # No ground-truth oracle is available: this may be a coherent false page.
        self.page()
        result = self.ask()
        self.assertTrue(result['answer_supported'])
        a = result['source_assurance']
        self.assertTrue(a['outside_world_confirmation_required'])
        self.assertEqual(a['declared_evidence_root_count'], 1)
        self.assertTrue(a['single_declared_root'])
        self.assertFalse(a['authorship_authenticated'])
        self.assertFalse(a['independence_verified'])
        self.assertFalse(result['verification']['truth_verified'])
        self.assertIn('coherent false original', a['notice'])
        self.assertIn('authenticate arbitrary testimony', a['notice'])

    def test_multiple_roots_do_not_waive_confirmation(self):
        self.page()
        self.page('SRC-2')
        a = self.ask()['source_assurance']
        self.assertEqual(a['declared_evidence_root_count'], 2)
        self.assertFalse(a['single_declared_root'])
        self.assertTrue(a['outside_world_confirmation_required'])
        self.assertFalse(a['independence_verified'])

    def test_absent_eligible_source_not_universal_absence(self):
        result = self.ask()
        self.assertEqual(result['diagnostic']['category'], 'absent_eligible_source')
        self.assertEqual(result['diagnostic']['corpus_answerability'], 'not_established')
        self.assertIsNone(result['source_assurance']['declared_evidence_root_count'])

    def test_conflict_stays_conflict_even_if_budget_omits_one_witness(self):
        self.page(body='Record-ID: CASE-1\nOwner: Alice\nOwner: Bob')
        for budget in (1, 12):
            result = self.ask(max_passages=budget)
            self.assertFalse(result['answer_supported'])
            self.assertEqual(result['diagnostic']['category'], 'known_source_conflict')

    def test_budget_exhaustion_without_conflict(self):
        self.page(body='Record-ID: CASE-1\nOwner: Alice\nOwner: Alice')
        result = self.ask(max_passages=1)
        self.assertEqual(result['diagnostic']['category'], 'index_exhaustion')
        self.assertFalse(result['answer_supported'])

    def test_unsupported_grammar_and_ambiguity_are_not_known_conflicts(self):
        self.page()
        result = answer_query(self.root, 'Explain archive metaphysics').contract
        self.assertEqual(result['diagnostic']['category'], 'unsupported_question_grammar')
        self.assertFalse(result['answer_supported'])
        self.assertEqual(refusal_category('retrieval_ambiguous', 'conflict'), 'clarification_required')
        self.assertEqual(refusal_category('reader_reported_conflict', 'conflict'), 'unverified_reported_conflict')

    def test_changed_source_discards_assurance_roots_and_old_quotes(self):
        self.page()
        from mplpb_answers import pipeline
        # Exercise normal final recheck through the existing fresh gather hook.
        gather = pipeline.G.gather
        calls = []
        def changed(*args, **kw):
            value = gather(*args, **kw)
            calls.append(1)
            if len(calls) > 1:
                value.corpus_snapshot = 'changed'
            return value
        with patch.object(pipeline.G, 'gather', changed):
            result = self.ask()
        self.assertEqual(result['diagnostic']['category'], 'source_state_changed')
        self.assertFalse(result['answer_supported'])
        self.assertEqual(result['sources'], [])
        self.assertIsNone(result['source_assurance']['single_declared_root'])

    def test_restricted_sources_not_counted_as_corroboration(self):
        from mplpb_combined.reader import PROFILES
        self.page()
        self.page('SRC-2', external='no')
        result = self.ask(profile=PROFILES['external'])
        self.assertNotIn('SRC-2', {s['id'] for s in result['sources']})
        self.assertEqual(result['source_assurance']['declared_evidence_root_count'], 1)


class OperationalReceiptBoundaryTests(unittest.TestCase):
    # Reuse the existing fixture without inheriting or changing its tests.
    from tests.test_scoped_extensions import WorkExtensionTests as _Fixture
    setUp = _Fixture.setUp
    put = _Fixture.put

    def execute(self, action_id):
        self.put(action_id, 'action', {'task': 'T1', 'task_revision': 1, 'operation': 'fixture',
            'arguments': {}, 'side_effect': 'local', 'executor_seat': 'worker',
            'state': 'proposed', 'retry_of': {}, 'retry_reason': ''})
        self.store.executors['fixture'] = lambda r: {'result': 'passed',
            'validation': {'done': True}, 'artifact': 'local execution only'}
        return self.store.execute(self.token, id=action_id, expected_revision=1,
            expected_head=self.store.snapshot(self.token)['head'])['receipt']['id']

    def observe(self, execution, kind, predecessor=None):
        return self.store.record_external_receipt(self.host, receipt=execution, kind=kind,
            predecessor=predecessor, artifact='Distinct host observation for '+kind,
            expected_head=self.store.head(self.host)['hash'])

    def test_every_transition_needs_its_own_receipt_and_remains_host_declared(self):
        from mplpb_work import WorkError
        execution = self.execute('A1')
        with self.assertRaises(WorkError):self.observe(execution, 'COMPLETION')
        previous = None
        for kind in ('STORE', 'DISPATCH', 'DELIVERY', 'READ', 'ACK', 'COMPLETION'):
            receipt = self.observe(execution, kind, previous)
            self.assertTrue(receipt['transition_checked'])
            self.assertEqual(receipt['predecessor'], previous)
            self.assertFalse(receipt['answer_supported'])
            self.assertFalse(receipt['external_world_verified'])
            self.assertEqual(receipt['basis'], 'host_declared')
            previous = receipt['id']
        self.assertEqual(len(self.store.handoff(self.token)['external_receipts']), 6)

    def test_missing_or_foreign_predecessor_and_legacy_ack_cannot_bridge(self):
        from mplpb_work import WorkError
        first, second = self.execute('A1'), self.execute('A2')
        stored = self.observe(first, 'STORE')
        with self.assertRaises(WorkError):self.observe(first, 'DELIVERY', stored['id'])
        with self.assertRaises(WorkError):self.observe(second, 'DISPATCH', stored['id'])
        legacy = self.observe(first, 'ACK')
        self.assertFalse(legacy['transition_checked'])
        with self.assertRaises(WorkError):self.observe(first, 'COMPLETION', legacy['id'])
        with self.assertRaises(WorkError):self.observe(first, 'DISPATCH', 'missing')
