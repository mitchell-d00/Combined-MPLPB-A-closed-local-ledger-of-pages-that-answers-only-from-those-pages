"""Append-only Bubble and Wrap orchestration and external authored-key scoring."""
import argparse
from collections import Counter
import hashlib
import html
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.bubble_wrap_adapter import execute, sha, snapshot, runtime_files

BASELINE = '5bef945e401f96a6422bb8c468932d330b705fc4'
HOME = ROOT / 'evaluation/bubble-wrap/2026-11-25'
INVENTORY = ROOT / 'evaluation/current-failure-inventory'
FROZEN_TOOLS = ['tools/bubble_wrap_trial.py', 'tools/bubble_wrap_adapter.py',
                'tools/bubble_wrap_worker.py', 'tools/bubble_wrap_packets.py',
                'tools/pole_worker.py', 'tools/study_sandbox.py', 'tests/test_reported_content.py',
                'tools/audit_bubble_wrap.py','tests/test_bubble_wrap_accounting.py']


def read(path):
    return json.loads(Path(path).read_text())


def save(path, value):
    path.parent.mkdir(exist_ok=True, parents=True)
    with path.open('x') as stream:
        stream.write(json.dumps(value, indent=2, ensure_ascii=False) + '\n')


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def normal(value):
    if isinstance(value, dict):
        return {k: normal(v) for k, v in value.items() if k != 'code_sha256'}
    if isinstance(value, list):
        return [normal(v) for v in value]
    return value


def text(value):
    return ' '.join(str(value).split()).casefold()


def register(a):
    from tools.bubble_wrap_packets import prepare
    if not (HOME / 'wrap/matrix-freeze.json').exists():
        prepare(HOME / 'wrap')
    else:
        seal=read(HOME / 'wrap/matrix-freeze.json')
        assert seal['generator_sha256']==sha(ROOT / 'tools/bubble_wrap_packets.py')
        assert seal['matrix_sha256']==sha(HOME / 'wrap/matrix.json')
        assert seal['key_sha256']==sha(HOME / 'wrap/matrix-key.json')
    rows, keys = [], {}
    primary = set(read(INVENTORY / 'proposal/freeze.json')['primary_development_targets'])
    role_key = read(INVENTORY / 'proposal/role-obligations.json')['required_roles']
    writers = {'DP00196':'Mira Vale', 'POLE-f2d6d27cee88948d-00005':'NOEL ASH',
               **{f'FRESH-{n:02d}':'TOMAS HERON' for n in (1,2,4,6)}, 'FRESH-03':'Tomas Heron'}
    # Explicit complete governors, frozen independently of a candidate parser.
    witnesses = {
        'DP00196': 'Mina Cole reported that Mira Vale wrote the canal register.',
        'DP00284': 'Ivo Hart reported that Edda Marén wrote the copper survey report.',
        'POLE-f2d6d27cee88948d-00005': 'Arun Moss reported that Noel Ash wrote the orchard inventory.',
        'POLE-f2d6d27cee88948d-00007': 'Owen Pike reported that Mina Cole wrote the orchard inventory.',
        'POLE-f2d6d27cee88948d-00011': 'Edda Marén said, "Iris Beck wrote the coastal dispatch."',
        'FRESH-01': 'Lina Mercer reported that Hugo Sato wrote the tide ledger.',
        'FRESH-02': 'Lina Mercer said, “Hugo Sato wrote the tide ledger.”',
        'FRESH-03': 'Lina Mercer stated that Hugo Sato wrote the tide ledger.',
        'FRESH-04': 'Lina Mercer reported that Hugo Sato did not write the tide ledger.',
        'FRESH-06': 'Lina Mercer did not report that Hugo Sato wrote the tide ledger.',
    }
    for relative in ('', 'fresh-contrasts', 'matched-contrasts'):
        folder = INVENTORY / relative
        for case in read(folder / 'selection.json')['cases']:
            ident = 'BW-INV-' + case['id']
            packet = folder / case['input_path']
            row = {'id': ident, 'original_id': case['id'], 'family': 'BW-INVENTORY',
                   'origin_prs': [103], 'mechanism': case['family'],
                   'memberships': ['inventory'] + (['proposal_primary'] if case['id'] in primary else []),
                   'packet': str(packet.relative_to(ROOT)), 'files': case['files'],
                   'original_output': str((folder / 'replay' / case['suite'] / case['id'] / 'result.json').relative_to(ROOT)),
                   'protected_rule': 'Source-role/polarity proof; preserve unaffected full contracts',
                   'prior_expected':case['expected'],
                   'allowed_target_change': case['id'] in primary, 'public_raw_output': True}
            rows.append(row)
            if case['id'] in primary:
                keys[ident] = {'expected': 'source_answer', 'roles': dict(role_key[case['id']],
                               conditions=[],source_writer_or_unknown=writers.get(case['id'])),
                               'eligible_complete_witnesses': [witnesses[case['id']]], 'allow_claims': True}
    for row, key in zip(read(HOME / 'wrap/matrix.json')['cases'], read(HOME / 'wrap/matrix-key.json'), strict=True):
        row = dict(row, original_id=row['id'], packet='evaluation/bubble-wrap/2026-11-25/wrap/' + row['packet'],
                   origin_prs=[17, 28, 56, 101, 102, 103], memberships=['wrap'],
                   protected_rule='Writer/reporter/actor, denial scope, conditional reporting and independent authorship',
                   allowed_target_change=True, public_raw_output=True)
        keys[row['id']] = key; rows.append(row)
    # Consumed instruction cohorts: unchanged input objects and admission semantics.
    for cohort, path in [('development', 'development'), ('first', 'transfer'), ('fresh', 'fresh-transfer')]:
        folder = ROOT / 'evaluation/attribution/2026-11-25' / path
        originals = read(folder / 'inputs.json')
        reference = read(folder / 'candidate.json') if (folder / 'candidate.json').exists() else read(
            ROOT / 'evaluation/attribution/2026-11-25/fresh-development/fresh-candidate-development.json')
        reference_rows = {r['id']: r for r in reference['cases']}
        for original in originals:
            ident = 'BW-ATTR-' + cohort + '-' + original['id']
            packet = HOME / 'attribution-inputs' / ident
            case = dict(original, adapter_mode='documentary')
            save(packet / 'case.json', case)
            ref = HOME / 'preservation-references' / (ident + '.json')
            save(ref, reference_rows[original['id']])
            rows.append({'id': ident, 'original_id': original['id'], 'family': 'BW-ATTRIBUTION',
                         'origin_prs': [102], 'memberships': ['attribution'],
                         'mechanism': 'instruction voice and modality', 'protected_rule': 'Entire prior contract',
                         'packet': str(packet.relative_to(ROOT)), 'files': snapshot(packet),
                         'original_case_sha256': digest(original), 'original_output': str(ref.relative_to(ROOT)),
                         'allowed_target_change': False, 'public_raw_output': True})
    # Permission-reprinted originals stay in private custody; only hashes and comparisons publish.
    from tools.pole_focus_extend import frus_rendered
    sources = {r['id']: r for r in read(a.pe02 / 'sources.json')}
    references = {r['id']: r for r in read(a.pe02_reference)['cases']}
    for q in read(a.pe02 / 'questions.json'):
        ident = 'BW-PE02-' + q['id']; packet = a.custody / 'pe02' / ident
        admitted = []
        for source_id in q['sources']:
            s = sources[source_id]; raw = (a.pe02 / s['path']).read_bytes()
            assert hashlib.sha256(raw).hexdigest() == s['sha256']
            admitted.append({'id': source_id, 'title': source_id, 'body_html': frus_rendered(raw, s),
                             'scope': 'public documentary originals', 'when': '2026-11-24T00:00Z',
                             'withdraw': s.get('withdraw', False), 'original_sha256': s['sha256']})
        save(packet / 'case.json', dict(q, sources=admitted, adapter_mode='documentary', discovery=True))
        ref = a.custody / 'pe02-references' / (ident + '.json'); save(ref, references[q['id']])
        rows.append({'id': ident, 'original_id': q['id'], 'family': 'BW-PE02', 'origin_prs': [97, 101, 102],
                     'memberships': ['pe02'], 'mechanism': 'Permanent checked partials, attribution and source states',
                     'protected_rule': 'Entire prior contract and discovery', 'packet': str(packet), 'files': snapshot(packet),
                     'original_output': str(ref), 'allowed_target_change': False, 'public_raw_output': False,
                     'custody': 'Approved permission-reprinted inputs/raw receipts retained privately; hashes and comparisons publish'})
    for row in rows:
        row['case_hash'] = digest(row['files'])
        case=read(ROOT/row['packet']/'case.json');case.pop('id')
        row['semantic_input_hash']=digest({'case':case,'source_hashes':{n:v for n,v in row['files'].items() if n!='case.json'}})
        if row['original_id'] in {r['id'] for r in read(INVENTORY/'proposal/development.json')}:
            row['memberships'].append('proposal')
        row['budgets'] = {'cpu_seconds': 30, 'wall_seconds': 45, 'records': 8, 'scan_characters': 200000,
                          'units': 1000, 'passages': 12, 'output_characters': 8000}
        row['custody_status'] = 'same-operator; worker receives source inputs only; independent adjudication NOT_RUN'
        row['reproduction_command']='python tools/bubble_wrap_trial.py run --implementation BASELINE_OR_CANDIDATE_ROOT --source-commit READER_COMMIT --phase baseline --case-id '+row['id']+' --output NEW_IMMUTABLE_RUN_DIRECTORY'
        row['run_lookup']='Join this stable id to runs/*/run.json and separately appended score records; planned is not passed.'
        row['baseline_pin']=BASELINE
        row['candidate_pin_status']='NOT_RUN at registry freeze; actual pins append in immutable run records'
    save(HOME / 'registry.json', {'baseline_commit': BASELINE, 'cases': rows,
         'original_proposal_seals': {str(p.relative_to(ROOT)): sha(p) for p in (INVENTORY / 'proposal').glob('*.json')},
         'planned_native_controls': {'focused': 56, 'older_integrity_and_status_authority': 'tests.test_record, tests.test_ledger, tests.test_integrity_hunt, tests.test_literal_evidence, tests.test_answer_reliability, tests.test_answer_support',
                                     'report_pins': 'tools/replay_report_pins.py'},
         'independence': 'NOT_RUN; isolation does not establish independent preparation, blinding or adjudication'})
    save(HOME / 'scoring-key.json', keys)
    print('Registered', len(rows), 'rows;', len(primary), 'primary targets; transfer untouched')


def verify_frozen():
    freeze = read(HOME / 'harness-freeze.json')
    for name, expected in freeze['files'].items():
        assert sha(ROOT / name) == expected, 'Changed frozen harness/key: ' + name
    registry = read(HOME / 'registry.json')
    for name, expected in registry['original_proposal_seals'].items():
        assert sha(ROOT / name) == expected, 'Changed original proposal seal'
    for row in registry['cases']:
        assert snapshot(ROOT / row['packet']) == row['files'], 'Changed packet: ' + row['id']
    return registry


def freeze(a):
    parity=read(a.parity)
    assert parity['execution_success'] and all(r.get('parity') for r in parity['rows'])
    for n in ('tools/bubble_wrap_adapter.py','tools/bubble_wrap_worker.py','tools/pole_worker.py','tools/study_sandbox.py'):
        assert parity['harness_sha256'][n]==sha(ROOT/n)
    names = FROZEN_TOOLS + [str(p.relative_to(ROOT)) for p in [HOME / 'registry.json', HOME / 'scoring-key.json',
             HOME / 'wrap/matrix.json', HOME / 'wrap/matrix-key.json', HOME / 'wrap/matrix-freeze.json']]
    save(HOME / 'harness-freeze.json', {'baseline_commit': BASELINE, 'files': {n: sha(ROOT / n) for n in names},
         'adapter_parity_receipt': str(a.parity), 'adapter_parity_sha256': sha(a.parity),
         'native_source_unchanged_at_freeze': True, 'transfer_instances_or_key_opened': False,
         'templates_previously_visible': True, 'same_operator': True})


def run(a):
    registry = read(HOME / 'registry.json') if a.phase == 'parity' else verify_frozen()
    if a.transfer_manifest:
        registry = read(a.transfer_manifest)
    selected = [r for r in registry['cases'] if not a.membership or a.membership in r['memberships']]
    if a.case_id:selected=[r for r in selected if r['id']==a.case_id]
    if not selected:raise ValueError('No planned cases selected')
    if a.phase == 'parity':
        selected = [r for r in selected if 'wrap' not in r['memberships']]
    a.output.mkdir(parents=True, exist_ok=False)
    pins = {str(p.relative_to(a.implementation)): sha(p) for p in runtime_files(a.implementation)}
    rows, failed = [], False
    for row in selected:
        target = a.output / row['id']
        try:
            assert snapshot(ROOT / row['packet']) == row['files']
            result = execute(a.implementation, ROOT / row['packet'], target)
            entry = {'id': row['id'], 'execution_status': 'completed', 'semantic_outcome': 'UNSCORED',
                     'result_sha256': sha(target / 'result.json'), 'case_hash': row['case_hash']}
            if a.phase == 'parity':
                original = read(ROOT / row['original_output'])
                equal = normal(result['answer']) == normal(original['answer'])
                if 'retrieval' in original:
                    equal &= result['retrieval'] == original['retrieval']
                if 'discovery' in original:
                    equal &= result['discovery'] == original['discovery']
                entry['parity'] = bool(equal)
                if not equal: failed = True
        except Exception as error:
            entry = {'id': row['id'], 'execution_status': 'BLOCKED_EXECUTION',
                     'semantic_outcome': 'NOT_RUN', 'error': str(error), 'case_hash': row['case_hash']}
            failed = True
        rows.append(entry)
        save(a.output / (row['id'] + '.record.json'), entry)
    assert pins == {str(p.relative_to(a.implementation)): sha(p) for p in runtime_files(a.implementation)}
    receipt = {'phase': a.phase, 'source_commit': a.source_commit, 'implementation': str(a.implementation),
               'runtime_sha256': pins, 'harness_sha256': {n: sha(ROOT / n) for n in FROZEN_TOOLS},
               'registry_sha256': sha(a.transfer_manifest or HOME / 'registry.json'),
               'rows': rows, 'counts': {'planned': len(rows), 'attempted': len(rows),
                   'completed': sum(r['execution_status'] == 'completed' for r in rows),
                   'failed': sum(r['execution_status'] != 'completed' for r in rows), 'not_run': 0,
                   'scored': 0, 'unscored': sum(r['execution_status'] == 'completed' for r in rows)},
               'execution_success': not failed, 'independent_semantic_adjudication': 'NOT_RUN'}
    save(a.output / 'run.json', receipt)
    print(json.dumps({'counts': receipt['counts'], 'execution_success': not failed}))
    return int(failed)


def citations(result):
    records = {r.get('id', r.get('source_id')): r for r in result.get('records', result.get('source_receipts', []))}
    errors = []
    for claim in result['answer']['claims']:
        if not claim.get('citations'): errors.append('uncited claim')
        for c in claim.get('citations', []):
            record = records.get(c['source_id'])
            body = (record.get('body', record.get('canonical_body')) if record else '')
            if not record or record['hash'] != c['hash'] or body[c['body_start']:c['body_end']] != c['quote']:
                errors.append('invalid eligible canonical witness')
    return errors


def original_citations(result, descriptor):
    """Check raw admitted HTML coordinates without using the candidate parser."""
    packet=ROOT/descriptor['packet']; case=read(packet/'case.json');sources={}
    for number,source in enumerate(case['sources'],1):
        if case.get('adapter_mode')=='documentary':
            sources[source['id']]=source['body_html'].encode()
        else:
            sources[f'SOURCE-{number:04d}']=('<pre>'+html.escape((packet/source['path']).read_bytes().decode())+'</pre>').encode()
    errors=[]
    for claim in result['answer']['claims']:
        if claim.get('proposition',{}).get('relation')!='source_attributed_report_content':continue
        for c in claim['citations']:
            raw=sources[c['source_id']];w=c.get('original_witness',{})
            selected=raw[w.get('start_byte',0):w.get('end_byte',0)]
            if (w.get('coordinate_space')!='admitted_record_body_html_utf8'
                or w.get('body_html_sha256')!=hashlib.sha256(raw).hexdigest()
                or html.unescape(selected.decode())!=c['quote']):
                errors.append('original HTML witness coordinates/hash mismatch')
    return errors


def source_claim_errors(result, key):
    answer = result['answer']; claims = answer['claims']; errors = citations(result)
    expected = key['expected']
    if expected == 'withhold':
        if claims or answer['answer_supported']: errors.append('unsupported claim on independent-authorship target')
        return errors
    kind = 'conflict' if expected == 'conflict' else 'supported_answer'
    if answer['kind'] != kind or answer['answer_supported'] != (kind == 'supported_answer'):
        errors.append('wrong source-scoped decision')
    if len(claims) != (2 if kind == 'conflict' else 1): errors.append('wrong claim count')
    used = []
    for claim in claims:
        prop = claim.get('proposition', {})
        # A witness must contain the whole reporting governor, not just its inner event.
        matches = [i for i, w in enumerate(key['eligible_complete_witnesses'])
                   if any(text(c['quote']) == text(w) for c in claim.get('citations', []))]
        if len(matches) != 1: errors.append('complete reporting witness absent'); continue
        n = matches[0]; used.append(n); roles = dict(key['roles'])
        if n and key.get('conflicting_roles'):
            negative = not (key['roles']['inner_negative'] is True or key['roles']['outer_negative'])
            roles.update(inner_negative=negative, outer_negative=False, content_asserted_by_reporter=True,
                         source_writer_or_unknown=None)
            if roles['conditions']:
                roles.update(inner_negative=None, content_asserted_by_reporter=False)
        for name, expected_value in roles.items():
            actual = prop.get(name)
            if isinstance(expected_value, str):
                equal = text(actual) == text(expected_value)
            else:
                equal = actual == expected_value and (actual is expected_value if expected_value is None or type(expected_value) is bool else True)
            if not equal: errors.append('wrong role/polarity/condition: ' + name)
        if prop.get('historical_truth_independently_verified') is not False:
            errors.append('independent truth asserted')
        if prop.get('relation') != 'source_attributed_report_content': errors.append('wrong proof operation')
        if roles.get('conditions'):
            if prop.get('outer_polarity')!='conditional_unestablished' or prop.get('conditional_content_negative') is not bool(n):
                errors.append('conditional payload or modality changed')
        elif prop.get('outer_polarity') != ('negative' if roles['outer_negative'] else 'affirmative'):
            errors.append('outer reporting polarity changed')
        if not claim.get('source_support_established'): errors.append('missing source support marker')
        if not claim.get('qualifiers'): errors.append('missing reporting qualification')
    if kind == 'conflict' and sorted(used) != [0, 1]: errors.append('conflicting appearance lost')
    return errors


def score(a):
    registry = read(a.transfer_manifest) if a.transfer_manifest else verify_frozen()
    selected = {r['id']: r for r in registry['cases']}
    keys = read(a.transfer_key) if a.transfer_key else read(HOME / 'scoring-key.json')
    run_record = read(a.run / 'run.json'); rows, totals = [], Counter()
    for entry in run_record['rows']:
        ident = entry['id']; descriptor = selected[ident]
        if entry['execution_status'] != 'completed':
            totals['failed_execution'] += 1
            rows.append(dict(entry, score='NOT_RUN')); continue
        raw = a.run / ident / 'result.json'; assert sha(raw) == entry['result_sha256']
        result = read(raw); answer = result['answer']; errors = citations(result)+original_citations(result,descriptor)
        if ident in keys:
            errors += source_claim_errors(result, keys[ident])
        else:
            before = read(ROOT / descriptor['original_output'])
            if normal(answer) != normal(before['answer']): errors.append('unaffected answer contract changed')
            if 'discovery' in before and result.get('discovery') != before['discovery']:
                errors.append('preserved discovery changed')
        totals['scored'] += 1; totals['passed' if not errors else 'failed'] += 1
        totals['complete'] += answer['answer_supported']; totals['partial'] += answer['kind'] == 'partial_answer'
        totals['claims'] += len(answer['claims'])
        totals['false_supported_claim_cases'] += bool(errors and answer['claims'])
        totals['misses'] += bool(errors and not answer['claims'])
        totals['budget_stops'] += 'budget' in answer['diagnostic']['code']
        rows.append({'id': ident, 'family': descriptor['family'], 'case_hash': descriptor['case_hash'],
                     'kind': answer['kind'], 'diagnostic': answer['diagnostic']['code'], 'claim_count': len(answer['claims']),
                     'answer_sha256': digest(normal(answer)), 'errors': errors, 'score': 'PASS' if not errors else 'FAIL',
                     'raw_output_sha256': sha(raw), 'raw_output_public': descriptor['public_raw_output']})
        rows[-1]['known_non_target_incomplete_positive']=(descriptor.get('prior_expected')=='answer'
            and not descriptor['allowed_target_change'] and not answer['answer_supported'])
    save(a.output, {'source_commit': run_record['source_commit'], 'run_sha256': sha(a.run / 'run.json'),
         'registry_sha256': run_record['registry_sha256'], 'counts': dict(totals), 'rows': rows,
         'acceptance_passed': not totals['failed'] and not totals['failed_execution'],
         'custody': 'Same operator; authored source-role keys, no independent semantic adjudication',
         'independent_historical_accuracy': 'NOT_RUN', 'independent_semantic_adjudication': 'NOT_RUN',
         'outside_custodian_scoring': 'NOT_RUN', 'native_oocc': 'NOT_RUN'})
    print(json.dumps(dict(totals)))
    return int(bool(totals['failed'] or totals['failed_execution']))


def main():
    parser = argparse.ArgumentParser(description=__doc__); sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('register')
    for n in ('pe02', 'pe02-reference', 'custody'): p.add_argument('--' + n, type=Path, required=True)
    p = sub.add_parser('freeze'); p.add_argument('--parity', type=Path, required=True)
    p = sub.add_parser('run')
    for n in ('implementation', 'output'): p.add_argument('--' + n, type=Path, required=True)
    p.add_argument('--source-commit', required=True); p.add_argument('--membership');p.add_argument('--case-id')
    p.add_argument('--phase', choices=['parity', 'baseline', 'candidate', 'transfer'], required=True)
    p.add_argument('--transfer-manifest', type=Path)
    p = sub.add_parser('score')
    for n in ('run', 'output'): p.add_argument('--' + n, type=Path, required=True)
    p.add_argument('--transfer-manifest', type=Path); p.add_argument('--transfer-key', type=Path)
    args = parser.parse_args()
    return {'register': register, 'freeze': freeze, 'run': run, 'score': score}[args.command](args)


if __name__ == '__main__':
    raise SystemExit(main())
