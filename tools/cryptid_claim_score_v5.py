"""Same-operator claim/qualification/citation scoring, outside isolated workers."""
import argparse
from collections import Counter
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from tools.cryptid_trial import read,save,sha
VERSION='cryptid-claim-scorer-v5'


def norm(s):return ' '.join(s.split()).casefold()
def subset(actual,expected):
    if isinstance(expected,dict):return isinstance(actual,dict) and all(k in actual and subset(actual[k],v) for k,v in expected.items())
    if isinstance(expected,list):return isinstance(actual,list) and len(actual)==len(expected) and all(subset(x,y) for x,y in zip(actual,expected))
    if isinstance(expected,str):return isinstance(actual,str) and norm(actual)==norm(expected)
    return type(actual) is type(expected) and actual==expected


def score(a):
    key=read(a.key);freeze=read(a.registry.parent/'freeze.json');registry=read(a.registry)
    assert sha(a.registry)==freeze['registry_sha256'] and sha(a.key)==freeze['key_sha256']
    assert sha(Path(__file__))==freeze['harness']['tools/cryptid_claim_score_v5.py']
    run=read(a.run/'run.json');assert run['registry_sha256']==sha(a.registry);rows=[];descriptors={r['id']:r for r in registry['cases']}
    for entry in run['cases']:
        ident=entry['id'];k=key[ident];errors=[];wrong=False;miss=False
        if entry['execution_status']!='completed':
            rows.append({'id':ident,'execution_status':entry['execution_status'],'scored':False,'passed':False});continue
        raw=read(a.run/ident/'result.json');assert sha(a.run/ident/'result.json')==entry['raw_sha256']
        answer=raw['answer'];claims=answer['claims'];records={r.get('id',r.get('source_id')):dict(r,body=r.get('body',r.get('canonical_body'))) for r in raw.get('records',raw.get('source_receipts',[]))}
        packet_path=descriptors[ident]['packet'];packet=(a.registry.parent if packet_path.startswith('inputs/') else ROOT)/packet_path
        original_question=read(packet/'case.json')['question']
        if answer['question']!=original_question:errors.append('original_question_changed');wrong=True
        target=k['decision'];expected=list(k['claims']);used=set()
        if target=='complete' and answer['kind']=='partial_answer':expected+=k.get('allowed_partial_claims',[])
        if target=='diagnostic':
            rows.append({'id':ident,'execution_status':'completed','scored':False,'passed':False,'diagnostic_only':True,'kind':answer['kind'],'reason':'Historical expected answer is retained as a lead; source-voice answerability not adjudicated.','claims':len(claims)});continue
        if target=='conflict' and (answer['kind']!='conflict' or answer['answer_supported']):errors.append('conflict_not_preserved');wrong|=answer['answer_supported'];miss|=not claims
        if target=='complete' and (not answer['answer_supported'] or answer['kind']!='supported_answer'):errors.append('positive_completion_miss');miss=True
        if target=='partial' and (answer['answer_supported'] or answer['kind']!='partial_answer' or not answer['missing']):
            errors.append('partial_obligation_not_preserved');wrong|=answer['answer_supported'];miss|=not claims
        if target=='withhold' and (claims or answer['answer_supported']):errors.append('unsupported_claim_or_completion');wrong=True
        if target=='partial':
            for fragment in k.get('missing_fragments',[]):
                if not any(norm(fragment) in norm(s) for s in answer['missing']):errors.append('missing_obligation_dropped');wrong|=bool(claims)
        for claim in claims:
            matching=[i for i,e in enumerate(expected) if i not in used and subset(claim.get('proposition',{}),e['proposition'])]
            if len(matching)!=1:errors.append('unexpected_or_duplicate_claim');wrong=True;continue
            i=matching[0];used.add(i);e=expected[i]
            if claim.get('source_support_established') is not True or (claim.get('historical_truth_independently_verified',claim.get('proposition',{}).get('historical_truth_independently_verified')) is not False and not (claim.get('historical_truth_independently_verified',claim.get('proposition',{}).get('historical_truth_independently_verified')) is None and answer.get('verification',{}).get('truth_verified') is False)):errors.append('support_or_truth_scope_wrong');wrong=True
            for fragment in e['qualification_fragments']:
                if not any(norm(fragment) in norm(q) for q in claim.get('qualifiers',[])):errors.append('qualification_missing');wrong=True
            for witness in e['complete_witnesses']:
                if not any(norm(witness)==norm(c['quote']) for c in claim.get('citations',[])):errors.append('complete_witness_missing');wrong=True
            if not claim.get('citations'):errors.append('citation_missing');wrong=True
            for c in claim.get('citations',[]):
                r=records.get(c['source_id']);lo,hi=c.get('body_start'),c.get('body_end')
                if not r or not isinstance(lo,int) or not isinstance(hi,int) or not 0<=lo<hi<=len(r['body']) or r['body'][lo:hi]!=c['quote'] or r['hash']!=c['hash']:
                    errors.append('invalid_citation');wrong=True
        if len(used)!=len(expected):errors.append('positive_claim_miss');miss=True
        inspection=raw.get('interpretation_inspection',{});plan=inspection.get('documentary_plan');frame=inspection.get('finite_frame')
        recognized=bool(plan or frame);passages=raw.get('discovery',raw.get('retrieval',{}).get('simple_bm25',{})).get('passages',[])
        discovery=all(any(norm(w) in norm(p['text']) for p in passages) for e in expected for w in e['complete_witnesses']) if expected else None
        diag=answer['diagnostic']['code'];stage=('interpretation' if not recognized else 'discovery' if discovery is False else 'proof') if miss else None
        rows.append({'id':ident,'execution_status':'completed','scored':True,'passed':not errors,'expected':target,'kind':answer['kind'],'claims':len(claims),'positive_miss':miss,'false_support':wrong,'errors':errors,'interpretation_inspection_recognized':recognized,'required_witness_discovery':discovery,'miss_stage_diagnostic':stage,'budget_stop':'budget' in diag,'measurements':raw.get('measurements',{})})
    counts={'planned':len(registry['cases']),'attempted':len(rows),'completed':sum(r['execution_status']=='completed' for r in rows),'scored':sum(r['scored'] for r in rows),'unscored':sum(not r['scored'] for r in rows),'passed':sum(r['passed'] for r in rows),'false_support':sum(r.get('false_support',False) for r in rows),'positive_misses':sum(r.get('positive_miss',False) for r in rows),'budget_stops':sum(r.get('budget_stop',False) for r in rows),'diagnostic_only':sum(r.get('diagnostic_only',False) for r in rows)}
    result={'schema':'cryptid-claim-score-v1','version':VERSION,'scorer_sha256':sha(Path(__file__)),'run_sha256':sha(a.run/'run.json'),'key_sha256':sha(a.key),'counts':counts,'cases':rows,'custody':'Same-operator keys/scoring; no independent historical or semantic adjudication.'}
    save(a.output,result);print(counts)

if __name__=='__main__':
    p=argparse.ArgumentParser()
    for n in ('registry','key','run','output'):p.add_argument('--'+n,type=Path,required=True)
    score(p.parse_args())
