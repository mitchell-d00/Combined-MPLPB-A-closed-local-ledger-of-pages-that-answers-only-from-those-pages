"""Check a continuous, source-attributed first-person presentation."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from mplpb_answers.pipeline import answer_query
from mplpb_combined.ledger import write


QUESTION = ('What transport-planning emphasis did Morgan recommend to Patel before her inspection trip, '
            'and what framework did Patel say she presented in her meetings?')
ADVICE = ('<p>Ottawa, May 4, 1972.</p>'
          '<p>The focus of the discussion was Director Patel’s upcoming inspection trip.</p>'
          '<p>Ms. Morgan recommended that Director Patel emphasize “scheduled service” in transport planning.</p>')
REPORT = (
    '<p>On May 20, 1972, Director Anika Patel reported to Minister Lopez on the results of a mission '
    'she had just led to consult with the transit authorities. Patel reported the trip a success. '
    'She also reported positive reactions to her emphasis on two transport principles '
    'as the basis for dealing with service problems:</p>'
    '<p>“In my meetings with station managers, I presented the planning framework '
    'in terms of two transport principles expressed as ideals:</p>'
    '<p>“1. Access to stations</p><p>“2. Predictable schedules</p>'
    '<p>“The discussion was constructive.” '
    '(Memorandum from Director Patel to Minister Lopez, May 20, 1972; City Archive)</p>'
)


class PresentationTests(unittest.TestCase):
    def ask(self, report=REPORT, advice=ADVICE, max_passages=12, duplicate=False):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            write(root, doc_id='NOTES', title='Meeting notes', scope='minutes', body_html=advice)
            if report:
                write(root, doc_id='REPORT', title='Editorial account', scope='report', body_html=report)
                if duplicate:
                    write(root, doc_id='COPY', title='Second appearance', scope='report', body_html=report)
            return answer_query(root, QUESTION, max_passages=max_passages).contract

    def test_attributes_first_person_quote_and_complete_list(self):
        answer = self.ask()
        self.assertEqual(answer['kind'], 'supported_answer')
        self.assertTrue(answer['answer_supported'])
        advice, presentation = answer['claims']
        self.assertEqual(advice['proposition']['adviser'], 'Morgan')
        self.assertEqual(presentation['proposition']['speaker'], 'Patel')
        self.assertEqual(presentation['proposition']['framework_items'],
                         ['Access to stations', 'Predictable schedules'])
        self.assertEqual(presentation['proposition']['modality'], 'quoted_self_report')
        self.assertFalse(answer['verification']['truth_verified'])

    def test_preserves_advice_on_unresolved_presentation(self):
        for options in (
            {'report': ''},
            {'report': REPORT.replace('Patel reported the trip', 'Rivera reported the trip')},
            {'report': REPORT.replace('She also reported', 'He also reported')},
            {'report': REPORT.replace('a success.', 'a success, according to Rivera.')},
            {'report': REPORT.replace('Memorandum from Director Patel', 'Memorandum from Director Priya Patel')},

            {'report': REPORT.replace('“In my meetings', 'Rivera said, “In my meetings')},
            {'report': REPORT.replace('Memorandum from Director Patel', 'Memorandum from Director Rivera')},
            {'report': REPORT.replace('from Director Patel to Minister Lopez', 'from Director Patel to Minister Bello')},
            {'report': REPORT.replace('May 20, 1972; City', 'May 21, 1972; City')},
            {'report': REPORT.replace('“2. Predictable schedules', '“3. Predictable schedules')},
            {'report': REPORT.replace('I presented', 'I might present')},
            {'report': REPORT.replace('planning framework', 'hypothetical planning framework')},
            {'advice': ADVICE.replace('May 4', 'May 24')},
            {'advice': ADVICE.replace('<p>Ottawa, May 4, 1972.</p>',
                                      '<blockquote>Ottawa, May 4, 1972.</blockquote>')},

            {'max_passages': 2},
            {'duplicate': True},
        ):
            with self.subTest(options=options):
                answer = self.ask(**options)
                self.assertEqual(answer['kind'], 'partial_answer')
                self.assertFalse(answer['answer_supported'])
                self.assertEqual(len(answer['claims']), 1)
