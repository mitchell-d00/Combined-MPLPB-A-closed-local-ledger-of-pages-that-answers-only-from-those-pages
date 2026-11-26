"""Frozen same-operator exact source and full-claim scoring, never a worker."""
import argparse,collections,hashlib,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def norm(s):return ' '.join(s.casefold().split())
def subset(a,e):
    if isinstance(e,dict):return isinstance(a,dict) and all(k in a and subset(a[k],v) for k,v in e.items())
    return norm(a)==norm(e) if isinstance(a,str) and isinstance(e,str) else type(a)==type(e) and a==e

def score(registry,key,run,output):
    reg=read(registry);keys=read(key);seal=read(registry.parent/'freeze.json');assert sha(registry)==seal['registry_sha256'] and sha(key)==seal['key_sha256'];assert sha(Path(__file__))==seal['harness']['tools/bunyip_score.py'];runs=read(run/'run.json');rows=[]
    descriptions={c['id']:c for c in reg['cases']}
    for row in runs['cases']:
        c=descriptions[row['id']];k=keys[row['id']];errors=[];wrong=False;miss=False;rawpath=run/row['id']/'result.json'
        if row['execution_status']!='completed':rows.append({'id':row['id'],'execution':'failed','scored':False,'passed':False});continue
        assert sha(rawpath)==row['raw_sha256'];raw=read(rawpath);a=raw['answer'];claims=a['claims'];records={x['id']:x for x in raw['records']};packet=(registry.parent if c['packet'].startswith('inputs/') else ROOT)/c['packet'];case=read(packet/'case.json')
        if a['question']!=case['question']:errors.append('original_question_changed');wrong=True
        if k['decision']=='withhold' and (a['answer_supported'] or claims):errors.append('unsupported_claim_or_completion');wrong=True
        if k['decision']=='complete' and (a['kind']!='supported_answer' or not a['answer_supported']):errors.append('positive_completion_miss');miss=True
        if claims and a['verification'].get('truth_verified') is not False:errors.append('truth_scope_not_preserved');wrong=True
        citations=[cite for claim in claims for cite in claim.get('citations',[])];witnesses=k['complete_witnesses']
        for claim in claims:
            prop=claim.get('proposition',{})
            if k['proposition'] and not subset(prop,k['proposition']):errors.append('wrong_proposition_roles_or_scope');wrong=True
            if k['literal_claim']:
                if norm(claim['text']) not in {norm('\n'.join(witnesses)),*(norm(w) for w in witnesses)}:errors.append('literal_claim_differs_from_key');wrong=True
            for fragment in k['qualification_fragments']:
                if not any(norm(fragment) in norm(q) for q in claim.get('qualifiers',[])):errors.append('qualification_missing');wrong=True
            for link in prop.get('date_links',[]):
                if k['date_roles'].get(link['requested_role'])!=link['date_text']:errors.append('wrong_date_role');wrong=True
            if not claim.get('citations'):errors.append('citation_missing');wrong=True
        for w in witnesses:
            if not any(norm(w)==norm(x['quote']) for x in citations):errors.append('complete_witness_missing');miss=True
        for x in citations:
            s=records.get(x['source_id']);lo,hi=x.get('body_start'),x.get('body_end')
            if not s or type(lo)!=int or type(hi)!=int or not 0<=lo<hi<=len(s['body']) or s['body'][lo:hi]!=x['quote'] or s['hash']!=x['hash']:errors.append('invalid_exact_citation');wrong=True
        inspection=raw['interpretation_inspection'];recognized=bool(inspection['finite_frame'] or inspection['documentary_plan']);discovery=all(any(norm(w) in norm(p['text']) for p in raw['discovery']['passages']) for w in witnesses) if witnesses else None
        diagnostic=a['diagnostic']['code'];stage='budget' if 'budget' in diagnostic else 'layout' if 'stacked' in diagnostic else 'question_interpretation' if not recognized else 'discovery' if discovery is False else 'proof' if miss else None
        rows.append({'id':row['id'],'group':c.get('question_group',c['mechanism']),'rendering':c.get('rendering'),'question':case['question'],'question_source_signature':hashlib.sha256(json.dumps({'q':case['question'],'source_texts':[s['body'] for s in raw['records']]},sort_keys=True).encode()).hexdigest(),'execution':'completed','scored':True,'passed':not errors,'kind':a['kind'],'complete':a['answer_supported'],'claims':len(claims),'false_support':wrong,'positive_miss':miss,'errors':errors,'discovery_complete':discovery,'interpretation_recognized':recognized,'miss_stage':stage,'raw_sha256':sha(rawpath)})
    counts={'planned':len(reg['cases']),'executed':len(rows),'completed':sum(r['execution']=='completed' for r in rows),'scored':sum(r['scored'] for r in rows),'passed':sum(r['passed'] for r in rows),'complete':sum(r.get('complete',False) for r in rows),'positive_misses':sum(r.get('positive_miss',False) for r in rows),'false_support_flags':sum(r.get('false_support',False) for r in rows)}
    result={'schema':'bunyip-source-audit-v1','scorer_sha256':sha(Path(__file__)),'registry_sha256':sha(registry),'key_sha256':sha(key),'run_sha256':sha(run/'run.json'),'counts':counts,'rows':rows,'custody':'Same operator; synthetic source-claim software test, no independent accuracy/semantic evaluation.'};output.write_text(json.dumps(result,indent=2)+'\n');print(counts)
if __name__=='__main__':
    p=argparse.ArgumentParser()
    for n in ['registry','key','run','output']:p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args();score(a.registry,a.key,a.run,a.output)
