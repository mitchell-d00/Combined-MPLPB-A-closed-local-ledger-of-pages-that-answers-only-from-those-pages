"""General field-request structures; authored controls, not blind accuracy evidence."""
import html
from pathlib import Path
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
            'Tell me the current state listed on record ARCH-91.',
        ]:
            with self.subTest(q=q):
                self.assertFalse(self.ask(q)['answer_supported'])

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
        for kw in [{'record_id': 'ARCH-92'}, {'field': 'Owner'}]:
            with self.assertRaises(ValueError):
                self.ask('Tell me the custody location listed on record ARCH-91.', **kw)

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
