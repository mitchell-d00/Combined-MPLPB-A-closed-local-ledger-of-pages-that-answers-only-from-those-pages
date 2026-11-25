"""Score proposal validation separately from answer support; keys stay outside."""
import argparse,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from tools.cryptid_trial import read,save,sha

def main(a):
 key=read(a.key);run=read(a.run/'run.json');rows=[]
 for row in run['cases']:
  raw=read(a.run/row['id']/'result.json');info=raw.get('source_structure_inspection',{});expected=key[row['id']]['structure_expected'];completed=info.get('status')=='completed';items=info.get('items',[])
  errors=[]
  if completed:
   if not items:errors.append('no_inspection')
   for item in items:
    v=item['verdict']
    if (v.get('status')=='accepted')!=expected:errors.append('wrong_structure_verdict')
    if v.get('source_support_established') is not False or v.get('authoritative') is not False:errors.append('structure_awarded_answer_authority')
  rows.append({'id':row['id'],'execution_status':'completed' if completed else 'NOT_RUN','scored':completed,'passed':completed and not errors,'errors':errors,'automatic_extraction_errors':sum(len(i.get('proposal',{}).get('extraction_errors',[])) for i in items),'nodes':sum(len(i.get('proposal',{}).get('nodes',[])) for i in items),'relations':sum(len(i.get('proposal',{}).get('relations',[])) for i in items),'wall_seconds':info.get('wall_seconds'),'cpu_seconds':info.get('cpu_seconds')})
 result={'schema':'cryptid-structure-score-v1','scorer_sha256':sha(Path(__file__)),'key_sha256':sha(a.key),'run_sha256':sha(a.run/'run.json'),'counts':{'planned':len(rows),'attempted':sum(r['scored'] for r in rows),'completed':sum(r['scored'] for r in rows),'passed':sum(r['passed'] for r in rows),'not_run':sum(not r['scored'] for r in rows),'unscored':sum(not r['scored'] for r in rows),'automatic_extraction_errors':sum(r['automatic_extraction_errors'] for r in rows)},'cases':rows,'meaning':'Structural validity, not answer coverage or independent classification accuracy; same-operator key.'};save(a.output,result);print(result['counts'])
if __name__=='__main__':
 p=argparse.ArgumentParser()
 for n in ['key','run','output']:p.add_argument('--'+n,type=Path,required=True)
 main(p.parse_args())
