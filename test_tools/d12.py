"""Generate paired D6 path controls and trace separate historical observations."""
import argparse
from collections import Counter
import gzip
from html import escape
import json
from pathlib import Path
from random import Random
from tempfile import TemporaryDirectory

from mplpb_answers.d6 import SCHEMA, compile_plan
from mplpb_combined.ledger import withdraw, write
from test_tools.d6 import compare_value, dice_bag, field, read_field
from test_tools.dice_bag import put, read
from tools.sorter_first_study import FAMILIES, ROOT
from tools.unprepared_challenge import frozen, projections, sha


def fixtures(seed):
    rng = Random(seed)
    year, span = rng.randint(1811, 1900), rng.randint(2, 120)
    weather, other = rng.sample(('crisp', 'cool', 'mild', 'dry'), 2)
    earlier = year - span
    day = rng.randint(1, 28)
    exact = f'Oct {day} {year}'
    primary = f'Record-ID: ITEM-11\nEvent Date: October {day}, {year}\nWeather: {weather}\nWitness Count: {earlier}'
    reference = f'Record-ID: ERA-02\nReference Year: {earlier}'
    date_read = read_field('Event Date')
    yes = compare_value('Event Date', exact)
    weather_read = read_field('Weather')
    confirmed = compare_value('Weather', weather)
    difference = {'op': 'year_difference', 'left': field('Reference Year', 'ERA-02'), 'right': field('Event Date')}
    condition = {'op': 'if', 'when': confirmed, 'then': weather_read, 'else': date_read}
    return {'primary': primary, 'reference': reference, 'other_weather': other}, [
        ('record_identity', 'discovery', [weather_read], [read_field('Weather', 'ITEM-12')], None, None, None),
        ('competing_owner', 'eligibility', [weather_read], [weather_read], None, 'duplicate', None),
        ('withdrawn_source', 'eligibility', [weather_read], [weather_read], None, 'withdraw', None),
        ('missing_field', 'field_read', [weather_read], [read_field('Arrival Date')], None, None, None),
        ('explicit_contrast', 'comparison', [confirmed], [compare_value('Weather', other)], False, None, None),
        ('nearby_year', 'comparison', [yes], [compare_value('Event Date', f'Oct {day} {year - 1}')], False, None, None),
        ('lost_precision', 'comparison', [yes], [compare_value('Event Date', str(year))], None, None, None),
        ('wrong_operand_role', 'relation', [difference], [{**difference, 'left': field('Witness Count')}], None, None, None),
        ('reversed_operands', 'relation', [difference], [{**difference, 'left': difference['right'],
                                                          'right': difference['left']}], -span, None, None),
        ('unknown_condition', 'branch', [condition], [{**condition, 'when': compare_value('Unknown Weather', weather)}],
         None, None, None),
        ('missing_required_link', 'composition', [weather_read, difference], [weather_read, {**difference,
         'left': field('Missing Year', 'ERA-02')}], None, None, None),
        ('insufficient_evidence_budget', 'composition', [weather_read, date_read], [weather_read, date_read],
         None, None, 1),
    ]


def observe(report):
    result = report['compiled']
    if len(result.get('steps', [])) == 1:
        result = result['steps'][0]
    return ('unresolved', None) if not report['answer_supported'] else ('resolved', result.get('value'))


def first_unresolved(node, path=()):
    current = path + (node['operation'],)
    if node['status'] == 'resolved':
        return None
    for child in node.get('steps', []):
        trace = first_unresolved(child, current)
        if trace:
            return trace
    return {'path': list(current), 'why': node['why'], 'diagnostic': node.get('diagnostic')}


def generate(seed):
    sources, cases = fixtures(seed)
    rows = []
    for name, stage, before, after, expected, change, budget in cases:
        with TemporaryDirectory(prefix='mplpb-d12-') as ledger:
            def add(ident, body):
                write(ledger, doc_id=ident, title='Fictional historical record', scope='D12 evidence test',
                      body_html='<pre>' + escape(body) + '</pre>', when='2026-11-22')

            add('LOG-1', sources['primary'])
            add('LOG-2', sources['reference'])
            baseline = compile_plan(ledger, {'schema': SCHEMA, 'steps': before})
            if change == 'duplicate':
                base = sources['primary'].splitlines()
                base[-2] = 'Weather: ' + sources['other_weather']
                add('LOG-3', '\n'.join(base))
            elif change == 'withdraw':
                withdraw(ledger, 'LOG-1', when='2026-11-23')
            variant = compile_plan(ledger, {'schema': SCHEMA, 'steps': after}, max_passages=budget or 12)

        wanted = ('unresolved', None) if expected is None else ('resolved', expected)
        correct = baseline['answer_supported'] and observe(variant) == wanted
        rows.append({'seed': seed, 'class': name, 'perturbed_stage': stage,
                     'control_plan': before, 'variant_plan': after, 'source_change': change, 'max_passages': budget or 12,
                     'sources': sources, 'expected': list(wanted), 'passed': correct,
                     'unexpected_completion': wanted[0] == 'unresolved' and variant['answer_supported'],
                     'first_unresolved': first_unresolved(variant['compiled']),
                     'control': baseline, 'variant': variant})
    return rows


def trace_history(original, expansion):
    """Use precomputed frozen-source probes as observations for human review."""
    groups = {}
    cases = []
    for row in original['cases']:
        cases.append((row['id'], 'original_22', row['question'], row['native_kind'], row['native_diagnostic'],
                      row['anchors'], row['baseline_anchors'], row['graph_anchors']))
    for row in expansion['cases']:
        native = row['native']
        panel = 'new_topics' if row['collection'] == 'new' else 'followups'
        cases.append((row['id'], panel, row['question'], native['kind'], native['diagnostic'],
                      native['anchors'], row['baseline_anchors'], row['graph_anchors']))
    for ident, panel, question, kind, diagnostic, anchors, baseline, guided in cases:
        if not anchors:
            signal = 'reference_needed'
        elif kind == 'supported_answer':
            signal = 'native_full_support'
        elif kind == 'conflict':
            signal = 'inspect_conflict'
        elif max(baseline, guided) < anchors:
            signal = 'inspect_passage_discovery'
        else:
            signal = 'inspect_proof_after_discovery'
        entry = {'case_id': ident, 'panel': panel, 'question': question, 'native_kind': kind,
                 'diagnostic': diagnostic, 'draft_anchor_count': anchors,
                 'ordinary_anchors': baseline, 'graph_anchors': guided, 'signal': signal,
                 'independent_truth_review': None}
        groups.setdefault(panel, []).append(entry)
    return {
        'panels': {name: dict(Counter(r['signal'] for r in rows)) for name, rows in groups.items()},
        'fields_by_record': expansion['declared_fields_in_imports'],
        'source_seals': original['originals'],
        'rows': [row for rows in groups.values() for row in rows],
    }


def audit_original(replay, original):
    """Reconstruct source projections from sealed bytes and check native citations."""
    packet_path = replay / 'packets.json.gz'
    if original['native_replay_sha256'] != sha(packet_path.read_bytes()):
        raise ValueError('Historical graph report and native replay differ')
    with gzip.open(packet_path, 'rt', encoding='utf-8') as stream:
        packets = json.load(stream)
    bodies = {}
    for family, (folder, seal) in FAMILIES.items():
        corpus = ROOT / folder
        frozen(corpus, seal)
        bodies[family] = projections(corpus, read(replay / f'{family}-import-receipt.json'))
    results = []
    for packet in packets:
        for ident, answer in zip(packet['ids'], packet['standalone'], strict=True):
            citations = [cite for claim in answer['claims'] for cite in claim['citations']]
            failures = []
            for cite in citations:
                pin, body = bodies[packet['family']].get(cite['source_id'], ({}, ''))
                start, end = cite.get('body_start'), cite.get('body_end')
                if (pin.get('hash') != cite['hash'] or pin.get('path') != cite['path']
                        or type(start) is not int or type(end) is not int
                        or not 0 <= start < end <= len(body) or body[start:end] != cite['quote']):
                    failures.append({'source_id': cite['source_id'], 'start': start, 'end': end})
            results.append({'case_id': ident, 'citations': len(citations), 'mismatches': failures,
                            'native_supported': answer['answer_supported']})
    return {'rows': results, 'citations': sum(r['citations'] for r in results),
            'mismatches': sum(len(r['mismatches']) for r in results),
            'supported_without_citations': sum(r['native_supported'] and not r['citations'] for r in results)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seed', type=int, default=12)
    parser.add_argument('--count', type=int, default=12)
    parser.add_argument('--original-replay', type=Path)
    parser.add_argument('--original-graph', type=Path)
    parser.add_argument('--expanded-graph', type=Path)
    parser.add_argument('--dice-bag-inputs', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    historical = (args.original_replay, args.original_graph, args.expanded_graph)
    if not 1 <= args.count <= 64 or (any(historical) and not all(historical)):
        parser.error('Use 1–64 seeds and supply the replay and both historical graph reports when tracing history')
    cases = [row for seed in range(args.seed, args.seed + args.count) for row in generate(seed)]
    report = {'schema': 'mplpb-d12-study-v1', 'cases': cases, 'pairs': len(cases),
              'passed': sum(row['passed'] for row in cases),
              'unexpected_completions': sum(row['unexpected_completion'] for row in cases),
              'pairs_by_class': dict(Counter(row['class'] for row in cases))}
    history_failed = False
    if args.original_graph:
        original = read(args.original_graph)
        report['history'] = trace_history(original, read(args.expanded_graph))
        audit = audit_original(args.original_replay, original)
        report['history']['citation_audit'] = audit
        history_failed = bool(audit['mismatches'] or audit['supported_without_citations'])
    transfer_failed = False
    if args.dice_bag_inputs:
        transfer = dice_bag(args.dice_bag_inputs)
        records = transfer['records']
        passed = sum(r['passed'] and r['missing_field_withheld'] for r in records)
        report['dice_bag'] = {**transfer, 'passed': passed}
        transfer_failed = passed != len(records)
    put(args.output, report)
    print({k: report[k] for k in ('pairs', 'passed', 'unexpected_completions')})
    if 'history' in report:
        print(report['history']['panels'])
        print('Original citation audit:', audit['citations'], 'citations,', audit['mismatches'], 'mismatches')
    if 'dice_bag' in report:
        print('Dice Bag:', report['dice_bag']['passed'], '/', len(report['dice_bag']['records']))
    return int(report['passed'] != report['pairs'] or transfer_failed or history_failed)


if __name__ == '__main__':
    raise SystemExit(main())
