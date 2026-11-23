"""Run or index the fixed historical 22, frozen D20, and Primary Book benches."""
import argparse
from collections import Counter, defaultdict
from hashlib import sha256
import json
from pathlib import Path

from test_tools import d20, historical_seams, primary_book_test as books
from tools.article_study import run as replay_history


def read(path):
    return json.loads(path.read_bytes())


def save(path, value):
    with path.open('x', encoding='utf-8') as out:
        json.dump(value, out, ensure_ascii=False, indent=2)
        out.write('\n')


def observations(history, owner, book):
    signals = defaultdict(list)
    for case in history['cases']:
        if case['native_kind'] == 'supported_answer':
            continue
        if case['native_kind'] == 'conflict':
            tag = 'conflict_to_preserve_or_review'
        elif not case['draft_anchors']:
            tag = 'reference_needed'
        elif case['native_kind'] == 'partial_answer':
            tag = 'remaining_proof_obligations'
        elif not case['native_question_plan']:
            tag = 'question_plan_absent'
        elif max(case['ordinary_probe_anchors'], case['record_graph_probe_anchors'],
                 (case['section_edge'] or {}).get('anchor_visibility', 0)) < case['draft_anchors']:
            tag = 'drafted_span_visibility_gap'
        else:
            tag = 'drafted_span_visible_native_support_withheld'
        signals[tag].append({'id': case['case_id'], 'diagnostic': case['native_diagnostic'],
                             'passage_anchors': case['ordinary_probe_anchors'],
                             'graph_anchors': case['record_graph_probe_anchors'],
                             'citations': case['native_citations']})

    return {'schema': 'mplpb-training-benchmarks-v1', 'answer_supported': False,
            'historical_22': {'native_outcomes': history['native_outcomes'], 'case_count': len(history['cases']),
                              'signals': dict(sorted(signals.items())),
                              'independent_historical_assessment': False},
            'd20_seed_20': {'counts': owner['totals'],
                            'review': [row for row in owner['cases']
                                       if row['outcome'] not in ('supported', 'withheld')]},
            'primary_books': {'counts': dict(Counter(row['outcome'] for row in book)), 'cases': book}}


def execute(folder, book_inputs, book_key):
    folder.mkdir()
    history_root = folder / 'original22'
    if replay_history(history_root):
        raise ValueError('Historical replay state or contract preservation guard failed')
    history = historical_seams.run(history_root)
    save(folder/'historical-seams.json', history)
    suite = Path(__file__).resolve().parents[1] / 'evaluation/d20'
    d20_run = d20.run(read(suite/'fixtures.json'))
    save(folder/'d20-native.json', d20_run)
    owner = d20.score(d20_run, read(suite/'answer-key.json'))
    save(folder/'d20-score.json', owner)
    book_run = books.run(book_inputs, read(book_inputs/'questions.json'))
    save(folder/'book-run.json', book_run)
    book_score = books.score(book_run, read(book_key))
    save(folder/'book-score.json', book_score)
    return folder/'historical-seams.json', folder/'d20-score.json', folder/'book-score.json'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    rescore = commands.add_parser('tag')
    for arg in ('historical', 'd20', 'book', 'output'):
        rescore.add_argument('--' + arg, required=True, type=Path)
    run = commands.add_parser('replay')
    for arg in ('book-inputs', 'book-key', 'output'):
        run.add_argument('--' + arg, required=True, type=Path)
    args = parser.parse_args()
    if args.command == 'replay':
        inputs = execute(args.output, args.book_inputs, args.book_key)
        output = args.output/'observations.json'
    else:
        inputs = (args.historical, args.d20, args.book)
        output = args.output
    result = observations(*(read(path) for path in inputs))
    result['inputs_sha256'] = {name: sha256(path.read_bytes()).hexdigest()
                               for name, path in zip(('historical', 'd20', 'book'), inputs, strict=True)}
    save(output, result)
    return int(any(result['d20_seed_20']['counts'].get(k) for k in ('false_support', 'incorrect_support'))
               or any(outcome not in ('correct_source_and_quote', 'withheld')
                      for outcome in result['primary_books']['counts']))


if __name__ == '__main__':
    raise SystemExit(main())
