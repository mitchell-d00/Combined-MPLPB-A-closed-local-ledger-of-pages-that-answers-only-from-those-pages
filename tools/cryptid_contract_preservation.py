"""Exact whole-contract comparison for consumed Cryptid preservation cohorts."""
import argparse
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from tools.cryptid_trial import read,save,sha,digest
from tools.bubble_wrap_trial import normal


def main(a):
    before=read(a.before/'run.json');after=read(a.after/'run.json');assert before['registry_sha256']==after['registry_sha256']
    earlier={r['id']:r for r in before['cases']};rows=[]
    assert {r['id'] for r in after['cases']}==set(earlier)
    for row in after['cases']:
        ident=row['id'];old=earlier[ident];errors=[]
        if row['execution_status']!='completed' or old['execution_status']!='completed':errors.append('execution_not_completed')
        else:
            assert sha(a.before/ident/'result.json')==old['raw_sha256'] and sha(a.after/ident/'result.json')==row['raw_sha256']
            left=read(a.before/ident/'result.json')['answer'];right=read(a.after/ident/'result.json')['answer']
            if normal(left)!=normal(right):errors.append('claim_qualification_citation_or_outcome_changed')
        rows.append({'id':ident,'passed':not errors,'errors':errors,'input_hash':row['input_hash']})
    result={'schema':'cryptid-contract-preservation-v1','before_run_sha256':sha(a.before/'run.json'),'after_run_sha256':sha(a.after/'run.json'),'counts':{'planned':len(rows),'passed':sum(r['passed'] for r in rows),'failed':sum(not r['passed'] for r in rows)},'rows':rows,'meaning':'Exact contracts except recursive code_sha256 maps; no semantic target transitions are silently accepted.'}
    save(a.output,result);print(result['counts'])

if __name__=='__main__':
    p=argparse.ArgumentParser()
    for n in ('before','after','output'):p.add_argument('--'+n,type=Path,required=True)
    main(p.parse_args())
