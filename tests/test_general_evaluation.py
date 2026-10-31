import copy
import unittest
from mplpb_answers.evaluation import seal_report, review_template, score, DEFAULT_POLICY
from mplpb_answers.evidence_contract import pin


class GeneralEvaluationTests(unittest.TestCase):
    def report(self,n=6,kind='model_assisted_answer',role='development'):
        rows=[{'id':str(i),'domain':['software','library','office'][i%3],'question':'Fixture',
               'answerability':'answerable','retrieval_recall':1,
               'answer':{'kind':kind,'answer_supported':kind=='supported_answer','confidence':0.9}} for i in range(n)]
        return seal_report({'role':role,'mode':'assisted','reader':{'live_inference':False},'rows':rows,
                            'release_policy':DEFAULT_POLICY,'release_policy_sha256':pin(DEFAULT_POLICY)})

    def reviewed(self,report):
        template=review_template(report);template['reviewers']=['development reviewer']
        for row in template['judgments']:
            row.update(correct=True,citation_complete=True,complete=True,reason='Specified development judgment')
        return template

    def test_six_correct_returns_do_not_certify_shipping(self):
        report=self.report(); result=score(report,self.reviewed(report))
        self.assertEqual(result['metrics']['reviewed_return_precision'],1)
        self.assertGreater(result['metrics']['assisted_error_upper95_wilson'],0.3)
        self.assertEqual(result['release_assessment'],'blocked')
        self.assertFalse(result['independence_verified'])

    def test_unreviewed_quotes_and_model_confidence_are_not_correctness(self):
        report=self.report(); result=score(report,review_template(report))
        self.assertIsNone(result['metrics']['reviewed_return_precision'])
        self.assertEqual(result['metrics']['unreviewed_returns'],6)
        self.assertEqual(result['metrics']['correct_complete_answers'],0)

    def test_partial_success_does_not_inflate_complete_question_coverage(self):
        report=self.report(kind='partial_answer'); review=self.reviewed(report)
        result=score(report,review)
        self.assertEqual(result['metrics']['reviewed_return_precision'],1)
        self.assertEqual(result['metrics']['complete_answerable_coverage'],0)

    def test_judgments_pin_exact_run_and_policy_cannot_move_after_answers(self):
        report=self.report(); review=self.reviewed(report)
        altered=copy.deepcopy(report); altered['rows'][0]['question']='Changed'
        with self.assertRaises(ValueError): score(altered,review)
        review['run_sha256']='sha256:'+'0'*64
        with self.assertRaises(ValueError): score(report,review)
        with self.assertRaises(ValueError): score(report,self.reviewed(report),dict(DEFAULT_POLICY,min_reviewed_returns=1))

    def test_many_strict_answers_cannot_certify_a_general_model_reader(self):
        report=self.report(n=210,kind='supported_answer',role='test')
        report['reader']['live_inference']=True
        report['calibration_run_sha256']='sha256:'+'1'*64
        report=seal_report(report)
        result=score(report,self.reviewed(report))
        self.assertEqual(result['metrics']['reviewed_assisted_returns'],0)
        self.assertEqual(result['release_assessment'],'blocked')

    def test_risk_curve_keeps_original_answerable_denominator(self):
        report=self.report(); review=self.reviewed(report)
        result=score(report,review)
        self.assertEqual(result['risk_coverage_curve'][-1]['complete_answerable_coverage'],0)
        self.assertEqual(result['risk_coverage_curve'][0]['complete_answerable_coverage'],1)

    def test_wrong_citations_count_as_wrong_returns(self):
        report=self.report(); review=self.reviewed(report)
        review['judgments'][0]['citation_complete']=False
        result=score(report,review)
        self.assertEqual(result['metrics']['wrong_reviewed_assisted_returns'],1)

    def test_duplicates_cannot_silently_replace_human_judgments(self):
        report=self.report(); review=self.reviewed(report)
        review['judgments'].append(dict(review['judgments'][0]))
        with self.assertRaises(ValueError):score(report,review)

    def test_evaluation_never_supplies_gold_labels_to_reader(self):
        from tools.evaluate_general_answers import run
        from tests.test_general_answers import FixtureReader
        reader=FixtureReader(outcome='abstain')
        report=run('evaluation/general-reader/development.json',reader,'assisted')
        data=str(reader.calls)
        self.assertNotIn('gold_passages',data)
        self.assertNotIn('answerability',data)
        self.assertFalse(report['independence_verified'])
        self.assertEqual(report['reader']['live_inference'],False)
        import tempfile
        from pathlib import Path
        from mplpb_answers.evaluate import main
        with tempfile.TemporaryDirectory() as folder:
            output=Path(folder)/'run.json'
            original=output.with_suffix('.review.json')
            original.write_text('KEEP HUMAN REVIEW')
            with self.assertRaises(FileExistsError):
                main(['run','evaluation/general-reader/development.json','--output',str(output)])
            self.assertEqual(original.read_text(),'KEEP HUMAN REVIEW')
            self.assertFalse(output.exists())

    def test_inline_corpus_runner_rejects_filesystem_paths(self):
        import hashlib,json,tempfile
        from pathlib import Path
        from tools.evaluate_general_answers import run
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'suite.json'
            suite={'schema':'mplpb-general-evaluation-v1','role':'development','cases':[{'id':'x','domain':'office','question':'Fixture?','answerability':'answerable','documents':[{'doc_id':'../../escape','title':'Fixture','scope':'fixture','body':'A fixture.'}]}]}
            path.write_text(json.dumps(suite));path.with_suffix('.json.sha256').write_text(hashlib.sha256(path.read_bytes()).hexdigest())
            with self.assertRaises(ValueError): run(path)
