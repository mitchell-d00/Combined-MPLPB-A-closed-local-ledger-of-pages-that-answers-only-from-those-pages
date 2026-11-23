"""Whole pipeline controls for named statutes and source-attributed summaries."""
from html import escape
from tempfile import TemporaryDirectory
import unittest

from mplpb_answers.pipeline import answer_query
from mplpb_combined.ledger import write
from mplpb_combined.reader import PROFILES


class HistoricalSeamTests(unittest.TestCase):
    def query(self, question, *texts, **kwargs):
        with TemporaryDirectory() as root:
            for number, text in enumerate(texts):
                write(root, doc_id=f'SRC-{number}', title='Imported record', scope='Documentary material',
                      body_html='<pre>' + escape(text) + '</pre>', when='2026-11-23')
            return answer_query(root, question, PROFILES['internal'], **kwargs).contract

    def test_discretion_and_term_share_a_source_span(self):
        question = 'Is leasing mandatory under the North Point statute, or discretionary with a maximum term?'
        law = ('North Point Statute\nTranscript\nThe warden may, in her discretion, grant leases for storage '
               'for terms not exceeding four years, subject to annual access inspection.')
        answer = self.query(question, law)
        self.assertEqual(answer['kind'], 'supported_answer', answer['diagnostic'])
        self.assertIn('annual access inspection', answer['claims'][0]['citations'][0]['quote'])
        self.assertFalse(answer['verification']['truth_verified'])

    def test_wrong_title_qualified_rule_or_competing_terms_stops(self):
        question = 'Is leasing mandatory under the North Point statute, or discretionary with a maximum term?'
        clause = 'The warden may, in her discretion, grant leases for storage for terms not exceeding four years.'
        for texts in [
            ('West Point Statute\n' + clause,),
            ('North Point Statute\nIf authorized, the warden may in her discretion grant leases for terms not exceeding four years.',),
            ('North Point Statute\n' + clause + ' The warden shall grant leases for storage.',),
            ('North Point Statute\n' + clause,
             'North Point Statute\n' + clause.replace('four', 'seven')),
            ('North Point Statute\nThe warden may grant leases for storage. Licenses shall have terms not exceeding four years.',),
        ]:
            with self.subTest(texts=texts):
                self.assertFalse(self.query(question, *texts)['answer_supported'])

    def test_report_summary_spans_are_cited_under_bounded_scope(self):
        question = 'According to the North Reach summary, why was the survey aborted and what equipment supported return to base?'
        report = ('NORTH REACH SURVEY REPORT\n1. 0\nSUMMARY\n'
                  'The North Reach trip, planned as a survey in the inlet, was aborted because of engine vibration.\n'
                  'The radio provided the necessary support to sustain a safe return to base.\n'
                  '2. 0\nOPERATIONS\nThe crew recorded its arrival at the harbor.')
        answer = self.query(question, report)
        self.assertIn(answer['kind'], ('partial_answer', 'supported_answer'), answer['diagnostic'])
        quotes = ' '.join(cite['quote'] for claim in answer['claims'] for cite in claim['citations'])
        self.assertIn('engine vibration', quotes)
        self.assertIn('The radio provided', quotes)
        self.assertFalse(answer['verification']['truth_verified'])

    def test_summary_locator_withholds_competing_or_unrelated_sources(self):
        question = 'According to the North Reach summary, why was the survey aborted and what equipment supported return to base?'
        report = ('NORTH REACH SURVEY REPORT\n1. 0\nSUMMARY\n'
                  'The North Reach survey was aborted because of engine vibration.\n'
                  'The radio provided the necessary support to sustain a safe return to base.')
        variants = (
            (report, report.replace('engine vibration', 'radio loss')),
            (report.replace('NORTH REACH SURVEY REPORT', 'SOUTH REACH SURVEY REPORT'),),
            (report + '\nA correction to the report changes the finding.',),
            (report.replace('was aborted', 'was not aborted').replace('return to base', 'return to port'),),
        )
        for texts in variants:
            with self.subTest(texts=texts):
                answer = self.query(question, *texts)
                self.assertFalse(answer['answer_supported'])
                self.assertNotIn('section_edge', answer.get('documentary_support', {}))

    def test_motion_correction_does_not_erase_cited_documentary_statements(self):
        question = 'According to the North Reach summary, why was the survey aborted and what equipment supported return to base?'
        report = ('NORTH REACH SURVEY REPORT\n1. 0\nSUMMARY\n'
                  'The North Reach survey was aborted because of engine vibration.\n'
                  'The radio provided the necessary support to sustain a safe return to base.\n'
                  'The pilot made a course correction before arriving at the harbor.')
        result = self.query(question, report)
        self.assertEqual(result['kind'], 'partial_answer')
        self.assertEqual(len(result['claims']), 2)
        self.assertFalse(result['documentary_support']['section_edge']['source_support_established'])
