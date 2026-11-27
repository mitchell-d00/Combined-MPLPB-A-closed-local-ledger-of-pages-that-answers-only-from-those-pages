"""Run the retained BB artifacts and audit the unchanged 96-case comparator."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tarfile
import zipfile

from tools.bubble_wrap_trial import normal
from tools.cryptid_trial_v5 import read, save, sha

BB = Path('evaluation/cryptid/bunyip/round2/bb-c3-retained-v2.tar.xz')
FIELD = Path('evaluation/field-question-normalization/2026-11-20')
REFERENCE = Path('evaluation/cryptid/full-reproducible-replay/bb-replay-raw-v1.zip')
EGYPTIAN = Path('evaluation/egyptian-gods')
PROPOSAL = EGYPTIAN/'attribution-scope/diagnostic-compatibility-proposal-v1.json'


def bb(output, work):
    from mplpb_combined.reader import PROFILES

    assert sha(BB) == 'f2d4950b0f9943ddebce0d5852e1f0dfb5bfe62f602fb51958ca17ed3009e220'
    packet = FIELD/'public-reproduction.zip'
    assert sha(packet) == 'f4d1c8263dbb8dcf9f7ddbc9fc85be5d005864db4c74fce1a93cda1bb4865718'
    work.mkdir()
    output.mkdir()
    package = work/'package'
    with zipfile.ZipFile(packet) as source:
        source.extractall(package)
    with tarfile.open(BB) as source:
        source.extractall(work, members=[m for m in source.getmembers()
                          if m.name.startswith('baseline-replay/fixtures/')], filter='data')
    fixtures = work/'baseline-replay/fixtures'
    assert len(list(fixtures.iterdir())) == 50
    before = {p.relative_to(fixtures): sha(p) for p in fixtures.rglob('*') if p.is_file()}
    subprocess.run([sys.executable, '-m', 'tools.evaluate_field_questions', '--package', str(package),
                    '--fixtures', str(fixtures), '--output', str(output/'positives')], check=True)
    subprocess.run([sys.executable, str(FIELD/'verify_citations.py'), '--cases',
                    str(output/'positives/cases.jsonl'), '--fixtures', str(fixtures),
                    '--output', str(output/'citations.json')], check=True)
    spec = importlib.util.spec_from_file_location('original_bb', package/'reproduce.py')
    original = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(original)
    with zipfile.ZipFile(REFERENCE) as source:
        reference = json.loads(source.read('candidate/negative-results.json'))
    rows = []
    for row in reference:
        record, tag = row['id'].split('/')
        kwargs = {'profile': PROFILES['external']} if tag == 'external' else {}
        result = original.ask(fixtures/record, row['question'], **kwargs)
        rows.append(dict(id=row['id'], question=row['question'], result=result,
                         identical=result == row['result']))
    save(output/'negatives.json', rows)
    assert before == {p.relative_to(fixtures): sha(p) for p in fixtures.rglob('*') if p.is_file()}
    positive = read(output/'positives/report.json')['counts']
    citations = read(output/'citations.json')
    receipt = dict(positives=positive, citations=citations, negative_cases=len(rows),
                   exact_withholds=sum(r['identical'] and r['result'].get('supported') is False
                                       for r in rows),
                   negative_errors=sum('error' in r['result'] for r in rows), retained_fixture_files=len(before))
    save(output/'receipt.json', receipt)
    print(json.dumps(receipt), flush=True)
    assert positive['exact_field_value_matches'] == positive['tested'] == 900
    assert citations['accepted_questions_checked'] == citations['exact_eligible_citations_checked'] == 900
    assert receipt['negative_cases'] == receipt['exact_withholds'] == 200


def digest(item):
    raw = json.dumps(item, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False)
    return hashlib.sha256(raw.encode()).hexdigest()


def retained(output, strict_exit):
    assert sha(PROPOSAL) == '22868e9f9604a4c3fee87226eecc7ef2aa5d5bdb1982eaa3c47e176b5d7ae97a'
    policy = read(PROPOSAL)
    comparison = read(output/'comparison.json')
    historic = read(EGYPTIAN/'attribution-scope/retained-exact-96.json')
    assert strict_exit == 1 and comparison['rows'] == historic['rows']
    assert comparison['planned'] == comparison['executed'] == 96 and comparison['same_contract'] == 87

    exceptions = {(r['arm'], r['case_id']): r for r in policy['exceptions']}
    matched = []
    for row in comparison['rows']:
        if row['same_contract']:
            continue
        arm, ident = row['arm'], row['case']
        exception = exceptions[(arm, ident)]
        raw = read(output/arm/ident/'result.json')
        assert raw['id'] == ident
        actual = normal(raw['answer'])
        assert actual['kind'] == 'abstain' and not actual['answer_supported'] and not actual['claims']
        assert digest(actual) == exception['candidate']['normalized_contract_sha256']
        assert digest(actual['diagnostic']) == exception['candidate']['diagnostic_sha256']
        matched.append(dict(id=ident, arm=arm, diagnostic=actual['diagnostic']['code']))
    assert len(matched) == len(exceptions) == 9
    save(output/'round3-readback.json', dict(original_exact='FAIL', exact=87, replayed=96,
         unchanged_candidate_diagnostic_fingerprints=matched,
         scope='Byte-identical released reader replay; original PR 110 policy is neither reapplied nor expanded.'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('cohort', choices=('bb','retained'))
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--work', type=Path)
    parser.add_argument('--strict-exit', type=int)
    args = parser.parse_args()
    if args.cohort == 'bb':
        bb(args.output, args.work)
    else:
        retained(args.output, args.strict_exit)
