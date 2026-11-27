"""Grade attributable claims, exact witnesses and proof reach outside the worker."""
import argparse
from collections import Counter
import importlib.util
from pathlib import Path

from tools.cryptid_trial_v5 import read, save, sha

HOME = Path(__file__).resolve().parent
ROOT = HOME.parents[3]
checker_spec = importlib.util.spec_from_file_location(
    'attribution_readout', ROOT/'evaluation/egyptian-gods/attribution-scope/readout.py')
checker = importlib.util.module_from_spec(checker_spec)
checker_spec.loader.exec_module(checker)


def match(claim, target, records):
    if claim.get('source_support_established') is not True or not checker.check_claim(claim, target, records):
        return False
    spans = {w['source_id']: {} for w in target['witnesses']}
    for w in target['witnesses']:
        spans[w['source_id']][w['quote']] = w
    return all(c.get('original_witness') == {
        'coordinate_space': 'admitted_record_body_html_utf8',
        **{k: spans[c['source_id']][c['quote']][k]
           for k in ('start_byte', 'end_byte', 'body_html_sha256')},
    } for c in claim['citations'])


def disposition(answer, target, records):
    claims, supported = answer['claims'], answer['answer_supported']
    expected = target['decision']
    if expected == 'withhold':
        return 'unsupported' if supported or claims else 'correct_withhold'
    if not claims:
        return 'unsupported' if supported else 'miss'
    if answer['verification']['truth_verified'] is not False:
        return 'unsupported'
    remaining = list(target['claims'])
    for claim in claims:
        possible = [m for m in remaining if match(claim, m, records)]
        if len(possible) != 1:
            return 'unsupported'
        remaining.remove(possible[0])
    if answer['kind']=='conflict' and not supported and expected=='conflict' and not remaining:
        return 'checked_conflict'
    if answer['kind']=='supported_answer' and supported and expected=='complete' and not remaining:
        return 'complete'
    if not supported and answer['kind']=='partial_answer' and answer['missing']:
        return 'checked_partial'
    return 'unsupported' if supported else 'miss'


def score(phase, key_path, armdir):
    arm = HOME/phase
    seal = read(arm/'freeze.json')
    registry = arm/'registry.json'
    assert sha(registry) == seal['registry_sha256'] and sha(key_path) == seal['key_sha256']
    assert all(sha(ROOT/name) == digest for name,digest in seal['harness'].items())
    run = read(armdir/'run.json')
    assert run['registry_sha256']==seal['registry_sha256'] and run['harness']==seal['harness']
    key=read(key_path)
    rows=[]
    for case, attempt in zip(read(registry)['cases'], run['cases'], strict=True):
        ident=case['id']
        assert ident==attempt['id'] and case['semantic_input_hash']==attempt['input_hash']
        packet=ROOT/case['packet']/'case.json'
        assert sha(packet)==case['files']['case.json']
        question=read(packet)['question']
        expected=key[ident]
        row=dict(id=ident, family=case['family'], question=question, expected=expected['decision'],
                 execution=attempt['execution_status'])
        if attempt['execution_status']!='completed':
            row.update(score='execution_failure', proof_reached=False)
        else:
            path=armdir/ident/'result.json'
            assert sha(path)==attempt['raw_sha256']
            raw=read(path)
            answer=raw['answer']
            assert raw['id']==ident and answer['question']==question
            records={r['id']:r for r in raw['records']}
            diag=answer['diagnostic']
            witnessed=[w for e in expected['claims'] for w in e['witnesses']]
            passages=raw['discovery'].get('passages',[])
            row.update(score=disposition(answer, expected, records), diagnostic=diag['code'],
                       stage=diag['stage'], raw_sha256=sha(path),
                       proof_reached=diag['stage']=='bounded_records' and
                           ((expected['proof_diagnostic'] is not None and
                             diag['code']==expected['proof_diagnostic'])
                            or answer['verification']['semantic']=='bounded_source_report_content'),
                       required_witnesses_discovered=(all(any(w['quote'] in p['text'] for p in passages)
                                               for w in witnessed) if witnessed else None))
        rows.append(row)
    assert len(rows)==len(key)==len({r['id'] for r in rows})
    return dict(reader=run['reader_commit'], cases=len(rows),
                distinct_questions=len({r['question'] for r in rows}),
                counts=dict(Counter(r['score'] for r in rows)), rows=rows,
                run_sha256=sha(armdir/'run.json'), scorer_sha256=sha(Path(__file__)),
                registry_sha256=sha(registry), key_sha256=sha(key_path))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('phase', choices=('diagnostic','fresh'))
    for name in ('key','run','output'):
        parser.add_argument('--'+name, type=Path, required=True)
    args=parser.parse_args()
    result=score(args.phase, args.key, args.run)
    save(args.output, result)
    print(result['reader'], result['counts'])
