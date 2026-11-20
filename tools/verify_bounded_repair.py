"""Replay unchanged public expanded D% packets and check the bounded repair.

The baseline execution and public score are read after the isolated run. New
compound answers are checked against the literal fields of the frozen original.
"""
import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import tarfile

from tools import dpercent as D

PACKETS = D.ROOT / 'evaluation/dpercent-expanded/2026-11-20/public-packets.tar.gz'
BASELINE = D.ROOT / 'evaluation/field-aliases/2026-11-20/final'


def unpack_inputs(archive, output):
    with tarfile.open(archive, 'r:gz') as sources:
        for member in sources:
            relative = Path(member.name)
            if relative.is_absolute() or '..' in relative.parts or relative.parts[0] != 'packets':
                raise ValueError('Unexpected packet path: ' + member.name)
            dest = output / relative
            if member.isdir():
                dest.mkdir(parents=True, exist_ok=True)
            elif member.isfile():
                with sources.extractfile(member) as stream:
                    dest.write_bytes(stream.read())
            else:
                raise ValueError('Unexpected packet member: ' + member.name)
    return output / 'packets'


def citations_valid(answer, receipts):
    source_by_pin = {(row['source_id'], row['path'], row['hash']): row for row in receipts}
    for claim in answer['claims']:
        if not claim['citations']:
            return False
        for cite in claim['citations']:
            source = source_by_pin.get((cite['source_id'], cite['path'], cite['hash']))
            start, end = cite.get('body_start'), cite.get('body_end')
            if source is None:
                return False
            body = source['canonical_body']
            if (type(start) is not int or type(end) is not int
                    or not 0 <= start < end <= len(body) or body[start:end] != cite['quote']):
                return False
    return True


def compound_matches(folder, result, field):
    case = D.read(folder / 'case.json')
    if len(case['sources']) != 1 or len(result['source_receipts']) != 1:
        return False
    raw = (folder / case['sources'][0]['path']).read_bytes()
    lines = raw.decode('utf-8').splitlines()
    required = [line for line in lines if line.startswith((field + ': ', 'Other Label: '))]
    answer = result['answer']
    claims = answer['claims']
    return (len(required) == 2 and len(claims) == 2
            and {claim['text'] for claim in claims} == set(required)
            and all([c['quote'] for c in claim['citations']] == [claim['text']] for claim in claims)
            and result['source_receipts'][0]['raw_sha256'] == D.sha(raw)
            and citations_valid(answer, result['source_receipts']))


def score(packets, run, output):
    baseline = {row['id']: row for row in D.read(BASELINE / 'expanded-score.json')['cases']}
    receipt = D.read(run / 'run.json')
    if receipt['packet_seal_sha256'] != D.sha((packets / 'seal.json').read_bytes()):
        raise ValueError('Run receipt does not pin the unchanged packet seal')
    execution = {row['case_id']: row for row in receipt['cases']}
    if len(baseline) != 1000 or len(execution) != len(receipt['cases']) or set(baseline) != set(execution):
        raise ValueError('Expanded acceptance requires every frozen case once')
    counts = defaultdict(Counter)
    findings = []
    with tarfile.open(BASELINE / 'expanded-execution.tar.gz', 'r:gz') as originals:
        old_receipt = json.load(originals.extractfile('run/run.json'))
        old_hashes = {row['case_id']: row['sha256'] for row in old_receipt['cases']}
        for ident, row in baseline.items():
            family = row['family']
            entry = execution[ident]
            if entry['execution'] != 'completed':
                outcome = 'execution_failure'
            else:
                current_bytes = (run / ident / 'result.json').read_bytes()
                old_bytes = originals.extractfile('run/' + ident + '/result.json').read()
                if D.sha(current_bytes) != entry['sha256'] or D.sha(old_bytes) != old_hashes[ident]:
                    raise ValueError('Result hash mismatch: ' + ident)
                result = json.loads(current_bytes)
                answer = result['answer']
                old = json.loads(old_bytes)['answer']
                supported = answer['answer_supported']
                if row['expected'] == 'refuse':
                    outcome = 'false_support' if supported else 'retained_refusal'
                elif family == 'field_compound':
                    if supported:
                        outcome = ('new_complete' if compound_matches(
                            packets / 'packets' / ident, result, row['features']['field']) else 'incorrect_support')
                    else:
                        outcome = 'missing_compound'
                elif row['outcome'] == 'detected_answer':
                    same = all(answer[key] == old[key] for key in ('claims', 'text', 'kind'))
                    outcome = ('retained_complete' if supported and same and
                               citations_valid(answer, result['source_receipts']) else 'lost_or_changed_support')
                else:
                    outcome = 'unscored_support' if supported else 'retained_unresolved'
            counts[family][outcome] += 1
            if outcome not in {'new_complete', 'retained_complete', 'retained_unresolved', 'retained_refusal'}:
                findings.append({'case': ident, 'family': family, 'outcome': outcome})
    totals = Counter()
    for family_counts in counts.values():
        totals.update(family_counts)
    report = {'revision': receipt['checkout_revision'], 'isolated_run': receipt['network_isolated'],
              'counts': dict(totals), 'by_family': {k: dict(v) for k, v in counts.items()},
              'findings': findings, 'independent_semantic_review': 'NOT RUN'}
    D.save(output, report)
    print(json.dumps({**report, "findings": findings[:10], "finding_count": len(findings)}, indent=2))
    return not findings and totals == {
        'retained_complete': 189, 'new_complete': 21, 'retained_unresolved': 210, 'retained_refusal': 580}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    packets = unpack_inputs(PACKETS, output)
    D.verify(packets)
    run = output / 'run'
    D.run(packets, run, implementation=D.ROOT)
    return 0 if score(packets, run, output / 'acceptance.json') else 1


if __name__ == '__main__':
    raise SystemExit(main())
