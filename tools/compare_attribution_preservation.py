"""Exact permanent-corpus contract/discovery comparison, excluding code pins only."""
import argparse
import hashlib
import json
from pathlib import Path


def normalized(value):
    if isinstance(value, dict):
        return {k: normalized(v) for k, v in value.items() if k != 'code_sha256'}
    if isinstance(value, list):
        return [normalized(v) for v in value]
    return value


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def compare(before, after):
    assert before['revision'] == '28b8feb871cd0c2eb29440f2ab46623e410622b6'
    assert before['packet_seal_sha256'] == after['packet_seal_sha256']
    assert len(before['cases']) == len(after['cases']) == 17
    rows = []
    for left, right in zip(before['cases'], after['cases'], strict=True):
        assert left['id'] == right['id'] and left['question'] == right['question']
        a, b = normalized(left['answer']), normalized(right['answer'])
        rows.append({'id': left['id'], 'answer_contract_identical': a == b,
            'discovery_identical': left['discovery'] == right['discovery'],
            'before_contract_sha256': digest(a), 'after_contract_sha256': digest(b),
            'before_discovery_sha256': digest(left['discovery']),
            'after_discovery_sha256': digest(right['discovery']),
            'before_kind': a['kind'], 'after_kind': b['kind'],
            'propositions_before': len(a['claims']), 'propositions_after': len(b['claims'])})
    return {'schema': 'permanent-pe02-preservation-v1', 'cases': rows,
            'acceptance_passed': all(r['answer_contract_identical'] and r['discovery_identical'] for r in rows),
            'scope': 'Entire answer contract and discovery arrays; only code_sha256 fields excluded.',
            'before_receipt_sha256': digest(before), 'after_receipt_sha256': digest(after)}


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    for name in ['before', 'after', 'output']:
        p.add_argument('--'+name, type=Path, required=True)
    a = p.parse_args()
    result = compare(json.loads(a.before.read_text()), json.loads(a.after.read_text()))
    with a.output.open('x') as f:
        f.write(json.dumps(result, indent=2)+'\n')
    print(json.dumps({'cases': len(result['cases']), 'acceptance_passed': result['acceptance_passed']}))
    raise SystemExit(0 if result['acceptance_passed'] else 1)
