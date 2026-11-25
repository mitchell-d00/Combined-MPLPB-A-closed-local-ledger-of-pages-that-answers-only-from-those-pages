"""Create two small, identical-engine pilot bundles differing only in entry docs."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import zipfile

ROOT=Path(__file__).resolve().parents[1]
HOME=ROOT/'evaluation/onboarding/2026-11-25'
ENGINE='7f6641dd979ab3f4df5c3ddfbfc28961c095b016'
DOCUMENTATION='2ab4b0160315cbc5a4892ad95f57e7544fcadb51'

def sha_bytes(data):return hashlib.sha256(data).hexdigest()
def save(path,value):
    with path.open('x') as f:json.dump(value,f,indent=2,ensure_ascii=False);f.write('\n')

def render(text):
    import markdown
    if markdown.__version__!='3.8.2':raise ValueError('Use frozen Markdown==3.8.2 renderer')
    body=markdown.markdown(text,extensions=['fenced_code','tables','toc'])
    base='https://github.com/mitchell-d00/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages/blob/'+DOCUMENTATION+'/'
    def link(match):
        target=match[1]
        if target.startswith(('#','https:','http:','mailto:')):return match[0]
        return 'href="'+base+target+'"'
    body=re.sub(r'href="([^"]+)"',link,body)
    return ('<!doctype html><meta charset="utf-8"><title>MPLPB entry documentation</title>'
            '<style>body{max-width:52rem;margin:2rem auto;padding:0 1rem;font:18px/1.5 system-ui}'
            'pre{overflow:auto;background:#f2f3f5;padding:1rem}table{border-collapse:collapse}td,th{padding:.4rem;border:1px solid #ccc}</style>'
            +body).encode()

def build(output):
    output=Path(output);output.mkdir(parents=True,exist_ok=False)
    participant=HOME/'participant';wheel=next((HOME/'wheel').glob('*.whl'))
    common={n:(participant/n).read_bytes() for n in ['pilot.py','collection-sha256.json','COMMON_SETUP.md','participant-form.json']}
    common[wheel.name]=wheel.read_bytes();common['LICENSE']=(ROOT/'LICENSE').read_bytes()
    common['MATERIALS.json']=(json.dumps({'engine_commit':ENGINE,'engine_wheel_sha256':sha_bytes(wheel.read_bytes()),
        'collection_manifest_sha256':sha_bytes(common['collection-sha256.json']),
        'runtime_sha256':json.loads((ROOT/'evaluation/bubble-wrap/2026-11-25/continuation/candidate-freeze.json').read_text())['runtime_sha256'],
        'runtime_identical_between_groups':True,'tasks_and_interface_identical_between_groups':True,
        'human_execution':'NOT_RUN'},indent=2)+'\n').encode()
    materials=participant/'MATERIALS.json'
    if materials.exists():assert materials.read_bytes()==common['MATERIALS.json']
    else:materials.write_bytes(common['MATERIALS.json'])
    packages={}
    for arm,name in [('existing','EXISTING_ENTRY.md'),('new_path','START_HERE.md')]:
        text=(participant/name).read_bytes();files=dict(common,**{'ENTRY.md':text,'ENTRY.html':render(text.decode())})
        target=output/('onboard-'+arm+'.zip')
        with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
            for path,data in sorted(files.items()):
                info=zipfile.ZipInfo(path,date_time=(2026,11,25,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
                info.external_attr=0o100644<<16;z.writestr(info,data)
        packages[arm]={'file':target.name,'bytes':target.stat().st_size,'sha256':sha_bytes(target.read_bytes()),
                       'entries':{p:sha_bytes(data) for p,data in files.items()}}
    left,right=packages['existing']['entries'],packages['new_path']['entries']
    differences=sorted(p for p in left if left[p]!=right[p])
    assert differences==['ENTRY.html','ENTRY.md']
    save(output/'packages.json',{'engine_commit':ENGINE,'engine_wheel_sha256':sha_bytes(wheel.read_bytes()),
        'documentation_control_commit':DOCUMENTATION,'packages':packages,
        'only_differences':differences,'renderer':'Markdown==3.8.2','human_execution':'NOT_RUN'})
    print(json.dumps({'only_differences':differences,'packages':{k:{n:v[n] for n in ['file','bytes','sha256']} for k,v in packages.items()}}))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();build(a.output)
