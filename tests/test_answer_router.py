"""Answer router: official only from strict MPLPB; everything else labelled."""
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from mplpb_combined.ledger import write
from mplpb_work import answer_router, classing
from tests.test_classing import DEMO, reviewed


class RouterOnDemoLedger(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        root = Path(cls.tmp.name)
        cls.dump = root / 'dump'
        shutil.copytree(DEMO, cls.dump)
        cls.ledger = root / 'ledger'
        classing.build(reviewed(classing.propose(cls.dump, auto_accept_clean=True)), cls.dump, cls.ledger, ratify_by='Tester')

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def ask(self, question, **kw):
        return answer_router.route(question, self.ledger, self.dump, **kw)

    def test_supported_question_is_official(self):
        r = self.ask('What is the from for record SHIP-7?')
        self.assertEqual(r['status'], 'official')
        self.assertTrue(r['official']['answer_supported'])
        self.assertEqual(r['official']['sources'][0]['id'], 'SHIP-7')

    def test_rewrite_answers_the_field_the_question_points_at(self):
        r = self.ask('Who sent SHIP-7?')
        self.assertEqual(r['status'], 'official_via_rewrite')
        self.assertEqual(r['official']['text'], 'From: Boston flour office')
        self.assertEqual(r['official']['reformulated_from'], 'Who sent SHIP-7?')
        self.assertIn('caution', r['official'])

    def test_field_scoped_successor_is_asked_for_the_corrected_field(self):
        r = self.ask('What is the cargo for record SHIP-7?')
        self.assertEqual(r['status'], 'official_via_rewrite')
        self.assertEqual(r['official']['sources'][0]['id'], 'SHIP-8')
        self.assertTrue(any('field-scoped correction' in d for d in r['explanation']['details']))

    def test_rewrite_never_switches_to_an_unrelated_field(self):
        for q in ('Who sent SHIP-7?', 'When was SHIP-7 sent?'):
            r = self.ask(q)
            if r['official']:
                self.assertNotIn('Cargo', r['official']['text'], q)

    def test_unofficial_is_labelled_cited_and_never_supported(self):
        r = self.ask('How many bales were shipped in Letter No. 41?')
        self.assertEqual(r['status'], 'unofficial')
        u = r['unofficial']
        self.assertFalse(u['answer_supported'])
        self.assertTrue(u['label'].startswith('UNOFFICIAL'))
        self.assertTrue(all('page' in p or 'bytes' in p for p in u['passages']))
        self.assertTrue(any(c['from_path'] == 'letter-42.txt' for c in u['possible_corrections']))

    def test_withdrawn_source_is_flagged(self):
        r = self.ask('What are the freight rates for flour?')
        flagged = [p for p in r['unofficial']['passages'] if 'withdrawn_in_ledger' in p['warnings']]
        self.assertTrue(flagged)

    def test_external_refusal_quotes_gate_reason(self):
        r = self.ask('What is the from for record SHIP-7?', profile='external')
        self.assertNotEqual(r['status'], 'official')
        self.assertTrue(any('source authorship unknown' in d for d in r['explanation']['details']))

    def test_strict_pipeline_never_receives_dump_hints(self):
        # PR #52 report: sorter hints displaced H05's required evidence.
        calls = []
        real = answer_router.answer_query
        def spy(*args, **kwargs):
            calls.append(kwargs)
            return real(*args, **kwargs)
        with mock.patch.object(answer_router, 'answer_query', spy):
            self.ask('How many bales were shipped in Letter No. 41?')
        self.assertTrue(calls)
        self.assertTrue(all(not k.get('source_hints') for k in calls))

    def test_no_ledger_still_answers_unofficially(self):
        r = answer_router.route('How many barrels left Boston?', None, self.dump)
        self.assertEqual(r['status'], 'unofficial')
        self.assertIsNone(r['official'])
        self.assertTrue(r['classing_help'])


class StackedFieldSafety(unittest.TestCase):
    """Defect found while building the router: plain_to_html joins a header
    block into one line, and the field reader certified the joined text."""

    def test_stacked_header_block_is_refused_not_certified(self):
        from mplpb_answers.pipeline import answer_query
        with tempfile.TemporaryDirectory() as root:
            write(root, doc_id='SHIP-7', title='Shipment', scope='SHIP-7 shipment', origin='human',
                  body='Sender: Boston flour office\nRecipient: Albany depot\nCargo: forty barrels\n\nForty barrels left Boston.')
            c = answer_query(root, 'What is the sender for record SHIP-7?').contract
            self.assertEqual(c['kind'], 'abstain')
            self.assertEqual(c['diagnostic']['code'], 'stacked_field_paragraph')
            self.assertFalse(c['answer_supported'])

    def test_one_field_per_paragraph_still_answers(self):
        from mplpb_answers.pipeline import answer_query
        with tempfile.TemporaryDirectory() as root:
            write(root, doc_id='SHIP-7', title='Shipment', scope='SHIP-7 shipment', origin='human',
                  body='Sender: Boston flour office\n\nRecipient: Albany depot\n\nCargo: forty barrels')
            c = answer_query(root, 'What is the recipient for record SHIP-7?').contract
            self.assertEqual(c['kind'], 'supported_answer')
            self.assertEqual(c['text'], 'Recipient: Albany depot')

    def test_value_with_ordinary_colon_still_answers(self):
        from mplpb_answers.pipeline import answer_query
        with tempfile.TemporaryDirectory() as root:
            write(root, doc_id='MIX-1', title='Mix', scope='MIX-1 mix', origin='human', body='Ratio: 3:1 sand to lime')
            c = answer_query(root, 'What is the ratio for record MIX-1?').contract
            self.assertEqual(c['kind'], 'supported_answer')


if __name__ == '__main__':
    unittest.main()
