"""Resource, completeness and limiter visibility, separate from claim scores."""
import argparse,sys,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from tools.cryptid_trial import read,save,sha

def main(a):
 key=read(a.key);run=read(a.run/'run.json');rows=[]
 for entry in run['cases']:
  ident=entry['id'];k=key[ident];completed=entry['execution_status']=='completed'
  if not completed:rows.append({'id':ident,'execution_status':entry['execution_status'],'scored':False,'passed':False});continue
  p=a.run/ident/'result.json';assert sha(p)==entry['raw_sha256'];r=read(p);answer=r['answer'];support=answer.get('documentary_support',{});code=answer['diagnostic']['code'];errors=[]
  phrase=support.get('unparsed_relevant_units',[])
  if k['require_visible_phrase_stop'] and not ('phrase' in code and 'budget' in code or any(u.get('reason')=='statement_phrase_budget' for u in phrase)):errors.append('phrase_budget_not_disclosed')
  if k['counterevidence_present'] and answer['answer_supported']:errors.append('counterevidence_silently_completed')
  rows.append({'id':ident,'execution_status':'completed','scored':True,'passed':not errors,'errors':errors,'kind':answer['kind'],'source_answerable_without_caps':k['source_answerable_without_caps'],'fixed_cap_positive_miss':k['source_answerable_without_caps'] and not answer['answer_supported'],'expected_limiter':k['expected_limiter'],'native_diagnostic':code,'native_budget_disclosed':'budget' in code or bool(phrase),'proof_complete':answer['kind'] in {'supported_answer','conflict'},'counterevidence_present':k['counterevidence_present'],'measurements':r.get('measurements',{}),'available_discovery_passages':len(r.get('discovery',{}).get('passages',[]))})
 counts={'planned':len(rows),'attempted':len(rows),'completed':sum(r['scored'] for r in rows),'passed':sum(r['passed'] for r in rows),'failed':sum(r['scored'] and not r['passed'] for r in rows),'unscored':sum(not r['scored'] for r in rows),'source_answerable_positives':sum(r.get('source_answerable_without_caps',False) for r in rows),'fixed_cap_positive_misses':sum(r.get('fixed_cap_positive_miss',False) for r in rows),'native_budget_stops':sum(r.get('native_budget_disclosed',False) for r in rows)}
 save(a.output,{'schema':'cryptid-resource-score-v1','scorer_sha256':sha(Path(__file__)),'run_sha256':sha(a.run/'run.json'),'key_sha256':sha(a.key),'counts':counts,'rows':rows,'custody':'Same operator. Expected resource visibility frozen before repair; semantic decisions separately scored.','limits_changed':False,'source_reads':'Python audit open calls; not all in-memory reads or operating-system byte measurements.'});print(counts)
 if counts['failed'] or counts['unscored']:raise SystemExit(2)
if __name__=='__main__':
 p=argparse.ArgumentParser()
 for n in ['key','run','output']:p.add_argument('--'+n,type=Path,required=True)
 main(p.parse_args())
