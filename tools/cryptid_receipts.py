"""Retain local preservation receipts without redistributing restricted originals."""
import argparse
from pathlib import Path
import shutil
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from tools.cryptid_trial import read,save,sha


def retain(source,target):
    registry={r['id']:r for r in read(ROOT/'evaluation/bubble-wrap/2026-11-25/continuation/development.json')['cases']}
    target.mkdir(parents=True,exist_ok=False);run=read(source/'run.json')
    for row in run['rows']:
        ident=row['id'];out=target/ident;out.mkdir();original=source/ident
        for name in ('stdout.log','stderr.log','process.json','execution.json'):
            if (original/name).exists():shutil.copyfile(original/name,out/name)
        if (original/'result.json').exists():
            if registry[ident]['public_raw_output']:shutil.copyfile(original/'result.json',out/'result.json')
            else:save(out/'private-raw.json',{'id':ident,'sha256':sha(original/'result.json'),'custody':'Restricted originals and raw output retained in existing operator custody, not redistributed.','semantic_scoring':'NOT independent; score links retained separately'})
        shutil.copyfile(source/(ident+'.record.json'),target/(ident+'.record.json'))
    shutil.copyfile(source/'run.json',target/'run.json')
    save(target/'custody.json',{'source_run_sha256':sha(source/'run.json'),'public_raw':263,'restricted_raw_receipts':17,'local_only':True})

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--target',type=Path,required=True);a=p.parse_args();retain(a.source,a.target)
