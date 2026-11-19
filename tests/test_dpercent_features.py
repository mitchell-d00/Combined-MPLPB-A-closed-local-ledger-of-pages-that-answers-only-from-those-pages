"""Roll-cohort tooling tests; synthetic scores here are not experiment results."""
from pathlib import Path
import tempfile
import unittest
from tools import dpercent as study
from tools.dpercent_features import analyze


class FeatureCohortTests(unittest.TestCase):
    def test_replays_exact_seal_and_reports_both_denominators_without_names(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);public=root/'public';private=root/'private'
            study.prepare(public,private,count=62,seed=8751)
            key=study.read(private/'key.json')['cases']
            rows=[{'id':k['id'],'family':k['family'],'expected':k['expected'],
                   'execution':'completed','outcome':'over_refusal' if k['expected']=='answer' else 'appropriate_refusal'} for k in key]
            study.save(root/'score.json',{'cases':rows})
            result=analyze(public,private,root/'score.json',root/'features.json')
            self.assertTrue(result['roll_replay_verified']);self.assertEqual(len(result['cases']),62)
            for row in result['cases']:
                self.assertNotIn('actor',row['features']);self.assertNotIn('expected',row['features'])
                self.assertNotIn('subject',row['features'])
            for cohort in result['by_feature']['family'].values():
                self.assertEqual(cohort['cases'],2)
                if cohort['answer_cases']:self.assertEqual(cohort['missed_complete_answer_rate'],1)
                if cohort['refuse_cases']:self.assertEqual(cohort['false_alarm_rate'],0)
            rows[0]['expected']='invalid';(root/'score.json').unlink();study.save(root/'score.json',{'cases':rows})
            with self.assertRaisesRegex(ValueError,'labels differ'):
                analyze(public,private,root/'score.json',root/'bad.json')
