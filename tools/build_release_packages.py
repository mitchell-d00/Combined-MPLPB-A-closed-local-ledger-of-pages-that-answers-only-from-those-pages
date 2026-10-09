"""Package committed source plus the tested browser build; never collect local state."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import zipfile

ROOT=Path(__file__).resolve().parents[1]

def build(output, browser):
    output=Path(output).resolve();output.mkdir(parents=True,exist_ok=True)
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    source=output/'mplpb-monster.zip'
    subprocess.run(['git','archive','--format=zip','--prefix=mplpb-monster/','--output='+str(source),'HEAD'],cwd=ROOT,check=True)
    browser=Path(browser).resolve()
    with zipfile.ZipFile(output/'mplpb-monster-browser.zip','w',zipfile.ZIP_DEFLATED) as z:
        z.write(browser,'MPLPB_Browser.html')
        z.writestr('READ_ME.txt','Open MPLPB_Browser.html in a current browser. Browser storage permissions are needed to save sessions. Optional Wikipedia lookup uses the network.\nSource commit: '+commit+'\n')
    files=[source,output/'mplpb-monster-browser.zip']
    manifest={'commit':commit,'files':[{ 'name':p.name,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]}
    (output/'SHA256.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(manifest,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',default='release');p.add_argument('--browser',default='dist/index.html');a=p.parse_args()
    build(a.output,a.browser)
