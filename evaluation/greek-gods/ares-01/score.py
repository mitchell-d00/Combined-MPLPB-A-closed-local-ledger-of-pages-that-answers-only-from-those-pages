"""Grade Ares events and independent Git/store observations."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess


def read(path):
    return json.loads(path.read_bytes())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('inputs','key','run','output'):
        parser.add_argument(name,type=Path)
    a=parser.parse_args()
    packet,key,run=read(a.inputs),read(a.key),read(a.run/'run.json')
    freeze=read(Path(__file__).with_name('freeze.json'))
    draw=packet['draw']
    seal=freeze['draws'][draw]
    assert draw==key['draw']==run['draw']
    assert sha(a.inputs)==seal['inputs']==run['inputs_sha256']
    assert seal['key']==sha(a.key)
    assert len(packet['cases'])==len(run['cases'])==len(key['cases'])==seal['cases']
    grades=[]
    for case, observed in zip(packet['cases'],run['cases'],strict=True):
        ident=case['id']
        assert observed['id']==ident
        root=a.run/ident
        events=[json.loads(line) for line in (root/'events.jsonl').read_text().splitlines()]
        actual=observed['outcome']|{'ordered':[e['event'] for e in events]}
        expected=key['cases'][ident]
        differences={k:{'wanted':v,'actual':actual.get(k)} for k,v in expected.items() if actual.get(k)!=v}

        pids=observed['pids']
        is_restart=case['scenario']=='restart'
        has_revoker=case['scenario']!='active'
        if (len(set(pids.values()))!=len(pids) or
            set(pids)!=({'worker','driver'}|({'prime'} if is_restart else set())|({'revoker'} if has_revoker else set()))):
            differences['process_identities']=pids
        for event in events:
            prefix=event['event'].split(':',1)[0]
            if prefix=='revoked':
                role='revoker'
            elif prefix=='prime':
                role='prime'
            elif event['event']=='signal:restart':
                role='driver'
            else:
                role='worker'
            if event['pid']!=pids.get(role):
                differences['event_process_id']=event

        before,after=observed['before'],observed['after']
        git=lambda *args:subprocess.check_output(['git','-C',root/'repo',*args],text=True).strip()
        oid=git('rev-parse','refs/heads/canary')
        marker=git('show',oid+':marker')
        if (oid,marker)!=(observed['commits'][expected['marker']],after['ref']['marker']):
            differences['independent_ref_marker']=after['ref']
        if expected['writes']==0 and before!=after:
            differences['protected_ref_store']=after
        if expected['writes']==1 and not after['reservation_files']:
            differences['durable_reservation']='No reservation outcome recorded'
        grant=read(root/'authority.json')
        if grant != {'epoch':expected['authority_epoch'],'status':'active' if expected['authority_epoch']==1 else 'revoked'}:
            differences['authority_file']=grant
        grades.append({'id':ident,'scenario':case['scenario'],'match':not differences,'differences':differences})
    report={'draw':draw,'matched':sum(item['match'] for item in grades),'cases':len(grades),
        'writer_attempts':sum(row['outcome']['attempts'] for row in run['cases']),
        'writes':sum(row['outcome']['writes'] for row in run['cases']),
        'durable_completions':sum(row['outcome']['store']=='completed' for row in run['cases']),
        'rows':grades}
    with a.output.open('x') as out:
        out.write(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='rows'}))
    if report['matched']!=report['cases']:
        raise SystemExit(1)


if __name__=='__main__':
    main()
