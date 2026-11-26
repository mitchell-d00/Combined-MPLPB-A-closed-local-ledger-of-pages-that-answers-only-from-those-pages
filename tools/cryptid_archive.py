"""Freeze a committed scoped study ZIP; final integration still needs full source."""
import argparse
import hashlib
from pathlib import Path
import subprocess
import sys
import zipfile
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from tools.cryptid_trial import read,save,sha


def main(a):
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    assert not subprocess.check_output(['git','status','--porcelain','--','mplpb_answers','mplpb_combined','mplpb_work'],cwd=ROOT,text=True).strip(),'Native changes must be committed'
    assert not a.output.exists() and not a.extraction.exists()
    names=['mplpb_answers','mplpb_combined','mplpb_work','tests','AGENTS.md','HANDOFF.md','handoff','.github',
           'evaluation/cryptid/programme.json','evaluation/cryptid/shared-rules.json','evaluation/cryptid/scorer-v4.json',
           'tools/bubble_wrap_adapter.py','tools/bubble_wrap_worker.py','tools/pole_worker.py','tools/study_sandbox.py']
    names+=subprocess.check_output(['git','ls-files','tools/cryptid*.py','tools/audit_cryptid.py'],cwd=ROOT,text=True).splitlines()
    for suffix in ('development','transfer-sealed.zip','transfer-seal.json','scorer-amendment-v2.json','README.md','selector-controls/freeze.json','wrap','safety-guards'):
        p=a.study/suffix
        if p.exists():names.append(str(p.relative_to(ROOT)))
    names += [str(p.relative_to(ROOT)) for p in a.study.glob('*-wrap') if p.is_dir()]
    a.output.parent.mkdir(exist_ok=True,parents=True)
    subprocess.run(['git','archive','--format=zip','-1','-o',str(a.output),commit,*names],cwd=ROOT,check=True)
    run=read(a.runtime_run);pins=run['reader_files']
    with zipfile.ZipFile(a.output) as z:
        assert z.testzip() is None
        for p,h in pins.items():assert hashlib.sha256(z.read(p)).hexdigest()==h
        members=len(z.infolist());total=sum(i.file_size for i in z.infolist());assert total<128*1024**2
        z.extractall(a.extraction)
    save(a.receipt,{'candidate_commit':commit,'candidate_tree':subprocess.check_output(['git','rev-parse','HEAD^{tree}'],cwd=ROOT,text=True).strip(),
         'zip_sha256':sha(a.output),'zip_path':str(a.output),'scope':'Committed scoped runtime/study source ZIP; not complete repository archive',
         'selected_paths':names,'members':members,'extracted_bytes':total,'runtime_sha256':pins,'native_equals_development_run_sha256':sha(a.runtime_run),
         'transfer_unopened_at_freeze':not (a.study/'transfer-open.json').exists(),'extraction':str(a.extraction),
         'full_repository_extraction_and_manifest_gate':'PENDING final integration; not claimed for this scoped archive'})
    print(commit,sha(a.output),members,total)

if __name__=='__main__':
    p=argparse.ArgumentParser()
    for n in ('study','runtime-run','output','receipt','extraction'):p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args();a.study=a.study.resolve();main(a)
