"""Use the unchanged isolated reader harness on a publicly frozen synthetic arm."""
import argparse
import re
import subprocess
import sys
from pathlib import Path
from zipfile import ZipFile

from tools.cryptid_trial_v5 import read, sha

HOME = Path(__file__).resolve().parent
ROOT = HOME.parents[3]
PACKAGES = ('mplpb_answers','mplpb_combined','mplpb_work')


def verify(phase):
    home=HOME/phase
    seal=read(home/'freeze.json')
    registry=home/'registry.json'
    assert seal['public_raw_output'] is True and sha(registry)==seal['registry_sha256']
    assert all(sha(ROOT/name)==value for name,value in seal['harness'].items())
    rows=read(registry)['cases']
    assert len(rows)==len({r['id'] for r in rows})==8
    for row in rows:
        ident=row['id']
        assert re.fullmatch('BUNYIP-R4-'+phase[0].upper()+r'0[1-8]',ident)
        packet=home/'inputs'/ident
        assert str(packet.relative_to(ROOT))==row['packet'] and {p.name for p in packet.iterdir()}=={'case.json'}
        case=packet/'case.json'
        assert not case.is_symlink() and sha(case)==row['files']['case.json']
        value=read(case)
        assert value['id']==ident and value['adapter_mode']=='documentary' and value['profile']=='internal'
        assert 1<=len(value['sources'])<=2
        for source in value['sources']:
            assert source['origin']=='machine' and source['title']=='Synthetic documentary record'
            assert set(source)=={'id','title','origin','external','when','body_html'}
    return registry


def run(phase, out, staging):
    registry=verify(phase)
    pins={'baseline':read(registry.with_name('freeze.json'))['baseline']}
    if phase=='fresh':
        pins['candidate']=read(HOME/'dispatch.json')['candidate']
    out.mkdir()
    staging.mkdir()
    failures=[]
    for role,pin in pins.items():
        revision=pin['commit']
        assert re.fullmatch(r'[a-f0-9]{40}',revision)
        runtime=staging/role
        archive=out/f'{role}-runtime.zip'
        with (out/f'{role}.log').open('x') as log:
            subprocess.run(['git','fetch','--no-tags','--depth=1','origin',revision],
                           stdout=log, stderr=subprocess.STDOUT, check=True)
            subprocess.run(['git','archive','--format=zip','-0','-o',str(archive),revision,*PACKAGES],check=True)
            assert sha(archive)==pin['zip_sha256']
            with ZipFile(archive) as zipped:
                zipped.extractall(runtime)
            log.flush()
            result=subprocess.run(['sudo','env',f'PYTHONPATH={ROOT}','MPLPB_REQUIRE_SANDBOX=1',
                sys.executable,'-m','tools.cryptid_trial_v5','--registry',str(registry),
                '--implementation',str(runtime),'--source-commit',revision,'--output',str(out/role)],
                stdout=log, stderr=subprocess.STDOUT)
            failures.append(result.returncode)
    return int(any(failures))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('phase', choices=('diagnostic','fresh'))
    parser.add_argument('--output', type=Path)
    parser.add_argument('--work', type=Path)
    args=parser.parse_args()
    if not args.output:
        verify(args.phase)
    else:
        raise SystemExit(run(args.phase,args.output.resolve(),args.work.resolve()))
