#!/usr/bin/env python3
"""Local synthetic scale experiment, not a production/SLA benchmark."""
import argparse
import json
import math
import platform
import statistics
import sys
import tempfile
import time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from mplpb_combined import ledger as L
from tools.ledger_ui import App
from tools.evaluate_grounded_chat import engine_pins

def run(sizes,repeats):
    rows=[]
    with tempfile.TemporaryDirectory(prefix='mplpb-scale-') as tmp:
        for size in sizes:
            root=Path(tmp)/str(size)/'corpus';root.mkdir(parents=True)
            begin=time.perf_counter()
            for i in range(size):
                title='Object '+str(i)
                L.write(root,title=title,scope=title,body='The '+title+' is 12 km in diameter.',
                        when='2026-01-01T00:00Z',origin='machine',owner='unknown',source_authorship='unknown',external='no')
            author_seconds=time.perf_counter()-begin
            app=App(root,topic_base=root.parent/'topics')
            sid=app.chat({'corpus':'custom','message':'topic Object 0'})['session']
            samples=[];kinds=[]
            for _ in range(repeats):
                tick=time.perf_counter();reply=app.chat({'corpus':'custom','session':sid,'message':'how big is it?'})['response']
                samples.append((time.perf_counter()-tick)*1000);kinds.append(reply['kind'])
            rows.append({'pages':size,'repeats':repeats,'synthetic_corpus_build_seconds':author_seconds,
                         'latency_ms':samples,'median_ms':statistics.median(samples),
                         'p95_ms':sorted(samples)[math.ceil(.95*len(samples))-1],
                         'correct_answers':kinds.count('grounded_answer'),'response_kinds':kinds,
                         'corpus_bytes':sum(p.stat().st_size for p in root.rglob('*') if p.is_file())})
    return {'schema':1,'environment':{'python':platform.python_version(),'platform':platform.platform()},
            'engine_sha256':engine_pins(),'rows':rows,'independence_verified':False,
            'limitations':['Synthetic short pages; no concurrency, long documents, browser memory, or production traffic.',
                           'Warm filesystem; timings include hash checks and session persistence.',
                           'Few repetitions: p95 is descriptive, not a stable tail-latency estimate.',
                           'Build time is programmatic ledger construction, not human authoring effort.']}
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--sizes',nargs='+',type=int,default=[10,50,100]);p.add_argument('--repeats',type=int,default=5);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args()
    if not 1<=a.repeats<=100 or any(not 1<=n<=1000 for n in a.sizes):p.error('Use 1–100 repeats and 1–1000 pages')
    data=run(a.sizes,a.repeats);a.out.write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps([{k:r[k] for k in ('pages','median_ms','p95_ms','correct_answers')} for r in data['rows']],indent=2))
