"""Compare the frozen FRUS packet with explicit checked-partial accounting."""
import argparse
from collections import Counter
from pathlib import Path
from tempfile import TemporaryDirectory

from tools import pole_authentic as authentic


def compare(packet, custody, freeze, rule, before, after, output):
    frozen = authentic.read(freeze)
    seal = authentic.seal_for(packet)
    if (frozen['packet_seal_sha256'] != authentic.digest((packet / 'seal.json').read_bytes())
            or frozen['custody_key_sha256'] != seal['key_sha256']
            or frozen['candidate_rule_sha256'] != authentic.digest(rule.read_bytes())):
        raise ValueError('Frozen single-class commitments changed')
    receipts = [authentic.read(path) for path in (before, after)]
    order = frozen['same_cases'] + frozen['added_controls']
    if any([r['id'] for r in receipt['cases']] != order for receipt in receipts):
        raise ValueError('Frozen case identities or order changed')
    if receipts[0]['revision'] != frozen['baseline_commit']:
        raise ValueError('Baseline checkout differs from the frozen pin')
    keys = {row['id']: row for row in authentic.read(custody / 'key.json')}
    with TemporaryDirectory() as directory:
        scores = []
        for label, path in [('before', before), ('after', after)]:
            out = Path(directory) / (label + '.json')
            authentic.score(packet, custody, path, out)
            scores.append(authentic.read(out))
    totals = [Counter(), Counter()]
    rows = []
    for index, ident in enumerate(order):
        decisions = [receipt['cases'][index]['answer'] for receipt in receipts]
        coverage = [arm['cases'][index]['complete_discovery_anchor_coverage'] for arm in scores]
        expected = keys[ident]['expected']
        labels = []
        for label, answer in enumerate(decisions):
            claims = answer['claims']
            if expected == 'withhold':
                result = 'false_support' if claims or answer['answer_supported'] else 'expected_withhold'
            elif answer['answer_supported']:
                result = 'complete' if scores[label]['cases'][index]['outcome'] == 'complete_with_all_anchors' else 'false_support'
            elif answer['kind'] == 'partial_answer':
                result = 'partial'
            else:
                result = 'miss'
            totals[label][result] += 1
            labels.append(result)
        after_answer = decisions[1]
        if labels[1] == 'partial':
            claim, = after_answer['claims']
            proposition = claim['proposition']
            anchor = keys[ident]['anchors'][0]
            cites = claim['citations']
            if (proposition['relation'] != 'source_named_advice_report'
                    or proposition['modality'] != 'reported_advice'
                    or len(cites) != 2 or not after_answer['missing']
                    or not all(c['source_id'] == anchor['id'] for c in cites)
                    or not any(authentic.normal(anchor['quote']) in authentic.normal(c['quote']) for c in cites)):
                raise ValueError('The partial does not bind the frozen advice witness')
        rows.append({'id': ident, 'discovery_before': coverage[0] if expected == 'answer' else None,
                     'discovery_after': coverage[1] if expected == 'answer' else None,
                     'before': labels[0], 'after': labels[1],
                     'diagnostic': after_answer['diagnostic']['code'],
                     'claims': after_answer['claims'], 'missing': after_answer['missing']})
    if any(counts['false_support'] for counts in totals):
        raise ValueError('Unsupported complete or partial answer in a frozen run')
    authentic.save(output, {**frozen, 'before': dict(totals[0]), 'after': dict(totals[1]),
        'before_receipt_sha256': authentic.digest(before.read_bytes()),
        'after_receipt_sha256': authentic.digest(after.read_bytes()),
        'native_runtime_sha256': receipts[1]['runtime_sha256'], 'rows': rows,
        'false_supported_bridges': 0, 'execution_failures': 0,
        'outside_custodian_scoring': 'NOT_RUN', 'independent_historical_accuracy': 'NOT_RUN',
        'independent_semantic_adjudication': 'NOT_RUN', 'native_oocc': 'NOT_RUN'})


if __name__ == '__main__':
    cli = argparse.ArgumentParser(description=__doc__)
    for field in ('packet', 'custody', 'freeze', 'rule', 'before', 'after', 'output'):
        cli.add_argument('--' + field, required=True, type=Path)
    compare(**vars(cli.parse_args()))
