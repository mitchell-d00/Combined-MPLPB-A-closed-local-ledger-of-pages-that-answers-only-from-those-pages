"""Exact preservation except previously frozen, fully checked positive recoveries.

The original scorer and its failures remain unchanged. This supplementary audit
joins exact input hashes to the frozen Mothman key and its full-claim scores.
Restricted original outputs never enter the public receipt.
"""
import argparse
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from tools.cryptid_trial import read,save,sha,digest
from tools.bubble_wrap_trial import normal


def audit(a):
    registry=read(ROOT/'evaluation/bubble-wrap/2026-11-25/continuation/development.json')
    old=ROOT/'evaluation/bubble-wrap/2026-11-25/runs/source-tags-preservation-zip'
    run=read(a.run/'run.json');dev=read(a.development/'run.json');scores=read(a.score)
    assert sha(a.development/'run.json')==scores['run_sha256']
    assert run['runtime_sha256']==dev['reader_files']
    scored={r['id']:r for r in scores['cases']}
    source=read(ROOT/'evaluation/cryptid/mothman/development/registry.json')
    targets={digest(r['files']):r for r in source['cases'] if r['origin'].get('historical_miss')}
    baseline_run=read(old/'run.json');baseline_rows={r['id']:r for r in baseline_run['rows']}
    records={r['id']:r for r in run['rows']};rows=[]
    for descriptor in registry['cases']:
        ident=descriptor['id'];record=records[ident];errors=[];recovered=False
        if record['execution_status']!='completed':
            rows.append({'id':ident,'execution_status':record['execution_status'],'errors':['execution failure'],'passed':False});continue
        result=read(a.run/ident/'result.json');answer=result['answer']
        assert sha(a.run/ident/'result.json')==record['result_sha256']
        prior_path=old/ident/'result.json'
        # Prior public release withheld restricted raw bytes; their native
        # full-contract hashes are still publicly pinned in score records.
        if prior_path.exists():
            before=read(prior_path)['answer'];equal=normal(before)==normal(answer)
        else:
            private_reference=ROOT/descriptor['original_output'];before=read(private_reference)['answer']
            equal=normal(before)==normal(answer)
        target=targets.get(digest(descriptor['files']))
        if not equal:
            if not target:errors.append('unapproved claim, qualification, citation or refusal change')
            else:
                target_id=target['id'];s=scored[target_id]
                checked=read(a.development/target_id/'result.json')['answer']
                if not s['passed'] or not checked['answer_supported'] or s.get('false_support'):errors.append('recovery not fully checked')
                if normal(checked)!=normal(answer):errors.append('recovery differs from exact frozen-input full claim/citation check')
                if before['claims'] or before['answer_supported']:errors.append('recovery changes prior valid support')
                recovered=not errors
        rows.append({'id':ident,'execution_status':'completed','passed':not errors,'unchanged_contract':equal,
                     'recovered_complete':recovered,'claims':len(answer['claims']), 'kind':answer['kind'],
                     'contract_sha256':digest(normal(answer)), 'private_output':not descriptor['public_raw_output'],
                     'raw_sha256':sha(a.run/ident/'result.json'),'errors':errors})
    result={'schema':'cryptid-preservation-audit-v1','baseline_release_reader':'2af8ba8442cfcc343cbca5fd7e5daba5e49228a5',
            'baseline_current_main':'c01021c0b9983f9a607fbe782dea7ed5872d1f11','baseline_equivalence':'Unchanged original runtime files except the explicit local candidate date-rule diff; prior release280contracts used verbatim.',
            'source_run_sha256':sha(a.run/'run.json'),'development_score_sha256':sha(a.score),
            'counts':{'planned':280,'completed':sum(r['execution_status']=='completed' for r in rows),'passed':sum(r['passed'] for r in rows),'unchanged':sum(r.get('unchanged_contract',False) for r in rows),'recovered_complete':sum(r.get('recovered_complete',False) for r in rows),'failed':sum(not r['passed'] for r in rows)},'rows':rows,
            'custody':'Same-operator external key and exact contract comparison. Independent adjudication NOT_RUN.'}
    save(a.output,result);print(json.dumps(result['counts']))

if __name__=='__main__':
    p=argparse.ArgumentParser()
    for n in ('run','development','score','output'):p.add_argument('--'+n,type=Path,required=True)
    audit(p.parse_args())
