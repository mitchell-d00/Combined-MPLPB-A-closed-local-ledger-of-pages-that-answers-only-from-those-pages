"""Isolated, separate-budget discovery on unchanged development questions."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

from tools.sorter_first_study import FAMILIES,ROOT
from tools.unprepared_sources import import_corpus
from tools.unprepared_challenge import read,frozen,covers,code_pins
from tools.report_sorter_options_study import visible
from tools.study_sandbox import command,_limits


def run(native_study,output):
    study=Path(native_study);output=Path(output);output.mkdir(parents=True,exist_ok=False)
    if code_pins(ROOT)!=read(study/'protocol.json')['reader_sha256']:
        raise ValueError('Exploration runtime differs from frozen native study')
    rows=[]
    with tempfile.TemporaryDirectory(prefix='mplpb-exploration-') as temporary:
        tmp=Path(temporary);code=tmp/'code';code.mkdir()
        for package in ('mplpb_answers','mplpb_combined','mplpb_work'):
            shutil.copytree(ROOT/package,code/package,ignore=shutil.ignore_patterns('__pycache__'))
        for family,(relative,seal) in FAMILIES.items():
            corpus=ROOT/relative;frozen(corpus,seal);data=tmp/family;data.mkdir()
            receipt=import_corpus(corpus,data/'ledger')
            if receipt!=read(study/family/'import-receipt.json'):raise ValueError('Import receipt differs')
            (data/'ledger/import-receipt.json').unlink()
            for case in read(corpus/'questions.json')['cases']:
                (data/'question.json').write_text(json.dumps(case))
                dest=tmp/(family+'-'+case['id']);dest.mkdir()
                program='''import json,resource,time
from pathlib import Path
from mplpb_work.answer_router import explore
q=json.loads(Path('/study/question.json').read_text());start=time.perf_counter();cpu=time.process_time()
r=explore(q['question'],'/study/ledger',max_passages=12,max_characters=16000)
Path('/output/result.json').write_text(json.dumps({'case_id':q['id'],'result':r,'cpu_seconds':time.process_time()-cpu,'wall_seconds':time.perf_counter()-start,'peak_rss_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024}))
'''
                start=time.perf_counter()
                try:
                    process=subprocess.run(command(shutil.which('bwrap'),code,data,dest,program),
                        stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=180,preexec_fn=_limits)
                    log=process.stdout.decode(errors='replace')
                    if process.returncode:raise ValueError('Worker exit '+str(process.returncode)+': '+log[-500:])
                    row=read(dest/'result.json');row['execution_status']='completed'
                except Exception as exc:
                    row={'case_id':case['id'],'execution_status':'failed','error':str(exc)};log=str(exc)
                row.update(family=family,parent_wall_seconds=time.perf_counter()-start)
                (output/(family+'-'+case['id']+'.json')).write_text(json.dumps(row,indent=2)+'\n')
                (output/(family+'-'+case['id']+'.log')).write_text(log)
                rows.append(row);print(family,case['id'],row['execution_status'],flush=True)
    # No reference/expected files are mounted in any worker. Score discovery only
    # after every execution, including failed workers, has been retained.
    cases=[]
    for row in rows:
        family=row['family'];corpus=ROOT/FAMILIES[family][0]
        refs=next(r for r in read(corpus/'reference-draft.json')['cases'] if r['id']==row['case_id'])['citations']
        base=read(study/family/'direct'/(row['case_id']+'.json'))
        report=row.get('result',{}).get('report') or {};shown=report.get('passages',[])
        native=[any(covers(p,ref) for p in visible(base)) for ref in refs]
        extra=[any(covers(p,ref) for p in shown) for ref in refs]
        cases.append({'id':row['case_id'],'family':family,'native_draft_spans':native,
                      'exploration_draft_spans':extra,'combined_draft_spans':[a or b for a,b in zip(native,extra)],
                      'native_kind':base.get('answer',{}).get('kind'),'exploration_answer_supported':False})
    result={'schema':'separate-exploration-evaluation-v1','runtime_sha256':code_pins(ROOT),
            'cases':cases,'completed':sum(r['execution_status']=='completed' for r in rows),
            'questions':len(rows),'native_draft_spans':sum(sum(c['native_draft_spans']) for c in cases),
            'combined_draft_spans':sum(sum(c['combined_draft_spans']) for c in cases),
            'draft_span_total':sum(len(c['native_draft_spans']) for c in cases),
            'exploration_cpu_seconds':sum(r.get('cpu_seconds',0) for r in rows),
            'exploration_wall_seconds':sum(r.get('wall_seconds',0) for r in rows),
            'source_bytes_read':None,'reference_keys_mounted':False,'strict_slots_consumed':0,
            'independent_semantic_review':'NOT RUN','historical_recall':None,
            'notice':'Separate discovery of draft anchors is not supported-answer or relationship accuracy improvement.'}
    (output/'summary.json').write_text(json.dumps(result,indent=2)+'\n');return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--native-study',required=True,type=Path)
    p.add_argument('--output',required=True,type=Path);a=p.parse_args();print(json.dumps(run(a.native_study,a.output),indent=2))
