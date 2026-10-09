import json
import tempfile
import unittest
from pathlib import Path
from tools.evaluate_grounded_chat import metrics,run,sha,validate,wilson
from tools.prepare_chat_review import packet

FIXTURE=Path(__file__).resolve().parents[1]/'evaluation/contextual/developer-cases.json'
class ContextEvaluationTests(unittest.TestCase):
    def test_wrong_hash_is_rejected(self):
        with self.assertRaisesRegex(ValueError,'hash mismatch'):run(FIXTURE,'0'*64)
    def test_metrics_penalize_refuse_everything(self):
        rows=[{'supported':True,'chat':{'answered':False,'correct_answer':False}},
              {'supported':False,'chat':{'answered':False,'correct_answer':False}}]
        m=metrics(rows,'chat');self.assertIsNone(m['supported_answer_precision'])
        self.assertEqual(m['answerable_coverage'],0);self.assertEqual(m['unnecessary_refusal_rate'],1)
        self.assertGreater(wilson(0,36)[1],0)
    def test_missing_labels_and_duplicate_ids_rejected(self):
        data=json.loads(FIXTURE.read_text());data['domains'][0]['probes'][0]['evidence']=[]
        with self.assertRaises(ValueError):validate(data)
        data=json.loads(FIXTURE.read_text());data['domains'][0]['probes'].append(data['domains'][0]['probes'][0])
        with self.assertRaises(ValueError):validate(data)
    def test_blind_packet_drops_labels_scopes_and_outputs(self):
        data=packet(FIXTURE,sha(FIXTURE),1)
        self.assertEqual(len(data['cases']),54)
        for case in data['cases']:
            self.assertNotIn('supported',case);self.assertNotIn('category',case)
            self.assertIsNone(case['review']['label'])
            self.assertTrue(all(set(p)=={'title','body'} for p in case['pages']))
    def test_changed_external_corpus_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'corpus').mkdir();(root/'corpus/page').write_text('changed')
            data={'schema':1,'domains':[{'name':'external','root':'corpus','corpus_sha256':{'page':'0'*64},'probes':[{'id':'one','topic':'Page','question':'Who may use it?','supported':False,'rationale':'Absent'}]}]}
            p=root/'manifest.json';p.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError,'bytes changed'):run(p,sha(p))
