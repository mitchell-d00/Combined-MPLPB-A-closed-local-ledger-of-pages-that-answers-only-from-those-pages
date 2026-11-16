"""Adversarial documentary checks; expert output never supplies its own oracle."""
import copy
import html
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from mplpb_answers.body_text import body_text
from mplpb_combined.ledger import Ledger, write, revise
from mplpb_combined.reader import PROFILES
from mplpb_work import historical_evidence as extractor
from mplpb_work import historical_verifier as verifier


class HistoricalVerifierTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.question = 'archive historical documentary relationships'
        self.body = ('Document ID: ARCHIVE-CASE-101\n'
                     'Updated: 1850-05-01T12:00Z v5\n'
                     'Related: ARCHIVE-CASE-102 v2.\n'
                     'Supersedes: ARCHIVE-CASE-101 v4 (1849-01-01), v3 (1848-01-01). '
                     'No earlier paper or implementation is superseded.\n\n'
                     'Abstract\nThis is a fictional documentary fixture.')
        self.record = self.add('DOC-0001', self.body)

    def add(self, identifier, body, **kwargs):
        return write(self.root, doc_id=identifier, title='Untrusted fixture title',
                     scope=kwargs.pop('scope','archive historical documentary relationships'),
                     body_html='<pre>'+html.escape(body)+'</pre>', **kwargs)

    def proposed(self, record=None):
        record = record or self.record
        body = body_text(record.body_html)
        return [dict(row, source_id=record.id, path=record.path, hash=record.hash_actual)
                for row in extractor.extract(body)]

    def verify(self, observations=None, profile=None, snapshot=None):
        profile = profile or PROFILES['internal']
        return verifier.verify_observations(self.root, self.question, profile,
                    observations if observations is not None else self.proposed(),
                    snapshot or verifier.verification_snapshot(self.root, self.question, profile))

    def test_independent_verification_accepts_explicit_headers_without_calling_extractor(self):
        observations = self.proposed()
        with patch.object(extractor, 'extract', side_effect=AssertionError('extractor used as its own oracle')):
            result = self.verify(observations)
        self.assertEqual(result['code'], 'verified', result)
        self.assertEqual(result['verified'], observations)
        self.assertFalse(result['answer_supported'])
        self.assertFalse(result['truth_verified'])
        self.assertEqual({(o['target_id'], o['target_version']) for o in observations if o['kind']=='supersedes'},
                         {('ARCHIVE-CASE-101','v4'), ('ARCHIVE-CASE-101','v3')})

    def test_forged_meaning_cannot_reuse_a_real_quote(self):
        original = next(row for row in self.proposed() if row['kind']=='related')
        for changes in ({'kind':'supersedes'}, {'value':'ARCHIVE-CASE-999','target_id':'ARCHIVE-CASE-999'},
                        {'target_version':'v3'}, {'target_version':''}, {'kind':'caused'}):
            with self.subTest(changes=changes):
                forged = dict(original, **changes)
                result = self.verify([forged])
                self.assertEqual(result['verified'], [])
                self.assertEqual(len(result['rejected']), 1)

    def test_negation_cannot_be_stripped_or_changed_into_a_positive_edge(self):
        rec = self.add('DOC-0002', 'Document ID: ARCHIVE-CASE-202\n'
                       'Updated: 1851-01-01 v1\n'
                       'Supersedes: No earlier paper ARCHIVE-CASE-999 is superseded.\n\nAbstract\nFixture.')
        observation = next(row for row in self.proposed(rec) if row['kind']=='not_superseded')
        forged = dict(observation,kind='supersedes',value='ARCHIVE-CASE-999',target_id='ARCHIVE-CASE-999')
        self.assertEqual(self.verify([forged])['verified'], [])
        self.assertEqual(self.verify([observation])['verified'], [observation])
        shortened = dict(observation)
        shortened.update(start=observation['quote'].index('ARCHIVE-CASE-999')+observation['start'],
                         quote='ARCHIVE-CASE-999')
        shortened['end']=shortened['start']+len(shortened['quote'])
        self.assertEqual(self.verify([shortened])['verified'], [])

    def test_title_example_and_later_body_fields_cannot_become_documentary_headers(self):
        for suffix in ('\n## Example\n', '\nExample:\n', '\nAbstract\n', '\nIntroduction\n'):
            with self.subTest(suffix=suffix):
                record = self.add('EXAMPLE-'+str(len(list(self.root.glob('*.html')))),
                    'Document ID: ARCHIVE-CASE-303\nUpdated: 1852-01-01 v1'+suffix+
                    'Related: ARCHIVE-CASE-999 v9.')
                body = body_text(record.body_html)
                quote = 'Related: ARCHIVE-CASE-999 v9.'
                start = body.index(quote)
                forged = dict(source_id=record.id,path=record.path,hash=record.hash_actual,
                    start=start,end=start+len(quote),quote=quote,kind='related',
                    value='ARCHIVE-CASE-999',target_id='ARCHIVE-CASE-999',target_version='v9')
                self.assertEqual(self.verify([forged])['verified'], [])

    def test_exact_offsets_unicode_and_closed_fields(self):
        row = self.proposed()[0]
        for changes in ({'start':True}, {'end':-1}, {'quote':row['quote']+' changed'},
                        {'path':'../outside.html'}, {'hash':'sha256:'+'0'*64}, {'verified':True}):
            with self.subTest(changes=changes):
                self.assertEqual(self.verify([dict(row,**changes)])['verified'], [])

    def test_original_question_and_profile_are_part_of_the_snapshot(self):
        snapshot = verifier.verification_snapshot(self.root,self.question,PROFILES['internal'])
        result = verifier.verify_observations(self.root,self.question+' secret',PROFILES['internal'],
                                              self.proposed(),snapshot)
        self.assertFalse(result['source_state_current'])
        self.assertEqual(result['verified'], [])
        result = self.verify(profile=PROFILES['external'],snapshot=snapshot)
        self.assertFalse(result['source_state_current'])

    def test_not_for_and_external_policy_are_checked_against_original_question(self):
        self.add('PRIVATE-0001','Document ID: ARCHIVE-CASE-401\nUpdated: 1853-01-01 v1\nRelated: ARCHIVE-CASE-102 v2.',external='no')
        private = Ledger(self.root).by_id['PRIVATE-0001'][0]
        self.assertEqual(self.verify(self.proposed(private),profile=PROFILES['external'])['verified'], [])
        rec = self.add('EXCLUDED-0001','Document ID: ARCHIVE-CASE-402\nUpdated: 1853-01-01 v1\nRelated: ARCHIVE-CASE-102 v2.',not_for='relationships',scope='archive notes')
        self.assertEqual(self.verify(self.proposed(rec))['verified'], [])

    def test_state_change_before_or_during_verification_discards_old_quotes(self):
        rows = self.proposed()
        snapshot = verifier.verification_snapshot(self.root,self.question)
        revise(self.root,self.record.id,body='Document ID: ARCHIVE-CASE-101\nUpdated: 1854-01-01 v6')
        result = self.verify(rows,snapshot=snapshot)
        self.assertFalse(result['source_state_current'])
        self.assertEqual(result['verified'], [])
        self.assertEqual(result['rejected'], [])
        current = Ledger(self.root).servable()[0]
        rows = self.proposed(current)
        snapshot = verifier.verification_snapshot(self.root,self.question)
        original = verifier._semantic
        called = []
        def changed(*args):
            if not called:
                called.append(True)
                revise(self.root,current.id,body='Document ID: ARCHIVE-CASE-101\nUpdated: 1855-01-01 v7')
            return original(*args)
        with patch.object(verifier,'_semantic',side_effect=changed):
            result = self.verify(rows,snapshot=snapshot)
        self.assertEqual(result['code'],'source_changed')
        self.assertEqual(result['verified'],[])
        self.assertEqual(result['rejected'],[])

    def test_conflicting_or_impossible_header_dates_are_not_certified(self):
        for tail in ('Updated: 1850-02-30 v1',
                     'Updated: 1850-01-01 v1\nUpdated: 1851-01-01 v2'):
            with self.subTest(tail=tail):
                raw = 'Document ID: ARCHIVE-CASE-501\n'+tail
                record = self.add('DATE-'+str(len(list(self.root.glob('*.html')))),raw)
                rows = self.proposed(record)
                if rows:
                    self.assertFalse(any(row['kind']=='declared_date' for row in self.verify(rows)['verified']))

    def test_actual_pinned_originals_have_compatible_complete_header_citations(self):
        repo = Path(__file__).resolve().parents[1]
        for index,path in enumerate(('parts/local-mirror/docs/MPLPB_Local_Web_v4.md',
                                     'parts/smart-local/docs/Smart_Local_MPLPB.txt',
                                     'docs/Combined_MPLPB.md')):
            with self.subTest(path=path):
                record = self.add('ORIGINAL-%04d'%index,(repo/path).read_text())
                rows = self.proposed(record)
                result = self.verify(rows)
                self.assertEqual(result['rejected'],[],result)
                self.assertEqual(result['verified'],rows)


if __name__=='__main__':
    unittest.main()
