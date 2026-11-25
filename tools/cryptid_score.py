"""Externally held same-operator expectations; never imported by runtime/worker."""
import argparse
from collections import Counter
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from tools.cryptid_trial import read, save, sha
VERSION='cryptid-scorer-v1'


def score(a):
    registry=read(a.registry);freeze=read(a.registry.parent/'freeze.json');key=read(a.key)
    assert sha(a.registry)==freeze['registry_sha256'] and sha(a.key)==freeze['key_sha256']
    assert sha(Path(__file__))==freeze['harness']['tools/cryptid_score.py']
    run=read(a.run/'run.json');assert run['registry_sha256']==sha(a.registry)
    rows=[]
    for row in run['cases']:
        ident=row['id'];k=key[ident];errors=[];accepted=False;miss=False
        if row['execution_status']!='completed':
            rows.append({'id':ident,'execution_status':row['execution_status'],'score_status':'UNSCORED','passed':False});continue
        raw=read(a.run/ident/'result.json');answer=raw['answer'];claims=answer['claims']
        if sha(a.run/ident/'result.json')!=row['raw_sha256']:raise ValueError('Changed raw')
        records={r.get('id',r.get('source_id')):r for r in raw.get('records',raw.get('source_receipts',[]))}
        for claim in claims:
            if claim.get('source_support_established') is not True:errors.append('claim_not_checked')
            if not claim.get('citations'):errors.append('claim_without_citations')
            if not claim.get('qualifiers'):errors.append('claim_without_qualifications')
            for c in claim.get('citations',[]):
                r=records.get(c['source_id']);body=(r or {}).get('body',(r or {}).get('canonical_body',''))
                lo,hi=c.get('body_start',c.get('start')),c.get('body_end',c.get('end'))
                if not r or c['hash']!=r['hash'] or not isinstance(lo,int) or not isinstance(hi,int) or body[lo:hi]!=c['quote'] or not 0<=lo<hi<=len(body):errors.append('invalid_citation')
        if k['decision']=='withhold':
            if claims or answer['answer_supported']:errors.append('false_supported_claim');accepted=True
        else:
            expected=k['expected_date_links'];actual=[]
            for claim in claims:
                p=claim.get('proposition',{})
                if p.get('relation')!='source_event_date_inventory':errors.append('unexpected_claim_relation');accepted=True;continue
                if p.get('historical_truth_independently_verified') is not False or p.get('causation_established') is not False:errors.append('overclaimed_truth_or_causality');accepted=True
                for link in p['date_links']:
                    v=[link['requested_role'],link['date_text'],link.get('year')];actual.append(v)
                    if v not in expected:errors.append('wrong_date_role_or_value');accepted=True
                    if not any(link['statement_text'] in c['quote'] for c in claim['citations']):errors.append('unwitnessed_date');accepted=True
            if sorted(actual)!=sorted(expected):errors.append('positive_miss');miss=True
            if not answer['answer_supported']:errors.append('incomplete_positive');miss=True
        rows.append({'id':ident,'execution_status':'completed','score_status':'SCORED','passed':not errors,
                     'expected':k['decision'],'outcome':answer['kind'],'claims':len(claims),
                     'false_support':accepted,'positive_miss':miss,'errors':errors})
    result={'schema':'cryptid-score-v1','scorer_version':VERSION,'scorer_sha256':sha(Path(__file__)),
            'run_sha256':sha(a.run/'run.json'),'key_sha256':sha(a.key),
            'counts':{'planned':len(registry['cases']),'completed':sum(r['execution_status']=='completed' for r in rows),
                      'unscored':sum(r['score_status']=='UNSCORED' for r in rows),'passed':sum(r['passed'] for r in rows),
                      'false_support':sum(r.get('false_support',False) for r in rows),'positive_misses':sum(r.get('positive_miss',False) for r in rows)},'cases':rows}
    save(a.output,result);print(json.dumps(result['counts']))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--registry',type=Path,required=True);p.add_argument('--key',type=Path,required=True);p.add_argument('--run',type=Path,required=True);p.add_argument('--output',type=Path,required=True);score(p.parse_args())
