"""Grade sealed Apollo traces with independent Git readback."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess


def load(path):
    return json.loads(path.read_bytes())


def sha(value):
    return hashlib.sha256(value).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('inputs','key','run','output'):
        parser.add_argument(name,type=Path)
    a=parser.parse_args()
    packet,key,run=load(a.inputs),load(a.key),load(a.run/'run.json')
    lab=Path(__file__).parent
    freeze=load(lab/'freeze.json')
    draw=packet['draw']
    seal=freeze['draws'][draw]
    assert draw==key['draw']==run['draw']
    assert sha(a.inputs.read_bytes())==seal['inputs']==run['inputs_sha256']
    assert sha(a.key.read_bytes())==seal['key']
    assert sha((lab/'trust.json').read_bytes())==freeze['trust_sha256']==run['trust_sha256']
    assert len(packet['cases'])==len(key['cases'])==len(run['cases'])==seal['cases']
    graded=[]
    for case,observed in zip(packet['cases'],run['cases'],strict=True):
        ident=case['id']
        assert ident==observed['id']
        expected=key['cases'][ident]
        actual=observed['outcome']
        differences={k:dict(expected=v,actual=actual.get(k)) for k,v in expected.items() if actual.get(k)!=v}
        path=a.run/ident
        readback=observed['after']
        git=lambda *args: subprocess.check_output(['git','-C',path/'repo',*args],text=True).strip()
        oid=git('rev-parse','refs/heads/canary')
        if (oid,git('show',oid+':marker')) != (readback['ref']['oid'],expected['marker']):
            differences['independent_readback']=readback
        if expected['writes']==0 and observed['before']!=readback:
            differences['unchanged_ref_and_store']=readback
        if expected['writes']==1 and (oid!=observed['commits']['intended'] or not readback['reservation_files']):
            differences['durable_ref_and_store']=readback
        if actual['marker']!=readback['ref']['marker'] or actual['store']!=readback['store']:
            differences['readback_consistency']=readback
        proof=load(path/'producer-proof.json')
        q=proof['answer']
        native='complete' if q['kind']=='supported_answer' and q['answer_supported'] else q['diagnostic']['code']
        if native!=actual['proof']:
            differences['real_proof']=native
        grades={'id':ident,'scenario':case['scenario'],'match':not differences,'differences':differences}
        graded.append(grades)
    report={'draw':draw,'cases':len(graded),'matched':sum(g['match'] for g in graded),
            'writer_attempts':sum(row['outcome']['attempts'] for row in run['cases']),
            'writes':sum(row['outcome']['writes'] for row in run['cases']),
            'durable_completions':sum(row['outcome']['store']=='completed' for row in run['cases']),
            'rows':graded}
    with a.output.open('x') as f:
        f.write(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='rows'}))
    if report['matched']!=report['cases']:
        raise SystemExit(1)


if __name__=='__main__':
    main()
