"""Measure bounded postprocessing independently of query-worker costs."""
import argparse
import json
from pathlib import Path
import resource
import subprocess
import sys
import time
p=argparse.ArgumentParser();p.add_argument('corpus');p.add_argument('before');p.add_argument('after');p.add_argument('--output',required=True);p.add_argument('--metrics',required=True);args=p.parse_args()
command=[sys.executable,'-m','tools.compare_documentary_scope',args.corpus,args.before,args.after,'--output',args.output]
start=time.perf_counter();before=resource.getrusage(resource.RUSAGE_CHILDREN)
metrics={'command':command,'wall_budget_seconds':600,'source_bytes_read':None,'independent_review':'NOT RUN'}
with Path(args.metrics+'.log').open('x') as log:
    try:
        result=subprocess.run(command,stdout=log,stderr=log,timeout=600,check=False)
        metrics.update(status='completed' if result.returncode==0 else 'failed',exit_code=result.returncode)
    except subprocess.TimeoutExpired:
        metrics.update(status='timed_out',exit_code=None)
after=resource.getrusage(resource.RUSAGE_CHILDREN)
metrics.update(wall_seconds=time.perf_counter()-start,cpu_seconds=after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime,
               peak_process_rss_bytes=after.ru_maxrss*1024,scope='Fresh Linux audit child including imports; separate from query-worker costs. Source read bytes not instrumented.')
with Path(args.metrics).open('x') as stream:json.dump(metrics,stream,indent=2)
if metrics['status']!='completed':raise SystemExit(1)
