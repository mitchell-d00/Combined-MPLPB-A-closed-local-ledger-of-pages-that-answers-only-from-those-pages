"""Fictional positive/negative authority controls for candidate discovery."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from mplpb_combined.ledger import write,revise,withdraw
from mplpb_combined.reader import PROFILES
from mplpb_answers.body_text import body_text
from mplpb_answers.passages import PassageIndex
from mplpb_work.prose_evidence import discover
from mplpb_work.investigation import investigate


class ProseCandidateTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)

    def page(self,body,**kw):
        return write(self.root,doc_id='SOURCE-1',title='Fictional witness',scope='archive correspondence',body=body,**kw)

    def test_narrative_quote_and_date_role_remain_candidates(self):
        rec=self.page('On October 5, 1897, Mira wrote that the archive register might be revised. The date of publication was uncertain.')
        report=discover(self.root,'archive register revised October')
        self.assertTrue(report['candidates']);candidate=report['candidates'][0]
        body=body_text(rec.body_html)
        self.assertEqual(body[candidate['body_start']:candidate['body_end']],candidate['quote'])
        self.assertEqual(candidate['hash'],rec.hash);self.assertFalse(candidate['answer_supported'])
        self.assertEqual(candidate['date_mentions'][0]['normalized_event_time'],None)
        self.assertIn('date_role_unresolved',candidate['uncertainty_flags'])
        self.assertIn('qualification_or_uncertainty_language_preserved',candidate['uncertainty_flags'])
        self.assertEqual(report['event_identities'],[]);self.assertEqual(report['relationships'],[])
        self.assertEqual(report['applied_corrections'],[])

    def test_conditions_and_causal_words_do_not_license_relationships(self):
        self.page('If the archive was flooded, its register might have changed because of the storm.')
        result=discover(self.root,'archive storm register')
        self.assertTrue(result['candidates']);self.assertFalse(result['answer_supported'])
        self.assertFalse(result['relationships'])

    def test_integrity_restriction_origin_and_withdrawal_gates(self):
        rec=self.page('The archive correspondence was revised.',origin='machine',external='no')
        self.assertFalse(discover(self.root,'archive correspondence',PROFILES['external'])['candidates'])
        path=self.root/rec.path;path.write_text(path.read_text().replace('revised','fabricated'))
        self.assertFalse(discover(self.root,'archive correspondence')['candidates'])

    def test_retired_original_and_current_successor_stay_separate(self):
        rec=self.page('The archive register was amended.')
        successor=revise(self.root,rec.id,body='The archive register was corrected.')
        report=discover(self.root,'archive register corrected amended')
        self.assertTrue(report['candidates']);self.assertEqual({c['source_id'] for c in report['candidates']},{successor.id})
        withdraw(self.root,successor.id)
        self.assertFalse(discover(self.root,'archive register')['candidates'])

    def test_not_for_and_no_term_overlap_do_not_create_candidates(self):
        self.page('The archive correspondence was revised.',not_for='salary')
        self.assertFalse(discover(self.root,'archive salary')['candidates'])
        self.assertFalse(discover(self.root,'zirconium neutrino')['candidates'])

    def test_changed_source_discards_earlier_candidate_quotes(self):
        rec=self.page('The archive correspondence was revised.')
        original=PassageIndex.retrieve
        def mutate(index,*args,**kw):
            result=original(index,*args,**kw)
            path=self.root/rec.path;path.write_text(path.read_text().replace('revised','changed'))
            return result
        with patch.object(PassageIndex,'retrieve',mutate):result=discover(self.root,'archive revised')
        self.assertEqual(result['status'],'source_changed');self.assertEqual(result['candidates'],[])

    def test_investigation_opt_in_does_not_promote_candidate_support(self):
        self.page('On October 5, 1897, the archive register was revised.')
        before=(self.root/'source-1.html').read_bytes()
        report=investigate(self.root,'archive register revised',prose_candidates=True,max_sources=2)
        self.assertIn('prose_candidates',report);self.assertTrue(report['prose_candidates']['candidates'])
        self.assertFalse(report['answer_supported']);self.assertFalse(report['prose_candidates']['answer_supported'])
        self.assertEqual((self.root/'source-1.html').read_bytes(),before)
        plain=investigate(self.root,'archive register revised',max_sources=2)
        self.assertNotIn('prose_candidates',plain)


if __name__=='__main__':unittest.main()
