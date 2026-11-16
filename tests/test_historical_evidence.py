"""Bounded documentary extraction; original pinned papers remain unchanged."""
import hashlib
import html
import json
from pathlib import Path
import unittest

from mplpb_work.historical_evidence import extract, FIELDS
from mplpb_answers.body_text import body_text


class HistoricalEvidenceTests(unittest.TestCase):
    def assert_spans(self, body, observations):
        for observation in observations:
            self.assertEqual(set(observation), set(FIELDS))
            self.assertEqual(body[observation['start']:observation['end']], observation['quote'])

    def test_generic_headers_and_typed_relations(self):
        body=('Document ID: ARCHIVE-CASE-101\nUpdated: 1850-05-01T12:00Z v5\n'
              'Supersedes: ARCHIVE-CASE-101 v4 (1849-01-01), v3 (1848-01-01)\n'
              'Related documents:\n\n- A ledger (ARCHIVE-LEDGER-202 v2)\n'
              '- A name without an identifier\n\nBack to: Index\n\n# Main text\n')
        observations=extract(body)
        self.assert_spans(body, observations)
        identity=next(o for o in observations if o['kind']=='document_identity')
        self.assertEqual((identity['value'],identity['target_version']),('ARCHIVE-CASE-101','v5'))
        self.assertEqual([o['value'] for o in observations if o['kind']=='declared_date'],['1850-05-01T12:00Z'])
        self.assertEqual([(o['target_id'],o['target_version']) for o in observations if o['kind']=='supersedes'],
                         [('ARCHIVE-CASE-101','v4'),('ARCHIVE-CASE-101','v3')])
        self.assertEqual([o['target_id'] for o in observations if o['kind']=='related'],['ARCHIVE-LEDGER-202'])

    def test_markdown_table_and_scoped_negative_are_preserved(self):
        body=('# A record\n| Document ID | NOTE-100 |\n| Updated | 1999-01-02 v3 |\n'
              '| Supersedes | NOTE-100 v2; NOTE-100 v1. No earlier paper or implementation is superseded. |\n'
              '**Related.** Companion (CASE-202 v7).\n\n## Abstract\nText\n')
        observations=extract(body)
        self.assert_spans(body,observations)
        self.assertEqual(len([o for o in observations if o['kind']=='not_superseded']),1)
        self.assertEqual(len([o for o in observations if o['kind']=='supersedes']),2)
        self.assertEqual(next(o for o in observations if o['kind']=='declared_date')['value'],'1999-01-02')
        self.assertEqual(next(o for o in observations if o['kind']=='related')['target_version'],'v7')

    def test_examples_body_discussion_and_fences_cannot_invent_headers(self):
        body=('Document ID: REAL-101\nUpdated: 2001-01-01 v1\n'
              '```text\nDocument ID: FAKE-999\nUpdated: 1800-01-01 v9\nRelated: FAKE-101 v1\n```\n'
              '## Body\nUpdated: 1700-01-01 v99\nRelated: FAKE-202 v2\n')
        observations=extract(body)
        self.assert_spans(body, observations)
        self.assertFalse(any('FAKE' in o['value'] for o in observations))
        self.assertEqual([o['value'] for o in observations if o['kind']=='declared_date'],['2001-01-01'])

    def test_unresolved_titles_and_negative_targets_are_not_guessed(self):
        body='Document ID: NOTE-101\nSupersedes: Does not supersede NOTE-202.\nRelated: An undated companion paper.\n'
        observations=extract(body)
        self.assertFalse(any(o['kind']=='supersedes' for o in observations))
        self.assertEqual(next(o for o in observations if o['kind']=='related')['target_id'],'')
        self.assertTrue(any(o['kind']=='not_superseded' for o in observations))

    def test_related_paragraph_and_list_do_not_swallow_later_mentions(self):
        for body in (
            'Document ID: NOTE-101\nRelated: CASE-202 v2.\n\nDiscussion mentions FAKE-999 v9.\n',
            'Document ID: NOTE-101\nRelated documents:\n- CASE-202 v2\n\nDiscussion mentions FAKE-999 v9.\n',
        ):
            observations=extract(body)
            self.assertEqual([o['target_id'] for o in observations if o['kind']=='related'],['CASE-202'])
            self.assertFalse(any('FAKE' in o['quote'] for o in observations))
        negative='Document ID: NOTE-101\nRelated: Not CASE-202 v2; unrelated to CASE-303 v3.\n'
        self.assertEqual([o['target_id'] for o in extract(negative) if o['kind']=='related'],[''])

    def test_real_original_headers_match_frozen_byte_pins(self):
        root=Path(__file__).resolve().parents[1]
        sources=json.loads((root/'docs/research/mplpb-originality/mplpb-sources.json').read_text())['sources']
        expectations={
            'local-web':('MPLPB-LOCAL-008','v4','2026-08-05T18:40Z'),
            'smart-paper':('MPLPB-SMART-011','v1','2026-08-12T00:00Z'),
            'combined-v3':('MPLPB-COMBINED-017','v3','2026-10-07T18:00Z'),
            'combined-v1':('MPLPB-COMBINED-017','v1','2026-10-07T00:00Z'),
        }
        for key,(identifier,version,date) in expectations.items():
            with self.subTest(source=key):
                raw=(root/sources[key]['path']).read_bytes()
                self.assertEqual(hashlib.sha256(raw).hexdigest(),sources[key]['sha256'])
                body=raw.decode()
                observations=extract(body)
                self.assert_spans(body, observations)
                identities=[o for o in observations if o['kind']=='document_identity']
                self.assertEqual([(o['value'],o['target_version']) for o in identities],[(identifier,version)])
                self.assertEqual([o['value'] for o in observations if o['kind']=='declared_date'],[date])
                if key=='local-web':
                    self.assertEqual([o['target_version'] for o in observations if o['kind']=='supersedes'],['v3','v2','v1'])
                if key=='combined-v3':
                    self.assertTrue(any(o['kind']=='not_superseded' for o in observations))
                    self.assertTrue(any(o['kind']=='related' and o['target_id']=='MPLPB-LOCAL-008' and o['target_version']=='v4'
                                        for o in observations))
                # The actual ledger body projection normalizes the Smart paper's
                # fixed-width table separators; its identity must still resolve.
                projected=body_text('<pre>'+html.escape(body)+'</pre>')
                projected_observations=extract(projected)
                self.assert_spans(projected, projected_observations)
                self.assertEqual([(o['value'],o['target_version']) for o in projected_observations
                                  if o['kind']=='document_identity'],[(identifier,version)])
                self.assertEqual([o['value'] for o in projected_observations if o['kind']=='declared_date'],[date])
                if key=='local-web':
                    related=next(o for o in projected_observations if o['kind']=='related')
                    self.assertIn('Navigator, Spinning, and the deployed companion',related['quote'])

    def test_limits_and_changed_identifiers(self):
        body='Document ID: OTHER-777\nUpdated: 2001-01-01 v1\nRelated: OTHER-202 v2; OTHER-303 v3\n'
        self.assertEqual(len(extract(body,max_observations=2)),2)
        self.assertEqual(extract(body)[0]['value'],'OTHER-777')
        for value in (0,257,True):
            with self.assertRaises(ValueError): extract(body,value)
        with self.assertRaises(ValueError): extract(None)

    def test_impossible_dates_and_competing_header_versions_do_not_create_chronology(self):
        invalid='Document ID: NOTE-101\nUpdated: 2001-02-30 v1\n'
        self.assertFalse(any(o['kind']=='declared_date' for o in extract(invalid)))
        body='Document ID: NOTE-101\nUpdated: 2001-01-01 v1\nUpdated: 2002-01-01 v2\n'
        observations=extract(body)
        self.assertEqual(next(o for o in observations if o['kind']=='document_identity')['target_version'],'')
        self.assertEqual([o['target_version'] for o in observations if o['kind']=='declared_date'],['v1','v2'])
        unrelated='Document ID: NOTE-101\nUpdated: 2001-01-01; cites earlier v9\n'
        self.assertEqual(next(o for o in extract(unrelated) if o['kind']=='document_identity')['target_version'],'')


if __name__=='__main__':
    unittest.main()
