"""Run actual source-linked workspace development cases under a frozen runtime.

No semantic answer key or candidate is promoted to reference truth. Original
questions/records are read unchanged; outputs and real resource costs are kept.
"""
import argparse
from collections import Counter
import json
from pathlib import Path
import resource
import sys
import tempfile
import time
from unittest.mock import patch


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--implementation',required=True,type=Path)
    p.add_argument('--native-study',required=True,type=Path);p.add_argument('--output',required=True,type=Path);a=p.parse_args()
    code=a.implementation.resolve();study=a.native_study.resolve();output=a.output.resolve()
    sys.path.insert(0,str(code))
    from tools.unprepared_challenge import code_pins,read,save,sha
    from tools.unprepared_sources import import_corpus
    from mplpb_work import sorter
    from mplpb_work.candidate_workspace import build,verify_workspace
    protocol=read(study/'protocol.json')
    if code_pins(code)!=protocol['reader_sha256']:raise ValueError('Use exactly the frozen native-replay runtime')
    output.mkdir(parents=True,exist_ok=False)
    rows=[]
    for family,corpus_path,ids in [
        ('original','evaluation/unprepared-originals/2026-11-16',['H02','H05']),
        ('government','evaluation/unprepared-originals/2026-11-16-followup/unfamiliar',['U01','U04'])]:
        corpus=code/corpus_path;questions={q['id']:q['question'] for q in read(corpus/'questions.json')['cases']}
        processed=code/'evaluation/sorter-first-originals/2026-11-18-witness-admission-final'/family
        graph=read(processed/'compare.json');rawdir=processed/'sorter-inputs'
        with tempfile.TemporaryDirectory() as tmp:
            ledger=Path(tmp)/'ledger';imported=import_corpus(corpus,ledger)
            save(output/(family+'-import-receipt.json'),imported)
            save(output/(family+'-source-manifest.json'),read(corpus/'corpus-manifest.json'))
            for qid in ids:
                for tiny in ([False,True] if qid=='H05' else [False]):
                    case=qid+('-tiny-exploration' if tiny else '')
                    counts={'processed_bytes_read':0,'native_original_bytes_read':0,'source_read_calls':0}
                    original_read=sorter._read;rb=Path.read_bytes;rt=Path.read_text
                    def processed_read(root,path,limit):
                        data=original_read(root,path,limit)
                        if Path(root).resolve()==rawdir.resolve() and data is not None:
                            counts['processed_bytes_read']+=len(data);counts['source_read_calls']+=1
                        return data
                    def byte_read(path,*args,**kwargs):
                        value=rb(path,*args,**kwargs)
                        if path.resolve().is_relative_to(ledger):counts['native_original_bytes_read']+=len(value);counts['source_read_calls']+=1
                        return value
                    def text_read(path,*args,**kwargs):
                        value=rt(path,*args,**kwargs)
                        if path.resolve().is_relative_to(ledger):counts['native_original_bytes_read']+=len(value.encode('utf-8'));counts['source_read_calls']+=1
                        return value
                    start=time.perf_counter();cpu=time.process_time()
                    with patch.object(sorter,'_read',processed_read),patch.object(Path,'read_bytes',byte_read),patch.object(Path,'read_text',text_read):
                        result=build(graph,rawdir,ledger,question=questions[qid],max_passages=1 if tiny else 24,max_chars=20 if tiny else 16000)
                        built=time.perf_counter();built_cpu=time.process_time()
                        verified=verify_workspace(result,graph,rawdir,ledger)
                    costs=dict(counts,build_wall_seconds=built-start,build_cpu_seconds=built_cpu-cpu,
                        replay_wall_seconds=time.perf_counter()-built,replay_cpu_seconds=time.process_time()-built_cpu,
                        peak_process_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,
                        rss_scope='Process lifetime high-water mark, not incremental memory per case.',api_usd=0,
                        compute_price_usd=None,human_review_seconds=None)
                    save(output/(case+'.json'),result)
                    row={'id':case,'family':family,'question':questions[qid],
                        'ownership':result['mplpb_decision']['status'],
                        'strict_answer_supported':(result['mplpb_decision']['strict_answer'] or {}).get('answer_supported',False),
                        'processed_passages':len(result['processed_passages']),'candidate_kinds':dict(Counter(c['kind'] for c in result['candidates'])),
                        'unmatched_passages':len(result['unmatched_passages']),'unresolved_references':len(result['unresolved_references']),
                        'budgets':result['exploration_budget'],'fresh_replay':verified,'costs':costs,
                        'workspace_sha256':sha((output/(case+'.json')).read_bytes()),'semantic_accuracy':'UNASSESSED'}
                    rows.append(row);save(output/(case+'-receipt.json'),row);print(case,row['ownership'],row['processed_passages'],row['candidate_kinds'],flush=True)
    save(output/'run.json',{'schema':'candidate-workspace-public-development-v1','runtime_revision':protocol['reader_revision'],
        'runtime_sha256':protocol['reader_sha256'],'cases':rows,'independent_human_evaluation':'NOT RUN',
        'unseen_evaluation':'NOT RUN','source_relationship_precision':None,'source_relationship_recall':None,
        'meaning':'Actual development exploration and fresh byte/eligibility/decision replay. Proposed matches are not historical semantic judgments. Logical reads are not physical disk traffic.'})


if __name__=='__main__':main()
