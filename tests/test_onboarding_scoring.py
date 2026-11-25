"""Arithmetic controls only: these invented rows are not human observations."""
import unittest
from tools.score_onboarding_pilot import summarize

ASSIGN={'groups':{'new_path':['N'+str(i) for i in range(6)],'existing':['E'+str(i) for i in range(6)]}}

def synthetic_rows(new=5,old=3):
    return [{'participant_id':ident,'group':group,'first_time_user':True,'coached':False,
             'elapsed_seconds':599,'answer_and_citation':i<(new if group=='new_path' else old),
             'classification_correct':[True]*4+[False],
             'evidence_records':['SYNTHETIC_ARITHMETIC_CONTROL_ONLY'],
             'judgment_reasons':['SYNTHETIC_ARITHMETIC_CONTROL_ONLY']}
            for group,people in ASSIGN['groups'].items() for i,ident in enumerate(people)]

class OnboardingScoreTests(unittest.TestCase):
    def test_empty_is_not_run(self):self.assertIsNone(summarize([],ASSIGN)['acceptance_passed'])
    def test_exact_declared_threshold_passes(self):self.assertTrue(summarize(synthetic_rows(),ASSIGN)['acceptance_passed'])
    def test_one_person_advantage_fails(self):self.assertFalse(summarize(synthetic_rows(old=4),ASSIGN)['acceptance_passed'])
    def test_four_new_answer_successes_fail(self):self.assertFalse(summarize(synthetic_rows(new=4,old=2),ASSIGN)['acceptance_passed'])
    def test_partial_is_not_passed(self):self.assertIsNone(summarize(synthetic_rows()[:-1],ASSIGN)['acceptance_passed'])
    def test_coaching_cannot_pass(self):
        rows=synthetic_rows();rows[0]['coached']=True;self.assertFalse(summarize(rows,ASSIGN)['acceptance_passed'])
    def test_duplicate_participants_raise(self):
        rows=synthetic_rows();rows[-1]=rows[0]
        with self.assertRaises(ValueError):summarize(rows,ASSIGN)

if __name__=='__main__':unittest.main()
