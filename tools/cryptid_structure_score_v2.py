"""Score proposal validation separately from answer support; keys stay outside."""
import argparse,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from tools.cryptid_trial import read,save,sha

def main(a):
 key=read(a.key);run=read(a.run/'run.json');rows=[];registry=read(a.key.parent/'registry.json');descriptors={r['id']:r for r in registry['cases']}
 for row in run['cases']:
  raw=read(a.run/row['id']/'result.json');info=raw.get('source_structure_inspection',{});expected=key[row['id']]['structure_expected'];completed=info.get('status')=='completed';items=info.get('items',[])
  errors=[]
  if completed:
   if not items:errors.append('no_inspection')
   for item in items:
    v=item['verdict']
    if (v.get('status')=='accepted')!=expected:errors.append('wrong_structure_verdict')
    if v.get('source_support_established') is not False or v.get('authoritative') is not False:errors.append('structure_awarded_answer_authority')
  from tools.cryptid_trial import digest
  c=descriptors[row['id']];packet=(a.key.parent if c['packet'].startswith('inputs/') else ROOT)/c['packet'];native_input=read(packet/'case.json');native_input.pop('id',None);native_input.pop('structure_mutation',None)
  graph_targets=len(key[row['id']]['claims']);graphs_verified=0
  for expected_claim in key[row['id']]['claims']:
   proposition=expected_claim['proposition']
   for item in items:
    nodes={n['id']:n for n in item['proposal']['nodes']}
    def literal(ref):return nodes.get(ref,{}).get('quote')
    for relation in item['proposal']['relations']:
     if proposition['relation']=='source_action_assertion' and literal(relation.get('actor'))==proposition['actor_text'] and literal(relation.get('object'))==proposition['object_text'] and relation.get('action')==proposition['action'] and relation.get('negative')==proposition['negative']:graphs_verified+=1;break
     if proposition['relation']=='source_attributed_report_content' and literal(relation.get('reporter'))==proposition['reporter'] and literal(relation.get('actor'))==proposition['author'] and literal(relation.get('object'))==proposition['object']:graphs_verified+=1;break
  rows.append({'native_input_signature':digest(native_input),'expected_positive_graphs':graph_targets,'extracted_positive_graphs':min(graphs_verified,graph_targets),'graph_extraction_misses':max(0,graph_targets-graphs_verified),'id':row['id'],'execution_status':'completed' if completed else 'NOT_RUN','scored':completed,'passed':completed and not errors,'errors':errors,'automatic_extraction_errors':sum(len(i.get('proposal',{}).get('extraction_errors',[])) for i in items),'nodes':sum(len(i.get('proposal',{}).get('nodes',[])) for i in items),'relations':sum(len(i.get('proposal',{}).get('relations',[])) for i in items),'wall_seconds':info.get('wall_seconds'),'cpu_seconds':info.get('cpu_seconds')})
 result={'schema':'cryptid-structure-score-v2','scorer_sha256':sha(Path(__file__)),'key_sha256':sha(a.key),'run_sha256':sha(a.run/'run.json'),'counts':{'planned':len(rows),'attempted':sum(r['scored'] for r in rows),'completed':sum(r['scored'] for r in rows),'passed':sum(r['passed'] for r in rows),'not_run':sum(not r['scored'] for r in rows),'unscored':sum(not r['scored'] for r in rows),'automatic_extraction_errors':sum(r['automatic_extraction_errors'] for r in rows),'graph_extraction_misses':sum(r['graph_extraction_misses'] for r in rows),'unique_native_input_pairs':len({r['native_input_signature'] for r in rows}),'unique_positive_claim_inputs':len({r['native_input_signature'] for r in rows if r['expected_positive_graphs']})},'cases':rows,'meaning':'Proposal validation is separate from clause-graph extraction. Graph targets derived from unchanged preimplementation semantic keys; same-operator diagnostic, not independent classification or answer truth.'};save(a.output,result);print(result['counts'])
if __name__=='__main__':
 p=argparse.ArgumentParser()
 for n in ['key','run','output']:p.add_argument('--'+n,type=Path,required=True)
 main(p.parse_args())
