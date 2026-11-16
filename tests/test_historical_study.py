"""Study protocol controls; these fixtures do not constitute human validation."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from tools import historical_study as S


class HistoricalStudyTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.directory=Path(self.tmp.name)/'study'
        S.prepare(self.directory)
        self.questions=Path(self.tmp.name)/'external-questions.json'
        S.save(self.questions,{'cases':[{'id':'Q1','question':'Trace declared Local Web relationships',
                                       'required_source_ids':['ORIGINAL-0001']}]})

    def sealed(self):S.seal(self.directory,self.questions)

    def reviews(self):
        S.execute(self.directory)
        template=S.read(self.directory/'review-template.json')
        paths=[]
        for n in (1,2):
            review=copy.deepcopy(template);review['reviewer_id']='fixture-reviewer-'+str(n)
            case=review['cases'][0];case.update(complete=False,false_bridge=False,source_accurate=True,
                labeling_seconds=3,correction_seconds=0,rationale='Specified test judgment; no human participant')
            path=Path(self.tmp.name)/('review-%d.json'%n);S.save(path,review);paths.append(path)
        return paths

    def test_originals_are_pinned_and_preparation_does_not_claim_independence(self):
        corpus=S.read(self.directory/'corpus.json')
        self.assertEqual(len(S.validate_corpus(corpus)),4)
        self.assertFalse(corpus['independence_verified'])
        self.assertEqual(corpus['status'],'awaiting_external_questions')
        with self.assertRaises(FileExistsError):S.prepare(self.directory)

    def test_gold_excluded_from_runtime_and_source_tampering_rejected(self):
        self.sealed();runtime=S.read(self.directory/'runtime-questions.json')
        self.assertEqual(set(runtime[0]),{'id','question'})
        gold=S.read(self.directory/'private/gold.json');receipt=S.read(self.directory/'seal.json')
        self.assertEqual(len(gold['salt']),64)
        self.assertNotIn(gold['salt'],json.dumps(receipt))
        self.assertNotEqual(S.digest(gold['cases']),receipt['gold_sha256'])
        corpus=S.read(self.directory/'corpus.json');corpus['sources'][0]['text']+='tampered'
        (self.directory/'corpus.json').write_text(json.dumps(corpus))
        with self.assertRaises(ValueError):S.execute(self.directory)

    def test_question_tampering_and_code_changes_rejected(self):
        self.sealed()
        path=self.directory/'runtime-questions.json';questions=S.read(path);questions[0]['question']='Changed'
        path.write_text(json.dumps(questions))
        with self.assertRaises(ValueError):S.execute(self.directory)

    def test_empty_or_duplicate_question_manifest_rejected(self):
        self.questions.write_text(json.dumps({'cases':[]}))
        with self.assertRaises(ValueError):self.sealed()

    def test_execution_does_not_need_access_to_private_gold(self):
        self.sealed()
        private=self.directory/'private';outside=Path(self.tmp.name)/'custodian-only'
        private.rename(outside)
        result=S.execute(self.directory)
        self.assertEqual(result['status'],'awaiting_external_review')
        self.assertFalse(result['independence_verified'])
        self.assertNotIn('required_source_ids',json.dumps(S.read(self.directory/'runtime-questions.json')))

    def test_implementation_pin_change_stops_before_execution(self):
        self.sealed()
        with patch.object(S,'implementation_pins',return_value={}):
            with self.assertRaises(ValueError):S.execute(self.directory)
        self.assertFalse((self.directory/'run.json').exists())

    def test_blank_reviews_cannot_be_scored_as_success(self):
        self.sealed();S.execute(self.directory)
        with self.assertRaises(ValueError):S.score(self.directory,[self.directory/'review-template.json']*2)

    def test_agreement_does_not_attest_independence_or_historical_truth(self):
        self.sealed();paths=self.reviews();score=S.score(self.directory,paths)
        self.assertEqual(score['status'],'review_submissions_agree')
        self.assertFalse(score['independence_verified']);self.assertFalse(score['reviewer_identity_attested'])
        self.assertEqual(score['reviewer_reported_labeling_seconds'],6)

    def test_disagreements_require_adjudication_and_fake_citations_rejected(self):
        self.sealed();paths=self.reviews();review=S.read(paths[1]);review['cases'][0]['false_bridge']=True
        paths[1].write_text(json.dumps(review));score=S.score(self.directory,paths)
        self.assertEqual(score['status'],'adjudication_required')
        (self.directory/'score.json').unlink()
        review['cases'][0]['citations']=[{'source_id':'ORIGINAL-0001','start':0,'end':4,'quote':'fake'}]
        paths[1].write_text(json.dumps(review))
        with self.assertRaises(ValueError):S.score(self.directory,paths)

    def test_duplicate_reviewer_identity_is_not_independent_review(self):
        self.sealed();paths=self.reviews();review=S.read(paths[1]);review['reviewer_id']='fixture-reviewer-1'
        paths[1].write_text(json.dumps(review))
        with self.assertRaises(ValueError):S.score(self.directory,paths)


if __name__=='__main__':unittest.main()
