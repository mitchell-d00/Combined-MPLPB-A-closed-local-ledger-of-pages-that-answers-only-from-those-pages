"""Companion boundary checks;reads frozen packets/native ledgers,never operator-key."""
import argparse
import hashlib
import json
from pathlib import Path
import resource
import subprocess
import sys
import time


def snapshot(root):
 return {p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(root.rglob('*')) if p.is_file() and '__pycache__' not in p.parts}


def main():
 p=argparse.ArgumentParser();p.add_argument('--mplpb-root',type=Path,required=True);p.add_argument('--batch',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
 root=a.mplpb_root.resolve();batch=a.batch.resolve();out=a.out.resolve();out.mkdir(parents=True,exist_ok=False);sys.path.insert(0,str(root))
 from mplpb_work import sorter_v2 as sorter,sorter_explorer as view
 from mplpb_answers.pipeline import answer_query
 from mplpb_combined.reader import PROFILES
 assert not subprocess.check_output(['git','-C',str(root),'status','--porcelain'])
 freeze=json.loads((batch/'freeze.json').read_text());assert subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],text=True).strip()==freeze['revision']
 before_packets=snapshot(batch/'packets');assert before_packets==freeze['packet_hashes']
 users=[];cases=[];start=time.perf_counter();cpu=time.process_time()
 for taskpath in sorted((batch/'packets').glob('*/*/tasks.json')):
  user=taskpath.parent.relative_to(batch/'packets');tasks=json.loads(taskpath.read_text());dump=taskpath.parent/'dump/processed';ledger=batch/'run'/user/'ledger'
  if not ledger.is_dir():raise ValueError('Run native B-Tests first:'+str(user))
  target=out/user;target.mkdir(parents=True);before_ledger=snapshot(ledger)
  graphs={mode:sorter.sort_directory(dump,mode) for mode in ('not-compared','compare')}
  views={mode:view.label_graph(g,dump) for mode,g in graphs.items()}
  assert graphs['not-compared']['sources']==graphs['compare']['sources']
  assert graphs['not-compared']['nodes']==graphs['compare']['nodes']
  assert views['not-compared']['node_labels']==views['compare']['node_labels']
  for mode,v in views.items():
   assert not v['answer_supported']
   for label in v['node_labels']+v['edge_labels']:
    assert all(label[k] is False for k in ('answer_supported','source_support_established','entity_identity_established','event_identity_established','historical_truth_independently_verified'))
   (target/(mode+'-view.json')).write_text(json.dumps(v,ensure_ascii=False)+'\n')
  for task in tasks['cases']:
   profile=tasks['characteristics']['profile'];question=task['question'];baseline=answer_query(ledger,question,PROFILES[profile]).contract
   r=view.explore_ideas(question,dump=dump,ledger=ledger,profile=profile)
   assert r['native_mplpb']['result']==baseline
   assert all(r[k] is False for k in ('answer_supported','source_support_established','entity_identity_established','event_identity_established','historical_truth_independently_verified'))
   assert r['strict_slots_consumed_by_exploration']==0 and r['model']['status']=='disabled'
   for segment in r['segments']:
    assert not segment['answer_supported'] and not segment['source_support_established']
    assert segment['kind']=='source_quote'
   if profile=='external':assert r['dump_withheld'] and all(p['origin']!='dump' for p in r['passages'])
   limits=r['retrieval_limits']
   if limits:assert limits.get('displayed_passages',0)<=8 and limits.get('display_characters',0)<=12000
   row={'user':user.as_posix(),'case_id':task['id'],'profile':profile,'status':'PASS','native_kind':baseline['kind'],'native_answer_supported':baseline['answer_supported'],'native_unchanged':True}
   cases.append(row);(target/(task['id']+'-ideas.json')).write_text(json.dumps(r,ensure_ascii=False)+'\n');print(row['user'],row['case_id'],'PASS',flush=True)
  assert snapshot(ledger)==before_ledger
  users.append({'user':user.as_posix(),'status':'PASS','nodes_identical':True,'node_labels_identical':True,'ledger_unchanged':True})
  (out/'partial.json').write_text(json.dumps({'users':users,'cases':cases},indent=2)+'\n')
 assert snapshot(batch/'packets')==before_packets
 assert not subprocess.check_output(['git','-C',str(root),'status','--porcelain'])
 result={'schema':'d100-exploration-companion-v1','mplpb_revision':freeze['revision'],'seed':freeze['seed'],'users':users,'cases':cases,'passed_users':len(users),'passed_cases':len(cases),'model_calls':0,'wall_seconds':time.perf_counter()-start,'cpu_seconds':time.process_time()-cpu,'peak_rss_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,'operator_key_read_by_companion':False,'historical_accuracy':None,'model_semantic_accuracy':None,'human_review_seconds':None,'scope':'Same fictional d100 packets;derived labels,source/ledger immutability,profile gates and native-result isolation only.'}
 assert len(users)==25 and len(cases)==100
 (out/'summary.json').write_text(json.dumps(result,indent=2)+'\n')


if __name__=='__main__':main()
