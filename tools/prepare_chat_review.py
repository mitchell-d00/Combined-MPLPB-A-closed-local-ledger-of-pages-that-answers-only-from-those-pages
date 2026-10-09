#!/usr/bin/env python3
"""Prepare blinded annotation packets; never expose gold labels or model outputs."""
import argparse
import hashlib
import json
import random
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from mplpb_combined import ledger as L
from mplpb_combined.record import text_of

def packet(path,expected_sha,seed):
    path=Path(path).resolve();raw=path.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=expected_sha:raise ValueError('Manifest bytes changed')
    data=json.loads(raw);cases=[]
    for domain in data['domains']:
        if 'pages' in domain:
            pages=[{'title':p['title'],'body':p['body']} for p in domain['pages']]
        else:
            root=(path.parent/domain['root']).resolve()
            actual={p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob('*') if p.is_file() and p.name!='.lock'}
            if actual!=domain['corpus_sha256']:raise ValueError('Corpus pins differ')
            pages=[{'title':r.title,'body':text_of(r.body_html)} for r in L.Ledger(root).servable()]
        for p in domain['probes']:
            cases.append({'id':p['id'],'domain':domain['name'],'selected_topic':p['topic'],
                          'prior_user_turns':p.get('setup',[]),'question':p['question'],'pages':pages,
                          'review':{'reviewer_id':None,'label':None,'evidence':[],'rationale':None,'confidence':None}})
    random.Random(seed).shuffle(cases)
    return {'schema':1,'source_sha256':expected_sha,'order_seed':seed,'blind_to':['gold labels','system outputs','scopes','exclusions'],
            'instructions':'Label supported, unsupported, ambiguous, or invalid. Cite exact body text. Judge only the selected topic; do not use outside knowledge. Complete independently before adjudication.',
            'cases':cases}
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('manifest',type=Path);p.add_argument('--sha256',required=True);p.add_argument('--seed',type=int,default=20261009);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();a.out.write_text(json.dumps(packet(a.manifest,a.sha256,a.seed),indent=2)+'\n')
