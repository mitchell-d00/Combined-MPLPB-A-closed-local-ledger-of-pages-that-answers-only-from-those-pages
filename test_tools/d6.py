"""Run mixed D6 development cases and optional Dice Bag corpus controls."""
import argparse
from collections import Counter
from html import escape
import json
from pathlib import Path
from random import Random
from tempfile import TemporaryDirectory

from mplpb_answers.d6 import SCHEMA, compile_plan, render
from mplpb_combined.ledger import withdraw, write
from test_tools.dice_bag import packet_with_seal, put, seal_ledger


def field(label, record='ITEM-11'):
    return {'record_id': record, 'field': label}


def read_field(label, record='ITEM-11'):
    return {'op': 'read', **field(label, record)}


def compare_value(label, value, op='match'):
    return {'op': op, **field(label), 'value': value}


def plans(seed):
    """Six operation families with varied source values and fixed counterexamples."""
    rng = Random(seed)
    year = rng.randint(1811, 1900)
    earlier = year - 98
    adjective, other = rng.sample(['crisp', 'mild', 'dry', 'cool'], 2)
    return {
        'body': f'Record-ID: ITEM-11\nObservation Date: October 28, {year}\nEarlier Year: {earlier}\n'
                f'Autumn Weather: {adjective}\nPrior Autumn Weather: {other}\nComparison Count: {earlier}',
        'cases': [
            ('read', 'literal', read_field('Observation Date'), 'resolved', f'October 28, {year}'),
            ('read', 'missing', read_field('Arrival Date'), 'unresolved', None),
            ('match', 'equivalent-date', compare_value('Observation Date', f'Oct 28 {year}'), 'resolved', True),
            ('match', 'nearby-year', compare_value('Observation Date', f'Oct 28 {year-1}'), 'resolved', False),
            ('match', 'precision', compare_value('Observation Date', str(year)), 'unresolved', None),
            ('not_match', 'explicit-contrast', compare_value('Prior Autumn Weather', adjective, 'not_match'), 'resolved', True),
            ('not_match', 'missing-not-false', compare_value('Arrival Date', f'Oct 28 {year}', 'not_match'), 'unresolved', None),
            ('year_difference', 'recorded-numbers', {'op': 'year_difference', 'left': field('Earlier Year'),
                'right': field('Observation Date')}, 'resolved', 98),
            ('year_difference', 'count-not-year', {'op': 'year_difference', 'left': field('Comparison Count'),
                'right': field('Observation Date')}, 'unresolved', None),
            ('if', 'then', {'op': 'if', 'when': compare_value('Autumn Weather', adjective),
                'then': read_field('Observation Date'), 'else': read_field('Arrival Date')}, 'resolved', 'then'),
            ('if', 'else', {'op': 'if', 'when': compare_value('Prior Autumn Weather', adjective),
                'then': read_field('Arrival Date'), 'else': read_field('Prior Autumn Weather')}, 'resolved', 'else'),
            ('if', 'unknown', {'op': 'if', 'when': compare_value('Arrival Date', f'Oct 28 {year}'),
                'then': read_field('Observation Date'), 'else': read_field('Earlier Year')}, 'unresolved', None),
            ('all', 'all-supported', {'op': 'all', 'steps': [read_field('Observation Date'),
                read_field('Autumn Weather'), read_field('Earlier Year')]}, 'resolved', None),
            ('all', 'one-missing', {'op': 'all', 'steps': [read_field('Observation Date'),
                read_field('Arrival Date')]}, 'unresolved', None),
        ],
    }


def evaluate(seed):
    fixture = plans(seed)
    rows = []
    with TemporaryDirectory(prefix='mplpb-d6-') as ledger:
        write(ledger, doc_id='ALMANAC-1', title='Fictional almanac', scope='documentary evidence',
              body_html='<pre>' + escape(fixture['body']) + '</pre>', when='2026-11-22')
        for operation, ident, step, expected, value in fixture['cases']:
            report = compile_plan(ledger, {'schema': SCHEMA, 'steps': [step]})
            result = report['compiled']['steps'][0]
            matched = (result['status'] == expected
                       and result.get('value', result.get('branch')) == value
                       and report['answer_supported'] == (expected == 'resolved'))
            rows.append({'family': operation, 'case': ident, 'passed': matched, 'report': report})
        withdraw(ledger, 'ALMANAC-1', when='2026-11-23')
        report = compile_plan(ledger, {'schema': SCHEMA, 'steps': [read_field('Observation Date')]})
        rows.append({'family': 'read', 'case': 'withdrawn', 'passed': not report['answer_supported']
                     and not report['evidence'], 'report': report})
    return rows


def dice_bag(inputs):
    packet, seal = packet_with_seal(inputs)
    rows = []
    with TemporaryDirectory(prefix='mplpb-d6-dice-') as ledger:
        seal_ledger(ledger, packet['sources'])
        for source in packet['sources']:
            fields = list(source['fields'])
            plan = {'schema': SCHEMA, 'steps': [read_field(label, source['id']) for label in fields]}
            compiled = compile_plan(ledger, plan)
            values = [s.get('value') for s in compiled['compiled'].get('steps', [])]
            valid = compiled['answer_supported'] and values == [source['fields'][label] for label in fields]
            absence = {'schema': SCHEMA, 'steps': [read_field(fields[0], source['id']),
                                                  read_field('Shaking Duration', source['id'])]}
            control = compile_plan(ledger, absence)
            rows.append({'id': source['id'], 'passed': valid, 'missing_field_withheld': not control['answer_supported'],
                         'report': compiled, 'boundary_report': control})
    return {'packet_sha256': seal['packet_sha256'], 'records': rows}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seed', type=int, default=6)
    parser.add_argument('--count', type=int, default=6)
    parser.add_argument('--dice-bag-inputs', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if not 1 <= args.count <= 64:
        parser.error('Use 1–64 seeds')
    cases = [{'seed': seed, **row} for seed in range(args.seed, args.seed + args.count)
             for row in evaluate(seed)]
    totals = Counter(row['family'] for row in cases if row['passed'])
    evidence = {'schema': 'd6-study-v1', 'cases': cases, 'passes_by_family': dict(totals),
                'total': len(cases), 'pass': sum(row['passed'] for row in cases)}
    if args.dice_bag_inputs:
        evidence['dice_bag'] = dice_bag(args.dice_bag_inputs)
    put(args.output, evidence)
    print(json.dumps({k: evidence[k] for k in ('total', 'pass', 'passes_by_family')}, indent=2))
    if 'dice_bag' in evidence:
        rows = evidence['dice_bag']['records']
        print('Dice Bag:', sum(r['passed'] and r['missing_field_withheld'] for r in rows), '/', len(rows))
    if cases:
        print(render(cases[12]['report']))
    return int(evidence['pass'] != evidence['total'] or any(
        not (r['passed'] and r['missing_field_withheld']) for r in evidence.get('dice_bag', {}).get('records', [])))


if __name__ == '__main__':
    raise SystemExit(main())
