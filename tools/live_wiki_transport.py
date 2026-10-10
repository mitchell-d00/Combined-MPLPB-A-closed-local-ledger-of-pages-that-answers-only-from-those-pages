"""Paced live Wikipedia transport for the Node/WASM development runner only."""
import datetime
import fcntl
import hashlib
import json
import pathlib
import subprocess
import sys
import time
from email.utils import parsedate_to_datetime

url,target,cache_dir=sys.argv[1:]
cache=pathlib.Path(cache_dir);cache.mkdir(parents=True,exist_ok=True)
key=hashlib.sha256(url.encode()).hexdigest();body=cache/(key+'.json');meta=cache/(key+'.meta.json')
with (cache/'lock').open('w') as lock:
    fcntl.flock(lock,fcntl.LOCK_EX)
    if body.exists() and meta.exists():
        metadata=json.loads(meta.read_text());metadata['cached_from_this_live_run']=True
        pathlib.Path(target).write_bytes(body.read_bytes());print(json.dumps(metadata));raise SystemExit
    pace=cache/'next.json';deadline=json.loads(pace.read_text()) if pace.exists() else 0
    while deadline>time.time():time.sleep(min(20,deadline-time.time()))
    started=time.time();headers=cache/(key+'.headers')
    result=subprocess.run(['curl','--silent','--show-error','--max-time','40','--user-agent',
        'MPLPB-development-smoke/1.0 (public repository: mitchell-d00/Combined-MPLPB)',
        '--dump-header',str(headers),'--output',target,'--write-out','%{http_code}',url],capture_output=True,text=True)
    status=int(result.stdout or 0);retry=0
    if status==429:
        retry=60
        for line in headers.read_text().splitlines():
            if line.lower().startswith('retry-after:'):
                value=line.split(':',1)[1].strip()
                try:retry=max(1,int(value))
                except ValueError:
                    try:retry=max(1,int(parsedate_to_datetime(value).timestamp()-time.time()))
                    except ValueError:pass
        retry=min(retry,3600)
    pace.write_text(json.dumps(max(started+2.1,time.time()+retry)))
    metadata={'url':url,'retrieved_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'http_status':status,'content_type':'application/json','transport':'paced-live-curl-for-node-wasm',
              'cached_from_this_live_run':False,'retry_after_seconds':retry}
    if status==200 and result.returncode==0:
        body.write_bytes(pathlib.Path(target).read_bytes());meta.write_text(json.dumps(metadata))
    if result.returncode:metadata['error']=result.stderr.strip()
    print(json.dumps(metadata))
