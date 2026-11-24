"""Controls for attributed scope and dates in a sequence of published corrections."""
from dataclasses import replace
from html import escape
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from mplpb_answers.pipeline import answer_query
from mplpb_combined.ledger import write
from mplpb_combined.reader import PROFILES


def document(number, page, day, ident, action, effective, body=''):
    return (f'[Federal Register Volume 77, Number {number} ({day})]\n[Page {page}]\n'
            f'[FR Doc No: {ident}]\nAGENCY: Office of Valley Books (OVB).\n'
            f'ACTION: {action}.\nDATES: Effective {effective}.\n{body}')


EARLIER = document(1, 101, 'January 3, 2012', '2012-101', 'Final rule', 'February 28, 2012')
CORRECTION = document(12, 210, 'February 3, 2012', '2012-210', 'Final rule; correction', 'February 28, 2012', (
    'On January 3, 2012, the Office of Valley Books (OVB) published a final rule in the Federal Register '
    'at 77 FR 101 (FR Doc. 2012-101).'))
LATER = document(20, 350, 'March 3, 2012', '2012-350', 'Correcting amendment', 'March 3, 2012', (
    'On February 3, 2012, OVB published a correction to the final rule titled Catalog Access. 77 FR 210. '
    'The correction included amendatory instruction 7 in the first column of page 211. '
    'A typographical error in that instruction caused the Office of the Federal Register to replace the whole of '
    'paragraph (b) with the text on page 211. OVB did not intend to do that. Rather, OVB intended '
    'to correct only the introductory text of paragraph (b). This document fixes that typographical error.\n'
    'This correction is applicable as if OVB had included this change in the final rule that published on '
    'January 3, 2012. That rule had an effective date of February 28, 2012. Accordingly, the correction is '
    'applicable as of February 28, 2012, at 12 a.m. Eastern Time.'))
SCOPE = ('What did the March OVB document say went wrong in the February correction, '
         'and what part of paragraph (b) had OVB intended to change?')
DATE = 'Across the January rule, February correction and March follow-up, what earlier applicability date is reaffirmed?'


class SuccessiveCorrectionTests(unittest.TestCase):
    def ask(self, question, *, old=EARLIER, previous=CORRECTION, later=LATER, earlier_external='yes'):
        with TemporaryDirectory() as root:
            for number, body in enumerate((old, previous, later), 1):
                if body is not None:
                    write(Path(root), doc_id=f'DOC-{number}', title=f'Document {number}', scope='evidence',
                          body_html='<pre>' + escape(body) + '</pre>',
                          external=earlier_external if number == 1 else 'yes')
            return answer_query(root, question, replace(PROFILES['external'], prose=True)).contract

    def test_keeps_attributed_scope_and_distinct_effective_date(self):
        answer = self.ask(SCOPE, old=EARLIER.replace(" (OVB).", "."))
        self.assertTrue(answer['answer_supported'], answer['diagnostic'])
        p = answer['claims'][0]['proposition']
        self.assertEqual(p['reported_replaced_scope'], 'whole of paragraph (b)')
        self.assertEqual(p['intended_scope'], 'introductory text of paragraph (b)')
        self.assertFalse(answer['verification']['truth_verified'])
        date = self.ask(DATE)
        self.assertTrue(date['answer_supported'], date['diagnostic'])
        p = date['claims'][0]['proposition']
        self.assertEqual(p['applicability_date'], 'February 28, 2012')
        self.assertEqual(p['later_effective_date'], 'March 3, 2012')

    def test_withholds_on_wrong_identity_scope_date_and_missing_source(self):
        for answer in (
            self.ask(SCOPE.replace('(b)', '(a)')),
            self.ask(SCOPE, later=LATER.replace('77 FR 210', '77 FR 211')),
            self.ask(DATE, previous=CORRECTION.replace('2012-101', '2012-999')),
            self.ask(DATE, previous=CORRECTION.replace('Effective February 28', 'Effective February 29')),
            self.ask(DATE, earlier_external='no'),
            self.ask(DATE, old=None),
            self.ask(DATE.replace('January rule', 'April rule')),
            self.ask(DATE.replace('reaffirmed?', 'reaffirmed for all applications?')),
        ):
            self.assertFalse(answer['answer_supported'])
