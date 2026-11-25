"""Check frozen onboarding artifacts without inventing human observations."""
import hashlib
import json
from pathlib import Path
import zipfile

ROOT=Path(__file__).resolve().parents[1]
HOME=ROOT/'evaluation/onboarding/2026-11-25'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def audit():
    frozen=read(HOME/'freeze.json')
    for name,expected in frozen['files'].items():assert sha(HOME/name)==expected,name
    assignment=read(HOME/'administrator-assignment.json')
    assert assignment['materials_freeze_sha256']==sha(HOME/'freeze.json')
    people=[p for group in assignment['groups'].values() for p in group]
    assert len(set(people))==12 and all(len(v)==6 for v in assignment['groups'].values())
    packages=read(HOME/'packages/packages.json');entries={}
    for arm,description in packages['packages'].items():
        path=HOME/'packages'/description['file'];assert sha(path)==description['sha256']
        with zipfile.ZipFile(path) as z:
            assert len(z.namelist())==len(set(z.namelist()))
            entries[arm]={n:hashlib.sha256(z.read(n)).hexdigest() for n in z.namelist()}
        assert entries[arm]==description['entries']
    assert set(entries['existing'])==set(entries['new_path'])
    differences=sorted(p for p,v in entries['existing'].items() if v!=entries['new_path'][p])
    assert differences==['ENTRY.html','ENTRY.md']
    parity=read(HOME/'software-checks/bundle-parity.json')
    assert parity['raw_contracts_identical'] and parity['engine_and_collection_identical']
    assert parity['actual_human_observations'] is None
    results=read(HOME/'results.json')
    if results['execution_status']=='NOT_RUN':
        assert results['participants_observed'] is None and results['acceptance_passed'] is None
    return {'frozen_materials':'PASS','package_parity':'PASS','only_differences':differences,
            'human_execution':results['execution_status'],'human_results_not_inferred_from_software':True}

if __name__=='__main__':print(json.dumps(audit(),indent=2))
