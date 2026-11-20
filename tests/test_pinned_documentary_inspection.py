"""Controls for opt-in literal comparisons and explicitly linked source chains."""
import html
from pathlib import Path
import tempfile
import unittest

from mplpb_combined import ledger
from mplpb_combined.reader import PROFILES
from mplpb_work.prose_evidence import reconstruct_report


class PinnedDocumentaryInspectionTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)

    def page(self, ident, body, **kwargs):
        return ledger.write(self.root, doc_id=ident, title='Register', scope='archival records',
                            body_html='<pre>' + html.escape(body) + '</pre>', **kwargs)

    def inspect(self, operation, *sources, **kwargs):
        return reconstruct_report(self.root, 'Inspect the archival records.',
                                  inspection=(operation, sources), **kwargs)['pinned_inspection']

    def test_literal_comparison_does_not_merge_occurrences(self):
        self.page('LEAF-A', 'The amber marker was stored in the north depot.')
        self.page('LEAF-B', 'The brass marker was stored in the north depot.')
        result = self.inspect('wording', 'LEAF-A', 'LEAF-B')
        self.assertEqual(result['status'], 'complete')
        self.assertFalse(result['answer_supported'])
        self.assertFalse(result['identical_canonical_text'])
        self.assertTrue(any(hunk['left_text'] == 'amber' and hunk['right_text'] == 'brass'
                            for hunk in result['alignment']))
        self.assertEqual([c['source_id'] for c in result['citations']], ['LEAF-A', 'LEAF-B'])
        self.assertEqual(self.inspect('wording', 'LEAF-A', 'LEAF-B', max_passages=1)['status'], 'unresolved')

    def test_writing_date_ignores_other_date_roles_and_ties(self):
        self.page('LEAF-A', 'Date Written: 1871-04-15\nDate Sent: 1871-04-16')
        self.page('LEAF-B', 'Date Written: 1871-04-15\nDate Received: 1871-04-20')
        result = self.inspect('writing_dates', 'LEAF-A', 'LEAF-B')
        self.assertEqual(result['status'], 'complete')
        self.assertEqual(result['earliest_sources'], ['LEAF-A', 'LEAF-B'])
        self.assertFalse(result['historical_priority_verified'])

    def test_withheld_excerpt_and_missing_date_remain_unresolved(self):
        self.page('LEAF-A', 'Date Written: 1871-04-15')
        self.page('LEAF-B', 'Date Sent: 1871-04-14')
        self.assertEqual(self.inspect('writing_dates', 'LEAF-A', 'LEAF-B')['status'], 'partial')
        self.page('LEAF-C', 'Date Written: 1871-04-17', external='no')
        result = self.inspect('wording', 'LEAF-A', 'LEAF-C', profile=PROFILES['external'])
        self.assertEqual(result['status'], 'unresolved')
        self.assertEqual(result['citations'], [])

    def test_chain_requires_literal_reference_and_keeps_report_attribution(self):
        self.page('LEAF-A', 'Mina Holt requested that Ari Lowe send the berth plan to the river depot.')
        self.page('LEAF-B', 'In response to request source LEAF-A, Ari Lowe sent the berth plan to the river depot.')
        self.page('LEAF-C', 'Referring to dispatch source LEAF-B, Jo Hall reported receiving the berth plan at the river depot from Ari Lowe.')
        result = self.inspect('request_dispatch_receipt', 'LEAF-A', 'LEAF-B', 'LEAF-C')
        self.assertEqual(result['status'], 'complete')
        self.assertFalse(result['answer_supported'])
        self.assertEqual(result['steps'][2]['reported_by'], 'Jo Hall')
        self.assertEqual([c['source_id'] for c in result['citations']], ['LEAF-A', 'LEAF-B', 'LEAF-C'])
        self.page('LEAF-D', 'Referring to dispatch source LEAF-B, Jo Hall reported receiving the wrong item at the river depot from Ari Lowe.')
        missing = self.inspect('request_dispatch_receipt', 'LEAF-A', 'LEAF-B', 'LEAF-D')
        self.assertEqual(missing['status'], 'partial')
        self.assertEqual(missing['missing'], ['reported receipt linked to the dispatch'])

    def test_chain_rejects_qualified_dispatch_and_does_not_guess(self):
        self.page('LEAF-A', 'Mina Holt requested that Ari Lowe send the berth plan to the river depot.')
        self.page('LEAF-B', 'If approved, Ari Lowe would send the berth plan to the river depot in response to request source LEAF-A.')
        self.page('LEAF-C', 'Referring to dispatch source LEAF-B, Jo Hall reported receiving the berth plan at the river depot from Ari Lowe.')
        result = self.inspect('request_dispatch_receipt', 'LEAF-A', 'LEAF-B', 'LEAF-C')
        self.assertEqual(result['status'], 'partial')
        self.assertEqual([step['role'] for step in result['steps']], ['request'])

    def test_html_blockquote_cannot_license_a_chain_step(self):
        ledger.write(self.root, doc_id='LEAF-A', title='Register', scope='archival records',
                     body_html='<blockquote>Mina Holt requested that Ari Lowe send the berth plan to the river depot.</blockquote>')
        self.page('LEAF-B', 'In response to request source LEAF-A, Ari Lowe sent the berth plan to the river depot.')
        self.page('LEAF-C', 'Referring to dispatch source LEAF-B, Jo Hall reported receiving the berth plan at the river depot from Ari Lowe.')
        result = self.inspect('request_dispatch_receipt', 'LEAF-A', 'LEAF-B', 'LEAF-C')
        self.assertEqual(result['status'], 'unresolved')
        self.assertEqual(result['steps'], [])

    def test_earliest_is_never_inferred_from_a_conflict_or_budget_limited_set(self):
        self.page('LEAF-A', 'Date Written: 1871-04-15')
        self.page('LEAF-B', 'Date Written: 1871-04-18')
        result = self.inspect('writing_dates', 'LEAF-A', 'LEAF-B', max_passages=1)
        self.assertEqual(result['status'], 'partial')
        self.assertEqual(result['earliest_sources'], [])
