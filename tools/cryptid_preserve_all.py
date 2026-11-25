"""Sequential preservation runs; prior transfer is consumed evidence, never fresh."""
import argparse,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from tools.cryptid_trial import read,save,sha
from tools.bubble_wrap_trial import normal
COHORTS=[('mothman-development','cryptid_trial.py','evaluation/cryptid/mothman/development','evaluation/cryptid/mothman/runs/candidate-5'),('mothman-first','cryptid_replay_packet.py','evaluation/cryptid/mothman/consumed-transfer','evaluation/cryptid/mothman/runs/consumed-development-c5'),('mothman-fresh','cryptid_replay_packet.py','evaluation/cryptid/mothman/fresh/consumed-transfer','evaluation/cryptid/mothman/runs/fresh-transfer-once'),('jackalope-development','cryptid_trial_v2.py','evaluation/cryptid/jackalope/development','evaluation/cryptid/jackalope/runs/candidate-1'),('jackalope-transfer','cryptid_replay_packet_v2.py','evaluation/cryptid/jackalope/consumed-transfer','evaluation/cryptid/jackalope/runs/transfer-once'),('yeti-development','cryptid_trial_v3.py','evaluation/cryptid/yeti/development','evaluation/cryptid/yeti/runs/candidate-2'),('yeti-wrap','cryptid_trial_v3.py','evaluation/cryptid/yeti/wrap','evaluation/cryptid/yeti/runs/wrap-candidate-2'),('yeti-transfer','cryptid_replay_packet_v3.py','evaluation/cryptid/yeti/consumed-transfer','evaluation/cryptid/yeti/runs/transfer-once')]
def main(a):
    a.output.mkdir(parents=True,exist_ok=False);rows=[]
    for name,tool,packet,before in COHORTS:
        before=ROOT/before
        if not (before/'run.json').exists():raise ValueError('Missing prior reference '+str(before))
        flag='--packet' if 'replay' in tool else '--registry';arg=packet if flag=='--packet' else packet+'/registry.json'
        command=[sys.executable,'tools/'+tool,flag,arg,'--implementation',str(a.implementation.resolve()),'--source-commit',a.source_commit,'--output',str((a.output/name).resolve())]
        with (a.output/(name+'.log')).open('x') as log:r=subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
        if r.returncode:raise RuntimeError((name,r.returncode))
        cmd=[sys.executable,'tools/cryptid_contract_preservation.py','--before',str(before),'--after',str(a.output/name),'--output',str(a.output/(name+'-score.json'))]
        scored=subprocess.run(cmd,cwd=ROOT);rows.append({'cohort':name,'run_sha256':sha(a.output/name/'run.json'),'score_sha256':sha(a.output/(name+'-score.json')),'returncode':scored.returncode});print(name,scored.returncode,flush=True)
    save(a.output/'prior-preservation.json',{'rows':rows,'source_commit':a.source_commit})
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--implementation',type=Path,required=True);p.add_argument('--source-commit',required=True);p.add_argument('--output',type=Path,required=True);main(p.parse_args())
