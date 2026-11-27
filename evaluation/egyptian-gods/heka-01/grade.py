"""Check frozen Heka reports against a held key and independent Git reads."""

import argparse
import hashlib
import json
import subprocess
from pathlib import Path


def read(path):
    return json.loads(path.read_bytes())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ['packet', 'key', 'run', 'output']:
        parser.add_argument(name, type=Path)
    args = parser.parse_args()
    packet, key, run = map(read, [args.packet, args.key, args.run / 'run.json'])
    freeze = read(Path(__file__).with_name('freeze.json'))
    draw = packet['draw']
    seal = freeze['packets'][draw]
    assert draw == key['draw'] == run['draw']
    assert seal['inputs'] == sha(args.packet) == run['inputs_sha256']
    assert seal['key'] == sha(args.key)
    assert len(packet['cases']) == len(run['cases']) == seal['cases']
    rows = []
    for case, entry in zip(packet['cases'], run['cases'], strict=True):
        ident = case['id']
        plan = key['expected'][ident]
        phases = entry['phases']
        assert ident == entry['id']
        assert len(phases) == (1 if run['mode'] == 'baseline' else len(plan))
        for n, (observed, expected) in enumerate(zip(phases, plan), 1):
            if run['mode'] == 'baseline':
                expected = dict(expected, code='bridge_unconnected', execution='not_run',
                                attempts=0, writes=0, ref='initial', store='unused', recheck=None)
                if case['scenario'] == 'revoked':
                    expected['authority'] = 'grant'
            differences = {k: {'wanted': v, 'actual': observed.get(k)}
                           for k, v in expected.items() if observed.get(k) != v}
            if n > 1 and (phases[n-2]['pid'] == observed['pid']
                          or phases[n-2]['readback'] != observed['before']):
                differences['restart'] = 'Expected a fresh process and unchanged prior ref'
            if observed.get('execution_error') is not None:
                differences['execution_error'] = observed['execution_error']
            observed_ref = observed['readback']
            if observed_ref['marker'] != expected['ref'] or observed_ref['ref'] != expected['ref']:
                differences['readback'] = observed_ref
            if n == len(phases):
                git_dir = args.run / ident / 'repo'
                oid = subprocess.check_output(['git', '-C', git_dir, 'rev-parse',
                                               'refs/heads/canary'], text=True).strip()
                marker = subprocess.check_output(['git', '-C', git_dir, 'show',
                                                  oid + ':marker'], text=True).strip()
                if (oid, marker) != (observed_ref['oid'], observed_ref['marker']):
                    differences['independent_final_ref'] = {'oid': oid, 'marker': marker}
            rows.append({'id': ident, 'phase': n, 'match': not differences, 'differences': differences})
    result = {'mode': run['mode'], 'draw': draw, 'scenarios': len(run['cases']),
              'phases': len(rows), 'matched': sum(row['match'] for row in rows), 'rows': rows}
    with args.output.open('x') as stream:
        stream.write(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k != 'rows'}))
    if result['matched'] != len(rows):
        raise SystemExit(1)


if __name__ == '__main__':
    main()
