"""Versioned acceptance extension for the original 21 reported positives.

The original v1 scorer, inputs and answer/refuse labels stay unchanged. This
host-side audit checks full source roles and both canonical/original witnesses;
it never runs inside the reader or supplies a runtime answer key.
"""
import argparse
import hashlib
import html
import json
from pathlib import Path

from tools import dpercent as D
from tools import verify_bounded_repair as prior

HOME = D.ROOT / 'evaluation/bubble-wrap/2026-11-25/bounded-transition'


def reported_match(folder, result, key):
    answer = result['answer']
    if (answer['kind'] != 'supported_answer' or not answer['answer_supported']
            or len(answer['claims']) != 1 or answer['missing']
            or not prior.citations_valid(answer, result['source_receipts'])):
        return False
    raw = (folder / key['source_file']).read_bytes()
    if D.sha(raw) != key['original_source_sha256']:
        return False
    claim = answer['claims'][0]
    if claim.get('proposition') != key['roles']:
        return False
    if (not claim.get('source_support_established') or not claim.get('qualifiers')
            or not any(' '.join(c['quote'].split()) == ' '.join(key['governing_clause'].split())
                       for c in claim['citations'])):
        return False
    receipts = {s['source_id']: s for s in result['source_receipts']}
    case = D.read(folder / 'case.json')
    for c in claim['citations']:
        source = receipts.get(c['source_id'])
        if source is None or source['raw_sha256'] != key['original_source_sha256']:
            return False
        number = next((i for i, s in enumerate(case['sources'], 1)
                       if s['path'] == source['source_file']), None)
        if number is None:
            return False
        # Documented write admission, independent of the native semantic parser.
        text = '<h1>Synthetic source ' + str(number) + '</h1>\n<pre>' + html.escape(raw.decode()) + '</pre>'
        admitted = text.replace('\r\n', '\n').strip().encode()
        w = c.get('original_witness', {})
        a, b = w.get('start_byte'), w.get('end_byte')
        if (w.get('coordinate_space') != 'admitted_record_body_html_utf8'
                or w.get('body_html_sha256') != hashlib.sha256(admitted).hexdigest()
                or type(a) is not int or type(b) is not int or not 0 <= a < b <= len(admitted)
                or html.unescape(admitted[a:b].decode()) != c['quote']):
            return False
    return True


def score_targets(packets, run):
    amendment = D.read(HOME / 'amendment.json')
    assert D.sha((HOME / 'positive-witness-key.json').read_bytes()) == amendment['key_sha256']
    receipt = D.read(run / 'run.json')
    executions = {r['case_id']: r for r in receipt['cases']}
    rows = []
    for key in D.read(HOME / 'positive-witness-key.json'):
        ident = key['id']; entry = executions.get(ident)
        errors = []
        if entry is None or entry['execution'] != 'completed':
            errors.append('execution unavailable; semantic outcome NOT_RUN')
        else:
            p = run / ident / 'result.json'
            assert D.sha(p.read_bytes()) == entry['sha256']
            if not reported_match(packets / 'packets' / ident, D.read(p), key):
                errors.append('full source-scoped claim, qualification or citation mismatch')
        rows.append({'id': ident, 'original_expected': 'answer', 'errors': errors,
                     'score': 'FAIL' if errors else 'PASS', 'raw_sha256': entry.get('sha256') if entry else None})
    return rows


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args(); output = a.output.resolve(); output.mkdir(parents=True, exist_ok=False)
    packets = prior.unpack_inputs(prior.PACKETS, output); D.verify(packets)
    run = output / 'run'; D.run(packets, run, implementation=D.ROOT)
    prior.score(packets, run, output / 'prior-v1-acceptance.json')
    original = D.read(output / 'prior-v1-acceptance.json')
    rows = score_targets(packets, run)
    allowed = {k['id'] for k in D.read(HOME / 'positive-witness-key.json')}
    expected_findings = {(i, 'reported_statement', 'unscored_support') for i in allowed}
    actual_findings = {(r['case'], r['family'], r['outcome']) for r in original['findings']}
    passed = (actual_findings == expected_findings and not any(r['errors'] for r in rows)
              and original['counts'] == {'retained_complete': 189, 'new_complete': 21,
                    'retained_unresolved': 189, 'retained_refusal': 580, 'unscored_support': 21})
    report = {'revision': original['revision'], 'acceptance_passed': passed,
              'prior_v1_result_preserved': 'prior-v1-acceptance.json', 'target_rows': rows,
              'complete_current_before': 210, 'complete_candidate': 231,
              'positive_denominator': 420, 'retained_refusals': 580,
              'remaining_positive_misses': 189, 'original_labels_unchanged': True,
              'interpretation': '21 already-expected positives independently checked by host witness audit; not a blinded semantic evaluation',
              'independent_semantic_adjudication': 'NOT_RUN', 'native_oocc': 'NOT_RUN'}
    D.save(output / 'acceptance.json', report)
    print(json.dumps(report, indent=2)); return int(not passed)


if __name__ == '__main__':
    raise SystemExit(main())
