"""Score an external system's frozen ownership decisions, not generated-answer truth."""
import argparse
import hashlib
import json
from pathlib import Path


def compare(cases_path,predictions_path):
    cases=[json.loads(x) for x in Path(cases_path).read_text().splitlines() if x.strip()]
    payload=json.loads(Path(predictions_path).read_text())
    for key in ['system','model_revision','retriever','prompt_sha256','input_sha256']:
        if not payload.get(key):raise ValueError('missing metadata: '+key)
    if payload['input_sha256']!=hashlib.sha256(Path(cases_path).read_bytes()).hexdigest():raise ValueError('input hash mismatch')
    rows=payload['predictions'];ids=[r['id'] for r in rows]
    if len(ids)!=len(set(ids)) or set(ids)!={c['id'] for c in cases}:raise ValueError('predictions must cover every unique case exactly once')
    byid={r['id']:r for r in rows};bad=returns=correct=misses=0
    for c in cases:
        r=byid[c['id']];kind=r['kind'];docs=r['source_ids']
        if kind not in ['return','ambiguous','not_in_corpus']:raise ValueError('invalid kind')
        if not isinstance(docs,list) or (kind!='return' and docs):raise ValueError('invalid source_ids')
        if kind=='return':
            returns+=1
            valid=c['expected']=='return' and len(docs)==1 and docs[0] in c['acceptable_ids']
            correct+=valid;bad+=not valid
        else:
            correct+=kind==c['expected'];misses+=c['expected']=='return'
    return {'n':len(cases),'correct':correct,'wrong_ownership':bad,'wrong_ownership_rate':bad/len(cases),
            'wrong_refusal':misses,'return_coverage':returns/len(cases),
            'return_precision':(returns-bad)/returns if returns else None,
            'answer_quality_scored':False,'system':payload['system']}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('predictions');p.add_argument('--input',default='evaluation/ownership/rag-input.jsonl');a=p.parse_args()
    print(json.dumps(compare(a.input,a.predictions),indent=2))
