from html import escape
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from mplpb_answers import bounded_records
from mplpb_answers.pipeline import answer_query
from mplpb_combined.ledger import withdraw, write
from mplpb_combined.reader import PROFILES


class BoundedRecordTests(unittest.TestCase):
    def setUp(self):
        folder = TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.root = Path(folder.name)

    def write(self, key, body, *, pre=True):
        return write(self.root, title='Official record ' + key, scope='documentary records',
                     doc_id=key, body_html=f'<pre>{escape(body)}</pre>' if pre else body)

    def query(self, question, **kwargs):
        return answer_query(self.root, question, PROFILES['internal'], **kwargs).contract

    def test_conflict_evidence_is_atomic_under_budget(self):
        statements = ['Dispatch D-81 at the pier was logged at 16:25.',
                      'Dispatch D-81 at the pier was logged at 16:45.']
        for key, body in zip(('R-A', 'R-B'), statements):
            self.write(key, body)
        question = 'Which logging time do the records support?'
        answer = self.query(question)
        self.assertEqual(answer['kind'], 'conflict')
        self.assertFalse(answer['answer_supported'])
        self.assertEqual([q['quote'] for q in answer['claims'][0]['citations']], statements)
        limited = self.query(question, max_passages=1)
        self.assertEqual(limited['diagnostic']['code'], 'contradictory_passages_pruned')
        self.assertEqual(limited['claims'], [])
        self.assertEqual(limited['sources'], [])

    def test_state_change_discards_new_answer(self):
        self.write('R-A', 'Report 15 at the pier was logged at 07:30.')
        original = bounded_records.verify

        def changed(index):
            checked = original(index)
            withdraw(self.root, 'R-A')
            return checked

        with patch.object(bounded_records, 'verify', side_effect=changed):
            result = self.query('Which logging time do the records support?')
        self.assertEqual(result['diagnostic']['code'], 'source_changed')
        self.assertEqual(result['claims'], [])
        self.assertEqual(result['sources'], [])

    def test_quoted_item_does_not_license_event(self):
        self.write('R-A', 'The July 3 coastal meeting was moved to July 6. Its docket number remains CM-19.')
        self.write('R-B', '<blockquote>Coastal meeting docket CM-19 opened July 6.</blockquote>', pre=False)
        query = 'Do sources R-A and R-B describe the same event?'
        self.assertEqual(self.query(query)['diagnostic']['code'], 'event_identity_unresolved')

    def test_cli_displays_verified_part_and_unresolved_part(self):
        self.write('R-A', 'At 7 a.m., Frances handed the token to Avery.')
        self.write('R-B', 'At 8 a.m., Avery handed it to Lane.')
        self.write('R-C', 'At 9 a.m., Quinn signed the return log. The log does not name who handed back the token.')
        question = 'Who held the token immediately after 8 a.m., and who returned it at 9 a.m.?'
        run = subprocess.run([sys.executable, '-m', 'mplpb_answers', 'ask', str(self.root), question,
                              '--profile', 'internal'], capture_output=True, text=True, timeout=20)
        self.assertIn('PARTIAL ANSWER', run.stdout)
        self.assertIn('Lane held the token', run.stdout)
        self.assertIn('returner at the requested time is unresolved', run.stdout)
        self.assertNotIn('Quinn returned', run.stdout)
