"""Exact-head replay of frozen pottery and regression probes, preserving 6/59.

The historical evaluation's document-ID comparison is a proxy, not semantic
entailment; new returned sentences require separately documented human review.
No existing frozen report or source file is updated by this runner.
"""
import argparse
import hashlib
import json
from pathlib import Path
from tools.evaluate_answer_reliability import evaluate as evaluate_all
from tools.simulate_relation_graph_users import run as simulate

ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / 'evaluation/practical-coverage/after.json'
SETS = ('probes', 'probes_heldout', 'probes_adjacent')


def evaluate():
    baseline_bytes = BASELINE.read_bytes()
    baseline = json.loads(baseline_bytes)
    current = evaluate_all()
    changes = {}
    for name in SETS:
        previous = baseline['datasets'][name]
        now = current['datasets'][name]
        original = {row['id']: row['supported'] for row in previous['rows']}
        changed = []
        for row in now['rows']:
            current_answer = row['supported']
            old = original[row['id']]
            if (current_answer['kind'], current_answer['id'], current_answer['text']) != (
                    old['kind'], old['id'], old['text']):
                changed.append({
                    'id': row['id'],
                    'question': row['question'],
                    'expected': row['expected'],
                    'expected_doc': row.get('expected_doc'),
                    'before': {'kind': old['kind'], 'record_id': old['id'],
                               'quote': old['text']},
                    'after': {'kind': current_answer['kind'],
                              'record_id': current_answer['id'],
                              'quote': current_answer['text'],
                              'return_correct_document_proxy': current_answer['return_correct'],
                              'support': current_answer['support']},
                })
        changes[name] = {
            'frozen_sha256': now['sha256'],
            'historical_metrics': previous['metrics'],
            'current_metrics': now['metrics']['supported'],
            'changed_cases': changed,
        }
    return {
        'report_schema': 'relation-graph-frozen-retest-v1',
        'historical_report_sha256': hashlib.sha256(baseline_bytes).hexdigest(),
        'historical_result_unchanged': '6/59 (10.2%), 2026-10-31',
        'current_role': 'inspected development reuse, not fresh holdout',
        'scoring_limit': 'Document ID and exact quotation are automated proxies; independently review every new return and near miss before any semantic accuracy or deployment claim.',
        'current_support_code_sha256': current['support_code'],
        'pottery_sets': changes,
        'synthetic_users': simulate(),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', default=None,
                        help='New report path only; historical after.json is never overwritten')
    args = parser.parse_args()
    result = evaluate()
    output = json.dumps(result, indent=2) + '\n'
    if args.output:
        target = Path(args.output)
        if target.resolve() == BASELINE.resolve() or target.resolve() == (
                ROOT / 'evaluation/reliability/after.json').resolve():
            raise SystemExit('Refusing to overwrite a historical result')
        target.write_text(output)
    else:
        summary = {
            name: {
                'old_correct': data['historical_metrics']['correct'],
                'new_correct': data['current_metrics']['correct'],
                'old_answerable_coverage': data['historical_metrics']['answerable_coverage'],
                'new_answerable_coverage': data['current_metrics']['answerable_coverage'],
                'wrong_returns': data['current_metrics']['wrong_returns'],
                'changes': [r['id'] for r in data['changed_cases']]
            }
            for name, data in result['pottery_sets'].items()
        }
        print(json.dumps({
            'pottery': summary,
            'synthetic_users': result['synthetic_users']['metrics'],
            'note': result['scoring_limit'],
        }, indent=2))


if __name__ == '__main__':
    main()
