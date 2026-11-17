"""Retain offline sorter mode/gate checks; fictional fixtures, no accuracy score.

Run from a frozen checkout: python -m tools.evaluate_sorter --output NEW_DIRECTORY
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import resource
import subprocess
import sys
import time


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args(argv)
    root=Path(__file__).resolve().parents[1];out=args.output.resolve()
    if out==root or root in out.parents:raise ValueError('Output must be outside source checkout')
    out.mkdir(parents=True,exist_ok=False)
    report={'schema':'sorter-development-checks-v1','revision':subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip() if (root/'.git').exists() else None,
            'environment':{'platform':platform.platform(),'python':sys.version,'cpu_count':os.cpu_count()},
            'harness_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'commands':[],'independent_review':'NOT RUN','historical_accuracy':None,'human_review_seconds':None}
    def save(): (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    def run(args,name,expected=0):
        before=resource.getrusage(resource.RUSAGE_CHILDREN);start=time.perf_counter()
        timed_out=False
        try:result=subprocess.run(args,cwd=root,capture_output=True,text=True,timeout=60)
        except subprocess.TimeoutExpired as exc:
            timed_out=True
            def decoded(value):return value.decode('utf-8',errors='replace') if isinstance(value,bytes) else value or ''
            result=subprocess.CompletedProcess(args,None,decoded(exc.stdout),decoded(exc.stderr))
        after=resource.getrusage(resource.RUSAGE_CHILDREN)
        (out/(name+'.log')).write_text(result.stdout+result.stderr)
        report['commands'].append({'command':args,'exit_code':result.returncode,'expected_exit_code':expected,'timed_out':timed_out,
            'wall_seconds':time.perf_counter()-start,'cpu_seconds':after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime,
            'peak_child_rss_bytes':after.ru_maxrss*(1 if sys.platform=='darwin' else 1024),
            'peak_memory_scope':'Process-lifetime maximum child RSS, not isolated incremental or process-tree memory.','log':name+'.log'})
        save()
        if result.returncode!=expected:raise RuntimeError(name+' failed; see retained log')
        return result.stdout
    for mode in ('not-compared','compare'):
        run([sys.executable,'-m','mplpb_work.sorter','sort','tests/fixtures/sorter','--mode',mode,'--output',str(out/(mode+'.json'))],mode)
    a=json.loads((out/'not-compared.json').read_text());b=json.loads((out/'compare.json').read_text())
    report['mode_audit']={'identical_nodes':a['nodes']==b['nodes'],'identical_sources':a['sources']==b['sources'],
        'identical_raw_edge_prefix':a['edges']==b['edges'][:len(a['edges'])],
        'nodes':len(a['nodes']),'raw_edges':len(a['edges']),'compare_edges':len(b['edges']),
        'all_added_edges_comparison_only':all(e['comparison_only'] for e in b['edges'][len(a['edges']):]),
        'source_bytes_read_per_mode':a['source_bytes_read'],'implementation_sha256':a['implementation_sha256']}
    save()
    if not all(report['mode_audit'][k] for k in ('identical_nodes','identical_sources','identical_raw_edge_prefix','all_added_edges_comparison_only')):raise RuntimeError('Mode invariant failed')
    run([sys.executable,'-m','mplpb_work.sorter','verify',str(out/'compare.json'),'--sources','tests/fixtures/sorter'],'verify')
    run([sys.executable,'-m','mplpb_work.sorter','export-retired',str(out/'compare.json'),'--sources','tests/fixtures/sorter','--ledger',str(out/'ledger')],'export-retired')
    # Gate directly inspects every non-index record, independently of answer grammar.
    from mplpb_combined.provenance_gate import gather
    from mplpb_combined.reader import PROFILES
    from mplpb_combined.ledger import Ledger
    record=next(r for r in Ledger(out/'ledger').records if r.id=='SORTER-CANDIDATES')
    assert record.intact and record.status=='retired'
    report['gate_audit']={}
    for profile in ('lab','internal','external'):
        gate=gather(out/'ledger','sorter candidate inspection',PROFILES[profile])
        assert not gate.sources
        exclusion=next(x for x in gate.excluded if x['id']=='SORTER-CANDIDATES')
        if profile!='external':assert exclusion['reason']=='retired'
        report['gate_audit'][profile]={'eligible_sources':0,'exclusion':exclusion}
        result=json.loads(run([sys.executable,'-m','mplpb_answers','ask',str(out/'ledger'),'What is Owner for record MAIL-001?','--profile',profile,'--json'],'reader-'+profile,3))
        assert result['answer_supported'] is False and result['answer_contract']['claims']==[]
    run([sys.executable,'-m','unittest','tests.test_sorter','-q'],'sorter-tests')
    report['passed']=True;save();print(json.dumps({'report':str(out/'report.json'),'passed':True}))
    return 0


if __name__=='__main__':raise SystemExit(main())
