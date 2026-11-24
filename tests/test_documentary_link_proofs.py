"""Named-source documentary proof and contrasting refusal controls."""
from html import escape
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from mplpb_answers.pipeline import answer_query
from mplpb_combined.ledger import write, withdraw
from mplpb_combined.reader import PROFILES


class DocumentaryLinkProofTests(unittest.TestCase):
    def setUp(self):
        temp = TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)

    def add(self, ident, text, *, markup='pre', **kwargs):
        return write(self.root, doc_id=ident, title=ident, scope='archival documents',
                     body_html=f'<{markup}>' + escape(text) + f'</{markup}>', **kwargs)

    def check(self, question, **kwargs):
        return answer_query(self.root, question, **kwargs).contract

    def test_partial_correction_keeps_both_citations_and_the_original_value(self):
        self.add('ENTRY-A', 'Load Weight: forty pounds\nLanding Site: West wharf')
        self.add('ENTRY-B', 'Correction to source ENTRY-A: Load Weight should read thirty pounds. '
                 'Landing Site remains West wharf.')
        question = 'What did source ENTRY-B change in source ENTRY-A, and what did it retain?'
        result = self.check(question)
        self.assertTrue(result['answer_supported'], result['diagnostic'])
        claim = result['claims'][0]
        self.assertEqual([c['source_id'] for c in claim['citations']], ['ENTRY-A', 'ENTRY-B'])
        self.assertEqual(claim['proposition']['previous_value'], 'forty pounds')
        self.assertEqual(claim['proposition']['retained_value'], 'West wharf')
        self.assertFalse(result['verification']['truth_verified'])
        self.assertFalse(self.check(question, max_passages=1)['answer_supported'])
        withdraw(self.root, 'ENTRY-B')
        self.assertFalse(self.check(question)['answer_supported'])

    def test_other_targets_and_unstated_retention_are_unresolved(self):
        self.add('ENTRY-A', 'Load Weight: forty pounds\nLanding Site: West wharf')
        for ident, text in (
            ('WRONG-1', 'Correction to source ENTRY-C: Load Weight should read thirty pounds. Landing Site remains West wharf.'),
            ('WRONG-2', 'Correction to source ENTRY-A: Load Weight should read thirty pounds. Landing Site remains East wharf.'),
            ('WRONG-3', 'Correction to source ENTRY-A: Load Weight should read thirty pounds.'),
            ('WRONG-4', 'Correction to source ENTRY-A: Load Weight should read thirty pounds. Landing Site remains West wharf if approved.'),
            ('WRONG-5', 'Correction to source ENTRY-A: Load Weight should read thirty pounds. Landing Site remains West wharf. The clerk denied the correction.'),
        ):
            with self.subTest(ident=ident):
                self.add(ident, text)
                self.assertFalse(self.check(f'What did source {ident} change in source ENTRY-A, and what did it retain?')['answer_supported'])

    def test_source_change_after_correction_verification_discards_evidence(self):
        from mplpb_answers import documentary_links

        self.add('ENTRY-A', 'Load Weight: forty pounds\nLanding Site: West wharf')
        self.add('ENTRY-B', 'Correction to source ENTRY-A: Load Weight should read thirty pounds. '
                 'Landing Site remains West wharf.')
        resolve = documentary_links.resolve

        def changed(*args, **kwargs):
            claim = resolve(*args, **kwargs)
            self.assertTrue(claim)
            withdraw(self.root, 'ENTRY-B')
            return claim

        with patch.object(documentary_links, 'resolve', side_effect=changed):
            result = self.check('What did source ENTRY-B change in source ENTRY-A, and what did it retain?')
        self.assertEqual(result['diagnostic']['code'], 'source_changed')
        self.assertFalse(result['answer_supported'])
        self.assertEqual(result['claims'], [])

    def test_named_chain_keeps_the_receipt_attributed(self):
        self.add('LEAF-A', 'Rita Snow requested that Len Kay send the water chart to the west landing.')
        self.add('LEAF-B', 'In response to request source LEAF-A, Len Kay sent the water chart to the west landing.')
        receipt = 'Referring to dispatch source LEAF-B, Bea Park reported receiving the water chart at the west landing from Len Kay.'
        self.add('LEAF-C', receipt, external='no')
        self.add('QUOTE-C', receipt, markup='blockquote')
        question = 'Trace the request, dispatch and reported receipt in sources LEAF-A, LEAF-B and LEAF-C.'
        answer = self.check(question)
        self.assertTrue(answer['answer_supported'], answer['diagnostic'])
        claim = answer['claims'][0]
        self.assertEqual(claim['proposition']['reported_by'], 'Bea Park')
        self.assertEqual(tuple(c['source_id'] for c in claim['citations']), ('LEAF-A', 'LEAF-B', 'LEAF-C'))
        self.assertFalse(answer['verification']['independence_verified'])
        for result in (
            self.check(question, max_passages=2),
            self.check(question, profile=PROFILES['external']),
            self.check(question.replace('LEAF-C', 'QUOTE-C')),
            self.check(question.replace('reported receipt', 'actual delivery')),
            self.check(question.replace('LEAF-C.', 'LEAF-C if the result was independently confirmed.')),
        ):
            self.assertFalse(result['answer_supported'])
