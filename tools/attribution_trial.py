"""Freeze, key-separated replay and scoring for source-attribution trials."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory

BASELINE = '28b8feb871cd0c2eb29440f2ab46623e410622b6'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def save(path, value):
    with Path(path).open('x') as f:
        f.write(json.dumps(value, indent=2, ensure_ascii=False)+'\n')


def prepare(a):
    from attribution_packets import packet
    a.custody.mkdir(mode=0o700)
    a.development.mkdir()
    transfer = a.custody/'transfer'
    transfer.mkdir(mode=0o700)
    seals = {}
    for cohort, target, count in [('development', a.development, 48), ('transfer', transfer, 24)]:
        rows, key = packet(a.seed+':'+cohort, cohort == 'transfer')
        assert len(rows) == count and len(key) == count
        save(target/'inputs.json', rows)
        save(a.custody/(cohort+'-key.json'), key)
        seals[cohort] = {'input_sha256': sha(target/'inputs.json'),
                         'key_sha256': sha(a.custody/(cohort+'-key.json')), 'cases': count}
    save(a.freeze, {'baseline_commit': BASELINE, 'seed': a.seed, 'cohorts': seals,
        'generator_sha256': sha(Path(__file__).with_name('attribution_packets.py')),
        'harness_sha256': sha(__file__), 'rule_sha256': sha(a.rule),
        'custody': {'preparer': 'Betty, same operator', 'scorer': 'Betty, same operator',
            'generator_templates_seen_by_implementer': True,
            'transfer_case_bytes_opened_before_candidate_freeze': False,
            'baseline_worker_reads_transfer_without_showing_implementer': True,
            'worker_receives_key_path': False, 'os_isolation': False,
            'independent_preparation': 'NOT_RUN', 'independent_blinding': 'NOT_RUN',
            'independent_semantic_adjudication': 'NOT_RUN',
            'independent_historical_accuracy': 'NOT_RUN',
            'outside_custodian_scoring': 'NOT_RUN', 'native_oocc': 'NOT_RUN'},
        'budgets': {'records': 8, 'scan_characters': 200000, 'units': 1000,
                    'passages': 12, 'output_characters': 8000}})
    print('Frozen 48 development and 24 unopened transfer cases; hashes, seed, rule, generator and keys recorded.')


def run(a):
    freeze = read(a.freeze)
    assert sha(__file__) == freeze['harness_sha256']
    assert sha(a.inputs) == freeze['cohorts'][a.cohort]['input_sha256']
    implementation = a.implementation.resolve()
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=implementation, text=True).strip()
    if a.phase == 'baseline':
        assert revision == BASELINE
    if a.cohort == 'transfer' and a.phase == 'candidate':
        pin = read(a.candidate)
        assert revision == pin['commit'] and sha(a.archive) == pin['archive_sha256']
        save(a.once, {'candidate': pin, 'started': True})
    sys.path.insert(0, str(implementation))
    from mplpb_combined.ledger import write
    from mplpb_answers.pipeline import answer_query
    from mplpb_answers.body_text import body_text
    from tools.unprepared_challenge import code_pins
    pins = code_pins(implementation)
    rows = []
    for case in read(a.inputs):
        with TemporaryDirectory(prefix='attribution-') as tmp:
            root = Path(tmp)
            records = []
            for source in case['sources']:
                r = write(root, doc_id=source['id'], title='Documentary original', scope='documentary evidence',
                          origin='machine', external='yes', body_html=source['body_html'], when='2026-11-25T00:00Z')
                records.append({'id': r.id, 'path': r.path, 'hash': r.hash_actual, 'body': body_text(r.body_html)})
            budget = case['budget']
            answer = answer_query(root, case['question'], max_passages=budget['passages'],
                                  max_chars=budget['characters']).contract
            rows.append({'id': case['id'], 'question': case['question'], 'records': records, 'answer': answer})
    assert pins == code_pins(implementation)
    if a.cohort == 'transfer' and a.phase == 'candidate':
        assert pins == pin['runtime_sha256']
    save(a.output, {'revision': revision, 'cohort': a.cohort, 'runtime_sha256': pins,
                    'input_sha256': sha(a.inputs), 'worker_receives_key_path': False, 'cases': rows})
    print('Replayed', len(rows), a.cohort, 'cases without key access; output retained.')


def score(a):
    frozen, receipt, key = read(a.freeze), read(a.receipt), read(a.key)
    cohort = receipt['cohort']
    assert sha(a.key) == frozen['cohorts'][cohort]['key_sha256']
    assert receipt['input_sha256'] == frozen['cohorts'][cohort]['input_sha256']
    assert [r['id'] for r in receipt['cases']] == [k['id'] for k in key]
    counts, by_form, rows = Counter(), {}, []
    for expected, observed in zip(key, receipt['cases'], strict=True):
        answer = observed['answer']; claims = answer['claims']; errors = []
        form = expected['document_form']; form_counts = by_form.setdefault(form, Counter())
        supported = expected['supported']
        counts['targets' if supported else 'withhold_targets'] += 1
        form_counts['targets' if supported else 'withhold_targets'] += 1
        if supported:
            if answer['kind'] != 'supported_answer' or not answer['answer_supported'] or len(claims) != 1:
                errors.append('positive target missing')
            for claim in claims:
                p = claim.get('proposition', {})
                checks = {'actor': expected['source_actor'], 'writer': expected['writer'],
                    'recipient': expected['recipient'], 'task': expected['task'],
                    'source_voice': expected['reporting_layer'], 'modality': 'instruction_only',
                    'polarity': 'affirmative', 'completion_established': False,
                    'historical_truth_independently_verified': False}
                for name, value in checks.items():
                    if p.get(name) != value:
                        errors.append('wrong or missing '+name)
                if not any(c['quote'] == expected['source_statement'] for c in claim['citations']):
                    errors.append('complete instruction witness absent')
        elif claims or answer['answer_supported']:
            errors.append('claim on withhold target')
        records = {r['id']: r for r in observed['records']}
        for claim in claims:
            if not claim['citations']:
                errors.append('uncited claim')
            for cite in claim['citations']:
                r = records.get(cite['source_id'])
                if not r or r['body'][cite['body_start']:cite['body_end']] != cite['quote'] or (
                        r['path'] != cite['path'] or r['hash'] != cite['hash']):
                    errors.append('invalid canonical witness')
        if errors:
            counts['failures'] += 1; form_counts['failures'] += 1
            if claims or answer['answer_supported']:
                counts['false_support'] += 1; form_counts['false_support'] += 1
            elif supported:
                counts['misses'] += 1; form_counts['misses'] += 1
        else:
            counts['passed'] += 1; form_counts['passed'] += 1
            if supported:
                counts['positive_coverage'] += 1; form_counts['positive_coverage'] += 1
        code = answer['diagnostic']['code']
        if code in {'reference_scan_budget', 'reader_budget_exceeded'}:
            counts['budget_failures'] += 1
        rows.append({'id': expected['id'], 'expected': expected, 'actual_kind': answer['kind'],
                     'diagnostic': code, 'errors': errors})
    save(a.output, {'cohort': cohort, 'counts': dict(counts), 'by_document_form': by_form,
                    'acceptance_passed': not counts['failures'] and all(v['positive_coverage'] for v in by_form.values()),
                    'receipt_sha256': sha(a.receipt), 'rows': rows, 'custody': frozen['custody']})
    print(json.dumps({'cohort': cohort, 'counts': dict(counts)}))
    return bool(counts['failures'])


def main():
    p = argparse.ArgumentParser(description=__doc__); sub = p.add_subparsers(dest='command', required=True)
    prep = sub.add_parser('prepare')
    for n in ['custody', 'development', 'freeze', 'rule']:
        prep.add_argument('--'+n, type=Path, required=True)
    prep.add_argument('--seed', required=True)
    runp = sub.add_parser('run')
    for n in ['inputs', 'freeze', 'implementation', 'output', 'candidate', 'archive', 'once']:
        runp.add_argument('--'+n, type=Path, required=n in {'inputs', 'freeze', 'implementation', 'output'})
    runp.add_argument('--cohort', choices=['development', 'transfer'], required=True)
    runp.add_argument('--phase', choices=['baseline', 'candidate'], required=True)
    scoring = sub.add_parser('score')
    for n in ['freeze', 'receipt', 'key', 'output']:
        scoring.add_argument('--'+n, type=Path, required=True)
    a = p.parse_args()
    return {'prepare': prepare, 'run': run, 'score': score}[a.command](a)


if __name__ == '__main__':
    raise SystemExit(main())
