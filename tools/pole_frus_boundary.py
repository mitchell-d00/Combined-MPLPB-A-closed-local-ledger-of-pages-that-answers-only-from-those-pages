"""Audit the frozen FRUS comparison boundary using the current native checker."""
import argparse
from pathlib import Path
import re
from tempfile import TemporaryDirectory

from mplpb_answers.documentary import plan
from mplpb_answers.reference_identity import parse_request
from tools import pole_authentic as authentic


def projected_anchor(anchor, body):
    pattern = r'\s+'.join(re.escape(word) for word in anchor['quote'].split())
    matches = list(re.finditer(pattern, body))
    if len(matches) != 1:
        raise ValueError(f'Expected one projected witness for {anchor["id"]}')
    return list(matches[0].span())


def audit(packet, custody, rule, freeze, previous, receipt, output):
    held = authentic.read(freeze)
    current = {
        'candidate_rule_sha256': authentic.digest(rule.read_bytes()),
        'packet_seal_sha256': authentic.digest((packet / 'seal.json').read_bytes()),
        'custody_key_sha256': authentic.digest((custody / 'key.json').read_bytes()),
        'prior_scored_readback_sha256': authentic.digest(previous.read_bytes()),
    }
    if any(held[key] != value for key, value in current.items()):
        raise ValueError('Frozen FRUS commitments changed')
    questions = authentic.read(packet / 'questions.json')
    native = authentic.read(receipt)
    if [row['id'] for row in native['cases']] != held['case_ids']:
        raise ValueError('The worker must run the same ordered frozen cases')
    if [row['id'] for row in questions] != held['case_ids']:
        raise ValueError('The sealed question set differs from the freeze receipt')
    sources = {row['id']: row for row in authentic.read(packet / 'sources.json')}
    refs = {row['id']: row for row in authentic.read(custody / 'key.json')}
    with TemporaryDirectory(prefix='frus-boundary-score-') as temporary:
        report = Path(temporary) / 'native-score.json'
        authentic.score(packet, custody, receipt, report)
        raw_scores = authentic.read(report)
    before = authentic.read(previous)
    if before['source_packet_seal'] != raw_scores['source_packet_seal']:
        raise ValueError('Before and after must use the same packet seal')
    rows = []
    for question, run, old, score in zip(questions, native['cases'], before['cases'],
                                       raw_scores['cases'], strict=True):
        ident = run['id']
        if ident != old['id'] or ident != score['id']:
            raise ValueError('Case order differs from the frozen score')
        records = {record['id']: record for record in run['receipts']}
        observed = [record['id'] for record in run['receipts']]
        if observed != question['sources'] or len(set(observed)) != 2:
            raise ValueError('Expected two distinct original appearances in packet order')
        if len({record['ledger_path'] for record in records.values()}) != 2:
            raise ValueError('Publisher originals must have distinct eligible paths')
        passages = run['discovery']
        chars = sum(len(passage['text']) for passage in passages)
        budget = question['budget']
        if len(passages) > budget['passages'] or chars > budget['characters']:
            raise ValueError('Discovery exceeded a frozen output budget')
        for passage in passages:
            source = records[passage['source_id']]
            start = passage['body_start']
            if (passage['hash'], passage['path']) != (source['ledger_hash'], source['ledger_path']):
                raise ValueError('Discovery witness points to the wrong appearance')
            if start < 0 or source['body'][start:start + len(passage['text'])] != passage['text']:
                raise ValueError('Discovery witness span does not match projected source text')
        witnesses = []
        for ref in refs[ident]['anchors']:
            record = records[ref['id']]
            raw_source = sources[ref['id']]
            path = packet / raw_source['path']
            if authentic.digest(path.read_bytes()) != raw_source['sha256']:
                raise ValueError('Original source bytes changed')
            span = projected_anchor(ref, record['body'])
            if not any(p['source_id'] == ref['id'] and p['body_start'] <= span[0]
                       and span[1] <= p['body_start'] + len(p['text']) for p in passages):
                raise ValueError(f'Frozen discovery witness was unavailable: {ident}')
            witnesses.append({key: ref[key] for key in ('id', 'path', 'sha256', 'byte_span', 'character_span')}
                             | {'projected_character_span': span, 'ledger_path': record['ledger_path'],
                                'ledger_sha256': record['ledger_hash']})
        positive = score['expected'] == 'answer'
        if (positive and {ref['id'] for ref in witnesses} != set(observed)) or (not positive and witnesses):
            raise ValueError(f'Unexpected frozen witness obligations: {ident}')
        answer = run['answer']
        if answer['answer_supported'] or answer['claims']:
            raise ValueError(f'New support requires separate semantic review: {ident}')
        rows.append({
            'id': ident,
            'discovery_before': old['complete_discovery_anchor_coverage'] if witnesses else None,
            'discovery_after': score['complete_discovery_anchor_coverage'] if witnesses else None,
            'strict_before': old['kind'],
            'strict_after': answer['kind'],
            'outcome': score['outcome'],
            'boundary_decision': ('withhold_missing_native_certificate' if positive
                                  else 'correct_withhold'),
            'native_diagnostic': answer['diagnostic']['code'],
            'native_named_reference_admitted': bool(parse_request(question['question'])),
            'native_documentary_goals': [goal['kind'] for goal in (plan(question['question']) or ())],
            'native_claims': len(answer['claims']),
            'discovery_search_complete': run['discovery_search_complete'],
            'passages_returned': len(passages),
            'characters_returned': chars,
            'budget': budget,
            'exact_witness_coordinates': witnesses,
        })
    authentic.save(output, {
        **current,
        'baseline_commit': held['baseline_commit'],
        'worker_checkout_revision': raw_scores['revision'],
        'native_worker_receipt_sha256': authentic.digest(receipt.read_bytes()),
        'native_runtime_sha256': native['runtime_sha256'],
        'candidate_scope': 'evaluation boundary over the existing native checker',
        'before': before['counts'],
        'after': raw_scores['counts'],
        'false_supported_bridges': 0,
        'independent_historical_accuracy': 'NOT_RUN',
        'outside_custodian_scoring': 'NOT_RUN',
        'independent_semantic_adjudication': 'NOT_RUN',
        'native_oocc': 'NOT_RUN',
        'rows': rows,
    })


if __name__ == '__main__':
    cli = argparse.ArgumentParser(description=__doc__)
    for field in ('packet', 'custody', 'rule', 'freeze', 'previous', 'receipt', 'output'):
        cli.add_argument('--' + field, required=True, type=Path)
    audit(**vars(cli.parse_args()))
