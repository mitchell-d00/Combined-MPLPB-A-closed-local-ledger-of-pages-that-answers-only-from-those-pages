"""Replay six developer-authored users against real, isolated sealed ledgers.

This is deterministic development coverage, not independent human evaluation.
Source documents and expected answers are separate from the parser code.
"""
import hashlib
import json
import tempfile
from pathlib import Path

from mplpb_combined.ledger import write
from mplpb_answers.support import supported_answer, code_pins

SPEC = Path(__file__).resolve().parents[1] / 'evaluation' / 'relation-graph' / 'synthetic-users.json'


def run(path=SPEC):
    path = Path(path)
    raw = path.read_bytes()
    data = json.loads(raw)
    rows = []
    for persona in data['personas']:
        with tempfile.TemporaryDirectory() as tmp:
            sources = {}
            for page in persona['documents']:
                write(tmp, doc_id=page['id'], title=page['title'],
                      scope='synthetic reference', body=page['body'],
                      when='2026-11-01T00:00Z')
                sources[page['id']] = page['body']
            for turn, question in enumerate(persona['questions'], 1):
                answer = supported_answer(tmp, question['q'])
                kind = answer.kind
                expected = question['expected']
                expected_quote = question.get('quote', '')
                returned = answer.text if kind == 'return' else ''
                record = answer.record.id if answer.record else None
                correct = kind == expected
                if expected == 'return':
                    correct = (correct and returned == expected_quote
                               and record in sources
                               and expected_quote in sources[record]
                               and answer.support.get('status') == 'supported')
                row = {
                    'persona': persona['id'], 'turn': turn,
                    'question': question['q'], 'expected': expected,
                    'kind': kind, 'correct': bool(correct), 'source_id': record,
                    'quote': returned, 'expected_quote': expected_quote,
                    'reason': answer.reason,
                    'relation_version': answer.support.get('version'),
                    'graph_version': answer.support.get('graph', {}).get('version'),
                    'source_hash': answer.record.hash if answer.record else None,
                }
                rows.append(row)
    answerable = [row for row in rows if row['expected'] == 'return']
    returned = [row for row in rows if row['kind'] == 'return']
    metrics = {
        'questions': len(rows),
        'answerable': len(answerable),
        'correct_returns': sum(row['correct'] for row in answerable),
        'returned': len(returned),
        'wrong_returns': sum(not row['correct'] for row in returned),
        'false_refusals_or_ambiguities': sum(not row['correct'] for row in answerable),
        'correct_refusals': sum(row['correct'] for row in rows if row['expected'] == 'not_in_corpus'),
        'correct_ambiguities': sum(row['correct'] for row in rows if row['expected'] == 'ambiguous'),
        'all_expected_outcomes': sum(row['correct'] for row in rows),
        'return_precision_proxy': (
            sum(row['correct'] for row in returned) / len(returned)
            if returned else None
        ),
        'answerable_coverage_proxy': (
            sum(row['correct'] for row in answerable) / len(answerable)
            if answerable else None
        ),
    }
    return {
        'protocol': 'synthetic-users-v1',
        'limitations': 'Developer-authored fixtures, exact quote and source-ID oracle only; not human-reviewed semantic accuracy or independent users.',
        'spec_sha256': hashlib.sha256(raw).hexdigest(),
        'code_sha256': code_pins(),
        'personas': len(data['personas']),
        'metrics': metrics,
        'rows': rows,
    }


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', default=None)
    args = parser.parse_args()
    result = run()
    report = json.dumps(result, indent=2) + '\n'
    if args.output:
        Path(args.output).write_text(report)
    else:
        print(report)
    if result['metrics']['all_expected_outcomes'] != result['metrics']['questions']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
