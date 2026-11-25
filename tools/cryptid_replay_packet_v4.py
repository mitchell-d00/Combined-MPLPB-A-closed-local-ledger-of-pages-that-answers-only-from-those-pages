"""Replay consumed packet bytes as development; this is never fresh transfer."""
import argparse
from pathlib import Path
import shutil
import tempfile
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from tools import cryptid_trial_v4 as trial


def main(a):
    with tempfile.TemporaryDirectory(prefix='cryptid-consumed-',dir='/workspace/cryptid-custody') as tmp:
        root=Path(tmp)/'packet';shutil.copytree(a.packet,root)
        frozen=trial.read(root/'freeze.json')
        for name,expected in frozen['harness'].items():
            assert trial.sha(ROOT/name)==expected
            dst=root/name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,dst)
        trial.ROOT=root
        trial.run(argparse.Namespace(registry=root/'registry.json',implementation=a.implementation,source_commit=a.source_commit,output=a.output))
        trial.save(a.output/'exposure.json',{'purpose':'Consumed transfer now development/preservation; no new transfer claim','original_registry_sha256':trial.sha(a.packet/'registry.json')})

if __name__=='__main__':
    p=argparse.ArgumentParser()
    for n in ('packet','implementation','output'):p.add_argument('--'+n,type=Path,required=True)
    p.add_argument('--source-commit',required=True);main(p.parse_args())
