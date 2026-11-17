"""Validate AI citation bytes and count blinded opinions; never certify semantics."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

CATEGORIES={'complete_correct','correct_refusal','incorrect_or_over_refusal','unassessed'}


def score(packet, runs):
    packet=Path(packet);runs=Path(runs)
    load=lambda name:json.loads((packet/name).read_text())
    assessment=load('assessment.json');key=load('unblinding-key.json')
    if (assessment['schema']!='ai-assessment-v1' or assessment['human_review'] is not False
            or assessment['review_class']!='fresh_context_AI_assessment'):
        raise ValueError('Expected explicitly labeled fresh-context AI assessment')
    inputs=load('responses.json')
    requested={r['response_id']:(case['id'],r) for case in inputs for r in case['responses']}
    if set(requested)!=set(key) or len(requested)!=sum(len(c['responses']) for c in inputs):
        raise ValueError('Missing, duplicate or unknown blinded response identity')
    sources={}
    for source in load('sources.json'):
        path=(packet/source['path']).resolve();path.relative_to(packet.resolve())
        raw=path.read_bytes()
        if len(raw)!=source['bytes'] or hashlib.sha256(raw).hexdigest()!=source['sha256']:
            raise ValueError('Original source bytes changed')
        sources[source['id']]=(source,raw)
    totals={p:Counter({c:0 for c in CATEGORIES}) for p in ('before','final')}
    seen=set();rows=[];anchors=0
    for case in assessment['cases']:
        for response in case['responses']:
            identity=response['response_id']
            if identity not in requested or identity in seen or requested[identity][0]!=case['id']:
                raise ValueError('Invalid/duplicate scored response')
            seen.add(identity);binding=key[identity];phase=binding['phase']
            family='original' if case['id'].startswith('H') else 'government'
            arm='after' if phase=='final' else 'before'
            original=runs/family/arm/(case['id']+'.json')
            if hashlib.sha256(original.read_bytes()).hexdigest()!=binding['response_sha256']:
                raise ValueError('Scored output changed')
            category=response['category']
            if category not in CATEGORIES:raise ValueError('Unknown assessment category')
            if category=='complete_correct' and not response['evidence']:
                raise ValueError('Positive assessment lacks source anchors')
            if category=='correct_refusal' and not response.get('absence_scope'):
                raise ValueError('Refusal judgment lacks examined scope')
            for cite in response['evidence']:
                source,raw=sources[cite['source_id']];a=cite['byte_start'];b=cite['byte_end']
                if (cite['sha256']!=source['sha256'] or type(a) is not int or type(b) is not int
                        or not 0<=a<b<=len(raw) or raw[a:b].decode('utf-8')!=cite['quote']):
                    raise ValueError('AI evidence is not an exact original byte slice')
                anchors+=1
            totals[phase][category]+=1
            rows.append({'case_id':case['id'],'phase':phase,'category':category,
                         'detail':response.get('detail'),'response_id':identity})
    if seen!=set(requested):raise ValueError('Unassessed responses omitted from record')
    return {'schema':'solo-ai-score-v1','label':'AI assessment','human_review':False,
            'model_independence_established':False,'model_identity_pin':None,
            'citation_fidelity_checked':True,'semantic_truth_verified':False,
            'counts':{p:dict(v) for p,v in totals.items()},'exact_byte_anchors_checked':anchors,'rows':rows,
            'notice':'Counts are fresh-context AI judgments with exact-byte citations, not authenticated historical truth or independent human validation.'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--packet',required=True,type=Path);parser.add_argument('--runs',required=True,type=Path)
    parser.add_argument('--output',required=True,type=Path);args=parser.parse_args()
    result=score(args.packet,args.runs)
    with args.output.open('x') as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps(result['counts'],indent=2))


if __name__=='__main__':main()
