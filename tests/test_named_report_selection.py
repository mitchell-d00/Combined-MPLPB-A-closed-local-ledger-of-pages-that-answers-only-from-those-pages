"""Independent checks for named report selection and attribution."""
import unittest

from mplpb_combined.ledger import withdraw
from tests import test_reported_content as legacy


class NamedReportSelection(unittest.TestCase):
    setUp = legacy.ReportedContentGuards.setUp
    source = legacy.ReportedContentGuards.source
    ask = legacy.ReportedContentGuards.ask
    withheld = legacy.ReportedContentGuards.withheld
    # Use independently worded records and actors rather than the frozen packet.
    writer = 'Iona Vale'
    named = 'In the report written by Iona Vale, which document did Celia Duarte say Bram Okoye wrote?'
    ending = 'Which document did Celia Duarte say Bram Okoye wrote, in the document from Iona Vale?'

    def named_source(self, ident='A', label='<p>Written by Iona Vale.</p>', **policy):
        return self.source(label + '<p>' + legacy.STATEMENT + '</p>', ident=ident, **policy)

    def test_selection_certifies_only_eligible_unique_byline(self):
        first = self.named_source()
        self.named_source('B')
        tied = self.ask(self.named)
        self.withheld(tied)
        self.assertEqual(tied['kind'], 'abstain')
        self.assertEqual(tied['documentary_support']['named_source_selection']['reason'],
                         'multiple_eligible_documents')
        withdraw(self.root, 'B')
        result = self.ask(self.named)
        self.assertTrue(result['answer_supported'])
        claim, = result['claims']
        self.assertEqual(claim['proposition']['source_writer_or_unknown'], self.writer)
        self.assertEqual(claim['proposition']['reporter'], 'Celia Duarte')
        self.assertEqual([c['quote'] for c in claim['citations']], ['Written by Iona Vale.', legacy.STATEMENT])
        self.assertEqual(result['documentary_support']['named_source_selection'],
                         dict(status='verified', source_id=first.id, path=first.path, hash=first.hash_actual))

    def test_selection_alone_cannot_prove_reporter(self):
        first = self.named_source()
        self.source('<p>Written by Juna Holt.</p><p>'
                    + legacy.STATEMENT.replace('Celia Duarte', self.writer) + '</p>', ident='B')
        result = self.ask(self.named.replace('Celia Duarte', self.writer))
        self.withheld(result)
        self.assertEqual(result['diagnostic']['code'], 'named_report_content_unresolved')
        self.assertEqual(result['documentary_support']['named_source_selection']['path'], first.path)

    def test_quoted_or_conflicting_labels_do_not_select(self):
        self.named_source(label='<blockquote><p>Written by Iona Vale.</p></blockquote>')
        self.withheld(self.ask(self.named))
        self.named_source('B', '<p>Written by Iona Vale.</p><p>Written by Juna Holt.</p>')
        result = self.ask(self.named)
        self.withheld(result)
        self.assertEqual(result['diagnostic']['code'], 'named_report_source_unresolved')

    def test_from_byline_requires_closed_physical_paragraph(self):
        self.named_source(label='<p>From: Iona Vale</p>')
        self.assertTrue(self.ask(self.ending)['answer_supported'])
        withdraw(self.root, 'A')
        self.named_source('B', '<pre>From: Iona Vale\nSubject: draft report</pre>')
        self.withheld(self.ask(self.ending))


    def test_from_selection_does_not_depend_on_any_reporting_clause(self):
        first = self.source('<p>From: Iona Vale</p><p>The estuary was quiet.</p>')
        result = self.ask(self.ending)
        self.withheld(result)
        self.assertEqual(result['diagnostic']['code'], 'named_report_content_unresolved')
        self.assertEqual(result['documentary_support']['named_source_selection']['path'], first.path)
