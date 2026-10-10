import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from tools.evaluate_ownership import evaluate
from tools.compare_ownership_predictions import compare

ROOT=Path(__file__).resolve().parents[1]/'evaluation'/'ownership'

class OwnershipEvaluationTests(unittest.TestCase):
    def test_frozen_results_reproduce(self):
        result=evaluate(ROOT/'rag-input.jsonl')
        self.assertEqual(result,json.loads((ROOT/'results.json').read_text()))
        self.assertEqual(result['summary']['n'],240)
        self.assertEqual(len(result['summary']['by_family']),12)
        # Known failures stay visible; this is a baseline, not an acceptance gate.
        self.assertEqual(result['summary']['arms']['ledger']['wrong_ownership'],180)

    def test_external_oracle_and_wrong_returns(self):
        cases=[json.loads(x) for x in (ROOT/'rag-input.jsonl').read_text().splitlines()]
        data=dict(system='scorer-test-only',model_revision='none',retriever='oracle',
                  prompt_sha256='test',input_sha256=hashlib.sha256((ROOT/'rag-input.jsonl').read_bytes()).hexdigest(),
                  predictions=[dict(id=c['id'],kind=c['expected'],source_ids=c['acceptable_ids']) for c in cases])
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'predictions.json';p.write_text(json.dumps(data))
            self.assertEqual(compare(ROOT/'rag-input.jsonl',p)['correct'],240)
            data['predictions'][0].update(kind='return',source_ids=['NONEXISTENT'])
            p.write_text(json.dumps(data))
            self.assertEqual(compare(ROOT/'rag-input.jsonl',p)['wrong_ownership'],1)

    def test_missing_predictions_and_wrong_input_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'predictions.json'
            data=dict(system='test',model_revision='none',retriever='none',prompt_sha256='test',
                      input_sha256='wrong',predictions=[])
            p.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError,'hash mismatch'):compare(ROOT/'rag-input.jsonl',p)
            data['input_sha256']=hashlib.sha256((ROOT/'rag-input.jsonl').read_bytes()).hexdigest()
            p.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError,'every unique case'):compare(ROOT/'rag-input.jsonl',p)
