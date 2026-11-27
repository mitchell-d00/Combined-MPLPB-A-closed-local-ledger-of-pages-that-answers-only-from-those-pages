from pathlib import Path, PurePosixPath
import hashlib
import json
import subprocess
import sys
import tarfile
import zipfile
from tools import dpercent_expanded

root = Path(sys.argv[1])
custody = Path(sys.argv[2])
review = root / 'public-review'
out = root / 'grader'
out.mkdir(mode=0o700)
repo = Path.cwd()
scope = Path('evaluation/cryptid/bunyip/round2')
old = '961be47602c5e3ccb94459c106b3fa28754549bf'
sha = lambda data: hashlib.sha256(data).hexdigest()

def read(path):
    return json.loads(path.read_bytes())

def write(path, contents):
    path.write_text(json.dumps(contents, indent=2, ensure_ascii=False) + '\n')

freeze = read(review / 'freeze.json')
for file, field in [('tools/dpercent.py','base_scorer_sha256'),
                    ('tools/dpercent_expanded.py','expanded_scorer_sha256')]:
    assert sha((repo / file).read_bytes()) == freeze[field]
assert sha((custody / 'custody/key.json').read_bytes()) == freeze['key_sha256']
assert sha((custody / 'public/seal.json').read_bytes()) == freeze['packet_seal_sha256']

def selected_member(name, prefix):
    if not name.startswith(prefix):
        return None
    suffix = PurePosixPath(name.removeprefix(prefix))
    assert not suffix.is_absolute() and '..' not in suffix.parts
    if len(suffix.parts) == 1 and suffix.name == 'run.json':
        return suffix
    if len(suffix.parts) == 2 and suffix.parts[0].startswith('DP') and suffix.name == 'result.json':
        return suffix
    return None

def primary(label, archive_name, prefix, old_score):
    dest = out / label
    dest.mkdir()
    if archive_name.endswith('.zip'):
        with zipfile.ZipFile(review / archive_name) as z:
            for name in z.namelist():
                target=selected_member(name,prefix)
                if target:
                    path=dest/target
                    path.parent.mkdir(parents=True,exist_ok=True)
                    path.write_bytes(z.read(name))
    else:
        with tarfile.open(review / archive_name) as tar:
            for member in tar:
                target=selected_member(member.name,prefix)
                if target:
                    assert member.isfile()
                    path=dest/target
                    path.parent.mkdir(parents=True,exist_ok=True)
                    path.write_bytes(tar.extractfile(member).read())
    result = dpercent_expanded.score(custody/'public', custody/'custody', dest, out/(label+'.json'))
    r=read(dest/'run.json')
    rows=lambda score: {row['id']:(row['execution'],row['outcome']) for row in score['cases']}
    assert rows(result)==rows(old_score)
    assert result['metrics']['outcomes']==old_score['metrics']['outcomes']
    return {'id':label,'archive':archive_name,'archive_sha256':sha((review/archive_name).read_bytes()),
            'run_sha256':sha((dest/'run.json').read_bytes()),
            'checkout_revision':r['checkout_revision'],
            'runtime_manifest_sha256':sha(json.dumps(r['runtime_sha256'],sort_keys=True,separators=(',',':')).encode()),
            'runtime_manifest':r['runtime_sha256'],
            'cases':len(result['cases']),'outcomes':result['metrics']['outcomes'],
            'matches_recorded_per_case_grade':True}

grades=[]
with tarfile.open(review/'baseline-retained.tar.xz') as tar:
    prior=json.load(tar.extractfile('baseline-score.json'))
grades.append(primary('historical-baseline','baseline-retained.tar.xz','baseline/',prior))
with tarfile.open(review/'public-evidence-v1.tar.xz') as tar:
    for label in ('c1-primary','c2-primary','c3-primary'):
        prior=json.load(tar.extractfile('assessments/'+label+'-score.json'))
        grades.append(primary(label,'public-evidence-v1.tar.xz','outputs/'+label+'/',prior))
with tarfile.open(review/'remote-483f35a-assessments-v1.tar.xz') as tar:
    for label in ('baseline','candidate'):
        prior=json.load(tar.extractfile('scores/'+label+'-primary-strict-v1.json'))
        grades.append(primary('remote-'+label,'remote-483f35a-'+label+'.zip',label+'/primary/',prior))

# Copy only the tracked public replacement tree into evaluator custody.
stage=out/'replacement-evaluator'
stage.mkdir()
rel=scope/'replacement'
data=subprocess.check_output(['git','archive','--format=tar','HEAD',str(rel)],cwd=repo)
import io
with tarfile.open(fileobj=io.BytesIO(data)) as tar:
    tar.extractall(stage,filter='data')
reader=stage/'readout.py'
reader.write_bytes(Path(__file__).with_name('readout.py').read_bytes())
replacement_keys=custody.parent/'keys'
for arm in ('development','R','X'):
    key=replacement_keys/(str(rel/arm).replace('/','--')+'.json')
    dest=stage/rel/arm/'custodian-key.json'
    assert not dest.exists()
    assert sha(key.read_bytes())==read(stage/rel/arm/'freeze.json')['key_sha256']
    dest.symlink_to(key)

replacement=[]
for name,arms in [('development',['development']),('fresh',['R','X'])]:
    archive=stage/rel/(name+'-evidence.zip')
    data=subprocess.check_output([sys.executable,str(reader),str(archive),*arms],cwd=stage)
    (out/(name+'-replacement.json')).write_bytes(data)
    new=json.loads(data)
    prior=read(stage/rel/(name+'-score.json'))
    assert new==prior
    replacement.append({'arm':name,'archives_sha256':sha(archive.read_bytes()),
        'scorer_sha256':sha(reader.read_bytes()),'comparison_matched':True,
        'summary':new['summary'],'distinct_original_questions':new['distinct_original_questions']})
summary={'source_pr106':old,'original_strict_key_sha256':freeze['key_sha256'],
         'original_scorer_sha256':freeze['expanded_scorer_sha256'],'primary_attempts':grades,
         'replacement_comparisons':replacement,
         'scope':'Regrade existing outputs with original scorers and keys in designated evaluator custody. No new reader executions. Unavailable original 128 grades retain their original receipts.'}
write(root/'original-grade-receipt.json',summary)
for grade in grades:
    print(grade['id'],grade['outcomes'])
for item in replacement:
    print(item['arm'],item['summary'])
