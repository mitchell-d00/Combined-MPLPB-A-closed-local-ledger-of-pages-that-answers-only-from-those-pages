"""Compare matched FRUS runs with separate advice and presentation accounting."""
import argparse
from collections import Counter
from pathlib import Path
from tempfile import TemporaryDirectory

from tools import pole_authentic as a

_ADVICE = 'source_named_advice_report'
_PRESENTATION = 'source_quoted_presentation_report'


def _require(condition, reason):
    if not condition:
        raise ValueError(reason)


def _claim_view(claims):
    return [dict(proposition=c['proposition'], citations=[
        {k: cite[k] for k in ('source_id', 'hash', 'quote', 'body_start', 'body_end')}
        for cite in c['citations']]) for c in claims]


def _original_spans(packet, sources):
    boundaries = {
        'FRUS-D19': ('<span class="tei-placeName">Washington', 'April 10, 1969</span>.'),
        'FRUS-D22': ('On April 28, 1969, Secretary of Commerce', 'Commerce, 1970, Vol. I)'),
    }
    spans = []
    for ident, (prefix, suffix) in boundaries.items():
        source = sources[ident]
        raw = (packet / source['path']).read_bytes().decode(source['encoding'])
        _require(raw.count(prefix) == raw.count(suffix) == 1, 'Original witness is ambiguous')
        begin = raw.index(prefix)
        end = raw.index(suffix, begin) + len(suffix)
        spans.append(a.anchor(source, packet, raw[begin:end]))
    return [{k: span[k] for k in ('id', 'path', 'sha256', 'byte_span', 'character_span')} for span in spans]


def _verify_presentation(claim, key):
    proposition = claim['proposition']
    dates, report = claim['citations']
    witness = report['quote']
    _require(
        report['source_id'] == key['anchors'][1]['id']
        and dates['source_id'] == key['anchors'][0]['id']
        and proposition['speaker'] == 'Stans'
        and proposition['addressee'] == 'President Nixon'
        and proposition['modality'] == 'quoted_self_report'
        and proposition['reporting_layer'] == 'editorial_account_quoting_attributed_memorandum'
        and proposition['advice_record_date'] == '1969-04-10'
        and proposition['report_date'] == '1969-04-28'
        and proposition['framework'] == 'four economic freedoms'
        and proposition['framework_items'] == ['Freedom to trade', 'Freedom to travel',
                                                'Freedom to invest', 'Freedom to exchange technology']
        and 'April 10, 1969' in dates['quote']
        and 'Maurice Stans reported to President Nixon' in witness
        and 'Stans reported the trip' in witness
        and 'He also reported positive reactions' in witness
        and 'I expressed the basis' in witness
        and 'Memorandum from Secretary Stans to President Nixon, April 28, 1969' in witness
        and all(f'“{number}. {item}' in witness for number, item in enumerate(proposition['framework_items'], 1)),
        'The checked presentation differs from the source-supported comparison')


def compare(packet, custody, freeze, rule, before, after, output):
    frozen = a.read(freeze)
    seal = a.seal_for(packet)
    _require((frozen['packet_seal_sha256'], frozen['custody_key_sha256'], frozen['candidate_rule_sha256'])
             == (a.digest((packet / 'seal.json').read_bytes()), seal['key_sha256'], a.digest(rule.read_bytes())),
             'The packet, key or rule differs from the freeze')
    receipts = [a.read(path) for path in (before, after)]
    order = frozen['same_cases'] + frozen['added_controls']
    _require(all([row['id'] for row in arm['cases']] == order for arm in receipts), 'Case order differs')
    _require(receipts[0]['revision'] == frozen['baseline_commit'], 'Baseline pin differs')
    keys = {row['id']: row for row in a.read(custody / 'key.json')}
    with TemporaryDirectory() as root:
        scores = []
        for label, path in [('before', before), ('after', after)]:
            scored = Path(root) / (label + '.json')
            a.score(packet, custody, path, scored)
            scores.append(a.read(scored))

    counts = [Counter(), Counter()]
    rows = []
    for index, ident in enumerate(order):
        key = keys[ident]
        decisions = [arm['cases'][index]['answer'] for arm in receipts]
        row = {'id': ident}
        for arm, answer in enumerate(decisions):
            scored = scores[arm]['cases'][index]
            claims = answer['claims']
            relations = [claim['proposition']['relation'] for claim in claims]
            if ident == 'PE-04':
                _require(relations == ([_ADVICE] if arm == 0 else [_ADVICE, _PRESENTATION]),
                         'PE-04 did not preserve advice and resolve the second obligation')
            elif ident in frozen['added_controls']:
                _require(relations == [_ADVICE] and not answer['answer_supported']
                         and answer['kind'] == 'partial_answer', 'Unsupported presentation on control')
            else:
                _require(not claims and not answer['answer_supported'], 'Unexpected claim outside scope')

            if _ADVICE in relations:
                ref = key['anchors'][0]
                _require(any(cite['source_id'] == ref['id']
                             and a.normal(ref['quote']) in a.normal(cite['quote'])
                             for cite in claims[0]['citations']), 'Advice lost its exact anchor')
            if answer['answer_supported']:
                _require(scored['outcome'] == 'complete_with_all_anchors' and not answer['missing']
                         and answer['kind'] == 'supported_answer', 'Complete answer lacks a witness')
                _verify_presentation(claims[1], key)
            decision = ('expected_presentation_withhold' if ident in frozen['added_controls']
                        else 'expected_withhold' if key['expected'] == 'withhold'
                        else 'complete' if answer['answer_supported']
                        else 'partial' if claims else 'miss')
            counts[arm][decision] += 1
            row[('before', 'after')[arm]] = dict(
                strict=decision, kind=answer['kind'], diagnostic=answer['diagnostic']['code'],
                discovery=scored['complete_discovery_anchor_coverage'] if key['expected'] == 'answer' else None,
                propositions=len(claims), claims=_claim_view(claims), missing=answer['missing'],
                presentation_withhold=answer.get('documentary_support', {}).get('presentation_withhold'))
        if row['before']['claims']:
            _require(row['before']['claims'][0] == row['after']['claims'][0], 'Prior advice claim changed')
        rows.append(row)
    sources = {source['id']: source for source in a.read(packet / 'sources.json')}
    a.save(output, {**frozen, 'before': dict(counts[0]), 'after': dict(counts[1]), 'rows': rows,
        'before_receipt_sha256': a.digest(before.read_bytes()), 'after_receipt_sha256': a.digest(after.read_bytes()),
        'native_runtime_sha256': receipts[1]['runtime_sha256'],
        'presentation_original_spans': _original_spans(packet, sources),
        'false_supported_bridges': 0, 'execution_failures': 0,
        'outside_custodian_scoring': 'NOT_RUN', 'independent_historical_accuracy': 'NOT_RUN',
        'independent_semantic_adjudication': 'NOT_RUN', 'native_oocc': 'NOT_RUN'})


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for field in ('packet', 'custody', 'freeze', 'rule', 'before', 'after', 'output'):
        parser.add_argument('--' + field, required=True, type=Path)
    compare(**vars(parser.parse_args()))
