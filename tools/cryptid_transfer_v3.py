"""Open a sealed same-operator packet once after a committed candidate ZIP freeze."""
import argparse
import json
from pathlib import Path
import shutil
import sys
import tempfile
import zipfile
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from tools import cryptid_trial_v3 as trial


def extract(archive,destination):
    with zipfile.ZipFile(archive) as z:
        for item in z.infolist():
            p=Path(item.filename)
            if p.is_absolute() or '..' in p.parts or item.external_attr>>16&0o170000==0o120000:
                raise ValueError('Unsafe ZIP path')
        if sum(i.file_size for i in z.infolist())>128*1024**2:raise ValueError('Scoped study archive too large')
        z.extractall(destination)


def main(a):
    seal=trial.read(a.home/'transfer-seal.json')
    packet=a.home/'transfer-sealed.zip';assert trial.sha(packet)==seal['packet_sha256']
    assert not (a.home/'transfer-open.json').exists(), 'Packet already opened; no second transfer run'
    frozen=trial.read(a.candidate_receipt)
    assert frozen['candidate_commit']==a.candidate_commit
    assert frozen['zip_sha256']==trial.sha(a.candidate_zip)
    trial.save(a.home/'transfer-open.json',{'candidate_commit':a.candidate_commit,'candidate_zip_sha256':trial.sha(a.candidate_zip),
              'candidate_receipt_sha256':trial.sha(a.candidate_receipt),'packet_sha256':trial.sha(packet),
              'custody':'same-operator; packet now opened and consumed, no independent blinding or adjudication',
              'run_once_output':str(a.output),'semantic_outcome':'NOT_RUN at opening'})
    with tempfile.TemporaryDirectory(prefix='cryptid-transfer-',dir='/workspace/cryptid-custody') as tmp:
        tmp=Path(tmp);implementation=tmp/'candidate';public=tmp/'packet';implementation.mkdir();public.mkdir()
        extract(a.candidate_zip,implementation);extract(packet,public)
        # Original packet paths are relative to its root. Preserve sealed
        # registry/key bytes; provide the unchanged frozen host harness there.
        freeze=trial.read(public/'freeze.json')
        for name,expected in freeze['harness'].items():
            assert trial.sha(implementation/name)==expected
            dst=public/name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(implementation/name,dst)
        assert all(trial.sha(implementation/p)==v for p,v in frozen['runtime_sha256'].items())
        trial.ROOT=public
        trial.run(argparse.Namespace(registry=public/'registry.json',implementation=implementation,
                  source_commit=a.candidate_commit,output=a.output))
        # Retain consumed packet and key outside workers for audit/scoring.
        destination=a.home/'consumed-transfer';assert not destination.exists()
        shutil.copytree(public,destination,ignore=shutil.ignore_patterns('tools'))

if __name__=='__main__':
    p=argparse.ArgumentParser()
    for n in ('home','candidate-zip','candidate-receipt','output'):p.add_argument('--'+n,type=Path,required=True)
    p.add_argument('--candidate-commit',required=True);main(p.parse_args())
