"""Append newly retained run/score records without rewriting previous attempts."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from tools.cryptid_trial import read,save,sha


def append():
    home=ROOT/'evaluation/cryptid';directory=home/'ledger';directory.mkdir(exist_ok=True)
    prior=sorted(directory.glob('*.json'));existing={}
    previous=None
    for p in prior:
        record=read(p);assert record['previous_sha256']==previous
        for entry in record['records']:
            assert entry['path'] not in existing
            assert sha(ROOT/entry['path'])==entry['sha256'],'Changed immutable run/score: '+entry['path']
            existing[entry['path']]=entry['sha256']
        previous=sha(p)
    paths={p:'reader_or_preservation_execution' for p in home.rglob('run.json')}
    for p in home.glob('*/scores/*.json'):paths[p]='score_or_contract_audit'
    for p in home.rglob('record.json'):paths[p]='native_control_execution'
    for p in home.glob('*/adapter-parity.json'):paths[p]='adapter_parity'
    rows=[]
    for p,kind in sorted(paths.items()):
        name=str(p.relative_to(ROOT))
        if name not in existing:rows.append({'path':name,'sha256':sha(p),'kind':kind})
    if not rows:raise ValueError('No new records')
    target=directory/f'{len(prior)+1:04d}.json'
    save(target,{'schema':'cryptid-immutable-ledger-v1','previous_sha256':previous,'records':rows,'publication':'LOCAL_ONLY','meaning':'Includes failures, misses, execution-only and unscored attempts; not a list of passes.'})
    programme=read(home/'programme.json');programme['run_ledger'].append(str(target.relative_to(home)))
    (home/'programme.json').write_text(__import__('json').dumps(programme,indent=2)+'\n')
    print(str(target.relative_to(ROOT)),len(rows),'records')

if __name__=='__main__':append()
