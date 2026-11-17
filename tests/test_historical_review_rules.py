"""Synthetic truth fixtures exercise entry rules, never real historical truth."""
import copy
from pathlib import Path
import tempfile
import unittest
from mplpb_combined.ledger import write
from mplpb_work import WorkStore, WorkError, Denied
from mplpb_work.store import digest
from mplpb_work.model import OPERATIONS
from mplpb_work.historical_review import enter_review, inspect_reviews


class HistoricalReviewRuleTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
        self.rec=write(self.root/'corpus',doc_id='FIXTURE-1',title='Synthetic chronology',scope='fixture',body='The expedition was delayed because of rain.')
        self.store,self.host=WorkStore.create(self.root/'work',{'fixture':self.root/'corpus'},clock=lambda:1000)
        self.tokens={}
        for seat in ['author','reviewer-a','reviewer-b']:
            self.tokens[seat]=self.store.assign(self.host,seat=seat,instance=seat+'-1',model={'name':seat,'provider':'synthetic-fixture','version':'1','context_policy_hash':'unknown'},contract={'operations':sorted(OPERATIONS),'tools':[],'scopes':['T1'],'share_with':['author','reviewer-a','reviewer-b'],'profile':'internal','expires_at':2000},expected_head=self.store.head(self.host)['hash'])['credential']
        self.put('T1','task',{'goal':'Synthetic test only','criteria':['review traceable'],'review_budget':8,'state':'open','acceptance':{}})
        self.put('E1','evidence',{'task':'T1','corpus':'fixture','source_id':self.rec.id,'source_hash':self.rec.hash_actual,'quote':'The expedition was delayed because of rain.','query':'expedition'})
        self.put('C1','claim',{'task':'T1','proposition':'The expedition was delayed because of rain.','basis':'observation','assessment':'proposed','assumptions':[],'alternatives':[],'revisit_when':'Any evidence changes'},{'E1':1})

    def put(self,id,kind,payload,deps=None):
        c=self.tokens['author'];return self.store.put(c,id=id,kind=kind,payload=payload,dependencies=deps or {},visibility=list(self.tokens),expected_revision=0,expected_head=self.store.snapshot(c)['head'])

    def entry(self,reviewer,**changes):
        e={'id':'R-'+reviewer,'claim_id':'C1','claim_revision':1,'reviewer_id':reviewer,'reviewer_kind':'synthetic_fixture','decision':'support','rationale':'Synthetic oracle fixture only; no real human participated.','independence_attestation':'Separate fixture seat; not real human independence.','evidence_ids':['E1'],'scope':'Synthetic expedition universe','uncertainties':['No real historical truth evaluated']}
        e.update(changes);return e

    def test_two_synthetic_reviewers_match_a_pinned_fixture_without_real_truth(self):
        for seat in ['reviewer-a','reviewer-b']:enter_review(self.store,self.tokens[seat],self.entry(seat))
        oracle={'universe':'synthetic-expedition-v1','proposition':'The expedition was delayed because of rain.','truth_value':True}
        r=inspect_reviews(self.store,self.tokens['author'],'C1',synthetic_oracle=oracle,oracle_sha256=digest(oracle))
        self.assertTrue(r['synthetic_fixture_truth_matches']);self.assertFalse(r['historical_truth_independently_verified'])
        self.assertFalse(r['answer_supported']);self.assertEqual(r['review_status'],'synthetic_fixture_reviewed')

    def test_wrong_or_tampered_oracle_does_not_pass(self):
        oracle={'universe':'synthetic-expedition-v1','proposition':'Different claim','truth_value':True}
        with self.assertRaises(WorkError):inspect_reviews(self.store,self.tokens['author'],'C1',synthetic_oracle=oracle,oracle_sha256=digest(oracle))

    def test_missing_review_information_is_rejected(self):
        for field in ['rationale','independence_attestation','scope']:
            with self.subTest(field=field),self.assertRaises(WorkError):
                enter_review(self.store,self.tokens['reviewer-a'],self.entry('reviewer-a',**{field:''}))

    def test_no_evidence_no_review_entry(self):
        with self.assertRaises(WorkError):enter_review(self.store,self.tokens['reviewer-a'],self.entry('reviewer-a',evidence_ids=[]))

    def test_stale_claim_revision_rejected(self):
        with self.assertRaises(WorkError):enter_review(self.store,self.tokens['reviewer-a'],self.entry('reviewer-a',claim_revision=2))

    def test_corruption_invalidates_the_review(self):
        enter_review(self.store,self.tokens['reviewer-a'],self.entry('reviewer-a'))
        p=self.root/'corpus'/self.rec.path;p.write_text(p.read_text().replace('rain','snow'))
        r=inspect_reviews(self.store,self.tokens['author'],'C1');self.assertEqual(r['review_status'],'needs_recheck')
        self.assertFalse(r['historical_truth_independently_verified'])

    def test_declared_human_is_not_automatically_authenticated(self):
        enter_review(self.store,self.tokens['reviewer-a'],self.entry('reviewer-a',reviewer_kind='human_declared'))
        r=inspect_reviews(self.store,self.tokens['author'],'C1');self.assertFalse(r['reviewer_identity_independently_verified'])
        self.assertFalse(r['historical_truth_independently_verified'])

    def test_bad_capability_is_rejected(self):
        with self.assertRaises(Denied):enter_review(self.store,'x'*40,self.entry('reviewer-a'))

    def test_synthetic_wrong_truth_value_fails_without_real_truth(self):
        for seat in ['reviewer-a','reviewer-b']:enter_review(self.store,self.tokens[seat],self.entry(seat))
        oracle={'universe':'synthetic-expedition-v1','proposition':'The expedition was delayed because of rain.','truth_value':False}
        r=inspect_reviews(self.store,self.tokens['author'],'C1',synthetic_oracle=oracle,oracle_sha256=digest(oracle))
        self.assertFalse(r['synthetic_fixture_truth_matches']);self.assertFalse(r['historical_truth_independently_verified'])

    def test_two_names_on_one_seat_are_not_two_reviewers(self):
        enter_review(self.store,self.tokens['reviewer-a'],self.entry('reviewer-a'))
        enter_review(self.store,self.tokens['reviewer-a'],self.entry('reviewer-b'))
        r=inspect_reviews(self.store,self.tokens['author'],'C1');self.assertNotEqual(r['review_status'],'synthetic_fixture_reviewed')

    def test_review_rule_is_exposed_through_existing_closed_work_api(self):
        from mplpb_work.api import request
        c=self.tokens['reviewer-a'];request(self.store,c,{'op':'historical_review','entry':self.entry('reviewer-a')})
        r=request(self.store,c,{'op':'historical_reviews','claim_id':'C1'})
        self.assertEqual(len(r['reviews']),1);self.assertFalse(r['answer_supported'])

    def test_plain_put_cannot_bypass_typed_review_rules(self):
        with self.assertRaises(WorkError):
            self.put('FAKE','review',{'task':'T1','target':{'C1':1},'target_variable':'synthetic truth',
                'regime':'historical-review-v1','finding':'{"historical_truth_independently_verified":true}',
                'outcome':'support','resolution':''},{'E1':1})
