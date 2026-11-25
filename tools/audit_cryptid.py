"""Audit Cryptid seals, source overlap and distinct execution/scoring accounting."""
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
def load(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=False).encode()).hexdigest()

def audit():
    home=ROOT/'evaluation/cryptid';programme=load(home/'programme.json');cases={};overlap=defaultdict(list);cohorts=defaultdict(int)
    registries=list(home.glob('*/development/registry.json'))+list(home.glob('*/consumed-transfer/registry.json'))+list(home.glob('*/fresh/consumed-transfer/registry.json'))
    for registry in sorted(registries):
        frozen=load(registry.parent/'freeze.json');assert sha(registry)==frozen['registry_sha256']
        assert sha(registry.parent/'key.json')==frozen['key_sha256']
        for name,expected in frozen['harness'].items():assert sha(ROOT/name)==expected, name
        for c in load(registry)['cases']:
            ident=c['id'];assert re.fullmatch(r'CRYPT-[A-Z]+-(?:T)?\d{4}',ident)
            assert ident not in cases, 'duplicate id';cases[ident]=c
            packet=(registry.parent if c['packet'].startswith('inputs/') else ROOT)/c['packet'];cohorts['consumed_transfer' if 'consumed-transfer' in str(registry) else 'development']+=1;actual={str(p.relative_to(packet)):sha(p) for p in packet.rglob('*') if p.is_file()}
            assert actual==c['files'], 'changed input '+ident
            value=load(packet/'case.json');value.pop('id',None)
            signature=digest({'case':value,'source_files':{k:v for k,v in actual.items() if k!='case.json'}})
            overlap[signature].append(ident)
    # Earlier cases remain their own cohorts, with exact original bytes.
    for c in load(ROOT/'evaluation/bubble-wrap/2026-11-25/continuation/development.json')['cases']:
        packet=ROOT/c['packet'];value=load(packet/'case.json');value.pop('id',None)
        signature=digest({'case':value,'source_files':{k:v for k,v in c['files'].items() if k!='case.json'}})
        overlap[signature].append(c['id'])
    runs=[]
    for path in sorted(home.glob('*/runs/*/run.json')):
        data=load(path);rows=data['cases'];ids=[c['id'] for c in rows]
        assert len(ids)==len(set(ids))==data['planned']==data['attempted']
        assert all(c['id'] in cases for c in rows)
        completed=sum(c['execution_status']=='completed' for c in rows)
        failed=sum(c['execution_status']=='failed' for c in rows)
        assert completed+failed==len(rows)
        for c in rows:
            if c['execution_status']=='completed':assert sha(path.parent/c['id']/'result.json')==c['raw_sha256']
            else:assert c['semantic_outcome']=='NOT_RUN' and c['score_status']=='UNSCORED'
        runs.append({'run':str(path.relative_to(ROOT)),'completed':completed,'failed':failed})
    for series in programme['series']:
        if series['status']=='PASS':
            assert series.get('transfer',{}).get('failed')==0
            assert series.get('candidate',{}).get('false_support')==0
    return {'schema':'cryptid-audit-v2','registered_cases':len(cases),'cohorts':dict(cohorts),'release_comparison_members':280,
            'unique_semantic_inputs':len(overlap),'overlapping_inputs':[{'semantic_hash':h,'members':v} for h,v in overlap.items() if len(v)>1],
            'runs':runs,'meaning':'Input seals, overlap and accounting only; semantic acceptance remains separately scored.',
            'publication':programme['publication']}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path);a=p.parse_args();result=audit()
    if a.output:
        with a.output.open('x') as f:json.dump(result,f,indent=2)
    print(json.dumps({k:v for k,v in result.items() if k not in {'overlapping_inputs','runs'}},indent=2))
