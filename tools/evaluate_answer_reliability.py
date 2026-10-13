"""Separate frozen retrieval labels, answer support, and external question coverage."""
import argparse, hashlib, json, tempfile, importlib.util, sys
from pathlib import Path
from mplpb_combined import reader as R
from mplpb_combined.ledger import write
from mplpb_combined.killtest import Result, score, check_hash
from mplpb_answers.support import supported_answer, code_pins


def metrics(rows):
    returned=[r for r in rows if r['kind']=='return']
    answerable=[r for r in rows if r['expected']=='return']
    right=lambda r:r['kind']==r['expected'] and (r['kind']!='return' or r['return_correct'])
    correct_returns=sum(r['return_correct'] for r in returned)
    return {'n':len(rows),'correct':sum(map(right,rows)),
            'wrong_returns':sum(not r['return_correct'] for r in returned),
            'return_precision':correct_returns/len(returned) if returned else None,
            'answerable_questions':len(answerable),
            'answerable_coverage':sum(r['kind']=='return' and r['return_correct'] for r in answerable)/len(answerable) if answerable else None,
            'false_refusals':sum(r['kind']=='not_in_corpus' for r in answerable),
            'ambiguity_on_answerable':sum(r['kind']=='ambiguous' for r in answerable),
            'ambiguity_total':sum(r['kind']=='ambiguous' for r in rows),
            'correct_ambiguity':sum(r['kind']==r['expected']=='ambiguous' for r in rows),
            'ambiguity_on_unanswerable':sum(r['kind']=='ambiguous' and r['expected']=='not_in_corpus' for r in rows)}


def observe(fn,root,q,expect,doc=None,value=None):
    a=fn(root,q)
    correct=(expect=='return' and (doc is None or (a.record and a.record.id==doc))
             and (value is None or value.casefold() in a.text.casefold()))
    return {'kind':a.kind,'expected':expect,'return_correct':bool(correct),
            'id':a.record.id if a.record else None,'text':a.text,'reason':a.reason,
            'support':getattr(a,'support',None),'candidates':[r.id for r,_ in a.candidates]}


def baseline_support():
    path=Path('evaluation/reliability/baseline_support.py')
    spec=importlib.util.spec_from_file_location('baseline_support_715d1b5',path)
    module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module
    spec.loader.exec_module(module)
    return module.supported_answer


def evaluate():
    arms=[('legacy_candidates',R.answer),('baseline_supported',baseline_support()),('supported',supported_answer)]
    output={'core_engine_unchanged_since':'715d1b5','support_code':code_pins(),'datasets':{}}
    for file in ['probes','probes_heldout','probes_adjacent']:
        path=Path('killtest')/(file+'.json');spec=json.loads(path.read_text())
        assert check_hash(path)=='OK'
        rows=[]
        for p in spec['probes']:
            row={'id':p['id'],'question':p['q'],'expected':p['expect'],'expected_doc':p.get('doc')}
            for name,fn in arms:
                result=observe(fn,spec['corpus'],p['q'],p['expect'],p.get('doc'))
                result['frozen_score']=score(p['expect'],p.get('doc'),Result(result['kind'],result['id']))
                row[name]=result
            rows.append(row)
        output['datasets'][file]={'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'role':'development; frozen labels unchanged',
                                 'rows':rows,'metrics':{a:metrics([r[a] for r in rows]) for a,_ in arms}}
    for name in ['development-cases','squad-sample']:
        path=Path('evaluation/reliability')/(name+'.json');spec=json.loads(path.read_text());rows=[]
        for c in spec['cases']:
            with tempfile.TemporaryDirectory() as tmp:
                if name=='squad-sample':
                    # The title is metadata; the original context is the only answer evidence.
                    documents=[{'doc_id':'EXT-0001','title':c['title'],'scope':c['title'],'body':c['context']}]
                    expect='not_in_corpus' if c['unanswerable'] else 'return'
                    values=[a['text'] for a in c['answers']]
                else:documents=c['documents'];expect=c['expected'];values=[c['value']] if c['value'] else []
                for doc in documents:write(tmp,**doc,when='2026-01-01T00:00Z')
                row={'id':c['id'],'question':c['question'],'expected':expect}
                for arm,fn in arms:
                    result=observe(fn,tmp,c['question'],expect)
                    if values:result['return_correct']=expect=='return' and any(v.casefold() in result['text'].casefold() for v in values)
                    row[arm]=result
                rows.append(row)
        output['datasets'][name]={'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
            'role':'external authored questions; one-time small coverage probe, not independent system validation' if name=='squad-sample' else 'developer-authored development scenarios',
            'rows':rows,'metrics':{a:metrics([r[a] for r in rows]) for a,_ in arms}}
    return output

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',default='evaluation/reliability/after.json');args=parser.parse_args()
    result=evaluate();Path(args.output).write_text(json.dumps(result,separators=(',',':'))+'\n')
    print(json.dumps({k:v['metrics'] for k,v in result['datasets'].items()},indent=2))
