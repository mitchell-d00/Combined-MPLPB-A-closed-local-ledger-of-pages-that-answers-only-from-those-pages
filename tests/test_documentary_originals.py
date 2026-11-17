"""Development regressions on unchanged public originals; no blind accuracy claim."""
import json
from pathlib import Path
import tempfile
import unittest
from mplpb_answers.pipeline import answer_query
from tools.unprepared_sources import import_corpus
from tools.source_roundtrip import original_passage

ROOT=Path(__file__).resolve().parents[1]


class DocumentaryOriginalTests(unittest.TestCase):
    def inspect(self,relative,case_id,expected_kind='partial_answer'):
        corpus=ROOT/relative;temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup)
        ledger=Path(temp.name)/'ledger';receipt=import_corpus(corpus,ledger)
        question=next(c['question'] for c in json.loads((corpus/'questions.json').read_text())['cases'] if c['id']==case_id)
        r=answer_query(ledger,question).contract
        self.assertEqual(r['kind'],expected_kind)
        self.assertEqual(r['answer_supported'],expected_kind=='supported_answer')
        self.assertTrue(r['claims']);self.assertEqual(bool(r['missing']),expected_kind=='partial_answer')
        for claim in r['claims']:
            self.assertTrue(claim['source_support_established'])
            self.assertFalse(claim['historical_truth_independently_verified'])
            for evidence in claim['citations']:
                original=original_passage(corpus,receipt,evidence)
                self.assertTrue(original['round_trip_quote_fidelity']);self.assertFalse(original['semantic_relationship_verified'])
        return r

    def test_original_correspondence_gets_checked_instruction_not_delivery(self):
        r=self.inspect('evaluation/unprepared-originals/2026-11-16','H02',expected_kind='supported_answer')
        p=next(c['proposition'] for c in r['claims'] if c['proposition']['relation']=='source_reports_instruction')
        self.assertEqual(p['writer_text'],'CHARLES DARWIN');self.assertEqual(p['intermediary_text'],'Murray')
        self.assertEqual(p['addressee_text'],'A.R. WALLACE');self.assertEqual(p['condition_text'],'if possible')
        self.assertEqual(p['heading_date_text'],'November 13th, 1859');self.assertFalse(p['dispatch_verified']);self.assertFalse(p['receipt_verified'])
        self.assertEqual(p['question_completion_rule'],'document_local_arrangement_reference_v1')
        self.assertFalse(p['actual_arrangement_independently_verified'])
        self.assertEqual(len(r['claims'][0]['citations']),3)

    def test_original_appointment_keeps_referenced_role_and_comparison_unresolved(self):
        r=self.inspect('evaluation/unprepared-originals/2026-11-16-followup/unfamiliar','U01')
        p=next(c['proposition'] for c in r['claims'] if c['proposition']['action']=='appoint')
        self.assertEqual(p['actor_text'],'Roosevelt');self.assertIn('that position',p['object_text'])
        self.assertTrue(p['unresolved_reference']);self.assertIsNone(p['event_identity'])
        self.assertTrue(any('differ' in m for m in r['missing']))


if __name__=='__main__':unittest.main()
