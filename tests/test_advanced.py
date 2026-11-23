"""Exercise Advanced MPLPB through the CLI and the normal strict reader."""
import contextlib
import io
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from mplpb_answers.__main__ import main
from mplpb_answers.advanced import advanced_query
from mplpb_answers.pipeline import answer_query
from mplpb_combined.ledger import withdraw, write
from tests.test_general_answers import FixtureReader


class AdvancedTests(unittest.TestCase):
    def setUp(self):
        temporary = TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.ledger = self.root / 'ledger'

    def page(self, body, scope='reference', ident='P-1'):
        write(self.ledger, doc_id=ident, title='Reference entry', scope=scope, body=body)

    def test_full_answer_stays_strict_under_automatic_or_assisted_selection(self):
        self.page('The kettle color is blue.', 'kettle color')
        question = 'What is the kettle color?'
        expected = answer_query(self.ledger, question).contract
        reader = FixtureReader('Unused')
        for options in ({}, {'follow_up': 'assisted', 'reader': reader}):
            result = advanced_query(self.ledger, question, **options)
            self.assertEqual(result['strict'], expected)
            self.assertTrue(result['answer_supported'])
            self.assertIsNone(result['inspection'])
            self.assertEqual(reader.calls, [])

    def test_unresolved_prose_lookup_and_assisted_inspection_keep_strict_result(self):
        quote = 'Drain the queue before restarting the worker.'
        self.page(quote, 'restart worker')
        question = 'How should an operator restart safely?'
        automatic = advanced_query(self.ledger, question)
        self.assertEqual(automatic['inspection']['path'], 'lookup')
        self.assertEqual(automatic['strict']['kind'], 'abstain')
        reader = FixtureReader(quote)
        result = advanced_query(self.ledger, question, follow_up='assisted', reader=reader)
        self.assertEqual(result['strict'], automatic['strict'])
        self.assertFalse(result['answer_supported'])
        self.assertEqual(result['inspection']['detail']['kind'], 'model_assisted_answer')
        self.assertFalse(result['inspection']['answer_supported'])

    def test_conflict_is_preserved_before_any_model_fallback(self):
        self.page('The kettle color is blue.', 'kettle color')
        self.page('The kettle color is green.', 'kettle color', 'P-2')
        reader = FixtureReader('Unused')
        result = advanced_query(self.ledger, 'What is the kettle color?', follow_up='assisted', reader=reader)
        self.assertEqual(result['status'], 'conflict')
        self.assertIsNone(result['inspection'])
        self.assertEqual(reader.calls, [])

    def test_retired_source_has_no_follow_up(self):
        self.page('The kettle color is blue.', 'kettle color')
        withdraw(self.ledger, 'P-1')
        result = advanced_query(self.ledger, 'What is the kettle color?', follow_up='investigate')
        self.assertFalse(result['answer_supported'])
        self.assertIsNone(result['inspection'])

    def test_partial_routes_to_investigation_without_promotion(self):
        self.page('Parcel BK-18 is listed as the court diary.')
        self.page('Dispatch JR-19 records that Ari Long sent parcel BK-18 to Noel King.', ident='P-2')
        result = advanced_query(self.ledger, 'Who sent the court diary and who received it?')
        self.assertEqual(result['strict']['kind'], 'partial_answer')
        self.assertEqual(result['inspection']['path'], 'investigate')
        self.assertFalse(result['answer_supported'])

    def test_source_change_between_paths_discards_combined_output(self):
        self.page('The kettle color is blue.', 'kettle color')

        def retire(*args, **kwargs):
            withdraw(self.ledger, 'P-1')
            return {'status': 'evidence_report'}

        with patch('mplpb_work.investigation.investigate', side_effect=retire):
            result = advanced_query(self.ledger, 'What is the kettle color?', follow_up='investigate')
        self.assertEqual(result['status'], 'source_changed')
        self.assertIsNone(result['strict'])
        self.assertIsNone(result['inspection'])

    def test_cli_reports_strict_status_for_json(self):
        self.page('The kettle color is blue.', 'kettle color')
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = main(['advanced', str(self.ledger), 'What is the kettle color?', '--json'])
        self.assertEqual(code, 0)
        self.assertTrue(json.loads(output.getvalue())['answer_supported'])

    def test_training_cli_retains_baseline_gate_and_stops_wrong_repair(self):
        packet = Path(__file__).resolve().parents[1] / 'evaluation/d12/coordinator'
        options = ['advanced-train', *(str(packet / name) for name in
                   ('fixtures.json', 'key.json', 'baseline-rule.json'))]
        for extra, expected, exit_code in (
            ([], 'baseline_recorded', 0),
            (['--candidate', str(packet/'elapsed-days-rule.json')], 'candidate_passed', 0),
            (['--objective', 'elapsed_days'], 'repair_selected', 0),
            (['--objective', 'inclusive_days'], 'review_needed', 1),
        ):
            with self.subTest(expected=expected), contextlib.redirect_stdout(io.StringIO()):
                path = self.root / (expected + '.json')
                self.assertEqual(main([*options, str(path), *extra]), exit_code)
                result = json.loads(path.read_text())
                self.assertEqual(result['status'], expected)
                self.assertFalse(result['promoted'])
                self.assertFalse(result['answer_supported'])
                self.assertIn('run_sha256', result['baseline'])
