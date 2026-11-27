from pathlib import Path
import hashlib, json, subprocess, sys, tempfile, zipfile

repo = Path.cwd()
study = repo / 'evaluation/cryptid/wampus-cat'
bunyip = repo / 'evaluation/cryptid/bunyip/round2/replacement'
readout = bunyip / 'readout.py'
readers = json.loads((study/'readers.json').read_text())
custody = Path(sys.argv[3]).resolve() if len(sys.argv) > 3 else Path('/workspace/wampus-cat-custody')

def sha(data):
    return hashlib.sha256(data).hexdigest()

def compare(arm, ref_role, reference, tested, prefixed=False):
    home = bunyip/arm if prefixed else study/arm
    registry = json.loads((home/'registry.json').read_text())
    key = (home/'custodian-key.json' if prefixed else custody/(arm+'-key.json')).read_bytes()
    original = json.loads((home/'freeze.json').read_text())
    assert sha(key) == original['key_sha256']
    assert sha((home/'registry.json').read_bytes()) == original['registry_sha256']
    with tempfile.TemporaryDirectory(prefix='wampus-readout-') as temp:
        temp = Path(temp)
        # Provide the original scorer's two named slots using immutable receipts
        # from these three-role runs. No input, expectation or result is rewritten.
        staging = temp / bunyip.relative_to(repo) / arm
        staging.mkdir(parents=True)
        (staging/'registry.json').write_bytes((home/'registry.json').read_bytes())
        (staging/'custodian-key.json').write_bytes(key)
        envelope = dict(original)
        for key_slot, source_role in [('released',ref_role),('candidate','wampus')]:
            envelope[key_slot+'_commit']=readers[source_role]['commit']
            envelope[key_slot+'_runtime_zip']=readers[source_role]['runtime_zip_sha256']
        (staging/'freeze.json').write_text(json.dumps(envelope))
        for case in registry['cases']:
            rel = Path(case['packet'])
            p = temp/rel
            p.parent.mkdir(parents=True,exist_ok=True)
            p.symlink_to(repo/rel,target_is_directory=True)
        view = temp/'scoring-view.zip'
        with zipfile.ZipFile(view,'w') as out:
            for source_file, role_slot, source_prefix, runtime in [
                (reference,'released',f'{arm}-candidate' if prefixed else f'{arm}-{ref_role}',
                 'candidate' if prefixed else ref_role),
                (tested,'candidate',f'bunyip-{arm}-wampus' if prefixed else f'{arm}-wampus','wampus')]:
                with zipfile.ZipFile(source_file) as f:
                    out.writestr(role_slot+'-runtime.zip',f.read(runtime+'-runtime.zip'))
                    for file in f.namelist():
                        if file.startswith(source_prefix+'/'):
                            out.writestr(f'{arm}-{role_slot}/'+file.split('/',1)[1],f.read(file))
        result = json.loads(subprocess.check_output([sys.executable,str(readout),str(view),arm],cwd=temp))
        result.pop('artifact_sha256')
        result['reference_reader']=ref_role
        result['reference_artifact_sha256']=sha(Path(reference).read_bytes())
        result['wampus_artifact_sha256']=sha(Path(tested).read_bytes())
        return result

mode = sys.argv[1]
run = Path(sys.argv[2])
if mode=='development':
    obj = {'development_vs_c3':compare(mode,'c3',run,run),
           'development_vs_released':compare(mode,'released',run,run),
           'consumed_bunyip':{arm:compare(arm,'c3',bunyip/('development-evidence.zip' if arm=='development' else 'fresh-evidence.zip'),run,True) for arm in ('development','R','X')}}
else:
    obj={'fresh_vs_c3':compare(mode,'c3',run,run),'fresh_vs_released':compare(mode,'released',run,run)}
print(json.dumps(obj,ensure_ascii=False,indent=2))
