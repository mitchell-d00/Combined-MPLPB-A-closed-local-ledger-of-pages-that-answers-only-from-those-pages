"""Grade namespace-only binding contrasts using the private sealed key."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess


def load(path):
    return json.loads(path.read_bytes())


def sha(data):
    return hashlib.sha256(data).hexdigest()


def digest(value):
    return sha(json.dumps(value, separators=(',', ':'), ensure_ascii=False).encode())


def without_namespace(binding):
    return dict(binding, target={k: v for k, v in binding['target'].items() if k != 'namespace'})


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    for name in ('inputs', 'key', 'run', 'output'):
        cli.add_argument(name, type=Path)
    args = cli.parse_args()
    packet, key, run = load(args.inputs), load(args.key), load(args.run/'run.json')
    freeze = load(Path(__file__).with_name('freeze.json'))
    seal = freeze['draws'][packet['draw']]
    assert packet['draw'] == run['draw'] == key['draw']
    assert seal['inputs'] == run['inputs_sha256'] == sha(args.inputs.read_bytes())
    assert seal['key'] == sha(args.key.read_bytes())
    assert run['bridge_sha256'] == freeze['bridge_sha256']
    assert len(run['phases']) == seal['phases'] == len(packet['phases']) == len(key['phases'])
    assert set(run['targets']) == {'A', 'B'}
    targets = run['targets']
    a,b = targets['A'],targets['B']
    assert a['commits'] == b['commits'] and a['ref'] == b['ref'] == 'refs/heads/canary'
    assert a['namespace'] != b['namespace'] and a['repo'] != b['repo']
    donor = None
    seen = set()
    rows = []
    previous = run['initial']
    canonical = None
    for phase, saved in zip(packet['phases'], run['phases'], strict=True):
        assert phase['id'] == saved['id']
        trace = saved['trace']
        actor = phase['target']
        expected = key['phases'][phase['id']]
        actual = {k:trace.get(k) for k in ('proof','code','execution','attempts','writes','authority','recheck')}
        actual['initial'] = (trace.get('admission') or {}).get('decision')
        actual['final'] = trace.get('controller', {}).get('verdict', {}).get('decision')
        actual['states'] = {k:{'marker':v['ref']['marker'],'store':v['store']} for k,v in saved['after'].items()}
        deltas = {k:{'expected':v,'actual':actual[k]} for k,v in expected.items() if actual[k]!=v}
        if saved['before'] != previous or trace['pid'] in seen or saved['child_pid'] != trace['pid']:
            deltas['continuity'] = 'Git/store readback or fresh worker identity changed unexpectedly'
        seen.add(trace['pid'])
        previous = saved['after']
        for host, observed in saved['after'].items():
            marker = expected['states'][host]['marker']
            if (observed['ref']['oid'], observed['ref']['ref']) != (targets[host]['commits'][marker], marker):
                deltas['ref_'+host] = observed['ref']
            if (not expected['writes'] or host != actor) and observed != saved['before'][host]:
                deltas['side_effect_'+host] = 'Git ref or reservation bytes changed on a protected target'

        proof = load(args.run/phase['id']/'initial-proof.json')
        selected = proof['selected']
        identity = (digest(proof['snapshot']),digest(proof['answer']),selected['hash'],selected['bytes_sha256'])
        canonical = canonical or identity
        if identity != canonical:
            deltas['proof_identity'] = 'Reader proof or eligible snapshot changed within a draw'
        expected_target = {'action':'record-canary','ref':targets[actor]['ref'],
                           'revision':targets[actor]['commits']['initial'],
                           'intended':targets[actor]['commits']['intended'],
                           'namespace':targets[actor]['namespace']}
        normal = dict(schema='heka-proof-binding-v1',readerPin=freeze['baseline'],question=packet['question'],
                      obligation=packet['obligation'],snapshot=identity[0],proof=identity[1],target=expected_target)
        binding = trace['binding']
        if trace['target'] != expected_target or without_namespace(binding) != without_namespace(normal):
            deltas['binding_scope'] = 'Scope fields outside the namespace differ'
        mode = phase['binding']
        if donor is None:
            donor = binding
        expected_namespace = {
            'local':expected_target['namespace'],
            'repeat':expected_target['namespace'],
            'foreign':targets[packet['donor']]['namespace'],
            'mutated':targets[packet['donor']]['namespace']+'-contrast',
        }[mode]
        if (binding['target']['namespace'] != expected_namespace or
                (mode == 'foreign' and binding != donor) or
                (mode in ('foreign','mutated') and expected_namespace == expected_target['namespace'])):
            deltas['namespace'] = {'want':expected_namespace,'actual':binding['target']['namespace']}
        if saved['binding_sha256'] != digest(binding):
            deltas['binding_digest'] = 'Binding digest did not match recorded fields'
        if actual['initial'] == 'allow' and trace['admission']['receiptIds'] != ['heka-'+digest(binding)]:
            deltas['admitted_receipt'] = trace['admission']['receiptIds']
        rows.append({'id':phase['id'],'target':actor,'mode':mode,'match':not deltas,'differences':deltas})
    for host, target in targets.items():
        repo = args.run/host/'repo'
        oid = subprocess.check_output(['git','-C',repo,'rev-parse',target['ref']],text=True).strip()
        marker = subprocess.check_output(['git','-C',repo,'show',oid+':marker'],text=True).strip()
        assert (oid, marker) == (previous[host]['ref']['oid'],previous[host]['ref']['marker'])
    report = {'draw':run['draw'],'phases':len(rows),'matched':sum(r['match'] for r in rows),
              'writer_attempts':sum(p['trace']['attempts'] for p in run['phases']),
              'intended_writes':sum(p['trace']['writes'] for p in run['phases']),
              'durable_completions':sum(p['trace']['execution']=='completed' for p in run['phases']),
              'rows':rows}
    with args.output.open('x') as stream:
        stream.write(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='rows'}))
    if report['matched'] != len(rows):
        raise SystemExit(1)


if __name__ == '__main__':
    main()
