"""Once-only final packet on an already verified clean full-source extraction."""
import argparse,sys,shutil,tempfile,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from tools import cryptid_trial_v5 as trial

def main(a):
 seal=trial.read(a.home/'transfer-seal.json');packet=a.home/'transfer-sealed.zip';receipt=trial.read(a.candidate_receipt)
 assert trial.sha(packet)==seal['packet_sha256'] and not (a.home/'transfer-open.json').exists()
 assert receipt['candidate_commit']==a.candidate_commit and receipt['zip_sha256']==trial.sha(a.candidate_zip)
 assert receipt['runtime_sha256']=={str(p.relative_to(a.implementation)):trial.sha(p) for p in trial.runtime_files(a.implementation)}
 trial.save(a.home/'transfer-open.json',{'candidate_commit':a.candidate_commit,'candidate_zip_sha256':receipt['zip_sha256'],'candidate_receipt_sha256':trial.sha(a.candidate_receipt),'packet_sha256':trial.sha(packet),'semantic_outcome':'NOT_RUN at opening','custody':'Same-operator, once opened now consumed. No independent preparation/blinding/adjudication.','implementation':str(a.implementation),'output':str(a.output)})
 with tempfile.TemporaryDirectory(prefix='cryptid-final-transfer-',dir='/workspace/cryptid-custody') as tmp:
  public=Path(tmp)/'packet';public.mkdir()
  with zipfile.ZipFile(packet) as z:
   assert sum(i.file_size for i in z.infolist())<128*1024**2
   for i in z.infolist():
    p=Path(i.filename);assert not p.is_absolute() and '..' not in p.parts and i.external_attr>>16&0o170000!=0o120000
   z.extractall(public)
  freeze=trial.read(public/'freeze.json')
  for name,expected in freeze['harness'].items():
   assert trial.sha(a.implementation/name)==expected
   dst=public/name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(a.implementation/name,dst)
  trial.ROOT=public
  trial.run(argparse.Namespace(registry=public/'registry.json',implementation=a.implementation,source_commit=a.candidate_commit,output=a.output))
  shutil.copytree(public,a.home/'consumed-transfer',ignore=shutil.ignore_patterns('tools'))
if __name__=='__main__':
 p=argparse.ArgumentParser()
 for n in ['home','implementation','candidate-zip','candidate-receipt','output']:p.add_argument('--'+n,type=Path,required=True)
 p.add_argument('--candidate-commit',required=True);main(p.parse_args())
