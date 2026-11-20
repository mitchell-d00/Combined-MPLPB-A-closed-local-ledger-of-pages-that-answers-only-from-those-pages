"""Development controls for independent field obligations on one record."""
import html
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from mplpb_answers import pipeline
from mplpb_combined import ledger
from mplpb_combined.reader import PROFILES


class CompoundFieldTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)

    def page(self, fields, doc_id='SHEET-A', **options):
        body = 'Record-ID: FOLIO-71\n' + fields
        return ledger.write(self.root, doc_id=doc_id, title='Archive sheet', scope='archive',
                            body_html='<pre>' + html.escape(body) + '</pre>', **options)

    def ask(self, question='What are the accession date and shelf code for record FOLIO-71?', **options):
        return pipeline.answer_query(self.root, question, **options).contract

    def test_complete_with_independent_citations(self):
        self.page('Accession Date: 1859-07-11\nShelf Code: R42')
        answer = self.ask()
        self.assertTrue(answer['answer_supported'])
        self.assertEqual([c['text'] for c in answer['claims']],
                         ['Accession Date: 1859-07-11', 'Shelf Code: R42'])
        self.assertTrue(all(len(c['citations']) == 1 for c in answer['claims']))

    def test_missing_field_and_conflict_keep_the_other_checked_part(self):
        self.page('Accession Date: 1859-07-11')
        answer = self.ask()
        self.assertEqual(answer['kind'], 'partial_answer')
        self.assertFalse(answer['answer_supported'])
        self.assertEqual([p['status'] for p in answer['question_parts']], ['verified', 'unresolved'])
        self.assertEqual(answer['question_parts'][1]['diagnostic']['code'], 'exact_field_missing')
        self.page('Accession Date: 1861-08-12\nShelf Code: R42', 'SHEET-B')
        answer = self.ask()
        self.assertEqual(answer['kind'], 'conflict')
        self.assertFalse(answer['answer_supported'])

    def test_unrelated_appearances_cannot_combine(self):
        self.page('Accession Date: 1859-07-11')
        self.page('Shelf Code: R42', 'SHEET-B')
        self.assertFalse(self.ask()['answer_supported'])

    def test_qualifiers_and_scope_are_not_dropped(self):
        self.page('Accession Date: 1859-07-11\nShelf Code: R42')
        for question in [
            'For record FOLIO-71, report its accession date and shelf code before the revision.',
            'For record FOLIO-71, report its accession date and shelf code and who put it there.',
            'For record FOLIO-71, report its accession date or shelf code.',
        ]:
            with self.subTest(question=question):
                self.assertFalse(self.ask(question)['answer_supported'])

    def test_original_question_controls_delivery_and_budget_is_shared(self):
        self.page('Accession Date: 1859-07-11\nShelf Code: R42', not_for='shelf')
        self.assertFalse(self.ask(profile=PROFILES['internal'])['answer_supported'])
        self.assertFalse(self.ask(max_passages=1)['answer_supported'])

    def test_shared_budget_retains_only_displayable_proofs(self):
        self.page('Accession Date: 1859-07-11\nShelf Code: R42')
        answer = self.ask(max_passages=1)
        self.assertEqual(answer['kind'], 'partial_answer')
        self.assertFalse(answer['answer_supported'])
        self.assertEqual(len(answer['claims']), 1)
        self.assertEqual(answer['question_parts'][1]['status'], 'unresolved')

    def test_field_scoped_correction_preserves_other_field(self):
        old = self.page('Accession Date: 1859-07-11\nShelf Code: R42')
        self.page('Accession Date: 1859-08-11', 'SHEET-B', supersedes=[old.id],
                  corrects_field='Accession Date', valid_from='2026-11-01')
        for as_of, day in [('2026-10-01', '1859-07-11'), ('2026-11-20', '1859-08-11')]:
            with self.subTest(as_of=as_of):
                answer = self.ask(as_of=as_of)
                self.assertTrue(answer['answer_supported'], answer['diagnostic'])
                self.assertEqual([c['text'] for c in answer['claims']],
                                 ['Accession Date: ' + day, 'Shelf Code: R42'])

    def test_change_after_first_proof_discards_both_parts(self):
        self.page('Accession Date: 1859-07-11\nShelf Code: R42')
        original = pipeline._answer_query

        def change_between_fields(*args, **kwargs):
            result = original(*args, **kwargs)
            if kwargs['exact']['field'] == 'accession date':
                self.page('Shelf Code: R52', 'SHEET-B')
            return result

        with patch.object(pipeline, '_answer_query', side_effect=change_between_fields):
            answer = self.ask()
        self.assertFalse(answer['answer_supported'])
        self.assertEqual(answer['diagnostic']['code'], 'source_changed')
        self.assertEqual(answer['claims'], [])

    def test_html_quotation_cannot_become_a_field_declaration(self):
        ledger.write(self.root, doc_id='SHEET-A', title='Source quotation', scope='archive',
                     body_html='<blockquote><pre>Accession Date: 1859-07-11\nShelf Code: R42</pre></blockquote>')
        compound = self.ask('What are the accession date and shelf code for record SHEET-A?')
        date = self.ask('What is the accession date for record SHEET-A?')
        self.assertFalse(compound['answer_supported'])
        self.assertFalse(date['answer_supported'])
        self.assertFalse(compound['claims'])
