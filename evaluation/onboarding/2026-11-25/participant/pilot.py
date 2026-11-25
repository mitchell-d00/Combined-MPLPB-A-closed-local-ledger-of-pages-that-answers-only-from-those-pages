"""Identical local task interface for both ONBOARD-12 documentation groups."""
import argparse
import datetime
import hashlib
import json
import importlib
from pathlib import Path

from mplpb_answers.pipeline import answer_query
from mplpb_combined.ledger import write

def tasks():
    return [
      {'id':1,'question':'When does the museum open?','record_id':'MUSEUM','field':'Opening time'},
      {'id':2,'question':'When does the museum close?','record_id':'MUSEUM','field':'Closing time'},
      {'id':3,'question':'What does Celia Duarte report about the writer of the estuary register, without independently verifying the event?'},
      {'id':4,'question':'According to the report, what did Selma Duarte instruct the coastal survey crew to do?'},
      {'id':5,'question':'According to the report, did the coastal survey crew complete the task instructed by Selma Duarte?'},
    ]

def verify_engine():
    materials=json.loads(Path(__file__).with_name('MATERIALS.json').read_text())
    actual={}
    for name in ['mplpb_answers','mplpb_combined','mplpb_work']:
        folder=Path(importlib.import_module(name).__file__).parent
        for p in folder.glob('*.py'):actual[name+'/'+p.name]=hashlib.sha256(p.read_bytes()).hexdigest()
    if actual!=materials['runtime_sha256']:raise ValueError('Installed engine differs from the frozen pilot runtime')

def prepare(root):
    verify_engine()
    if root.exists():raise ValueError('Use a new collection directory')
    sources=[('MUSEUM','<p>Opening time: 09:00.</p>'),
             ('REPORT-A','<p>Celia Duarte reported that Bram Okoye wrote the estuary register.</p>'),
             ('REPORT-B','<p>Celia Duarte reported that Kira Mensah wrote the estuary register.</p>'),
             ('INSTRUCTION','<p>Report.</p><p>Written by Tomas Ivers.</p><p>Selma Duarte instructed the coastal survey crew: “Chart the western inlet before Monday.”</p>')]
    for ident,body in sources:
        write(root,doc_id=ident,title=ident,scope='museum hours and documentary originals',body_html=body,origin='machine',external='yes',when='2026-11-25T00:00Z')

def verify_collection(root):
    manifest=Path(__file__).with_name('collection-sha256.json')
    expected=json.loads(manifest.read_text())
    actual={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(root.rglob('*')) if p.is_file()}
    if actual!=expected:raise ValueError('Trial collection differs from its frozen source bytes')

def answer(root,number):
    verify_engine()
    verify_collection(root)
    task=tasks()[number-1]
    return answer_query(root,task['question'],**{k:task[k] for k in ['record_id','field'] if k in task}).contract

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('command',choices=['prepare','tasks','ask','passage']);p.add_argument('number',type=int,nargs='?')
    p.add_argument('--root',type=Path,default=Path('pilot-ledger'));p.add_argument('--claim',type=int,default=0);p.add_argument('--citation',type=int,default=0)
    p.add_argument('--log',type=Path,default=Path('participant-actions.jsonl'));a=p.parse_args()
    if a.command=='prepare':prepare(a.root);verify_collection(a.root);print('Ready. Run: python pilot.py tasks');return
    if a.command=='tasks':print(json.dumps(tasks(),indent=2));return
    if a.number not in range(1,6):p.error('Task number must be1 through5')
    out=answer(a.root,a.number)
    if a.command=='ask':
        print(out['kind'].upper()+'\n'+(out['text'] or out['diagnostic']['message']))
        for i,claim in enumerate(out['claims']):
            print('Claim '+str(i)+': '+claim['text'])
            for j,cite in enumerate(claim['citations']):
                print('Passage '+str(i)+':'+str(j)+' — '+cite['source_id']+' '+cite['hash'])
        for missing in out.get('missing',[]):print('Unanswered: '+missing)
    else:
        if a.claim<0 or a.citation<0:p.error('Nonnegative claim/citation indices required')
        try: cite=out['claims'][a.claim]['citations'][a.citation]
        except IndexError:p.error('No current verified passage at those indices')
        print(json.dumps(cite,indent=2,ensure_ascii=False))
    event={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'command':a.command,'task':a.number,
           'claim':a.claim,'citation':a.citation,'outcome':out['kind'],
           'contract_sha256':hashlib.sha256(json.dumps(out,sort_keys=True,ensure_ascii=False).encode()).hexdigest()}
    with a.log.open('a') as f:f.write(json.dumps(event)+'\n')

if __name__=='__main__':main()
