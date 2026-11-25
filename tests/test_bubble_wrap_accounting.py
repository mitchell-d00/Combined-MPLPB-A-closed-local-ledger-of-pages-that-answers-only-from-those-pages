"""BW-ACCOUNT: rejected misleading coverage, duplicate IDs and false PASS."""
import unittest
from tools.audit_bubble_wrap import audit_record


class BubbleWrapAccountingTests(unittest.TestCase):
    def record(self):
        return {'rows':[{'id':'BW-CASE','execution_status':'completed'}],
                'counts':{'planned':1,'attempted':1,'completed':1,'failed':0,'not_run':0,'scored':0,'unscored':1}}

    def test_unscored_completed_is_not_an_acceptance_pass(self):
        r=self.record();r['acceptance_passed']=True
        with self.assertRaises(ValueError):audit_record(r)

    def test_duplicate_id_is_not_an_extra_execution(self):
        r=self.record();r['rows']*=2
        with self.assertRaises(ValueError):audit_record(r)

    def test_missing_output_is_not_a_semantic_abstention(self):
        r=self.record();r['rows'][0]['execution_status']='BLOCKED_EXECUTION'
        with self.assertRaises(ValueError):audit_record(r)

    def test_correct_unscored_execution_is_visible(self):
        self.assertEqual(audit_record(self.record())['completed'],1)

    def test_planned_case_cannot_be_hidden_from_counts(self):
        r=self.record();r['rows'].append({'id':'BW-NEXT','execution_status':'NOT_RUN'})
        with self.assertRaises(ValueError):audit_record(r)


if __name__=='__main__':unittest.main()
