import unittest
from tools import reduction as R

class ReductionTests(unittest.TestCase):
    def test_unique_after_constraints(self):
        chosen,trace=R.determine([{'id':'bad','basis':'conversation','failures':['Wrong intent']},
                                  {'id':'good','basis':'conversation'}],'chat')
        self.assertEqual(chosen['id'],'good');self.assertEqual(trace['outcome'],'unique')
        self.assertEqual(trace['eliminated'][0]['reasons'],['Wrong intent'])
        self.assertFalse(trace['elimination_creates_evidence'])
    def test_equivalent_variation_replays_and_ignores_input_order(self):
        choices=[{'id':'b','basis':'conversation','meaning':'greeting'}, {'id':'a','basis':'conversation','meaning':'greeting'}]
        first=R.determine(choices,'chat',2)
        self.assertEqual(first,R.determine(list(reversed(choices)),'chat',2))
        self.assertEqual(first[0]['id'],'b')
        self.assertEqual(first[1]['outcome'],'equivalent_wording_selected')
    def test_different_meanings_require_clarification(self):
        chosen,trace=R.determine([{'id':'one','basis':'procedure'},{'id':'two','basis':'procedure'}],'focus')
        self.assertIsNone(chosen);self.assertEqual(trace['outcome'],'clarify_or_present_alternatives')
    def test_focus_never_selects_conversation(self):
        chosen,trace=R.determine([{'id':'joke','basis':'conversation'}],'focus')
        self.assertIsNone(chosen);self.assertEqual(trace['outcome'],'no_eligible_candidate')
    def test_reduction_cannot_create_source_support(self):
        for candidate in ({'id':'claim','basis':'source_assertion','sources':[{'id':'x'}]},
                          {'id':'claim','basis':'source_assertion','support_checked':True},
                          {'id':'proof','basis':'deduction','support_checked':True,'premises':[{'quote':'x'}],'rules':['GUESS']}):
            self.assertIsNone(R.determine([candidate],'focus')[0])
    def test_explicit_deduction_contract(self):
        candidate={'id':'proof','basis':'deduction','support_checked':True,'premises':[{'id':'p','quote':'Fact: x | instance_of | y'}],'rules':['FACT-1','TYPE-2']}
        self.assertEqual(R.determine([candidate],'focus')[1]['basis'],'deduction')
        candidate['premises']=[];self.assertIsNone(R.determine([candidate],'focus')[0])
    def test_final_guard_preserves_conflicts_and_rejects_casual_focus(self):
        casual={'kind':'smalltalk','message':'a joke','context':{'title':'Moon'},'sources':[]}
        self.assertEqual(R.adjudicate(casual,'focus')['kind'],'unsupported')
        conflict={'kind':'conflict','message':'two competing values','sources':[]}
        self.assertEqual(R.adjudicate(conflict,'focus')['message'],'two competing values')
        self.assertEqual(conflict['determination']['basis'],'uncertainty')
    def test_focus_allows_explicit_nonfactual_conversation(self):
        result={'kind':'conversation','authority':'conversation_structure','sources':[],
                'response_structure':{'intent':'casual_echo','factual_claims':False}}
        self.assertEqual(R.adjudicate(result,'focus')['determination']['basis'],'conversation')
    def test_candidate_id_collision_fails(self):
        with self.assertRaises(ValueError):R.determine([{'id':'x'},{'id':'x'}],'chat')
