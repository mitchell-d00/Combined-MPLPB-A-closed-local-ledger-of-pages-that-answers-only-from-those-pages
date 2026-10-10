"""Frozen semantic source-ownership stress test; never tunes or alters the reader."""
import argparse
import hashlib
import json
import tempfile
from pathlib import Path
from mplpb_combined.evaluate import run


def summarize(result):
    rows = [r for d in result['domains'] for r in d['rows']]
    arms = sorted(rows[0]['arms'])
    def metrics(selected, arm):
        n=len(selected); returned=[r for r in selected if r['arms'][arm]['kind']=='return']
        bad=sum(r['arms'][arm]['score']=='wrong_return' for r in selected)
        return {'n':n,'wrong_ownership':bad,'wrong_ownership_rate':bad/n if n else None,
                'return_precision':sum(r['arms'][arm]['score']=='correct' for r in returned)/len(returned) if returned else None,
                'return_coverage':len(returned)/n if n else None,
                'wrong_refusal':sum(r['arms'][arm]['score']=='wrong_refusal' for r in selected)}
    return {'n':len(rows),'arms':{a:metrics(rows,a) for a in arms},
            'by_family':{f:{a:metrics([r for r in rows if r['id'].split('/')[0]==f],a) for a in arms}
                         for f in sorted({r['id'].split('/')[0] for r in rows})},
            'independent':False,'unit':'synthetic scenario, correlated within family',
            'modern_rag_results':'not run; lexical retrieval arms are not RAG systems'}


def evaluate(path):
    path=Path(path)
    cases=[json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    with tempfile.TemporaryDirectory() as tmp:
        root=Path(tmp);domains=[]
        for i,c in enumerate(cases):
            probe={'id':c['id'],'q':c['question'],'expect':c['expected']}
            if c['expected']=='return':probe.update(doc=c['acceptable_ids'][0],evidence=c['evidence'])
            else:probe['rationale']=c['rationale']
            raw=json.dumps({'probes':[probe]});name=str(i)+'.json';(root/name).write_text(raw)
            domains.append({'name':c['id'],'pages':c['documents'],'probes':name,'sha256':hashlib.sha256(raw.encode()).hexdigest()})
        manifest=root/'manifest.json';manifest.write_text(json.dumps({'domains':domains}))
        result=run(manifest)
    return {'input_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'summary':summarize(result),
            'rows':[r for d in result['domains'] for r in d['rows']]}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input',default='evaluation/ownership/rag-input.jsonl')
    p.add_argument('--out',default='evaluation/ownership/results.json')
    a=p.parse_args(); result=evaluate(a.input)
    Path(a.out).write_text(json.dumps(result,separators=(',',':'))+'\n')
    print(json.dumps(result['summary'],indent=2))

if __name__=='__main__':main()
