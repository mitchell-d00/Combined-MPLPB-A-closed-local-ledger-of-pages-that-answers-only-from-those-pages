"""Package committed source plus the tested browser build; never collect local state."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import zipfile

ROOT=Path(__file__).resolve().parents[1]

def build(output, browser):
    output=Path(output).resolve();output.mkdir(parents=True,exist_ok=True)
    subprocess.run([sys.executable,str(ROOT/'tools/build_handoff.py'),'--check'],cwd=ROOT,check=True)
    subprocess.run(['git','diff','--quiet','HEAD','--'],cwd=ROOT,check=True)
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


def build_native(output, wheel_directory):
    """Package one staged wheel and enforce its supported top-level contents."""
    manifest = json.loads((ROOT / 'docs/PRODUCT_DISTRIBUTION.json').read_text())['native']
    wheels = sorted(path for path in Path(wheel_directory).glob('*.whl') if path.is_file())
    if len(wheels) != manifest['wheel_count']:
        raise ValueError('The native ZIP needs exactly one wheel from the current build')
    wheel = wheels[0]
    with zipfile.ZipFile(wheel) as archive:
        members = [Path(entry.filename) for entry in archive.infolist() if not entry.is_dir()]
    if any(path.is_absolute() or '..' in path.parts for path in members):
        raise ValueError('The native wheel contains an invalid member path')
    roots = {path.parts[0] for path in members}
    packages = set(manifest['packages'])
    if any(path.parts[0] in packages and (len(path.parts) != 2 or path.suffix != manifest['module_suffix'])
           for path in members):
        raise ValueError('The native wheel contains files beyond the supported runtime modules')
    metadata = roots - packages
    if not packages <= roots or len(metadata) != 1 or not next(iter(metadata)).endswith('.dist-info'):
        raise ValueError('Wheel contents do not match the native distribution manifest')
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output / manifest['archive'], 'w', zipfile.ZIP_DEFLATED) as archive:
        archive.write(wheel, wheel.name)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', default='release')
    parser.add_argument('--browser', default='dist/index.html')
    parser.add_argument('--native-wheel-dir', type=Path)
    args = parser.parse_args()
    if args.native_wheel_dir is None:
        build(args.output, args.browser)
    else:
        build_native(args.output, args.native_wheel_dir)
