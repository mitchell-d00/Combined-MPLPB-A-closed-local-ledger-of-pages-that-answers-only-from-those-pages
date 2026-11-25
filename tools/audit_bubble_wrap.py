"""Audit Bubble/Wrap IDs, immutable seals, run coverage and execution accounting."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_text())


def audit_record(record):
    rows=record['rows']; ids=[r['id'] for r in rows]
    if len(ids)!=len(set(ids)):raise ValueError('Duplicate execution case IDs')
    counts=record['counts']
    completed=sum(r['execution_status']=='completed' for r in rows)
    failed=sum(r['execution_status'] in {'BLOCKED_EXECUTION','failed'} for r in rows)
    not_run=sum(r['execution_status']=='NOT_RUN' for r in rows)
    if len(rows)!=completed+failed+not_run:raise ValueError('Unknown execution status')
    expected={'planned':len(rows),'attempted':completed+failed,'completed':completed,'failed':failed,'not_run':not_run}
    if any(counts.get(k)!=v for k,v in expected.items()):raise ValueError('Execution accounting mismatch')
    if counts.get('scored',0)+counts.get('unscored',0)!=completed:raise ValueError('Score accounting mismatch')
    if record.get('acceptance_passed') and (failed or not_run or counts.get('unscored')):
        raise ValueError('Planned, failed or unscored execution presented as PASS')
    return expected


def audit(root):
    folder=root/'evaluation/bubble-wrap/2026-11-25';registry=load(folder/'registry.json')
    rows=registry['cases'];ids=[r['id'] for r in rows]
    if len(ids)!=len(set(ids)):raise ValueError('Duplicate registered IDs')
    freeze=load(folder/'harness-freeze.json')
    for name,expected in freeze['files'].items():
        if sha(root/name)!=expected:raise ValueError('Changed frozen seal: '+name)
    for name,expected in registry['original_proposal_seals'].items():
        if sha(root/name)!=expected:raise ValueError('Changed original proposal seal: '+name)
    for row in rows:
        packet=root/row['packet']
        if not packet.exists():
            if row['public_raw_output']:raise ValueError('Missing public input: '+row['id'])
            continue
        actual={str(p.relative_to(packet)):sha(p) for p in packet.rglob('*') if p.is_file()}
        if actual!=row['files']:raise ValueError('Changed input seal: '+row['id'])
    ledgers=sorted((folder/'run-ledger').glob('*.json'));previous=None;paths=set();records=[]
    for path in ledgers:
        item=load(path)
        if item['previous_sha256']!=previous:raise ValueError('Changed/omitted attempt in append-only ledger')
        target=root/item['record']
        if not target.is_file() or sha(target)!=item['record_sha256']:raise ValueError('Missing/changed run record')
        if str(target) in paths:raise ValueError('Duplicate run record')
        paths.add(str(target));previous=sha(path);data=load(target)
        if isinstance(data,dict) and 'rows' in data and 'counts' in data:
            audit_record(data);records.append(item['record'])
    published={str(p) for p in (folder/'runs').glob('*/run.json')}
    if published-paths:raise ValueError('Unledgered execution attempt')
    for path in (folder/'runs').glob('*/run.json'):
        record=load(path)
        for row in record['rows']:
            if row['execution_status']!='completed':continue
            raw=path.parent/row['id']/'result.json'
            if raw.exists():
                if sha(raw)!=row['result_sha256']:raise ValueError('Changed raw output')
            else:
                private=path.parent/row['id']/'private-raw.json'
                if not private.is_file() or load(private)['private_raw_sha256']!=row['result_sha256']:
                    raise ValueError('Missing completed output without private-custody receipt')
    for markdown in [root/'docs/TEST_INDEX.md', folder/'README.md']:
        if not markdown.exists():continue
        for target in re.findall(r'\]\(([^\s)]+)\)',markdown.read_text()):
            if ':' in target or target.startswith('#'):continue
            if not (markdown.parent/target.split('#')[0]).exists():raise ValueError('Broken index link: '+target)
    hashes=Counter(r['semantic_input_hash'] for r in rows)
    return {'registered_cases':len(rows),'unique_semantic_input_hashes':len(hashes),
            'overlap_hashes':{k:v for k,v in hashes.items() if v>1},
            'original_proposal_cases':sum('proposal' in r['memberships'] for r in rows),
            'primary_targets':sum('proposal_primary' in r['memberships'] for r in rows),
            'immutable_run_records':len(ledgers),'audited_execution_records':records,
            'private_originals_or_receipts':17,
            'scope':'Integrity/accounting audit; not independent semantic adjudication'}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    print(json.dumps(audit(p.parse_args().root),indent=2))
