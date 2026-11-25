"""Accept a prior miss recovery only after unchanged-input full-key scoring.

Existing supported claims, missing obligations, qualifications and citations
must remain exactly equal. Raw failed equality comparisons remain retained.
"""
import argparse,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from tools.cryptid_trial import read,save,sha
from tools.bubble_wrap_trial import normal

def main(a):
 before=read(a.before/'run.json');after=read(a.after/'run.json');score=read(a.score)
 assert before['registry_sha256']==after['registry_sha256'] and score['run_sha256']==sha(a.after/'run.json')
 old={r['id']:r for r in before['cases']};scores={r['id']:r for r in score['cases']};rows=[]
 for r in after['cases']:
  ident=r['id'];b=old[ident];errors=[];recovered=None;equal=False
  assert b['input_hash']==r['input_hash']
  if b['execution_status']!='completed' or r['execution_status']!='completed':errors.append('execution_failed')
  else:
   leftpath=a.before/ident/'result.json';rightpath=a.after/ident/'result.json';assert sha(leftpath)==b['raw_sha256'] and sha(rightpath)==r['raw_sha256'];left=read(leftpath)['answer'];right=read(rightpath)['answer'];equal=normal(left)==normal(right)
   if not equal:
    if left['claims'] or left['answer_supported']:errors.append('prior_supported_contract_changed')
    elif not scores[ident]['passed'] or scores[ident].get('false_support') or not right['claims']:errors.append('new_contract_not_fully_key_checked')
    else:recovered=right['kind']
  rows.append({'id':ident,'passed':not errors,'unchanged':equal,'recovered':recovered,'errors':errors,'input_hash':r['input_hash']})
 counts={'planned':len(rows),'passed':sum(r['passed'] for r in rows),'unchanged':sum(r['unchanged'] for r in rows),'recovered_complete':sum(r['recovered']=='supported_answer' for r in rows),'recovered_checked_partial':sum(r['recovered']=='partial_answer' for r in rows),'recovered_conflict':sum(r['recovered']=='conflict' for r in rows),'failed':sum(not r['passed'] for r in rows)}
 save(a.output,{'schema':'cryptid-prior-adjudication-v1','scorer_sha256':sha(Path(__file__)),'before_run_sha256':sha(a.before/'run.json'),'after_run_sha256':sha(a.after/'run.json'),'frozen_key_score_sha256':sha(a.score),'counts':counts,'rows':rows,'meaning':'Same-operator source-key and exact contract review; no source/decision relabeling or independent semantic adjudication.'});print(counts)
 if counts['failed']:raise SystemExit(2)
if __name__=='__main__':
 p=argparse.ArgumentParser()
 for n in ['before','after','score','output']:p.add_argument('--'+n,type=Path,required=True)
 main(p.parse_args())
