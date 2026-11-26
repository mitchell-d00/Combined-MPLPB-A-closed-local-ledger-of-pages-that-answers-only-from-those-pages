"""Run the README block verbatim in an empty directory; retain real CLI output.

This is software documentation verification, never simulated human usability.
Network is used only to download the public release named by the README.
"""
import argparse,hashlib,json,os,re,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(args):
    args.work.mkdir(parents=True,exist_ok=False);args.output.mkdir(parents=True,exist_ok=False)
    text=(ROOT/'README.md').read_text();block=re.search(r'<!-- quickstart:start -->\s*```sh\n(.*?)\n```\s*<!-- quickstart:end -->',text,re.S)[1]
    (args.output/'commands.sh').write_text(block+'\n')
    env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'};env.pop('PYTHONPATH',None)
    p=subprocess.run(['bash','-x','-c',block],cwd=args.work,env=env,text=True,capture_output=True,timeout=120)
    (args.output/'stdout.txt').write_text(p.stdout);(args.output/'stderr.txt').write_text(p.stderr)
    checks={'readme_under_180_lines':len(text.splitlines())<180,'script_expected_refusal_exit':p.returncode==3,'fresh_write':'wrote DOC-0001' in p.stdout,'supported_output':'SUPPORTED ANSWER\nOpening time: 09:00.\n' in p.stdout,'missing_output':'NO SUPPORTED ANSWER\nNot in the corpus.\n' in p.stdout,'no_traceback':'Traceback' not in p.stderr,'wheel_installed':(args.work/'.venv/bin/mplpb-combined').exists()}
    more=[];executable=str(args.work/'.venv/bin/mplpb-combined')
    def cli(tokens):
        q=subprocess.run([executable,*tokens],cwd=args.work,env=env,text=True,capture_output=True,timeout=30);more.append({'command':['mplpb-combined',*tokens],'exit_code':q.returncode,'stdout':q.stdout,'stderr':q.stderr});return q
    q=cli(['ask','demo-ledger','When does the museum open?','--record-id','DOC-0001','--field','Opening time','--json']);a=json.loads(q.stdout)['answer_contract']
    # CLI JSON is the answer contract, including exact canonical witnesses.
    checks['exact_citation']=any(c['source_id']=='DOC-0001' and c['quote']=='Opening time: 09:00.' for claim in a['claims'] for c in claim['citations'])
    q=cli(['ask','demo-ledger','What are Opening time and Closing time for record DOC-0001?']);checks['partial_output']=q.returncode==3 and q.stdout.startswith('PARTIAL ANSWER\nOpening time [verified]\nClosing time [unresolved]')
    cli(['write','studio-ledger','--title','Blue Heron Studio','--scope','Blue Heron Studio ownership','--body','Mira Stone owns Blue Heron Studio.'])
    q=cli(['ask','studio-ledger','Who owns Blue Heron Studio?']);checks['owner_output']=q.returncode==0 and 'Mira Stone owns Blue Heron Studio.' in q.stdout
    cli(['write','studio-ledger','--title','Blue Heron Studio second account','--scope','Blue Heron Studio ownership','--body','Rowan Vale owns Blue Heron Studio.'])
    q=cli(['ask','studio-ledger','Who owns Blue Heron Studio?']);checks['conflict_output']=q.returncode==3 and q.stdout.startswith('CONFLICT') and all(s in q.stdout for s in ['Mira Stone','Rowan Vale'])
    (args.output/'additional-commands.json').write_text(json.dumps(more,indent=2)+'\n')
    receipt={'meaning':'Fresh released-wheel software verification; human onboarding NOT_RUN','readme_sha256':digest(ROOT/'README.md'),'script_sha256':digest(args.output/'commands.sh'),'python':sys.version,'command_exit_code':p.returncode,'download_sha256':digest(args.work/'mplpb-native.zip'),'wheel_sha256':{p.name:digest(p) for p in (args.work/'mplpb-native').glob('*.whl')},'checks':checks,'passed':all(checks.values())}
    (args.output/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2));return 0 if receipt['passed'] else 1
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--work',type=Path,required=True);p.add_argument('--output',type=Path,required=True);raise SystemExit(run(p.parse_args()))
