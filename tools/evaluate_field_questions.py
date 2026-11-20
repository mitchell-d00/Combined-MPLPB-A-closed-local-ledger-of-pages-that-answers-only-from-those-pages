"""Score public field-question CSVs against already-created native fixture ledgers.

Keys stay in this evaluator; only question, ledger and profile reach answer_query.
No models, question rewriting, network access or source writes are performed.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import platform
import resource
import time

from mplpb_answers.pipeline import answer_query


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--package', type=Path, required=True)
    p.add_argument('--fixtures', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    keys = {r['record_id']: r for r in csv.DictReader((args.package/'fixtures.csv').open(newline=''))}
    questions = list(csv.DictReader((args.package/'test_questions.csv').open(newline='')))
    counts = {'tested': 0, 'supported': 0, 'exact_field_value_matches': 0,
              'incorrect_supported': 0, 'errors': 0, 'unscored': 0}
    before = time.perf_counter(), time.process_time()
    with (args.output/'cases.jsonl').open('x') as f:
        for row in questions:
            field = row['field']
            expected = field + ': ' + keys[row['record_id']][field.lower().replace(' ', '_')]
            counts['tested'] += 1
            try:
                result = answer_query(args.fixtures/row['record_id'], row['query']).contract
                supported = result['answer_supported']
                matches = supported and bool(result['claims']) and all(c['text'] == expected for c in result['claims'])
                counts['supported'] += int(supported)
                counts['exact_field_value_matches'] += int(matches)
                counts['incorrect_supported'] += int(supported and not matches)
                f.write(json.dumps({'question': row, 'expected_source_field': expected,
                                    'exact_field_value_match': matches, 'result': result})+'\n')
            except Exception as exc:
                counts['errors'] += 1
                f.write(json.dumps({'question': row, 'error': type(exc).__name__, 'message': str(exc)})+'\n')
    report = {'schema': 'field-question-csv-evaluation-v1', 'counts': counts,
              'input_sha256': {name: hashlib.sha256((args.package/name).read_bytes()).hexdigest()
                               for name in ('fixtures.csv', 'test_questions.csv')},
              'wall_seconds': time.perf_counter()-before[0], 'cpu_seconds': time.process_time()-before[1],
              'peak_process_rss_bytes': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,
              'environment': {'python': platform.python_version(), 'platform': platform.platform()},
              'source_bytes_read': None, 'human_review_seconds': None, 'independent_review': 'NOT RUN',
              'scope': 'Exact synthetic field/value scoring only; no historical accuracy or semantic synonym validation.'}
    (args.output/'report.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report))
    return int(counts['errors'] > 0 or counts['incorrect_supported'] > 0)


if __name__ == '__main__':
    raise SystemExit(main())
