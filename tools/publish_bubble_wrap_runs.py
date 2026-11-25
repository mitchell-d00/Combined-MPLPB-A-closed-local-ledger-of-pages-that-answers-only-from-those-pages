"""Publish immutable receipts, withholding permission-reprinted original bytes."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

ROOT=Path(__file__).resolve().parents[1]
HOME=ROOT/'evaluation/bubble-wrap/2026-11-25'


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path):return json.loads(path.read_text())
def save(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x') as stream:stream.write(json.dumps(value,indent=2,ensure_ascii=False)+'\n')


def append(path,kind):
    path=path.resolve()
    directory=HOME/'run-ledger';directory.mkdir(exist_ok=True)
    previous=sorted(directory.glob('*.json'))
    for p in previous:
        if read(p)['record']==str(path.relative_to(ROOT)):raise ValueError('Record already appended')
    target=directory/f'{len(previous)+1:04d}.json'
    save(target,{'record':str(path.relative_to(ROOT)),'record_sha256':sha(path),'kind':kind,
                 'previous_sha256':sha(previous[-1]) if previous else None})


def publish(source,name):
    registry={r['id']:r for r in read(HOME/'registry.json')['cases']}
    target=HOME/'runs'/name;target.mkdir(parents=True,exist_ok=False)
    receipt=read(source/'run.json')
    for row in receipt['rows']:
        ident=row['id'];out=target/ident;out.mkdir()
        original=source/ident
        for filename in ('stdout.log','stderr.log','process.json','execution.json'):
            if (original/filename).exists():shutil.copyfile(original/filename,out/filename)
        if (original/'result.json').exists():
            if registry.get(ident,{}).get('public_raw_output',True):
                shutil.copyfile(original/'result.json',out/'result.json')
            else:
                save(out/'private-raw.json',{'id':ident,'private_raw_sha256':sha(original/'result.json'),
                     'custody':'Retained in operator custody; permission-reprinted original bytes not redistributed',
                     'public_score':'See immutable score row for full-contract/discovery comparison hashes',
                     'independent_semantic_adjudication':'NOT_RUN'})
        shutil.copyfile(source/(ident+'.record.json'),target/(ident+'.record.json'))
    shutil.copyfile(source/'run.json',target/'run.json')
    append(target/'run.json','execution')
    return target


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='command',required=True)
    q=sub.add_parser('run');q.add_argument('--source',type=Path,required=True);q.add_argument('--name',required=True)
    q=sub.add_parser('append');q.add_argument('--record',type=Path,required=True);q.add_argument('--kind',required=True)
    args=p.parse_args()
    if args.command=='run':print(publish(args.source,args.name).relative_to(ROOT))
    else:append(args.record,args.kind)
