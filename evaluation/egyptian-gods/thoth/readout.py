from pathlib import Path
import hashlib, json, subprocess, sys, tempfile, zipfile

repo = Path.cwd()
study = repo / 'evaluation/egyptian-gods/thoth'
wampus = repo / 'evaluation/cryptid/wampus-cat'
bunyip = repo / 'evaluation/cryptid/bunyip/round2/replacement'
readout = bunyip / 'readout.py'
pins = json.loads((study/'readers.json').read_text())
custody = Path(sys.argv[3]) if len(sys.argv) > 3 else Path('/workspace/thoth-custody')
wampus_custody = Path(sys.argv[4]) if len(sys.argv) > 4 else Path('/workspace/wampus-cat-custody')
mode = sys.argv[1]
archive = Path(sys.argv[2]).resolve()

def digest(data):
    return hashlib.sha256(data).hexdigest()

def norm(value):
    if isinstance(value, dict):
        return {k: norm(v) for k, v in value.items() if k != 'code_sha256'}
    if isinstance(value, list):
        return [norm(v) for v in value]
    return value

def compare(arm, packet, key, prior_role, prior_archive, prior_prefix, test_prefix):
    registry_bytes = (packet/'registry.json').read_bytes()
    key_bytes = key.read_bytes()
    freeze = json.loads((packet/'freeze.json').read_text())
    assert digest(registry_bytes) == freeze['registry_sha256']
    assert digest(key_bytes) == freeze['key_sha256']
    rows = json.loads(registry_bytes)['cases']
    with tempfile.TemporaryDirectory(prefix='thoth-readout-') as temporary:
        staging = Path(temporary)
        original = staging/bunyip.relative_to(repo)/arm
        original.mkdir(parents=True)
        (original/'registry.json').write_bytes(registry_bytes)
        (original/'custodian-key.json').write_bytes(key_bytes)
        for slot, role in [('released',prior_role),('candidate','thoth')]:
            freeze[slot+'_commit'] = pins[role]['commit']
            freeze[slot+'_runtime_zip'] = pins[role]['runtime_zip_sha256']
        (original/'freeze.json').write_text(json.dumps(freeze))
        for row in rows:
            target = staging/row['packet']
            target.parent.mkdir(parents=True,exist_ok=True)
            target.symlink_to(repo/row['packet'],target_is_directory=True)
        view = staging/'score-view.zip'
        with zipfile.ZipFile(view,'w') as mapped, zipfile.ZipFile(prior_archive) as prior, zipfile.ZipFile(archive) as tested:
            for source, src_role, prefix, slot in [(prior,prior_role,prior_prefix,'released'),(tested,'thoth',test_prefix,'candidate')]:
                mapped.writestr(slot+'-runtime.zip',source.read(src_role+'-runtime.zip'))
                for name in source.namelist():
                    if name.startswith(prefix+'/'):
                        mapped.writestr(f'{arm}-{slot}/'+name.split('/',1)[1],source.read(name))
            protected=[]
            for row in rows:
                case=row['id']+'/result.json'
                before=json.loads(prior.read(prior_prefix+'/'+case))['answer']
                after=json.loads(tested.read(test_prefix+'/'+case))['answer']
                if before['answer_supported'] or before['kind']=='partial_answer' and before['claims']:
                    protected.append({'id':row['id'],'same_contract':norm(before)==norm(after)})
        result=json.loads(subprocess.check_output([sys.executable,str(readout),str(view),arm],cwd=staging))
        result.pop('artifact_sha256')
        result['reference_role']=prior_role
        result['reference_artifact_sha256']=digest(prior_archive.read_bytes())
        result['thoth_artifact_sha256']=digest(archive.read_bytes())
        result['protected_contracts']=protected
        return result

packet = study/mode
results = {
    'new_cases': {role: compare(mode,packet,custody/(mode+'-key.json'),role,archive,f'{mode}-{role}',f'{mode}-thoth')
                  for role in ('released','c3','wampus')}
}
if mode == 'development':
    results['consumed_wampus'] = {arm: compare(arm,wampus/arm,wampus_custody/(arm+'-key.json'),'wampus',
                         wampus/(arm+'-evidence.zip'),f'{arm}-wampus',f'wampus-{arm}-thoth')
                                   for arm in ('development','fresh')}
    results['consumed_bunyip'] = {arm: compare(arm,bunyip/arm,bunyip/arm/'custodian-key.json','wampus',
                         wampus/'development-evidence.zip',f'bunyip-{arm}-wampus',f'bunyip-{arm}-thoth')
                                   for arm in ('development','R','X')}
print(json.dumps(results,ensure_ascii=False,indent=2))
