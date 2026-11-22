"""Check that the discovery probe avoids contents listings and duplicate headings."""
import unittest

from test_tools.report_section_probe import summary_span


class ReportSectionProbeTests(unittest.TestCase):
    def test_contents_listing_cannot_select_the_report_section(self):
        body = ('1.0\nSUMMARY\n.....................\n'
                'I. 0\nSUMMARY\nThe field team published its dated survey report yesterday.\n'
                '2.0\nINTRODUCTION\nThe archive includes several other records.')
        start, end = summary_span(body)
        self.assertTrue(body[start:end].startswith('The field team'))
        self.assertNotIn('INTRODUCTION', body[start:end])

    def test_competing_sections_and_unnumbered_text_stay_unresolved(self):
        body = ('SUMMARY\nThe field team published its dated survey report yesterday.\n')
        self.assertIsNone(summary_span(body))
        self.assertIsNone(summary_span('1.0\n' + body + '2.0\n' + body))
