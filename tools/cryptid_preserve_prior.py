"""Sequential unchanged prior-family replays; consumed packets are preservation."""
import argparse
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from tools.cryptid_trial import save,sha


def main(a):
    a.output.mkdir(parents=True,exist_ok=False);rows=[]
    jobs=[('mothman-development','tools/cryptid_trial.py','--registry','evaluation/cryptid/mothman/development/registry.json'),
          ('mothman-first','tools/cryptid_replay_packet.py','--packet','evaluation/cryptid/mothman/consumed-transfer'),
          ('mothman-fresh','tools/cryptid_replay_packet.py','--packet','evaluation/cryptid/mothman/fresh/consumed-transfer'),
          ('jackalope-development','tools/cryptid_trial_v2.py','--registry','evaluation/cryptid/jackalope/development/registry.json'),
          ('jackalope-transfer','tools/cryptid_replay_packet_v2.py','--packet','evaluation/cryptid/jackalope/consumed-transfer')]
    for name,tool,flag,packet in jobs:
        cmd=[sys.executable,tool,flag,packet,'--implementation',str(a.implementation),'--source-commit',a.source_commit,'--output',str(a.output/name)]
        with (a.output/(name+'.log')).open('x') as log:result=subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
        rows.append({'cohort':name,'command':cmd,'returncode':result.returncode,'run_sha256':sha(a.output/name/'run.json') if (a.output/name/'run.json').exists() else None})
        print(name,result.returncode,flush=True)
    save(a.output/'prior-replay.json',{'source_commit':a.source_commit,'purpose':'Prior original and consumed-transfer preservation; no new transfer claim','rows':rows})
    if any(r['returncode'] for r in rows):raise SystemExit(2)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--implementation',type=Path,required=True);p.add_argument('--source-commit',required=True);p.add_argument('--output',type=Path,required=True);main(p.parse_args())
