"""Freeze and replay unchanged pre-existing selector controls across revisions."""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from tools.cryptid_trial import save,read,sha
MODULES=['tests.test_field_question_forms','tests.test_compound_fields','tests.test_field_aliases']


def freeze(a):
    rows=[]
    for module in MODULES:
        path=Path(module.replace('.','/')+'.py');assert sha(ROOT/path)==sha(a.baseline/path)
        tree=ast.parse((ROOT/path).read_text())
        for cls in tree.body:
            if not isinstance(cls,ast.ClassDef):continue
            for method in sorted((n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')),key=lambda n:n.name):
                rows.append({'id':f'CRYPT-JACKALOPE-{len(rows)+55:04d}','test_id':module+'.'+cls.name+'.'+method.name,'source':str(path),'source_sha256':sha(ROOT/path),'originating_test':module+'.'+cls.name+'.'+method.name,'protected_operation':'Explicit record/field selectors, compound obligations, source aliases, eligibility and original question preservation','expectation':'Unchanged authored unittest assertions; do not infer independent historical evidence'})
    save(a.output,{'schema':'cryptid-existing-controls-v1','baseline_commit':'42a61f3df4089dd42c126fd1a9c948faf5e6d321','modules':MODULES,'cases':rows,'harness_sha256':sha(Path(__file__))})


def run(a):
    frozen=read(a.registry);assert sha(Path(__file__))==frozen['harness_sha256']
    for row in frozen['cases']:assert sha(a.implementation/row['source'])==row['source_sha256']
    a.output.mkdir(parents=True,exist_ok=False)
    program='''import json,sys,unittest
class Result(unittest.TextTestResult):
 def __init__(self,*a,**k):super().__init__(*a,**k);self.rows=[]
 def addSuccess(self,t):super().addSuccess(t);self.rows.append({'id':t.id(),'outcome':'PASS'})
 def addFailure(self,t,e):super().addFailure(t,e);self.rows.append({'id':t.id(),'outcome':'FAIL'})
 def addError(self,t,e):super().addError(t,e);self.rows.append({'id':t.id(),'outcome':'ERROR'})
 def addSkip(self,t,r):super().addSkip(t,r);self.rows.append({'id':t.id(),'outcome':'NOT_RUN','reason':r})
r=unittest.TextTestRunner(verbosity=2,resultclass=Result).run(unittest.defaultTestLoader.loadTestsFromNames(json.loads(sys.argv[1])))
print(json.dumps({'rows':r.rows,'completed':r.testsRun,'failed':len(r.failures)+len(r.errors),'skips':len(r.skipped),'success':r.wasSuccessful()}))
sys.exit(not r.wasSuccessful())'''
    result=subprocess.run([sys.executable,'-B','-c',program,json.dumps(frozen['modules'])],cwd=a.implementation,capture_output=True,text=True)
    (a.output/'stdout.log').write_text(result.stdout);(a.output/'stderr.log').write_text(result.stderr)
    if not result.stdout.strip():raise ValueError('Control execution failed before outcome production')
    record=json.loads(result.stdout.splitlines()[-1]);assert {r['id'] for r in record['rows']}=={r['test_id'] for r in frozen['cases']}
    record.update(source_commit=a.source_commit,registry_sha256=sha(a.registry),harness_sha256=sha(Path(__file__)),returncode=result.returncode,execution_status='completed',kind='Unchanged existing software controls, not fresh transfer')
    save(a.output/'record.json',record);print(record['completed'],record['failed'],record['skips'])
    if result.returncode:raise SystemExit(result.returncode)

if __name__=='__main__':
    p=argparse.ArgumentParser();sub=p.add_subparsers(dest='command',required=True)
    f=sub.add_parser('freeze');f.add_argument('--baseline',type=Path,required=True);f.add_argument('--output',type=Path,required=True)
    r=sub.add_parser('run')
    for n in ('registry','implementation','output'):r.add_argument('--'+n,type=Path,required=True)
    r.add_argument('--source-commit',required=True);a=p.parse_args();(freeze if a.command=='freeze' else run)(a)
