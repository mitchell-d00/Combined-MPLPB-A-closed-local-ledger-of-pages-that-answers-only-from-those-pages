"""BW-GUARD: eligibility, scope, mutation and fixed-budget report protection."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from mplpb_answers import documentary_verify as kernel
from mplpb_answers.pipeline import answer_query
from mplpb_combined.ledger import write, withdraw, revise

Q = 'What does Celia Duarte report about the writer of the estuary register, without independently verifying the event?'
STATEMENT = 'Celia Duarte reported that Bram Okoye wrote the estuary register.'


class ReportedContentGuards(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def source(self, body=None, ident='A', **policy):
        return write(self.root, doc_id=ident, title='Documentary record', scope='archival records',
                     origin='machine', external='yes', body_html=body or '<p>' + STATEMENT + '</p>', **policy)

    def ask(self, q=Q):
        return answer_query(self.root, q).contract

    def withheld(self, result):
        self.assertFalse(result['answer_supported']); self.assertEqual(result['claims'], [])

    def test_positive_source_scoped_control(self):
        self.source(); a = self.ask(); self.assertTrue(a['answer_supported'])
        self.assertFalse(a['claims'][0]['proposition']['actual_authorship_established'])

    def test_withdrawn_original(self):
        self.source(); withdraw(self.root, 'A'); self.withheld(self.ask())

    def test_corrupt_original(self):
        r = self.source(); p = self.root / r.path
        p.write_text(p.read_text().replace('Bram Okoye', 'Other Actor'))
        self.withheld(self.ask())

    def test_not_for_original(self):
        self.source(not_for='estuary register'); self.withheld(self.ask())

    def test_quote_wrapper_cannot_supply_a_reporting_act(self):
        self.source('<blockquote><p>' + STATEMENT + '</p></blockquote>'); self.withheld(self.ask())

    def test_wrong_outer_speaker_cannot_be_discarded(self):
        self.source('<p>Soren Malik said, “' + STATEMENT + '”</p>'); self.withheld(self.ask())

    def test_initials_do_not_supply_full_name(self):
        self.source('<p>' + STATEMENT.replace('Celia Duarte', 'C. D.') + '</p>'); self.withheld(self.ask())

    def test_separate_conditional_heading_is_not_pruned(self):
        self.source('<h2>If the notebook is accurate</h2><p>' + STATEMENT + '</p>'); self.withheld(self.ask())

    def test_separate_conditional_paragraph_is_not_pruned(self):
        self.source('<p>If the notebook is accurate:</p><p>' + STATEMENT + '</p>'); self.withheld(self.ask())

    def test_unresolved_relevant_competitor_is_not_pruned(self):
        self.source(); self.source('<p>Celia Duarte allegedly reported that Bram Okoye wrote the estuary register.</p>', ident='B')
        self.withheld(self.ask())

    def test_record_limit_does_not_drop_counterevidence(self):
        self.source()
        for n in range(8): self.source('<p>Cabinet leaf.</p>', ident='X' + str(n))
        self.withheld(self.ask())

    def test_scan_character_limit(self):
        self.source('<p>' + STATEMENT + '</p><p>' + 'x' * 200001 + '</p>'); self.withheld(self.ask())

    def test_scan_unit_limit(self):
        self.source('<p>' + STATEMENT + '</p>' + '<p>Cabinet leaf.</p>' * 1001); self.withheld(self.ask())

    def test_final_mutation_discards_all_claims(self):
        self.source(); original = kernel.check
        def mutate(*args, **kwargs):
            result = original(*args, **kwargs); revise(self.root, 'A', body='Changed source.'); return result
        with patch.object(kernel, 'check', side_effect=mutate): result = self.ask()
        self.withheld(result); self.assertEqual(result['diagnostic']['code'], 'source_changed')

    def test_report_does_not_establish_execution_or_authorship(self):
        self.source(); self.withheld(self.ask('Do these records independently establish that Bram Okoye actually wrote the estuary register?'))

    def test_complete_witness_must_fit_output_budget(self):
        self.source()
        from mplpb_answers.passages import PassageIndex
        from mplpb_answers.reported_content import verify
        result = verify(PassageIndex(self.root, Q), 12, 20)
        self.assertEqual(result[:2], ('abstain', 'reader_budget_exceeded'))


if __name__ == '__main__':
    unittest.main()
