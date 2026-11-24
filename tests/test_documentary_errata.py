"""Independently worded erratum evidence and counterexamples."""
from dataclasses import replace
from hashlib import sha256
from html import escape
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from mplpb_answers.pipeline import answer_query
from mplpb_combined.ledger import write
from mplpb_combined.reader import PROFILES


QUESTION = ('According to the Safe-Probe erratum, what attribution was withdrawn '
            'and what happened to the earlier benchmark scores?')
EARLIER = ("# Comparing systems\n28 June 2025 · Version 3.7 · Draft\nThe available materials are listed below.\n"
           "The archive does not establish that Lane operated Reeve's private tracer.")
ERRATUM = ("# Comparing systems — Tracer attribution correction\n"
           "30 June 2025. Corrected in version 3.8.\n"
           "Version 3.7 mistakenly referred to “Reeve's private tracer.” That attribution is withdrawn.\n"
           "No benchmark scores change as a result of this erratum.")


class ErratumTests(unittest.TestCase):
    def ask(self, question=QUESTION, *, old=EARLIER, erratum=ERRATUM,
            wrong_origin=False, duplicate=False, blocked=False, max_passages=12):
        with TemporaryDirectory() as root:
            for ident, text in [('DOC-1', old), ('DOC-2', erratum)] + ([('DOC-3', old)] if duplicate else []):
                if text is None:
                    continue
                repo = 'other-probe' if wrong_origin and ident == 'DOC-1' else 'safe-probe'
                source_url = f'https://raw.githubusercontent.com/example/{repo}/' + 'a' * 40 + '/' + ident + '.md'
                digest = sha256(text.encode()).hexdigest()
                manifest = {'source_url': source_url, 'source_sha256': digest,
                            'text_sha256': digest, 'transport': 'local_fixture'}
                html = '<pre>' + escape(text) + '</pre><p>Source capture: ' + escape(json.dumps(manifest)) + '</p>'
                write(Path(root), doc_id=ident, title=ident, scope='documentary records', origin='machine',
                      body_html=html, source_authorship='declared-human', external='no' if blocked and ident == 'DOC-1' else 'yes')
            return answer_query(root, question, replace(PROFILES['external'], max_depth=1, prose=True),
                                max_passages=max_passages).contract

    def test_attributes_withdrawal_and_keeps_earlier_verification_limit(self):
        answer = self.ask()
        self.assertTrue(answer['answer_supported'], answer['diagnostic'])
        claim = answer['claims'][0]
        self.assertEqual(claim['proposition']['withdrawn_attribution'], "Reeve's private tracer")
        self.assertEqual(claim['proposition']['earlier_statement'],
                         "The archive does not establish that Lane operated Reeve's private tracer.")
        self.assertEqual(claim['proposition']['benchmark_scores'], 'unchanged')
        self.assertEqual({v['source_id'] for v in claim['citations']}, {'DOC-1', 'DOC-2'})
        self.assertFalse(answer['verification']['truth_verified'])

    def test_withholds_outside_bound_scope(self):
        for answer in (
            self.ask(old=None), self.ask(erratum=None), self.ask(duplicate=True),
            self.ask(blocked=True), self.ask(wrong_origin=True), self.ask(max_passages=1),
            self.ask(old=EARLIER.replace('does not establish', 'establishes')),
            self.ask(old=EARLIER.replace('Version 3.7', 'Version 3.6')),
            self.ask(erratum=ERRATUM.replace('No benchmark scores change', 'One benchmark score changes')),
            self.ask(erratum=ERRATUM.replace('No benchmark scores', 'If the review is released,\nNo benchmark scores')),
            self.ask(question=QUESTION.removesuffix('?') + ', and who actually ran the tracer?'),
        ):
            self.assertFalse(answer['answer_supported'])
