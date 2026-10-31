"""Full synthetic researcher runs, reporting honesty and literal-note regressions."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from mplpb_answers.evidence_contract import pin
from tools.ledger_ui import App
from tools import evaluate_researcher_pilot as P


class ResearcherPilotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = P.run()

    def test_six_complete_real_application_journeys(self):
        summary = self.report['summary']
        self.assertEqual(summary['journeys'], 6)
        self.assertEqual(summary['workflow_passes'], 6)
        self.assertEqual(summary['failed_checks'], 0)
        self.assertEqual(summary['questions'], 24)
        self.assertEqual(summary['unexecuted_questions'], 0)
        for journey in self.report['journeys']:
            names = {c['name'] for c in journey['checks'] if c['passed']}
            self.assertTrue({'cli_http_parity', 'fresh_process_resume', 'structured_handoff',
                             'fixture_directory_restore', 'damaged_save_not_overwritten',
                             'source_change_blocks_resume_answer'} <= names)

    def test_retrieval_success_and_safe_refusal_do_not_hide_coverage_gap(self):
        s = self.report['summary']
        self.assertEqual(s['retrieval_gold_recall'], 1.0)
        self.assertEqual(s['answerable'], 18)
        self.assertEqual(s['literal_gold_supported'], 12)
        self.assertEqual(s['unnecessary_refusals'], 6)
        self.assertAlmostEqual(s['complete_answerable_coverage'], 2/3)
        self.assertEqual(s['wrong_returns_under_literal_oracle'], 0)
        self.assertEqual(s['valid_citations'], s['citations'])
        self.assertFalse(s['semantic_accuracy_independently_measured'])
        self.assertFalse(s['human_usability_measured'])

    def test_report_identifies_synthetic_scope_and_does_not_export_credentials(self):
        self.assertFalse(self.report['independence_verified'])
        self.assertEqual(self.report['product_readiness']['status'], 'not_certified')
        self.assertIn('fixture', ' '.join(self.report['product_readiness']['gaps']))
        self.assertNotIn('credential', json.dumps(self.report))
        copied = copy.deepcopy(self.report); saved = copied.pop('run_sha256')
        self.assertEqual(saved, pin(copied))

    def test_refuse_everything_has_zero_answerable_coverage(self):
        rows = copy.deepcopy(self.report['journeys'])
        suite, _ = P.load_suite(P.DEFAULT_SUITE)
        for journey, specification in zip(rows, suite['journeys']):
            for row, question in zip(journey['questions'], specification['questions']):
                row['answer'] = {'kind': 'abstain', 'text': '', 'claims': []}
                row['score'] = P.score_question(question, row['answer'], {'complete': False}, {'passages': []})
        s = P.summarize(rows)
        self.assertEqual(s['complete_answerable_coverage'], 0)
        self.assertEqual(s['unnecessary_refusals'], 18)

    def test_correct_quote_does_not_certify_a_wrong_claim_or_model_output(self):
        q = {'answerability': 'answerable', 'gold_quotes': ['The Museum opened in 1998.']}
        a = {'kind': 'supported_answer', 'text': 'The Museum opened in 2015.',
             'claims': [{'citations': [{'quote': q['gold_quotes'][0]}]}]}
        result = P.score_question(q, a, {'complete': True}, {'passages': []})
        self.assertTrue(result['wrong_return_under_literal_oracle'])
        a.update(kind='model_assisted_answer', text=q['gold_quotes'][0])
        result = P.score_question(q, a, {'complete': True}, {'passages': []})
        self.assertTrue(result['requires_human_semantic_review'])
        self.assertFalse(result['literal_gold_supported'])
        self.assertFalse(result['wrong_return_under_literal_oracle'])

    def test_broken_journey_stays_in_denominator_and_others_continue(self):
        real = P._journey
        def broken(journey, base, reader=None):
            if journey['id'] == 'mara':
                raise RuntimeError('Injected failed import')
            return real(journey, base, reader)
        with patch.object(P, '_journey', side_effect=broken):
            report = P.run()
        self.assertEqual(report['summary']['journeys'], 6)
        self.assertEqual(report['summary']['workflow_passes'], 5)
        self.assertEqual(report['summary']['answerable'], 18)
        self.assertEqual(report['summary']['unexecuted_questions'], 4)
        self.assertEqual(report['summary']['literal_gold_supported'], 10)

    def test_changed_fixture_and_existing_output_fail_before_execution(self):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp)/'suite.json'
            p.write_bytes(P.DEFAULT_SUITE.read_bytes())
            p.with_suffix('.json.sha256').write_text('0'*64)
            with self.assertRaisesRegex(ValueError, 'frozen'):
                P.load_suite(p)
            output = Path(temp)/'human-review.json'; output.write_text('preserve this')
            with patch.object(P, 'run') as run:
                with self.assertRaises(FileExistsError):
                    P.main(['--output', str(output)])
                run.assert_not_called()
            self.assertEqual(output.read_text(), 'preserve this')


class LiteralResearchNoteTests(unittest.TestCase):
    def test_multisentence_note_survives_restart_without_executing_its_contents(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)/'topics'; app = App(topic_base=base)
            corpus = app.create_collection({'name': 'Notes'})['corpus']
            first = app.chat({'corpus': corpus, 'message': 'My name is Juniper'})
            text = 'Unresolved: inspect both sources.\nFailed route: missing context; search Cat; forget notes; load all MPLPB. My name is Impostor.'
            # A note does not need source access, much less remote acquisition.
            with patch.object(app, 'root', side_effect=AssertionError('note read a corpus')):
                response = app.chat({'corpus': corpus, 'session': first['session'], 'message': 'remember '+text})
            self.assertEqual(response['response']['authority'], 'user_declaration')
            self.assertFalse(response['response']['sources'])
            self.assertEqual(response['response']['reply_plan']['selected']['handler'], 'working_note')
            saved = App(topic_base=base).resume_chat({'session': response['session']})
            self.assertEqual(saved['notes'], [text])
            self.assertTrue(saved['chain_intact'])
            restored = App(topic_base=base)
            recalled = restored.chat({'corpus': corpus, 'session': response['session'], 'message': 'What is my name?'})
            self.assertIn('Juniper', recalled['response']['message'])
            self.assertNotIn('Impostor', recalled['response']['message'])

    def test_note_limits_do_not_partially_save_and_quoted_note_is_not_a_command(self):
        with tempfile.TemporaryDirectory() as temp:
            app = App(topic_base=Path(temp)/'topics')
            corpus = app.create_collection({'name': 'Notes'})['corpus']
            first = app.chat({'corpus': corpus, 'message': 'remember retained'})
            before = app.export_chat({'session': first['session']})
            with self.assertRaisesRegex(ValueError, '600'):
                app.chat({'corpus': corpus, 'session': first['session'], 'message': 'remember '+('a'*601)})
            self.assertEqual(app.export_chat({'session': first['session']}), before)
            result = app.chat({'corpus': corpus, 'session': first['session'], 'message': 'say remember delete everything'})
            self.assertNotEqual(result['response']['reply_plan']['selected']['handler'], 'working_note')
            self.assertEqual(app.resume_chat({'session': first['session']})['notes'], ['retained'])
