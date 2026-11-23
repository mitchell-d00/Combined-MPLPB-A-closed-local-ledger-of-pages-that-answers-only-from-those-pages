"""Check governed outcomes against the WorkStore log and actual report bytes."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from mplpb_combined.ledger import withdraw, write
from mplpb_work.store import digest
from tools.governance_demo import CitedReportGate, OPERATION


class GovernanceDemoTests(unittest.TestCase):
    def setUp(self):
        temporary = TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        self.corpus = root / 'corpus'
        write(self.corpus, doc_id='DEMO-1', title='Library register',
              scope='Daily hours', body='Opening time: 08:30.')
        self.gate = CitedReportGate(root / 'run', self.corpus, 'DEMO-1', 'Opening time')
        self.proposal = self.gate.proposal('library-opening.json')
        self.adapter = self.gate.store.executors[OPERATION]['run']
        self.calls = []

        def count(request):
            self.calls.append(request['idempotency_key'])
            return self.adapter(request)

        self.gate.store.executors[OPERATION]['run'] = count

    def receipts(self):
        events = self.gate.store.audit(self.gate.host)['events']
        return [(event['type'], event['payload']['receipt']['status']) for event in events
                if event['type'] in {'start', 'finish'}]

    def assert_no_dispatch(self, result):
        self.assertEqual(result['status'], 'denied')
        self.assertNotIn('receipt_id', result)
        self.assertEqual(self.calls, [])
        self.assertEqual(self.receipts(), [])
        self.assertEqual(list(self.gate.output.iterdir()), [])

    def test_approved_report_matches_bytes_citation_and_receipt(self):
        self.gate.approve(self.proposal)
        result = self.gate.submit(self.proposal)
        path, = self.gate.output.iterdir()
        text = path.read_text()
        self.assertEqual(result, {'status': 'verified', 'target': self.proposal['target'],
                                  'receipt_id': self.calls[0], 'artifact_hash': digest(text)})
        report = json.loads(text)
        self.assertEqual(report['receipt_id'], self.calls[0])
        self.assertFalse(report['historical_truth_verified'])
        cite, = report['claims'][0]['citations']
        self.assertEqual(cite['hash'], self.proposal['source_hash'])
        self.assertIn('Opening time: 08:30', cite['quote'])
        self.assertEqual(self.receipts(), [('start', 'started'), ('finish', 'passed')])

    def test_missing_approval(self):
        self.assert_no_dispatch(self.gate.submit(self.proposal))

    def test_fictional_tool_name(self):
        self.assert_no_dispatch(self.gate.submit({**self.proposal, 'operation': 'publish-report.v9'}))

    def test_model_cannot_supply_receipt_or_success(self):
        self.gate.approve(self.proposal)
        official = self.gate.submit({**self.proposal, 'receipt_id': 'claimed', 'status': 'verified'})
        self.assert_no_dispatch(official)

    def test_approval_does_not_follow_changed_target(self):
        self.gate.approve(self.proposal)
        self.assert_no_dispatch(self.gate.submit({**self.proposal, 'target': 'another-report.json'}))

    def test_source_pin_cannot_change_after_approval(self):
        self.gate.approve(self.proposal)
        self.assert_no_dispatch(self.gate.submit({**self.proposal, 'source_hash': 'sha256:' + '0'*64}))

    def test_source_retirement_after_approval(self):
        self.gate.approve(self.proposal)
        withdraw(self.corpus, 'DEMO-1')
        self.assert_no_dispatch(self.gate.submit(self.proposal))

    def test_duplicate_proposal_cannot_dispatch_twice(self):
        self.gate.approve(self.proposal)
        self.assertEqual(self.gate.submit(self.proposal)['status'], 'verified')
        retry = self.gate.submit(self.proposal)
        self.assertEqual(retry['status'], 'denied')
        self.assertNotIn('receipt_id', retry)
        self.assertEqual(len(self.calls), 1)
        self.assertEqual(len(self.receipts()), 2)
        self.assertEqual(len(list(self.gate.output.iterdir())), 1)

    def test_exception_after_write_stays_indeterminate(self):
        adapter = self.gate.store.executors[OPERATION]['run']

        def interrupted(request):
            adapter(request)
            raise TimeoutError('Outcome unavailable')

        self.gate.store.executors[OPERATION]['run'] = interrupted
        self.gate.approve(self.proposal)
        result = self.gate.submit(self.proposal)
        self.assertEqual(result, {'status': 'indeterminate', 'receipt_id': self.calls[0]})
        self.assertEqual(self.receipts(), [('start', 'started'), ('finish', 'indeterminate')])
        self.assertEqual(len(list(self.gate.output.iterdir())), 1)
        self.assertEqual(self.gate.submit(self.proposal)['status'], 'denied')
        self.assertEqual(len(self.calls), 1)

    def test_receipt_without_matching_readback_is_indeterminate(self):
        execute = self.gate.store.execute

        def remove_after_receipt(*args, **kwargs):
            result = execute(*args, **kwargs)
            (self.gate.output / self.proposal['target']).unlink()
            return result

        self.gate.approve(self.proposal)
        with patch.object(self.gate.store, 'execute', side_effect=remove_after_receipt):
            result = self.gate.submit(self.proposal)
        self.assertEqual(result, {'status': 'indeterminate', 'receipt_id': self.calls[0]})
        self.assertEqual(self.receipts(), [('start', 'started'), ('finish', 'passed')])
        self.assertEqual(list(self.gate.output.iterdir()), [])
