"""Isolated source-tag comparison; host scores remain outside the worker."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile

# When retained under tools/, resolve from the repository rather than cwd.
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from tools import study_sandbox

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def save(p,v):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x') as f:json.dump(v,f,indent=2,ensure_ascii=False);f.write('\n')
def snapshot(root):
    result={}
    for p in sorted(root.rglob('*')):
        if p.is_symlink():raise ValueError('Symlinks are not admitted')
        if p.is_file():result[str(p.relative_to(root))]=sha(p)
    return result

def run(a):
    packet=a.packet.resolve();output=a.output.resolve();implementation=a.implementation.resolve()
    seal=read(packet/'seal.json');manifest=read(packet/'manifest.json')
    assert sha(packet/'manifest.json')==seal['manifest_sha256']
    output.mkdir(parents=True,exist_ok=False)
    worker=Path(__file__).with_name('source_tags_worker.py')
    frozen=read(ROOT/'evaluation/source-tags/2026-11-25/harness-freeze.json')
    assert sha(worker)==frozen['files']['source_tags_worker.py']
    native=[p for name in ['mplpb_answers','mplpb_combined','mplpb_work'] for p in sorted((implementation/name).glob('*.py'))]
    pins={str(p.relative_to(implementation)):sha(p) for p in native}
    rows=[]
    with tempfile.TemporaryDirectory(prefix='source-tags-') as temp:
        temp=Path(temp);code=temp/'code';code.mkdir()
        for p in native:
            dest=code/p.relative_to(implementation);dest.parent.mkdir(exist_ok=True);shutil.copyfile(p,dest)
        (code/'tools').mkdir();shutil.copyfile(worker,code/'tools/source_tags_worker.py')
        for case in manifest['cases']:
            ident=case['id'];source=packet/'inputs'/ident
            assert snapshot(source)==case['files']
            dest=output/ident;dest.mkdir();stage=temp/ident
            public=stage/'inputs';results=stage/'outputs';public.mkdir(parents=True);results.mkdir()
            for relative in case['files']:
                src=source/relative;src.resolve().relative_to(source)
                target=public/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,target)
            entry={'id':ident,'execution_status':'started'}
            try:
                args=study_sandbox.command(shutil.which('bwrap'),code,public,results,'from tools.source_tags_worker import execute; execute()')
                study_sandbox.invoke(args,transcript=dest,wall_seconds=45)
                assert set(snapshot(results))=={'result.json'}
                assert snapshot(public)==snapshot(source)==case['files']
                shutil.copyfile(results/'result.json',dest/'result.json')
                entry.update(execution_status='completed',result_sha256=sha(dest/'result.json'))
            except Exception as error:
                entry.update(execution_status='BLOCKED',error=str(error))
            rows.append(entry)
            shutil.rmtree(stage)
    assert pins=={str(p.relative_to(implementation)):sha(p) for p in native}
    receipt={'source_commit':a.source_commit,'runtime_sha256':pins,'worker_sha256':sha(worker),
             'manifest_sha256':sha(packet/'manifest.json'),'rows':rows,'planned':len(manifest['cases']),
             'completed':sum(r['execution_status']=='completed' for r in rows),'keys_mounted':False,
             'generator_or_scorer_mounted':False,'git_credentials_or_host_network_mounted':False,
             'same_operator':True,'independent_preparation':'NOT_RUN'}
    save(output/'run.json',receipt)
    print(json.dumps({'completed':receipt['completed'],'planned':receipt['planned']}))
    return int(receipt['completed']!=receipt['planned'])

def score(a):
    packet=a.packet.resolve();seal=read(packet/'seal.json')
    assert sha(packet/'key.json')==seal['key_sha256']
    keys={k['id']:k for k in read(packet/'key.json')};run=read(a.run/'run.json');rows=[]
    before={r['id']:r for r in read(a.baseline/'run.json')['rows']} if a.baseline else None
    for entry in run['rows']:
        ident=entry['id'];key=keys[ident];errors=[];tags_run=False;accepted=False
        if entry['execution_status']!='completed':errors.append('execution blocked; semantic outcome NOT_RUN')
        else:
            p=a.run/ident/'result.json';assert sha(p)==entry['result_sha256'];result=read(p)
            if result['raw_answer']['answer_supported']!=key['raw_supported']:errors.append('raw native support mismatch')
            tags=result['tag_validation'];tags_run=tags['status']!='API_UNAVAILABLE';accepted=tags['status']=='accepted'
            if tags_run and accepted!=key['tags_accepted']:errors.append('tag decision mismatch')
            if tags_run and tags.get('verified_relations') and not key['tags_accepted']:errors.append('invalid proposal received verified relation')
            if before:
                old=a.baseline/ident/'result.json';assert sha(old)==before[ident]['result_sha256']
                def normal(c):return {k:v for k,v in c.items() if k!='code_sha256'}
                if normal(read(old)['raw_answer'])!=normal(result['raw_answer']):errors.append('raw answer contract changed')
        rows.append({'id':ident,'errors':errors,'raw_supported':result['raw_answer']['answer_supported'] if entry['execution_status']=='completed' else None,
                     'tag_check_executed':tags_run,'tags_accepted':accepted if tags_run else None,
                     'tag_target':key['tags_accepted'],'result_sha256':entry.get('result_sha256')})
    result={'source_commit':run['source_commit'],'rows':rows,'cases':len(rows),'passed':sum(not r['errors'] for r in rows),
            'tag_checks_executed':sum(r['tag_check_executed'] for r in rows),'raw_supported':sum(r['raw_supported'] is True for r in rows),
            'valid_tags_accepted':sum(r['tags_accepted'] is True and r['tag_target'] for r in rows),
            'tampered_tags_rejected':sum(r['tags_accepted'] is False and not r['tag_target'] for r in rows),
            'wrong_tag_assignments':sum(r['tags_accepted'] is True and not r['tag_target'] for r in rows),
            'recovered_answers':0 if before and not any('raw answer contract changed' in r['errors'] for r in rows) else None,
            'acceptance_passed':not any(r['errors'] for r in rows) and all(r['tag_check_executed'] for r in rows),
            'independent_historical_accuracy':'NOT_RUN','independent_semantic_adjudication':'NOT_RUN','outside_custodian_scoring':'NOT_RUN','native_oocc':'NOT_RUN'}
    save(a.output,result);print(json.dumps({k:v for k,v in result.items() if k!='rows'}));return int(any(r['errors'] for r in rows))

if __name__=='__main__':
    p=argparse.ArgumentParser();sub=p.add_subparsers(dest='command',required=True)
    r=sub.add_parser('run')
    for name in ['packet','implementation','output']:r.add_argument('--'+name,type=Path,required=True)
    r.add_argument('--source-commit',required=True)
    s=sub.add_parser('score')
    for name in ['packet','run','output']:s.add_argument('--'+name,type=Path,required=True)
    s.add_argument('--baseline',type=Path)
    a=p.parse_args();raise SystemExit(run(a) if a.command=='run' else score(a))
