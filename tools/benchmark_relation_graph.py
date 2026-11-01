"""Mitchell-Tech-style fixed-seed, deduplicated, multi-domain evidence smoke bench.

Sources and expectations are authored independently of the graph matcher.
Records are fictional and sealed through the real local ledger; scoring checks
exact source ID, full quote and source graph, plus refusals and ambiguities.
These are developer regressions, not independent human-language accuracy data.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import random
import re
import tempfile

from mplpb_answers.frames import normalize
from mplpb_answers.support import supported_answer, code_pins
from mplpb_combined.ledger import write

SPEC = (Path(__file__).resolve().parents[1]
        / 'evaluation' / 'relation-graph' / 'diverse-smoke-seeds.json')
SEED = 20261101
RELATIONS = (
    ('storage', 'Store {storage_subject} in {storage_location}.',
     ('Where should I store {storage_subject}?',
      'Where do we store {storage_subject}?',
      'Where do I keep {storage_subject}?',
      'Where should {storage_subject} be stored?')),
    ('responsibility', '{responsible_role} is responsible for {responsibility_subject}.',
     ('Who is responsible for {responsibility_subject}?',
      'Who has responsibility for {responsibility_subject}?')),
    ('due', 'The {due_subject} is due on {due_date}.',
     ('When is {due_subject} due?',
      'What date is {due_subject} due?',
      'What is the due date for {due_subject}?')),
    ('status', 'Status of {status_subject} is {status}.',
     ('What is the status of {status_subject}?',
      'What status is recorded for {status_subject}?')),
    ('location', 'The {location_subject} is located in {location}.',
     ('Where is {location_subject} located?',)),
    ('contents', 'The {contents_subject} contains {contents}.',
     ('What does {contents_subject} contain?',)),
    ('schedule', 'The {scheduled_subject} is scheduled for {scheduled_date}.',
     ('When is {scheduled_subject} scheduled?',)),
)
NEGATIVE_FORMS = (
    ('conditional_storage', 'Where should I store {storage_subject} if wet?'),
    ('negated_responsibility', 'Who is not responsible for {responsibility_subject}?'),
    ('time_bound_due', 'When is {due_subject} due tomorrow?'),
    ('wrong_subject_due', 'What is the due date for {status_subject}?'),
    ('time_bound_location', 'Where is {location_subject} located yesterday?'),
    ('negated_contents', 'What does {contents_subject} not contain?'),
    ('conditional_schedule', 'When is {scheduled_subject} scheduled after repairs?'),
    ('unknown_record', 'When is nonexistent {domain} invoice due?'),
    ('invalid_source_date', 'When is fabricated {domain} cycle due?'),
)


def _write(root, document_id, body):
    write(root, doc_id=document_id, title='Synthetic source record',
          scope='synthetic fixture evidence', body=body,
          when='2026-11-01T00:00Z')


def _source_pages(domain, idx):
    pages = []
    for part, (name, template, _) in enumerate(RELATIONS, 1):
        pages.append((f'SMK-{idx:02d}-{part:02d}', name, template.format(**domain)))
    pages.append((f'SMK-{idx:02d}-08', 'invalid_date',
                  f'The fabricated {domain["domain"]} cycle is due on 2027-19-67.'))
    return pages


def _case_plan(domain, idx):
    pages = _source_pages(domain, idx)
    rows = []
    for part, (relation, _, templates) in enumerate(RELATIONS, 1):
        ident, _, quote = pages[part - 1]
        for variant, template in enumerate(templates, 1):
            rows.append({
                'category': relation, 'variant': variant,
                'question': template.format(**domain),
                'expected': 'return', 'expected_doc': ident,
                'expected_quote': quote,
            })
    polite = (
        (0, 'Please, where should I store {storage_subject}?'),
        (2, 'Can you tell me when is {due_subject} due?'),
        (3, 'Could you tell me what is the status of {status_subject}?'),
    )
    for variant, (index, template) in enumerate(polite, 1):
        ident, relation, quote = pages[index]
        rows.append({
            'category': relation + '_polite', 'variant': variant,
            'question': template.format(**domain),
            'expected': 'return', 'expected_doc': ident,
            'expected_quote': quote,
        })
    for name, template in NEGATIVE_FORMS:
        rows.append({'category': name, 'variant': 1,
                     'question': template.format(**domain),
                     'expected': 'not_in_corpus', 'expected_doc': None,
                     'expected_quote': ''})
    return pages, rows


def _observe(root, row):
    answer = supported_answer(root, row['question'])
    support = getattr(answer, 'support', {}) or {}
    record = answer.record
    actual = answer.text if answer.kind == 'return' else ''
    correct = answer.kind == row['expected']
    if row['expected'] == 'return':
        graph = support.get('graph', {})
        correct = (correct and record is not None
                   and record.id == row['expected_doc']
                   and actual == row['expected_quote']
                   and support.get('status') == 'supported'
                   and graph.get('proof_kind') == 'exact_source_statement'
                   and graph.get('world_verified') is False
                   and graph.get('multi_hop_inference') is False)
    return {
        'question': row['question'], 'expected': row['expected'],
        'kind': answer.kind, 'correct': bool(correct),
        'expected_doc': row['expected_doc'],
        'source_id': record.id if record else None,
        'source_hash': record.hash if record else None,
        'expected_quote': row['expected_quote'], 'quote': actual,
        'graph_version': support.get('graph', {}).get('version'),
        'reason': answer.reason,
    }


def run(path=SPEC):
    path = Path(path)
    raw = path.read_bytes()
    spec = json.loads(raw)
    if spec['seed'] != SEED or spec['schema'] != 'source-graph-diverse-smoke-seeds-v1':
        raise ValueError('Benchmark fixture version or seed changed')
    rng = random.Random(SEED)
    seen = set()
    rows, duplicates, perturbations = [], [], []
    for idx, domain in enumerate(spec['domains'], 1):
        pages, questions = _case_plan(domain, idx)
        rng.shuffle(questions)
        with tempfile.TemporaryDirectory() as root:
            for doc_id, _, quote in pages:
                _write(root, doc_id, quote)
            for question in questions:
                dedup = re.sub(r'\s+', '', normalize(question['question']))
                if dedup in seen:
                    duplicates.append(question['question'])
                    continue
                seen.add(dedup)
                result = _observe(root, question)
                result.update(id=f'MPLPB-SM-{len(rows) + 1:06d}',
                              domain=domain['domain'],
                              category=question['category'],
                              variant=question['variant'])
                rows.append(result)
        # Metamorphic source-value checks reuse the question deliberately;
        # they are separate from the globally unique question numerator.
        with tempfile.TemporaryDirectory() as root:
            replacement = f'Store {domain["storage_subject"]} in revised {domain["domain"]} cabinet.'
            _write(root, f'SMK-{idx:02d}-X1', replacement)
            probe = {
                'question': f'Where should I store {domain["storage_subject"]}?',
                'expected': 'return', 'expected_doc': f'SMK-{idx:02d}-X1',
                'expected_quote': replacement,
            }
            outcome = _observe(root, probe)
            perturbations.append({'domain': domain['domain'], 'category': 'changed_source',
                                  'correct': outcome['correct'], 'actual': outcome})
        # Two independent eligible documents always remain ambiguous,
        # even when the quotes agree: no top-1 fact selector.
        with tempfile.TemporaryDirectory() as root:
            sentence = f'The {domain["due_subject"]} is due on {domain["due_date"]}.'
            _write(root, f'SMK-{idx:02d}-A1', sentence)
            _write(root, f'SMK-{idx:02d}-A2', sentence)
            probe = {
                'question': f'When is {domain["due_subject"]} due?',
                'expected': 'ambiguous', 'expected_doc': None,
                'expected_quote': '',
            }
            outcome = _observe(root, probe)
            perturbations.append({'domain': domain['domain'], 'category': 'duplicate_owner',
                                  'correct': outcome['correct'], 'actual': outcome})
    groups = {}
    for category in sorted({r['category'] for r in rows}):
        subset = [r for r in rows if r['category'] == category]
        groups[category] = {
            'questions': len(subset), 'passed': sum(r['correct'] for r in subset),
            'failed': sum(not r['correct'] for r in subset),
        }
    returned = [r for r in rows if r['kind'] == 'return']
    answerable = [r for r in rows if r['expected'] == 'return']
    return {
        'protocol': 'source-evidence-unique-smoke-v1',
        'seed': SEED,
        'spec_sha256': hashlib.sha256(raw).hexdigest(),
        'code_sha256': code_pins(),
        'role': 'Developer-authored fictional data, fixed-seed smoke regression; not human evaluation.',
        'domains': len(spec['domains']),
        'summary': {
            'unique_questions': len(rows),
            'duplicate_questions_skipped': len(duplicates),
            'duplicate_questions': duplicates,
            'passed': sum(r['correct'] for r in rows),
            'failed': sum(not r['correct'] for r in rows),
            'correct_returns': sum(r['correct'] for r in answerable),
            'answerable_questions': len(answerable),
            'wrong_returns': sum(not r['correct'] for r in returned),
            'correct_refusals': sum(r['correct'] for r in rows
                                    if r['expected'] == 'not_in_corpus'),
            'metamorphic_checks': len(perturbations),
            'metamorphic_passed': sum(r['correct'] for r in perturbations),
        },
        'categories': groups,
        'rows': rows,
        'metamorphic': perturbations,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', default=None)
    args = parser.parse_args()
    report = run()
    if args.output:
        Path(args.output).write_text(json.dumps(report, indent=2) + '\n')
    else:
        print(json.dumps({'summary': report['summary'],
                          'categories': report['categories']}, indent=2))
    if (report['summary']['failed'] or
            report['summary']['metamorphic_passed'] !=
            report['summary']['metamorphic_checks']):
        raise SystemExit(1)


if __name__ == '__main__':
    main()
