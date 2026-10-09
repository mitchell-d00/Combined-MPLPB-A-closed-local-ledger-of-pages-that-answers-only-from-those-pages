#!/usr/bin/env python3
"""Run frozen contextual-chat probes. Developer fixtures are not independent validation."""
import argparse
import hashlib
import json
import math
import platform
import statistics
import sys
import tempfile
import time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from mplpb_combined import ledger as L
from mplpb_combined.record import text_of
from tools.ledger_ui import App

ANSWER_KINDS={'grounded_answer','return','summary','relations'}


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def wilson(k,n):
    if not n:return None
    z=1.959963984540054;p=k/n;den=1+z*z/n
    mid=(p+z*z/(2*n))/den;half=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return [max(0,mid-half),min(1,mid+half)]

def metrics(rows,arm):
    n=len(rows);unsupported=sum(not r['supported'] for r in rows);supported=n-unsupported
    answers=sum(r[arm]['answered'] for r in rows)
    correct=sum(r[arm]['correct_answer'] for r in rows)
    false=sum(r[arm]['answered'] and not r['supported'] for r in rows)
    refused_supported=sum(r['supported'] and not r[arm]['answered'] for r in rows)
    return {'n':n,'supported':supported,'unsupported':unsupported,'answers':answers,'correct_answers':correct,
            'false_acceptances':false,'unnecessary_refusals':refused_supported,
            'unsupported_false_acceptance_rate':false/unsupported if unsupported else None,
            'unsupported_false_acceptance_wilson95':wilson(false,unsupported),
            'supported_answer_precision':correct/answers if answers else None,
            'supported_answer_precision_wilson95':wilson(correct,answers),
            'answerable_coverage':correct/supported if supported else None,
            'unnecessary_refusal_rate':refused_supported/supported if supported else None}

def engine_pins():
    return {str(p.relative_to(ROOT)):sha(p) for folder in ('tools','mplpb_combined')
            for p in sorted((ROOT/folder).glob('*.py'))}

def validate(spec):
    if spec.get('schema')!=1 or not spec.get('domains'):raise ValueError('Expected schema 1 and nonempty domains')
    ids=set()
    for domain in spec['domains']:
        if not domain.get('name') or not domain.get('probes'):raise ValueError('Domain needs name and probes')
        if ('pages' in domain)==('root' in domain):raise ValueError('Choose pages or a pinned root')
        if 'root' in domain and not domain.get('corpus_sha256'):raise ValueError('External corpus needs exact file pins')
        for p in domain['probes']:
            if p.get('id') in ids or not p.get('id'):raise ValueError('Probe IDs must be unique')
            ids.add(p['id'])
            if type(p.get('supported')) is not bool:raise ValueError('supported must be boolean')
            if not p.get('question') or not p.get('topic'):raise ValueError('Probe needs question and topic')
            evidence=p.get('evidence',[])
            if not isinstance(evidence,list) or any(not isinstance(s,str) or not s for s in evidence):
                raise ValueError('Evidence must be a list of nonempty strings')
            if p['supported'] and not evidence:raise ValueError('Supported label needs evidence')
            if not isinstance(p.get('setup',[]),list) or any(not isinstance(s,str) for s in p.get('setup',[])):
                raise ValueError('Setup must be a list of user messages')
            if not p['supported'] and not p.get('rationale'):raise ValueError('Unsupported label needs rationale')

def run(path,expected_sha):
    path=Path(path).resolve()
    if sha(path)!=expected_sha:raise ValueError('Frozen manifest hash mismatch')
    spec=json.loads(path.read_text());validate(spec);rows=[];latencies=[]
    with tempfile.TemporaryDirectory(prefix='mplpb-context-eval-') as temp:
        for di,domain in enumerate(spec['domains']):
            if 'root' in domain:
                root=(path.parent/domain['root']).resolve()
                actual={p.relative_to(root).as_posix():sha(p) for p in root.rglob('*') if p.is_file() and p.name!='.lock'}
                if actual!=domain['corpus_sha256']:raise ValueError('External corpus bytes changed: '+domain['name'])
            else:
                root=Path(temp)/str(di)/'corpus';root.mkdir(parents=True)
                for page in domain['pages']:
                    L.write(root,**page,when='2026-01-01T00:00Z',origin='machine',owner='unknown',external='no',source_authorship='unknown')
            for pi,probe in enumerate(domain['probes']):
                app=App(root,topic_base=Path(temp)/str(di)/str(pi)/'topics')
                records=[r for r in L.Ledger(root).servable() if r.title==probe['topic']]
                if len(records)!=1:raise ValueError('Gold topic must identify one eligible page')
                gold=probe.get('evidence',[])
                if not all(isinstance(s,str) and s and s in text_of(records[0].body_html) for s in gold):
                    raise ValueError('Gold evidence must be verbatim body text')
                sid=app.chat({'corpus':'custom','message':'topic '+probe['topic']})['session']
                for msg in probe.get('setup',[]):app.chat({'corpus':'custom','session':sid,'message':msg})
                tick=time.perf_counter()
                reply=app.chat({'corpus':'custom','session':sid,'message':probe['question']})['response']
                elapsed=(time.perf_counter()-tick)*1000;latencies.append(elapsed)
                expanded=probe['question']
                import re
                expanded=re.sub(r'\b(it|its|this topic|that topic)\b',lambda _:probe['topic'],expanded,flags=re.I)
                baseline=app.query({'corpus':'custom','question':expanded})['reader']
                row={'id':probe['id'],'domain':domain['name'],'question':probe['question'],'topic':probe['topic'],
                     'supported':probe['supported'],'gold_evidence':gold,'rationale':probe.get('rationale'),
                     'category':probe.get('category'),'latency_ms':elapsed,'response':reply}
                for arm,kind,body in [('chat',reply['kind'],reply['message']),('lexical_page_return',baseline['kind'],baseline.get('text',''))]:
                    answered=kind in ANSWER_KINDS
                    correct_source=(baseline.get('id')==records[0].id if arm=='lexical_page_return' else
                                    any(s.get('id')==records[0].id and s.get('hash')==records[0].hash for s in reply.get('sources',[])))
                    row[arm]={'kind':kind,'answered':answered,'correct_answer':bool(answered and probe['supported'] and correct_source and all(s in body for s in gold))}
                row['lexical_page_return']['notice']='Page-return baseline; returning a page is not proof of answer suitability.'
                rows.append(row)
    arms=('chat','lexical_page_return')
    return {'schema':1,'manifest_sha256':expected_sha,'engine_sha256':engine_pins(),
            'provenance':spec.get('provenance',{}),'independence_verified':False,
            'environment':{'python':platform.python_version(),'platform':platform.platform()},
            'metrics':{arm:metrics(rows,arm) for arm in arms},
            'per_domain':{d['name']:{arm:metrics([r for r in rows if r['domain']==d['name']],arm) for arm in arms} for d in spec['domains']},
            'latency_ms':{'median':statistics.median(latencies),'p95':sorted(latencies)[math.ceil(.95*len(latencies))-1]},
            'rows':rows,'limitations':['Developer-generated fixtures cannot establish independent validity.',
                'Matching gold spans checks mechanical agreement, not semantic entailment; human review is required.',
                'Wilson intervals assume independent samples; related/template-generated probes violate that assumption.',
                'Latency is local end-to-end chat timing, not a production load benchmark.']}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('manifest',type=Path)
    p.add_argument('--sha256',required=True);p.add_argument('--out',type=Path,required=True)
    args=p.parse_args();result=run(args.manifest,args.sha256)
    args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result['metrics'],indent=2))
if __name__=='__main__':main()
