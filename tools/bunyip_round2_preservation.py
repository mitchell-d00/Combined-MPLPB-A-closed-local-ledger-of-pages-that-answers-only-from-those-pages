"""Orchestrate existing frozen Cryptid runners; no worker, key or scoring change."""
import argparse, concurrent.futures, hashlib, json, subprocess, sys, tarfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from tools.cryptid_preserve_all import COHORTS
from tools.bubble_wrap_trial import normal
def main(a):
    a.output.mkdir(parents=True,exist_ok=False)
    reference=a.output/'released-reference'
    archive=ROOT/'evaluation/cryptid/bunyip/round2/released-849-reference-v1.tar.xz'
    assert hashlib.sha256(archive.read_bytes()).hexdigest()=='71bd781c5a10041652a6b83d7d4b29ff30042f79006c00c7f5301b75fc1ae7a2'
    with tarfile.open(archive) as t:t.extractall(reference,filter='data')
    specs=[]
    for name,tool,packet,_ in COHORTS:
        flag='--packet' if 'replay' in tool else '--registry'
        specs.append(('prior419/'+name,tool,flag,packet if flag=='--packet' else packet+'/registry.json'))
    specs.append(('release280','bubble_wrap_trial.py','run',None))
    for name,tool,flag,packet in [
        ('thunderbird-development','cryptid_trial_v4.py','--registry','evaluation/cryptid/thunderbird/development/registry.json'),
        ('thunderbird-consumed','cryptid_replay_packet_v4.py','--packet','evaluation/cryptid/thunderbird/consumed-transfer'),
        ('boundary-wrap','cryptid_trial_v5.py','--registry','evaluation/cryptid/nessie/layout-wrap/registry.json'),
        ('initial-final24','cryptid_replay_packet_v5.py','--packet','evaluation/cryptid/final/consumed-transfer'),
        ('second-final16','cryptid_replay_packet_v5.py','--packet','evaluation/cryptid/final/fresh2/consumed-transfer'),
        ('rev3-reporting','cryptid_trial_v5.py','--registry','evaluation/cryptid/revision3/reporting-development/registry.json'),
        ('rev3-shell','cryptid_trial_v5.py','--registry','evaluation/cryptid/revision3/reporting-shell-wrap/registry.json'),
        ('rev3-budget','cryptid_trial_v5.py','--registry','evaluation/cryptid/revision3/reporting-budget-wrap/registry.json'),
        ('rev3-compatibility','cryptid_trial_v5.py','--registry','evaluation/cryptid/revision3/reporting-compatibility-wrap/registry.json'),
        ('rev3-policy','cryptid_trial_v5.py','--registry','evaluation/cryptid/revision3/partial-policy-development/registry.json'),
        ('third-final24','cryptid_replay_packet_v5.py','--packet','evaluation/cryptid/revision3/fresh/consumed-transfer')]:
        specs.append((name,tool,flag,packet))
    def execute(spec):
        name,tool,flag,packet=spec
        output=a.output/'candidate'/name
        command=[sys.executable,'tools/'+tool]
        if packet:command += [flag,packet]
        else:command += ['run','--phase','candidate','--transfer-manifest','evaluation/bubble-wrap/2026-11-25/continuation/development.json']
        command += ['--implementation',str(ROOT),'--source-commit',a.source_commit,'--output',str(output)]
        log=a.output/'logs'/(name.replace('/','-')+'.log');log.parent.mkdir(exist_ok=True)
        with log.open('x') as stream:
            p=subprocess.run(command,cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT)
        print(name,p.returncode,flush=True)
        return {'cohort':name,'command':command,'returncode':p.returncode}
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        attempts=list(pool.map(execute,specs))
    expected=sorted(reference.rglob('result.json'))
    assert len(expected)==849
    rows=[]
    for before in expected:
        relative=before.relative_to(reference)
        after=a.output/'candidate'/relative
        row={'case':str(relative),'execution_status':'failed','strict_contract_equal':False}
        if after.exists():
            left=json.loads(before.read_text());right=json.loads(after.read_text())
            if isinstance(right.get('answer'),dict):
                old=left['answer'];new=right['answer']
                row.update(execution_status='completed',strict_contract_equal=normal(old)==normal(new),
                    before_supported=old['answer_supported'],after_supported=new['answer_supported'],
                    before_kind=old['kind'],after_kind=new['kind'],
                    before_sha256=hashlib.sha256(before.read_bytes()).hexdigest(),
                    after_sha256=hashlib.sha256(after.read_bytes()).hexdigest())
        rows.append(row)
    result={'schema':'bunyip-preservation-execution-v1','candidate_commit':a.source_commit,
        'reference_reader_revision':'2622813aba9ee1f1880693eeb71ae015cb3da999',
        'scope':'Consumed preservation; exact whole-contract comparison except existing code_sha256 exclusion. Changed contracts require separate source audit.',
        'attempts':attempts,'cases':rows,
        'counts':{'planned':len(rows),'completed':sum(r['execution_status']=='completed' for r in rows),
                  'execution_failures':sum(r['execution_status']!='completed' for r in rows),
                  'strict_contract_equal':sum(r['strict_contract_equal'] for r in rows),
                  'changed_contracts':sum(r['execution_status']=='completed' and not r['strict_contract_equal'] for r in rows)}}
    (a.output/'comparison-v1.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result['counts']),flush=True)
    if result['counts']['execution_failures'] or any(x['returncode'] for x in attempts):raise SystemExit(2)
    if result['counts']['changed_contracts']:raise SystemExit(3)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--source-commit',required=True);main(p.parse_args())
