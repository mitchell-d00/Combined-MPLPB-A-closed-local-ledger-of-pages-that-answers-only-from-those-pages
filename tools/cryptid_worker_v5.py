"""Execution-only frozen worker; no expectations, generator, scorer or Git."""
import json
from pathlib import Path
import resource
import sys
import time


def execute():
    resource.setrlimit(resource.RLIMIT_CPU,(30,30));resource.setrlimit(resource.RLIMIT_FSIZE,(8*1024**2,8*1024**2))
    from mplpb_combined.ledger import write,withdraw
    from mplpb_combined.reader import PROFILES
    from mplpb_answers.body_text import body_text
    from mplpb_answers.pipeline import answer_query
    from mplpb_answers.passages import PassageIndex
    from mplpb_answers.documentary import plan
    from mplpb_answers.frames import parse
    from tools.pole_worker import snapshot
    inputs,ledger=Path('/study'),Path('/scratch/ledger');case=json.loads((inputs/'case.json').read_text())
    if case.get('adapter_mode')!='documentary':
        from tools.pole_worker import execute as legacy_execute
        return legacy_execute(inputs,ledger,Path('/output/result.json'))
    record_objects=[];records=[];reads={'query':0,'discovery':0};phase=None
    def observe(event,args):
        if event=='open' and phase and isinstance(args[0],(str,bytes)):
            path=args[0].decode() if isinstance(args[0],bytes) else args[0]
            if path.startswith(str(ledger)+'/') and path.endswith('.html') and not (args[2]&3):reads[phase]+=1
    sys.addaudithook(observe)
    for s in case['sources']:
        r=write(ledger,doc_id=s['id'],title=s.get('title','Documentary original'),scope=s.get('scope','documentary evidence'),origin=s.get('origin','machine'),external=s.get('external','yes'),not_for=s.get('not_for',''),body_html=s['body_html'],when=s.get('when','2026-11-25T00:00Z'))
        if s.get('withdraw'):withdraw(ledger,s['id'],when='2026-11-25T00:00Z')
        if s.get('corrupt'):
            p=ledger/r.path;raw=p.read_bytes();old=s['corrupt']['old'].encode();new=s['corrupt']['new'].encode();assert old in raw and old!=new;p.write_bytes(raw.replace(old,new,1))
        record_objects.append(r)
        records.append({'id':r.id,'path':r.path,'hash':r.hash_actual,'body':body_text(r.body_html)})
    before=snapshot(ledger);profile=PROFILES[case.get('profile','internal')];b=case['budget'];question=case['question']
    frame=parse(question);inspection={'documentary_plan':plan(question),'finite_frame':frame.to_dict() if frame else None,'authority':False,'original_question':question}
    phase='query';wall,cpu=time.perf_counter(),time.process_time()
    answer=answer_query(ledger,question,profile,max_passages=b['passages'],max_chars=b['characters']).contract
    elapsed={'query_wall_seconds':time.perf_counter()-wall,'query_cpu_seconds':time.process_time()-cpu}
    phase='discovery'
    discovery=PassageIndex(ledger,question,profile).retrieve([question],b['passages'],b['characters'])
    phase=None
    assert before==snapshot(ledger),'Reader mutated ledger'
    result={'id':case['id'],'question':question,'records':records,'answer':answer,'interpretation_inspection':inspection,'discovery':discovery,
            'measurements':dict(elapsed,peak_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,source_html_open_calls=reads,source_read_measurement='Python audit open events for ledger HTML files during query/discovery; cached in-memory reads are not counted',admitted_source_count=len(records),admitted_canonical_characters=sum(len(r['body']) for r in records))}
    import importlib.util,copy
    inspection={'status':'unavailable','items':[],'source_support_established':False}
    if importlib.util.find_spec('mplpb_answers.source_structure') is not None:
        from mplpb_answers import source_structure
        sw,sc=time.perf_counter(),time.process_time()
        for r in record_objects:
            proposal=source_structure.propose(r);supplied=copy.deepcopy(proposal);mode=case.get('structure_mutation','none')
            people=[n for n in supplied.get('nodes',[]) if n.get('kind')=='person']
            nonroots=[n for n in supplied.get('nodes',[]) if n.get('kind')!='document']
            if mode=='private':supplied['private']=False
            elif mode=='famous':people[0]['famous']=True
            elif mode=='swapped_roles':people[0]['role'],people[1]['role']=people[1]['role'],people[0]['role']
            elif mode=='altered_span':nonroots[0]['body_start']+=1
            elif mode=='altered_original':nonroots[0]['original_start_byte']+=1
            elif mode=='stale_hash':supplied['source']['hash']='sha256:'+'0'*64
            elif mode=='wrong_kind':people[0]['kind']='object'
            elif mode=='forged_relation':supplied['relations'].append({'actor':'invented','authority':True})
            elif mode!='none':raise ValueError('Unknown public test mutation')
            verdict=source_structure.verify_proposals(ledger,question,supplied,profile)
            inspection['items'].append({'source_id':r.id,'proposal':proposal,'supplied':supplied,'mutation':mode,'verdict':verdict})
        inspection.update(status='completed',wall_seconds=time.perf_counter()-sw,cpu_seconds=time.process_time()-sc)
    result['source_structure_inspection']=inspection
    with Path('/output/result.json').open('x') as f:json.dump(result,f,ensure_ascii=False,allow_nan=False)

if __name__=='__main__':execute()
