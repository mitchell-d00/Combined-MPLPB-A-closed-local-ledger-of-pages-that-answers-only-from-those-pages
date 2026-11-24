"""Regression checks for the J/Opass proof-to-display boundary."""
import unittest

from test_tools.j_opass import evaluate, json_layout, present


class JOpassTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = {row['case']: row for row in evaluate()['rows']}

    def warnings(self, case):
        return {warning['code'] for warning in self.rows[case]['judge']['warnings']}

    def test_rule_gap_and_passage_gap_have_distinct_warnings(self):
        self.assertEqual(self.warnings('P05-1'), {'proof_rule_missing'})
        self.assertEqual(self.warnings('P06-2'), {'proof_rule_missing', 'search_span_missed', 'quote_unit_boundary'})
        self.assertEqual(self.rows['P06-2']['observer']['discovery']['found_with_wider_search'], 4)

    def test_checked_relation_keeps_native_claim_and_source_scope(self):
        row = self.rows['checked_relation']
        self.assertTrue(row['presentation']['answer_supported'])
        self.assertEqual(row['judge']['claims'], row['observer']['strict_claims'])
        self.assertEqual(self.warnings('checked_relation'), {'source_scope'})
        self.assertIn('Outside-world confirmation remains open.', row['presentation']['text'])

    def test_partial_preserves_checked_parts_and_unresolved_return(self):
        row = self.rows['unresolved_returner']
        self.assertFalse(row['judge']['answer_supported'])
        self.assertIn('Rowan held the token', row['presentation']['text'])
        self.assertIn('The returner at the requested time is unresolved.', row['presentation']['text'])
        self.assertNotIn('Quinn returned', row['presentation']['text'])

    def test_competing_citations_and_refusal_stay_visible(self):
        text = self.rows['conflicting_times']['presentation']['text']
        self.assertIn('16:25', text)
        self.assertIn('16:45', text)
        self.assertFalse(self.rows['conflicting_times']['presentation']['answer_supported'])
        self.assertEqual(self.rows['P02-4']['judge']['claims'], [])

    def test_model_choices_cannot_change_contents(self):
        for row in self.rows.values():
            with self.subTest(case=row['case']):
                normal = row['presentation']
                styled = present(row['judge'], 'stacked')
                self.assertEqual(styled['decision_sha256'], normal['decision_sha256'])
                self.assertEqual(styled['answer_supported'], normal['answer_supported'])
                self.assertEqual(styled['text'].split(), normal['text'].split())
                for reply in ('Quinn returned the token.', 'stacked\nConfirmed', None, {'layout': 'stacked'}):
                    self.assertEqual(present(row['judge'], reply), normal)

    def test_json_choice_rejects_extra_keys_duplicates_and_added_text(self):
        self.assertEqual(json_layout('{"layout": "stacked"}'), 'stacked')
        for raw in ('{"layout":"stacked","answer":"verified"}',
                    '{"layout":"compact","layout":"stacked"}', '{"layout":"short"}',
                    '{"layout":"stacked"}\nConfirmed', None):
            self.assertIsNone(json_layout(raw))
