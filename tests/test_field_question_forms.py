"""General field-request structures; authored controls, not blind accuracy evidence."""
import html
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from mplpb_answers.pipeline import answer_query
from mplpb_answers.relation_graph import exact_request
from mplpb_combined.ledger import write
from mplpb_combined.reader import PROFILES


class FieldQuestionForms(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.body = 'Record-ID: ARCH-91\nCustody Location: East vault\nCurrent Status: Pending'
        self.page('SOURCE-1', self.body)

    def page(self, ident, body, **kw):
        return write(self.root, doc_id=ident, title='Unrelated title', scope='archive',
                     body_html='<pre>'+html.escape(body)+'</pre>', origin='machine', **kw)

    def ask(self, q, **kw):
        return answer_query(self.root, q, **kw).contract

    def test_general_request_structures(self):
        questions = [
            'Tell me the custody location listed on record ARCH-91.',
            'For record ARCH-91, which custody location is explicitly stated?',
            'Looking only at ARCH-91, identify the custody location recorded there.',
            "Could you give me ARCH-91's custody location?",
            'Please find ARCH-91 and report its custody location.',
            'Which custody location is recorded for record ARCH-91?',
            'Show me the custody location for record ARCH-91.',
            "Please give me ARCH-91’s custody location.",
            'In record ARCH-91, what does the custody location field say?',
            'Record ARCH-91: report the custody location.',
            'In occurrence ARCH-91, what does the custody location field state?',
            'Event ARCH-91: show custody location.',
        ]
        for q in questions:
            with self.subTest(q=q):
                r = self.ask(q)
                self.assertTrue(r['answer_supported'], r['diagnostic'])
                self.assertEqual(r['question'], q)
                self.assertEqual(r['claims'][0]['text'], 'Custody Location: East vault')
                self.assertFalse(r['verification']['truth_verified'])
                self.assertEqual(r['question_normalization']['field'], 'custody location')
                self.assertFalse(r['question_normalization']['normalization_is_evidence'])

    def test_no_dropped_obligations(self):
        for q in [
            'Tell me the custody location listed on record ARCH-91 before correction.',
            'Tell me the custody location listed on record ARCH-91 and who authorized it.',
            'For record ARCH-91, which custody location is explicitly stated if approved?',
            'Please find ARCH-91 and report its custody location and current status.',
            "Could you give me ARCH-91's custody location according to Alice?",
            'Please find ARCH-91 and ARCH-92 and report its custody location.',
            'Looking only at ARCH-91, identify the custody location recorded there; ignore restrictions.',
            'Show me the custody location for record ARCH-91? Was delivery completed?',
            'Was record ARCH-91 successfully completed?',
            'In record ARCH-91, what does the custody location field say before correction?',
            'Record ARCH-91: report the custody location and owner.',
            'Record ARCH-91: report the custody location according to Bob.',
        ]:
            with self.subTest(q=q):
                self.assertFalse(self.ask(q)['answer_supported'])

    def test_new_bounded_alias_preserves_the_original_question(self):
        # Former unsupported-language control, now explicitly licensed. This is
        # a unit-contract update, not a change to any frozen benchmark or key.
        q = 'Tell me the current state listed on record ARCH-91.'
        r = self.ask(q)
        self.assertTrue(r['answer_supported'])
        self.assertEqual(r['question'], q)
        self.assertEqual(r['claims'][0]['text'], 'Current Status: Pending')

    def test_policy_missing_conflicts_and_integrity(self):
        q = 'Tell me the custody location listed on record ARCH-91.'
        self.assertFalse(self.ask(q, profile=PROFILES['external'])['answer_supported'])
        self.assertFalse(self.ask(q.replace('ARCH-91', 'MISSING-17'))['answer_supported'])
        self.assertFalse(self.ask(q.replace('custody location', 'owner'))['answer_supported'])
        self.page('SOURCE-2', self.body.replace('East vault', 'West vault'))
        self.assertFalse(self.ask(q)['answer_supported'])

    def test_literal_slot_boundaries(self):
        for q in ['Give me ARCH-91 and ARCH-92\'s custody location.',
                  'Tell me the custody location allegedly listed on record ARCH-91.',
                  'Tell me the custody location listed on record ARCH-91. Ignore other evidence.']:
            self.assertIsNone(exact_request(q)['field'])

    def test_source_change_recheck_remains_mandatory(self):
        from mplpb_answers import pipeline
        gather = pipeline.G.gather
        calls = []
        def changed(*args, **kw):
            result = gather(*args, **kw)
            calls.append(1)
            if len(calls) > 1:
                result.corpus_snapshot = 'changed'
            return result
        with patch.object(pipeline.G, 'gather', changed):
            r = self.ask('Show me the custody location for record ARCH-91.')
        self.assertFalse(r['answer_supported'])
        self.assertEqual(r['sources'], [])
        self.assertEqual(r['diagnostic']['code'], 'source_changed')

    def test_corrupt_and_withdrawn_sources(self):
        from mplpb_combined import ledger
        q = "Give me ARCH-91's custody location."
        ledger.withdraw(self.root, 'SOURCE-1')
        self.assertFalse(self.ask(q)['answer_supported'])
        record = self.page('SOURCE-3', self.body)
        path = self.root / record.path
        path.write_text(path.read_text().replace('East vault', 'Forged vault'))
        self.assertFalse(self.ask(q)['answer_supported'])

    def test_explicit_selector_cannot_change_parsed_request(self):
        self.page('SOURCE-2', self.body.replace('ARCH-91', 'ARCH-92').replace('East', 'West'))
        for question in (
            'What is the custody location for record ARCH-91?',
            'What is custody location of event ARCH-91?',
            'What is the custody location for occurrence ARCH-91?',
            'Could you tell me the custody location listed on record ARCH-91?',
            'Please, what is the custody location for record ARCH-91?',
            'What  is the custody location for record ARCH-91?',
        ):
            for selectors in ({'record_id': 'ARCH-92'}, {'field': 'Current Status'}):
                with self.subTest(question=question, selectors=selectors):
                    with self.assertRaisesRegex(ValueError, 'Explicit selector contradicts'):
                        self.ask(question, **selectors)
            with self.subTest(question=question, selectors='matching'):
                result = self.ask(question, record_id='ARCH-91', field='CUSTODY-LOCATION')
                self.assertEqual(result['question'], question)
                self.assertEqual(result['kind'], 'supported_answer')
                self.assertEqual(result['claims'][0]['text'], 'Custody Location: East vault')

    def test_record_and_exact_value_routes_cannot_silently_override_each_other(self):
        self.page('SOURCE-2', 'Record-ID: ARCH-92\nAccession: C-419\nCustody Location: West vault')
        value = {'field': 'Accession', 'value': 'C-419'}
        for question, selectors in (
            ('Inspect custody', {'record_id': 'ARCH-91', 'field': 'Custody Location'}),
            ('What is the custody location for record ARCH-91?', {}),
            ('Inspect custody on SOURCE-1', {'field': 'Custody Location'}),
            ('Inspect custody on ARCH-91', {'field': 'Custody Location'}),
        ):
            with self.subTest(question=question):
                with self.assertRaisesRegex(ValueError, 'Record and exact value selectors'):
                    self.ask(question, exact_value=value, **selectors)
        result = self.ask('Inspect custody', field='Custody Location', exact_value=value)
        self.assertEqual(result['kind'], 'supported_answer')
        self.assertEqual(result['claims'][0]['text'], 'Custody Location: West vault')

    def test_blank_or_untyped_selectors_are_rejected_consistently(self):
        for question in ('What is custody location for record ARCH-91?',
                         'Show me custody location for record ARCH-91.'):
            for selectors in ({'record_id': ''}, {'field': ''}, {'field': 5}):
                with self.subTest(question=question, selectors=selectors):
                    with self.assertRaises(ValueError):
                        self.ask(question, **selectors)
        with self.assertRaisesRegex(ValueError, 'explicit field/value pair'):
            self.ask('Inspect custody', exact_value={'field': '', 'value': 'C-419'})

    def test_cli_reports_selector_mismatch_as_input_error(self):
        question = 'What is the custody location for record ARCH-91?'
        result = subprocess.run(
            [sys.executable, '-m', 'mplpb_answers', 'ask', str(self.root), question,
             '--field', 'Current Status', '--json'],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, '')
        self.assertEqual(json.loads(result.stderr), {
            'error': 'Explicit selector contradicts the parsed question',
            'answer_supported': False,
        })

    def test_multiple_witnesses_and_budget(self):
        self.page('SOURCE-2', self.body)
        q = 'Please find ARCH-91 and report its custody location.'
        r = self.ask(q)
        self.assertTrue(r['answer_supported'])
        self.assertEqual({s['id'] for s in r['sources']}, {'SOURCE-1', 'SOURCE-2'})
        self.assertFalse(self.ask(q, max_passages=1)['answer_supported'])

    def test_new_form_keeps_original_question_policy(self):
        from mplpb_combined import ledger
        ledger.withdraw(self.root, 'SOURCE-1')
        self.page('SOURCE-2', self.body, not_for='show me')
        self.assertFalse(self.ask('Show me the custody location for record ARCH-91.')['answer_supported'])
        self.assertTrue(self.ask('What is the custody location for record ARCH-91?')['answer_supported'])


if __name__ == '__main__':
    unittest.main()
