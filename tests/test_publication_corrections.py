"""Independent publication-correction cases over eligible source bodies."""
from html import escape
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from mplpb_answers.pipeline import answer_query
from mplpb_combined.ledger import write
from mplpb_combined.reader import PROFILES


def notice(volume, page, date, doc, body):
    return (f'[Federal Register Volume {volume}, Number 5 ({date})]\n[Page {page}]\n'
            f'[FR Doc No: {doc}]\nAGENCY: Orchard Records Board.\n' + body)


class PublicationCorrectionTests(unittest.TestCase):
    def setUp(self):
        tmp = TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.workspace = Path(tmp.name)
        self.question = 'How did the Dover meeting venue change, and what meeting hours stayed the same?'
        self.old = notice(74, 500, 'February 3, 2009', 'E9-500', (
            'ACTION: Notice of public meetings.\n'
            'DATES: The meeting will be held from 10 a.m. to 3 p.m.\n'
            'ADDRESSES: Dover, DE: The Assembly Hall, 1 Willow Lane.'))
        self.new = notice(74, 550, 'February 5, 2009', 'E9-550', (
            'ACTION: Notice of public meetings; correction.\n'
            'SUMMARY: The notice published in the Federal Register on February 3, 2009 '
            '(74 FR 500), provided an incorrect location for the meeting to be held in Dover, DE.\n'
            'DATES: The Dover, DE, meeting will be held from 10 a.m. to 3 p.m.\n'
            'ADDRESSES: The Dover, DE, public meeting will be held at the Riverside Hotel, 2 Bank Road.'))

    def insert(self, root, ident, body, markup='pre', external='yes'):
        write(root, doc_id=ident, title=ident, scope='archives',
              body_html=f'<{markup}>' + escape(body) + f'</{markup}>', external=external)

    def test_resolves_unique_publication_and_rechecks_witness_budget(self):
        root = self.workspace
        self.insert(root, 'DOC-FIRST', self.old)
        self.insert(root, 'DOC-SECOND', self.new)
        answer = answer_query(root, self.question).contract
        self.assertTrue(answer['answer_supported'], answer['diagnostic'])
        p = answer['claims'][0]['proposition']
        self.assertEqual((p['from_venue'], p['to_venue'], p['retained_hours']),
                         ('The Assembly Hall', 'Riverside Hotel', '10 a.m. to 3 p.m.'))
        self.assertFalse(answer['verification']['truth_verified'])
        self.assertEqual(answer_query(root, self.question, max_passages=1).contract['diagnostic']['code'],
                         'reader_budget_exceeded')

    def test_refuses_when_target_scope_or_retention_is_unresolved(self):
        for n, (old, new, markup, external, duplicate) in enumerate((
            (self.old, self.new.replace('74 FR 500', '74 FR 501'), 'pre', 'yes', False),
            (self.old, self.new.replace('10 a.m. to 3 p.m.', '10 a.m. to 4 p.m.'), 'pre', 'yes', False),
            (self.old, self.new.replace('for the meeting', 'if approved, for the meeting'), 'pre', 'yes', False),
            (self.old, self.new, 'blockquote', 'yes', False),
            (self.old, self.new, 'pre', 'no', False),
            (self.old, self.new, 'pre', 'yes', True),
        )):
            with self.subTest(case=n):
                root = self.workspace / str(n)
                self.insert(root, 'DOC-FIRST', old, external=external)
                self.insert(root, 'DOC-SECOND', new, markup)
                if duplicate:
                    self.insert(root, 'DOC-COPY', old)
                result = answer_query(root, self.question, PROFILES['external']).contract
                self.assertFalse(result['answer_supported'])
