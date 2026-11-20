"""Source-bound field-language controls; not independent historical validation."""
import html
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch

from mplpb_answers.pipeline import answer_query
from mplpb_combined import ledger
from mplpb_combined.reader import PROFILES


class FieldAliasTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def page(self, body, ident='SOURCE-A', **kw):
        return ledger.write(self.root, doc_id=ident, title='Unrelated label', scope='archive',
                            body_html='<pre>'+html.escape('Record-ID: LEAF-77\n'+body)+'</pre>', **kw)

    def ask(self, field, **kw):
        return answer_query(self.root, 'What is the '+field+' for record LEAF-77?', **kw).contract

    def test_source_declared_reordered_and_lexical_fields(self):
        self.page('Inspection Date: 1884-06-11\nObservation Time: 09:30\nPostal Code: AB4 7XY\nTelephone Number: 020-555-0171')
        for query, label in [('date of inspection', 'Inspection Date'), ('time of observation', 'Observation Time'),
                             ('postcode', 'Postal Code'), ('phone number', 'Telephone Number')]:
            with self.subTest(query=query):
                r = self.ask(query)
                self.assertTrue(r['answer_supported'], r['diagnostic'])
                self.assertTrue(r['claims'][0]['text'].startswith(label+': '))
                self.assertEqual(r['question'], 'What is the '+query+' for record LEAF-77?')
                self.assertFalse(r['verification']['truth_verified'])

    def test_current_state_to_declared_status_preserves_qualifications(self):
        self.page('Present Status: Provisional; subject to review')
        r = self.ask('current state')
        self.assertTrue(r['answer_supported'])
        self.assertEqual(r['claims'][0]['text'], 'Present Status: Provisional; subject to review')

    def test_no_geographic_state_or_temporal_role_collapse(self):
        self.page('Current State: Maine\nReceipt Date: 1884-07-13\nStorage Location: Warehouse')
        for field in ['current status', 'sending date', 'date of dispatch', 'location of custody']:
            self.assertFalse(self.ask(field)['answer_supported'])

    def test_ambiguous_aliases_are_not_ranked_even_when_values_agree(self):
        self.page('Telephone Number: 123\nPhone Number: 123')
        r = self.ask('telephone no')
        self.assertFalse(r['answer_supported'])
        self.assertEqual(r['kind'], 'clarify')
        self.assertEqual(r['diagnostic']['category'], 'clarification_required')
        self.assertEqual(r['question_normalization']['candidate_fields'], ['phone number', 'telephone number'])

    def test_exact_spelling_does_not_hide_a_competing_synonymous_field(self):
        self.page('Telephone Number: 123\nPhone Number: 456')
        r = self.ask('phone number')
        self.assertFalse(r['answer_supported'])
        self.assertEqual(r['kind'], 'clarify')
        pinned = answer_query(self.root, 'Inspect the literal body label',
                              record_id='LEAF-77', field='Phone Number').contract
        self.assertTrue(pinned['answer_supported'])
        self.assertEqual(pinned['claims'][0]['text'], 'Phone Number: 456')

    def test_conflicts_and_quoted_contexts_still_block_support(self):
        self.page('Inspection Date: 1884-01-01\n\nBody:\nInspection Date: 1884-02-01')
        self.assertFalse(self.ask('date of inspection')['answer_supported'])

    def test_profiles_retirement_corruption_and_original_question_policy(self):
        rec = self.page('Telephone Number: 123', origin='machine', not_for='telephone no')
        self.assertFalse(self.ask('telephone no')['answer_supported'])
        self.assertFalse(self.ask('phone number', profile=PROFILES['external'])['answer_supported'])
        path = self.root/rec.path
        path.write_text(path.read_text().replace('123', '999'))
        self.assertFalse(self.ask('phone number')['answer_supported'])

    def test_quoted_or_conditional_field_is_not_a_declaration(self):
        self.page('If approved:\nTelephone Number: 123')
        self.assertFalse(self.ask('phone number')['answer_supported'])

    def test_extra_obligations_are_not_removed(self):
        self.page('Inspection Date: 1884-01-01')
        for suffix in [' before revision', ' and owner', ' according to Alice', ' if approved']:
            self.assertFalse(self.ask('date of inspection'+suffix)['answer_supported'])

    def test_corrected_field_and_unrelated_field_use_own_serving_views(self):
        old = self.page('Inspection Date: 1884-01-01\nLoan Location: West repository')
        ledger.write(self.root, doc_id='SOURCE-B', title='Correction', scope='archive',
                     body_html='<pre>Record-ID: LEAF-77\nInspection Date: 1884-02-01</pre>',
                     supersedes=[old.id], corrects_field='Inspection Date', valid_from='2026-11-01')
        later = self.ask('date of inspection', as_of='2026-11-20')
        self.assertTrue(later['answer_supported'])
        self.assertEqual(later['claims'][0]['text'], 'Inspection Date: 1884-02-01')
        earlier = self.ask('date of inspection', as_of='2026-10-01')
        self.assertTrue(earlier['answer_supported'])
        self.assertEqual(earlier['claims'][0]['text'], 'Inspection Date: 1884-01-01')
        other = self.ask('location of loan', as_of='2026-11-20')
        self.assertTrue(other['answer_supported'])
        self.assertEqual(other['claims'][0]['text'], 'Loan Location: West repository')

    def test_missing_identity_and_wrong_record_cannot_supply_alias(self):
        self.page('Inspection Date: 1884-01-01')
        r = answer_query(self.root, 'What is the date of inspection for record LEAF-OTHER?').contract
        self.assertFalse(r['answer_supported'])

    def test_source_change_between_normalization_and_answer_discards_mapping(self):
        from mplpb_answers import field_aliases
        self.page('Inspection Date: 1884-01-01')
        original = field_aliases.resolve
        def changed(*args, **kw):
            result = original(*args, **kw)
            self.page('Inspection Date: 1884-02-01', 'SOURCE-B')
            return result
        with patch.object(field_aliases, 'resolve', side_effect=changed):
            r = self.ask('date of inspection')
        self.assertFalse(r['answer_supported'])
        self.assertEqual(r['diagnostic']['code'], 'source_changed')
        self.assertFalse(r['claims'])
        self.assertNotIn('source_field_anchors', r['question_normalization'])

    def test_alias_budget_never_prunes_alternatives_and_explicit_selector_stays_literal(self):
        from mplpb_answers import field_aliases
        self.page('Telephone Number: 123')
        with patch.object(field_aliases, 'MAX_SOURCES', 0):
            self.assertFalse(self.ask('phone number')['answer_supported'])
            r = answer_query(self.root, 'Inspect exact label', record_id='LEAF-77',
                             field='Telephone Number').contract
            self.assertTrue(r['answer_supported'])

    def test_alias_witness_budget_keeps_all_same_identity_appearances(self):
        self.page('Inspection Date: 1884-01-01')
        self.page('Inspection Date: 1884-01-01', 'SOURCE-B')
        r = self.ask('date of inspection', max_passages=1)
        self.assertFalse(r['answer_supported'])

    def test_assisted_mode_cannot_promote_alias_proposal(self):
        self.page('Inspection Date: 1884-01-01')
        self.assertFalse(self.ask('date of inspection', mode='assisted')['answer_supported'])


if __name__ == '__main__': unittest.main()
