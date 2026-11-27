"""Score the frozen Egyptian batch outside the unmodified Cryptid worker."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

from tools.cryptid_claim_score_v5 import subset


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_bytes())


def check_claim(claim, expected, records):
    citations = claim['citations']
    witness_keys = {(w['source_id'], w['quote'], w['start'], w['end'])
                    for w in expected['witnesses']}
    actual_keys = {(c['source_id'], c['quote'], c.get('body_start'), c.get('body_end'))
                   for c in citations}
    if witness_keys != actual_keys or len(citations) != len(witness_keys):
        return False
    for cit in citations:
        rec = records.get(cit['source_id'])
        start, end = cit['body_start'], cit['body_end']
        if (not rec or not 0 <= start < end <= len(rec['body'])
                or rec['body'][start:end] != cit['quote'] or rec['hash'] != cit['hash']
                or rec['path'] != cit['path']):
            return False
    return subset(claim.get('proposition', {}), expected['proposition'])


def score(registry, key, output):
    freeze = read(registry.with_name('freeze.json'))
    assert digest(registry) == freeze['registry_sha256'] and digest(key) == freeze['key_sha256']
    run = read(output/'run.json')
    assert run['registry_sha256'] == freeze['registry_sha256']
    keys = read(key)
    cases = {c['id']: c for c in read(registry)['cases']}
    assert set(cases) == set(keys) == {entry['id'] for entry in run['cases']}
    rows, questions = [], set()
    for entry in run['cases']:
        ident = entry['id']
        packet = Path(cases[ident]['packet'])/'case.json'
        assert digest(packet) == cases[ident]['files']['case.json']
        question = read(packet)['question']
        questions.add(question)
        expected = keys[ident]
        row = {'id': ident, 'expected': expected['expect'], 'execution_status': entry['execution_status']}
        rows.append(row)
        if entry['execution_status'] != 'completed':
            row['score'] = 'execution_failure'
            continue
        result = output/ident/'result.json'
        assert digest(result) == entry['raw_sha256']
        raw = read(result)
        answer = raw['answer']
        claims = answer['claims']
        records = {r['id']: r for r in raw['records']}
        assert raw['id'] == ident and answer['question'] == question
        label = answer['kind']
        support = answer['answer_supported']
        row.update(kind=label, claims=len(claims), diagnostic=answer['diagnostic']['code'])
        discovery = raw['discovery'].get('passages', [])
        witnesses = expected['witnesses']
        row['discovery'] = (all(any(w['quote'] in p['text'] for p in discovery) for w in witnesses)
                            if witnesses else None)
        if expected['expect'] == 'withhold':
            decision = 'unsupported' if claims or support else 'expected_withhold'
        elif not claims:
            decision = 'unsupported' if support else 'miss'
        elif (len(claims) != 1 or answer['verification']['truth_verified'] is not False
              or not check_claim(claims[0], expected, records)):
            decision = 'unsupported'
        elif label == 'supported_answer' and support:
            decision = 'complete'
        elif label == 'partial_answer' and not support and answer['missing']:
            decision = 'useful_partial'
        else:
            decision = 'unsupported'
        row['score'] = decision
    return {'reader': run['reader_commit'], 'distinct_questions': len(questions),
            'counts': dict(Counter(row['score'] for row in rows)), 'rows': rows,
            'registry_sha256': freeze['registry_sha256'], 'key_sha256': freeze['key_sha256'],
            'run_sha256': digest(output/'run.json'), 'scorer_sha256': digest(Path(__file__)),
            'custody': 'Same operator authored and scored. Scoring key excluded from the worker.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('registry', 'key', 'run', 'output'):
        parser.add_argument('--'+name, type=Path, required=True)
    args = parser.parse_args()
    result = score(args.registry, args.key, args.run)
    with args.output.open('x') as stream:
        stream.write(json.dumps(result, indent=2)+'\n')
    print(args.registry.parent.parent.name, result['counts'], flush=True)
