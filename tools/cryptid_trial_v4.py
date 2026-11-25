"""Local append-only Cryptid runner. Keys and scorer never enter workers."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.cryptid_adapter_v4 import execute, sha, snapshot, runtime_files

VERSION = 'cryptid-host-runner-v4'


def read(path):
    return json.loads(Path(path).read_text())


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x') as f:
        f.write(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False)+'\n')


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def run(a):
    registry = read(a.registry)
    seal = read(a.registry.parent/'freeze.json')
    assert sha(a.registry) == seal['registry_sha256']
    for path, expected in seal['harness'].items():
        assert sha(ROOT/path) == expected, 'Changed frozen harness: '+path
    pins = {str(p.relative_to(a.implementation)):sha(p) for p in runtime_files(a.implementation)}
    a.output.mkdir(parents=True, exist_ok=False)
    rows = []
    for case in registry['cases']:
        packet = ROOT/case['packet']
        assert snapshot(packet) == case['files'], case['id']
        started = time.perf_counter()
        row = {'id':case['id'], 'input_hash':case['semantic_input_hash'],
               'execution_status':'attempted', 'score_status':'UNSCORED', 'semantic_outcome':'NOT_RUN'}
        try:
            raw = execute(a.implementation, packet, a.output/case['id'])
            answer = raw['answer']
            assert answer['schema'] == 'answer-contract-v1'
            assert isinstance(answer['claims'], list) and isinstance(answer['answer_supported'], bool)
            row.update(execution_status='completed', semantic_outcome=answer['kind'],
                       answer_supported=answer['answer_supported'], claims=len(answer['claims']),
                       raw_sha256=sha(a.output/case['id']/'result.json'),
                       diagnostic=answer.get('diagnostic'))
        except Exception as error:
            row.update(execution_status='failed', semantic_outcome='NOT_RUN', error=str(error))
        row['host_wall_seconds'] = time.perf_counter()-started
        rows.append(row)
        save(a.output/case['id']/'run-record.json', row)
        print(case['id'], row['execution_status'], row['semantic_outcome'], flush=True)
    assert pins == {str(p.relative_to(a.implementation)):sha(p) for p in runtime_files(a.implementation)}
    result = {'schema':'cryptid-run-v1','reader_commit':a.source_commit, 'reader_files':pins,
              'registry_sha256':sha(a.registry), 'registry_path':str(a.registry),
              'harness':seal['harness'], 'exposure':registry['exposure'],
              'execution_counts':dict(Counter(r['execution_status'] for r in rows)),
              'planned':len(registry['cases']),'attempted':len(rows),'cases':rows}
    save(a.output/'run.json',result)
    if any(r['execution_status']!='completed' for r in rows):
        raise SystemExit(2)


def main():
    p=argparse.ArgumentParser();p.add_argument('--registry',type=Path,required=True)
    p.add_argument('--implementation',type=Path,required=True);p.add_argument('--source-commit',required=True)
    p.add_argument('--output',type=Path,required=True);run(p.parse_args())

if __name__=='__main__':main()
