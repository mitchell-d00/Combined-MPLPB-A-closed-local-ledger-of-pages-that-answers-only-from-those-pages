"""Score Greek-sprint traces against sealed keys kept outside the worker."""
import argparse
import hashlib
import json
import subprocess
from collections import defaultdict
from pathlib import Path


def load(path):
    return json.loads(path.read_bytes())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(repo, *args):
    return subprocess.check_output(['git', '-C', repo, *args], text=True).strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('packet', 'key', 'run', 'output'):
        parser.add_argument(name, type=Path)
    args = parser.parse_args()
    packet, key, run = load(args.packet), load(args.key), load(args.run/'run.json')
    freeze = load(Path(__file__).with_name('freeze.json'))
    draw = run['draw']
    seal = freeze['packets'][draw]
    assert draw == key['draw'] == packet['draw']
    assert seal['inputs'] == sha(args.packet) == run['packet_sha256']
    assert seal['key'] == sha(args.key) and run['candidate'] == freeze['baseline']
    assert len(run['cases']) == seal['cases']
    assert set(key['expected']) == {row['id'] for row in packet['cases']}
    grades = []
    summary = defaultdict(lambda: dict(cases=0, phases=0, exact=0, attempts=0, successful_writes=0,
                                       durable_completions=0, failed=0, indeterminate=0))
    for item, actual in zip(packet['cases'], run['cases'], strict=True):
        assert (item['id'], item['set'], item['lane']) == (actual['id'], actual['set'], actual['lane'])
        phases = actual['phases']
        totals = summary[item['set']]
        totals['cases'] += 1
        for index, (trace, expected) in enumerate(zip(phases, key['expected'][item['id']], strict=True)):
            delta = {k:{'wanted':v,'actual':trace.get(k)} for k,v in expected.items() if trace.get(k) != v}
            readback = trace['readback']
            if trace.get('execution_error') or not trace.get('pid'):
                delta['process'] = trace.get('execution_error', 'no process identity')
            if readback['marker'] != expected['ref']:
                delta['independent_marker'] = readback['marker']
            if index and (phases[index-1]['pid'] == trace['pid'] or phases[index-1]['readback'] != trace['before']):
                delta['restart'] = 'process or ref continuity mismatch'
            if index == len(phases)-1:
                repo = args.run/item['id']/'repo'
                oid = git(repo,'rev-parse','refs/heads/canary')
                if (oid, git(repo,'show', oid+':marker')) != (readback['oid'], readback['marker']):
                    delta['independent_final_ref'] = oid
            if item['lane'] == 'bridge':
                if expected['execution'] == 'indeterminate' and trace['process']['receipt']:
                    delta['completion_receipt'] = 'unexpected receipt'
                proof_admitted = expected['proof'] == 'complete'
                expected_binding = (item['scenario'] != 'wrong-receipt') if proof_admitted else None
                if trace.get('binding_attested') != expected_binding:
                    delta['receipt_binding'] = trace.get('binding_attested')
            grades.append(dict(id=item['id'],set=item['set'],phase=index+1,match=not delta,differences=delta))
            totals['phases'] += 1
            totals['exact'] += int(not delta)
            totals['attempts'] += trace.get('attempts', 0)
            totals['successful_writes'] += trace.get('writes', 0)
            totals['durable_completions'] += int(trace.get('execution')=='completed' and trace.get('store')=='completed')
            totals['failed'] += int(trace.get('execution')=='failed')
            totals['indeterminate'] += int(trace.get('execution')=='indeterminate')
    assert len(grades) == seal['phases']
    report = {'draw':draw,'candidate':run['candidate'],'summary':summary,'phases':grades}
    with args.output.open('x') as stream:
        stream.write(json.dumps(report,indent=2)+'\n')
    print(json.dumps(summary,indent=2))
    if any(not grade['match'] for grade in grades):
        raise SystemExit(1)


if __name__ == '__main__':
    main()
