"""Append exact unittest outcomes for the separately indexed preservation gates."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
HOME=ROOT/'evaluation/bubble-wrap/2026-11-25'
GROUPS={
 'focused':['tests.test_source_attributed_instructions','tests.test_signed_instructions',
            'tests.test_documentary_named_advice','tests.test_documentary_presentation',
            'tests.test_documentary_errata','tests.test_pole_focus_extend'],
 'integrity':['tests.test_status_authority','tests.test_record','tests.test_ledger','tests.test_integrity_hunt',
              'tests.test_literal_evidence','tests.test_answer_reliability','tests.test_answer_support','tests.test_witness_admission'],
 'guards':['tests.test_reported_content'], 'accounting':['tests.test_bubble_wrap_accounting']}


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def save(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x') as f:f.write(json.dumps(value,indent=2)+'\n')
def cases(suite):
    for test in suite:
        if isinstance(test,unittest.TestSuite):yield from cases(test)
        else:yield test


class Result(unittest.TextTestResult):
    def __init__(self,*args,**kwargs):super().__init__(*args,**kwargs);self.outcomes=[]
    def addSuccess(self,test):super().addSuccess(test);self.outcomes.append({'id':test.id(),'outcome':'PASS'})
    def addFailure(self,test,err):super().addFailure(test,err);self.outcomes.append({'id':test.id(),'outcome':'FAIL'})
    def addError(self,test,err):super().addError(test,err);self.outcomes.append({'id':test.id(),'outcome':'ERROR'})
    def addSkip(self,test,reason):super().addSkip(test,reason);self.outcomes.append({'id':test.id(),'outcome':'NOT_RUN','reason':reason})


def main(a):
    path=HOME/'native-test-registry.json'
    if a.command=='prepare':
        rows=[]
        for group,names in GROUPS.items():
            for test in cases(unittest.defaultTestLoader.loadTestsFromNames(names)):
                module=test.__class__.__module__;source=module.replace('.','/')+'.py'
                rows.append({'id':'BW-'+group.upper()+'-'+test.id(),'unittest_id':test.id(),'family':group,
                 'origin_prs':[103] if group in {'guards','accounting'} else [97,101,102] if group=='focused' else [1,11],
                 'protected_rule':{'focused':'Instruction/assessment/presentation/erratum proof preservation',
                    'integrity':'Validate status, hash, lineage, eligibility and witness prerequisites',
                    'guards':'Report role/polarity, source state, counterevidence, mutation and fixed limits',
                    'accounting':'Distinguish execution, scoring and planned work'}[group],
                 'frozen_input':source,'frozen_input_sha256':sha(ROOT/source),'baseline_pin':'5bef945e401f96a6422bb8c468932d330b705fc4',
                 'reproduction_command':'python -m unittest '+test.id()+' -v',
                 'raw_output_and_candidate_pin':'Join unittest_id to immutable native-gates records',
                 'custody':'Same operator; software controls, not independent semantic adjudication',
                 'status_at_freeze':'PLANNED; not a pass','budgets':'Existing native guards and per-test fixtures; reader caps unchanged'})
        save(path,{'cases':rows});print('Frozen native tests',len(rows));return
    registry=json.loads(path.read_text())
    selected=[r for r in registry['cases'] if r['family']==a.group]
    for row in selected:assert sha(ROOT/row['frozen_input'])==row['frozen_input_sha256']
    a.output.mkdir(parents=True,exist_ok=False)
    with (a.output/'output.log').open('w') as stream:
        result=unittest.TextTestRunner(stream=stream,verbosity=2,resultclass=Result).run(
            unittest.defaultTestLoader.loadTestsFromNames(GROUPS[a.group]))
    assert {r['id'] for r in result.outcomes}=={r['unittest_id'] for r in selected}
    save(a.output/'record.json',{'group':a.group,'source_commit':a.source_commit,'execution_status':'completed',
         'registry_sha256':sha(path),'returncode':0 if result.wasSuccessful() else 1,
         'planned':len(selected),'completed':result.testsRun,'rows':result.outcomes,
         'passed':sum(r['outcome']=='PASS' for r in result.outcomes),
         'failed':sum(r['outcome'] in {'FAIL','ERROR'} for r in result.outcomes),
         'not_run':sum(r['outcome']=='NOT_RUN' for r in result.outcomes),
         'acceptance_passed':result.wasSuccessful() and not result.skipped,'raw_log_sha256':sha(a.output/'output.log')})
    print(a.group,result.testsRun,'tests',len(result.failures),'failures',len(result.errors),'errors',len(result.skipped),'skipped')
    return int(not result.wasSuccessful())


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('command',choices=['prepare','run'])
    p.add_argument('--group',choices=GROUPS);p.add_argument('--source-commit');p.add_argument('--output',type=Path)
    raise SystemExit(main(p.parse_args()))
