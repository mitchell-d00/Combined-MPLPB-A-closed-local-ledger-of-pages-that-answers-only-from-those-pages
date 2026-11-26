"""Release preservation with separately checked frozen positive transitions.

No source/key relabelling. Every changed contract must equal the complete
contract already checked against a frozen semantic key for identical input bytes.
"""
import argparse
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from tools.cryptid_trial import read,save,sha,digest
from tools.bubble_wrap_trial import normal


def audit(a):
    registry=read(ROOT/'evaluation/bubble-wrap/2026-11-25/continuation/development.json')
    baseline=ROOT/'evaluation/bubble-wrap/2026-11-25/runs/source-tags-preservation-zip'
    current=read(a.run/'run.json');entries={r['id']:r for r in current['rows']};transitions={};evidence=[]
    for item in read(a.transitions):
        inputs=read(ROOT/item['registry']);run_path=ROOT/item['run'];run=read(run_path/'run.json');score_path=ROOT/item['score'];score=read(score_path)
        assert score['run_sha256']==sha(run_path/'run.json') and run['reader_files']==current['runtime_sha256']
        scores={r['id']:r for r in score['cases']}
        for case in inputs['cases']:
            s=scores[case['id']]
            if not s['passed'] or s.get('false_support'):continue
            result=read(run_path/case['id']/'result.json')
            if result['answer']['answer_supported']:
                transitions[digest(case['files'])]={'id':case['id'],'answer':result['answer'],'score_sha256':sha(score_path)}
        evidence.append({'registry':item['registry'],'run_sha256':sha(run_path/'run.json'),'score_sha256':sha(score_path)})
    rows=[]
    for case in registry['cases']:
        ident=case['id'];entry=entries[ident];errors=[];recovered=False;equal=False
        if entry['execution_status']!='completed':errors.append('execution_failed')
        else:
            raw=a.run/ident/'result.json';assert sha(raw)==entry['result_sha256'];after=read(raw)['answer']
            path=baseline/ident/'result.json';before=read(path if path.exists() else ROOT/case['original_output'])['answer']
            equal=normal(before)==normal(after)
            if not equal:
                target=transitions.get(digest(case['files']))
                if not target:errors.append('unapproved_contract_change')
                elif before['claims'] or before['answer_supported']:errors.append('prior_valid_support_changed')
                elif normal(target['answer'])!=normal(after):errors.append('changed_claim_differs_from_complete_frozen_key_check')
                else:recovered=True
        rows.append({'id':ident,'passed':not errors,'execution_status':entry['execution_status'],'unchanged_contract':equal,'recovered_complete':recovered,'errors':errors,'raw_output_sha256':entry.get('result_sha256'),'raw_output_public':case['public_raw_output']})
    counts={'planned':280,'completed':sum(r['execution_status']=='completed' for r in rows),'passed':sum(r['passed'] for r in rows),'unchanged':sum(r['unchanged_contract'] for r in rows),'recovered_complete':sum(r['recovered_complete'] for r in rows),'failed':sum(not r['passed'] for r in rows)}
    save(a.output,{'schema':'cryptid-release-preservation-v2','run_sha256':sha(a.run/'run.json'),'transitions_sha256':sha(a.transitions),'evidence':evidence,'counts':counts,'rows':rows,'custody':'Same-operator semantic keys and exact claim/qualification/citation comparison; independent adjudication NOT_RUN.'});print(counts)

if __name__=='__main__':
    p=argparse.ArgumentParser()
    for n in ('run','transitions','output'):p.add_argument('--'+n,type=Path,required=True)
    audit(p.parse_args())
