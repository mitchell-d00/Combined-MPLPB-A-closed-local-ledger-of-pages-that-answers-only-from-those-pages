import copy
import json
from pathlib import Path
import tempfile
import unittest
from tools.archival_tutorial import build
from tools.benchmark_dashboard import row
from tools.blind_archival_packets import blind_output


class ArchivalOnboardingTests(unittest.TestCase):
    def test_tutorial_keeps_three_outcomes_and_originals(self):
        with tempfile.TemporaryDirectory() as tmp:
            r=build(Path(tmp)/'tutorial')
            self.assertEqual([a['kind'] for a in r['answers']],['supported_answer','clarify','abstain','supported_answer'])
            self.assertTrue(r['read_only_queries'])
            self.assertTrue(all(a['verification']['truth_verified'] is False for a in r['answers']))

    def score(self):
        return {'schema':'dpercent-v1-score','metrics':{'execution_failures':0,'unscored_supported':0,
            'answer_cases':2,'refuse_cases':1,'correct_complete_answers':1,'appropriate_refusals':1},'cases':[
            {'expected':'answer','outcome':'detected_answer','answer_supported':True,'quotation_fidelity':True},
            {'expected':'answer','outcome':'over_refusal','answer_supported':False},
            {'expected':'refuse','outcome':'appropriate_refusal','answer_supported':False}]}

    def dashboard(self,value):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'score.json';p.write_text(json.dumps(value));return row('test','revision',p,'synthetic_development')

    def test_denominators_and_failed_runs_do_not_hide_over_refusals(self):
        r=self.dashboard(self.score());self.assertEqual(r['metrics']['complete_answer_recall'],.5)
        self.assertEqual(r['metrics']['supported_answer_precision'],1)
        s=self.score();s['metrics']['execution_failures']=1
        self.assertTrue(all(v is None for v in self.dashboard(s)['metrics'].values()))

    def test_unscored_semantics_and_bad_citations_do_not_get_precision_credit(self):
        s=self.score();s['metrics']['unscored_supported']=1
        self.assertIsNone(self.dashboard(s)['metrics']['supported_answer_precision'])
        s=self.score();s['cases'][0]['quotation_fidelity']=False
        self.assertEqual(self.dashboard(s)['metrics']['citation_fidelity'],0)

    def test_inconsistent_denominators_are_rejected(self):
        s=self.score();s['metrics']['answer_cases']=8
        with self.assertRaises(ValueError):self.dashboard(s)

    def test_blinding_removes_implementation_hints_not_claim_meaning(self):
        a={'question':'Who wrote it?','code_sha256':{'kernel':'secret'},'trace':['revision'],
           'claims':[{'text':'No action occurred.','verification':'kernel-v11','proof_sha256':'secret','citations':[{'quote':'did not send'}]}],
           'verification':{'semantic':'kernel-v11','truth_verified':False,'independence_verified':False}}
        old=copy.deepcopy(a);r=blind_output(a)
        self.assertEqual(a,old);self.assertNotIn('code_sha256',r);self.assertNotIn('semantic',r['verification'])
        self.assertEqual(r['claims'][0]['text'],a['claims'][0]['text']);self.assertEqual(r['claims'][0]['citations'],a['claims'][0]['citations'])


if __name__=='__main__':unittest.main()
