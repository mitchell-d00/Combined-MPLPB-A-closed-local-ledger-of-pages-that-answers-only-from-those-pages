"""Apply the frozen Round 3 obligations with the existing exact claim checker."""
import argparse
from collections import Counter
import importlib.util
from pathlib import Path

from tools.cryptid_claim_score_v5 import norm
from tools.cryptid_trial_v5 import read, save, sha

ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT/'evaluation/egyptian-gods/attribution-scope/readout.py'
spec = importlib.util.spec_from_file_location('existing_readout', SOURCE)
existing_readout = importlib.util.module_from_spec(spec)
spec.loader.exec_module(existing_readout)


def evaluate(expected, answer, records):
    claims = answer['claims']
    support = answer['answer_supported']
    if expected['decision'] == 'withhold':
        return 'unsupported' if support or claims else 'correct_withhold'
    if not claims:
        return 'unsupported' if support else 'miss'
    if answer['verification']['truth_verified'] is not False:
        return 'unsupported'
    unmatched = list(expected['claims'])
    for claim in claims:
        matches = [e for e in unmatched
                   if (e['text'] is None or norm(e['text']) == norm(claim['text']))
                   and existing_readout.check_claim(claim, e, records)]
        if len(matches) != 1:
            return 'unsupported'
        unmatched.remove(matches[0])
    if answer['kind'] == 'supported_answer' and support:
        return 'complete' if not unmatched and expected['decision'] == 'complete' else 'unsupported'
    if support:
        return 'unsupported'
    if answer['kind'] != 'partial_answer' or not answer['missing']:
        return 'miss'
    if expected['decision'] == 'partial':
        return ('checked_partial' if not unmatched and
                {norm(m) for m in expected['missing']} == {norm(m) for m in answer['missing']}
                else 'miss')
    return 'checked_partial' if unmatched else 'miss'


def evaluate_arm(home, run_dir, role, pin, key):
    registry = read(home/'registry.json')
    seal = read(home/'freeze.json')
    record = read(run_dir/'run.json')
    assert record['reader_commit'] == pin['commit']
    assert record['registry_sha256'] == seal['registry_sha256']
    assert record['harness'] == seal['harness']
    assert {c['id'] for c in record['cases']} == {c['id'] for c in registry['cases']} == set(key)
    assert len(record['cases']) == len(registry['cases'])
    rows, questions = [], set()
    for case, attempt in zip(registry['cases'], record['cases'], strict=True):
        assert case['id'] == attempt['id'] and case['semantic_input_hash'] == attempt['input_hash']
        packet = ROOT/case['packet']/'case.json'
        assert sha(packet) == case['files']['case.json']
        question = read(packet)['question']
        questions.add(question)
        expected = key[case['id']]
        row = dict(id=case['id'], family=case['family'], question=question, expected=expected['decision'],
                   execution_status=attempt['execution_status'])
        rows.append(row)
        if attempt['execution_status'] != 'completed':
            row['score'] = 'execution_failure'
            continue
        result = run_dir/case['id']/'result.json'
        assert sha(result) == attempt['raw_sha256']
        raw = read(result)
        answer = raw['answer']
        assert raw['id'] == case['id'] and answer['question'] == question
        records = {r['id']: r for r in raw['records']}
        passages = raw['discovery'].get('passages', [])
        inspection = raw['interpretation_inspection']
        witnesses = [w for claim in expected['claims'] for w in claim['witnesses']]
        row.update(score=evaluate(expected, answer, records), kind=answer['kind'],
                   diagnostic=answer['diagnostic']['code'], claims=len(answer['claims']),
                   interpretation_observed=bool(inspection['documentary_plan'] or inspection['finite_frame']),
                   witnesses_discovered=(all(any(w['quote'] in p['text'] for p in passages)
                                               for w in witnesses) if witnesses else None),
                   raw_sha256=sha(result))
    return dict(role=role, commit=pin['commit'], distinct_questions=len(questions),
                run_sha256=sha(run_dir/'run.json'), counts=dict(Counter(r['score'] for r in rows)), rows=rows)


def compare(ref, released):
    grade = {'complete': 2, 'checked_partial': 1, 'correct_withhold': 1, 'miss': 0}
    recovered, lost, execution_uncompared = [], [], []
    for before, new in zip(ref['rows'], released['rows'], strict=True):
        assert before['id'] == new['id']
        old, after = before['score'], new['score']
        if 'execution_failure' in (old, after):
            execution_uncompared.append(new['id'])
            continue
        if grade.get(after, -1) > grade.get(old, -1) and grade.get(after, 0) > 0:
            recovered.append(new['id'])
        if grade.get(old, 0) > 0 and grade.get(after, -1) < grade[old]:
            lost.append(new['id'])
    return dict(coverage_recoveries=recovered, lost_valid_outcomes=lost,
                execution_uncompared=execution_uncompared)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('run', 'key', 'output'):
        parser.add_argument('--'+name, type=Path, required=True)
    args = parser.parse_args()
    study = SOURCE.parents[2]/'cryptid/bunyip/round3'
    home = study/'diagnostic'
    seal = read(home/'freeze.json')
    assert sha(home/'registry.json') == seal['registry_sha256']
    assert sha(args.key) == seal['key_sha256']
    assert all(sha(ROOT/path) == value for path, value in seal['harness'].items())
    pins = read(study/'readers.json')
    key = read(args.key)
    arms = {role: evaluate_arm(home, args.run/role, role, pin, key) for role, pin in pins.items()}
    save(args.output, dict(schema='bunyip-round3-first-score-v1', key_sha256=seal['key_sha256'],
                           arms=arms, paired_comparisons={role: compare(arm, arms['released'])
                               for role, arm in arms.items() if role != 'released'}))


if __name__ == '__main__':
    main()
