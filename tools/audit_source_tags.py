"""Audit sealed source-tag inputs, custody, raw outputs and once-only receipts."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
HOME=ROOT/'evaluation/source-tags/2026-11-25'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def snapshot(root):
    result={}
    for p in sorted(root.rglob('*')):
        if p.is_symlink():raise ValueError('Symlinked frozen input')
        if p.is_file():result[str(p.relative_to(root))]=sha(p)
    return result

def audit(require_fresh=False):
    frozen=read(HOME/'harness-freeze.json')
    names={'design.json':'proposal.json','generate.py':'frozen-tools/generate.py',
           'source_tags_trial.py':'frozen-tools/source_tags_trial_initial.py',
           'source_tags_worker.py':'frozen-tools/source_tags_worker.py',
           'dev/manifest.json':'development/manifest.json','dev/key.json':'development/key.json',
           'dev/seal.json':'development/seal.json'}
    for name,expected in frozen['files'].items():assert sha(HOME/names[name])==expected,name
    version2=read(HOME/'scorer-freeze-v2.json')
    assert sha(HOME/'frozen-tools/source_tags_trial.py')==version2['runner_sha256']
    assert sha(ROOT/'tools/source_tags_worker.py')==frozen['files']['source_tags_worker.py']
    portable=read(HOME/'portable-tools-amendment.json')
    for path,expected in portable['tools'].items():assert sha(ROOT/path)==expected,path
    manifest=read(HOME/'development/manifest.json');ids=[]
    for case in manifest['cases']:
        assert snapshot(HOME/'development/inputs'/case['id'])==case['files'];ids.append(case['id'])
    assert len(set(ids))==len(ids)==72
    for name in ['baseline','prototype-run']:
        run=read(HOME/name/'run.json');assert run['planned']==run['completed']==72
        assert {r['id'] for r in run['rows']}==set(ids)
        assert run['worker_sha256']==frozen['files']['source_tags_worker.py']
        assert not run['keys_mounted'] and not run['generator_or_scorer_mounted']
        for row in run['rows']:
            assert row['execution_status']=='completed'
            assert sha(HOME/name/row['id']/'result.json')==row['result_sha256']
    prototype=read(HOME/'prototype-run/run.json')
    assert sha(HOME/'prototype-source.py')==prototype['runtime_sha256']['mplpb_answers/source_tags.py']
    result={'development_inputs':72,'baseline_raw_supported':72,'baseline_tag_checks':'NOT_RUN',
            'frozen_worker_and_keys_unchanged':True,'prototype_tag_decisions':72,
            'prototype_recovered_answers':0,'fresh_transfer':'PENDING',
            'independent_historical_accuracy':'NOT_RUN','independent_semantic_adjudication':'NOT_RUN',
            'outside_custodian_scoring':'NOT_RUN','native_oocc':'NOT_RUN'}
    completion=HOME/'fresh-transfer/completion.json'
    if completion.exists():
        receipt=read(completion);score=read(HOME/'fresh-transfer/candidate-score.json')
        assert receipt['candidate_runs']==1 and receipt['native_fingerprints_unchanged_after_open']
        assert receipt['acceptance_passed'] and score['acceptance_passed']
        assert score['cases']==score['passed']==score['tag_checks_executed']==24
        assert score['wrong_tag_assignments']==0 and score['recovered_answers']==0
        result['fresh_transfer']='24/24 same-operator proposal decisions; zero answer recovery'
    elif require_fresh:raise ValueError('Fresh transfer has not completed')
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--require-fresh',action='store_true');a=p.parse_args()
    print(json.dumps(audit(a.require_fresh),indent=2))
