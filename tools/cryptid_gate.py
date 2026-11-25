"""Retain one actual integration command, status and bounded process lifetime."""
import argparse,datetime,hashlib,json,os,signal,subprocess,time
from pathlib import Path

def main(a):
 out=a.output/a.name;out.mkdir(parents=True,exist_ok=False);started=time.monotonic();status='ATTEMPTED';code=None;error=None
 command=a.command[1:] if a.command[:1]==['--'] else a.command
 record={'schema':'cryptid-integration-gate-v1','name':a.name,'command':command,'cwd':str(a.root),'timeout_seconds':a.timeout,'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source':'Clean committed source ZIP extraction; no checkout tests substituted.'}
 with (out/'output.log').open('xb') as log:
  try:
   proc=subprocess.Popen(command,cwd=a.root,stdout=log,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL,start_new_session=True)
   try:code=proc.wait(timeout=a.timeout);status='PASS' if code==0 else 'FAIL'
   except subprocess.TimeoutExpired:
    status='BLOCKED_TIMEOUT';os.killpg(proc.pid,signal.SIGTERM)
    try:proc.wait(timeout=5)
    except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL);proc.wait()
    code=proc.returncode
  except Exception as exc:status='BLOCKED_LAUNCH';error=str(exc)
 record.update(status=status,returncode=code,error=error,wall_seconds=time.monotonic()-started,raw_log_sha256=hashlib.file_digest((out/'output.log').open('rb'),'sha256').hexdigest())
 with (out/'record.json').open('x') as f:json.dump(record,f,indent=2)
 print(json.dumps(record));return 0 if status=='PASS' else 2
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--name',required=True);p.add_argument('--timeout',type=int,default=900);p.add_argument('command',nargs=argparse.REMAINDER);raise SystemExit(main(p.parse_args()))
