"""Install and compare two archived MPLPB revisions with an offline fixture replay."""
import argparse
from collections import Counter, defaultdict
from hashlib import sha256
from html import escape
import json
import os
from pathlib import Path
import platform
import shutil
import statistics
import subprocess
import sys
from tempfile import TemporaryDirectory
from time import perf_counter_ns
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return json.loads(path.read_bytes())


def save(path, value):
    with path.open('x', encoding='utf-8') as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2)
        handle.write('\n')


def checked(command, **options):
    return subprocess.run(command, check=True, **options)


def evaluate(fixtures, output):
    # Runs under the newly installed interpreter. It receives only public
    # fixtures. The coordinator grades the output in a separate process.
    from mplpb_answers.body_text import body_text
    from mplpb_answers.pipeline import answer_query
    from mplpb_combined.ledger import write, withdraw, Ledger

    rows = []
    started = perf_counter_ns()
    for case in read(fixtures)['cases']:
        with TemporaryDirectory(prefix='mplpb-demo-ledger-') as folder:
            ledger = Path(folder)
            for source in case['sources']:
                write(ledger, doc_id=source['id'], title='Documentary entry', scope='Shipment records',
                      body_html='<pre>' + escape(source['body']) + '</pre>', when='2026-11-23')
                if source.get('retired'):
                    withdraw(ledger, source['id'], when='2026-11-23')
            start_query = perf_counter_ns()
            contract = answer_query(ledger, case['question'], mode='strict').contract
            query_ns = perf_counter_ns() - start_query
            current = {(r.id, r.path, r.hash_actual): body_text(r.body_html) for r in Ledger(ledger).servable()}
            relations, witnesses, cites, exact = {}, {}, [], True
            relevant_roles = {'sent_by', 'received_by'}
            for claim in contract['claims']:
                for key, value in claim.get('proposition', {}).items():
                    if key in relevant_roles:
                        if key in relations:
                            exact = False
                        relations[key] = value
                        witnesses[key] = sorted(cite['source_id'] for cite in claim['citations'])
                for cite in claim['citations']:
                    a, b = cite.get('body_start'), cite.get('body_end')
                    body = current.get((cite.get('source_id'), cite.get('path'), cite.get('hash')), '')
                    exact &= type(a) is int and type(b) is int and 0 <= a < b <= len(body) and body[a:b] == cite['quote']
                    cites.append(cite)
            rows.append({'id': case['id'], 'kind': contract['kind'], 'answers': relations, 'witnesses': witnesses,
                         'answer_supported': contract['answer_supported'],
                         'source_truth_verified': contract['verification']['truth_verified'],
                         'text': contract['text'], 'citations': cites, 'exact_citations': exact, 'query_ns': query_ns})
    save(output, {'rows': rows, 'replay_wall_ns': perf_counter_ns() - started})


def score(native, labels):
    rows = {row['id']: row for row in native['rows']}
    keyed = {row['id']: row for row in labels['cases']}
    if len(rows) != len(native['rows']) or rows.keys() != keyed.keys() or len(keyed) != len(labels['cases']):
        raise ValueError('Replay coverage differs from the pinned adjudication key')
    families, outcomes = defaultdict(Counter), Counter()
    false_support = 0
    role_witnesses = {'sent_by': ['DISPATCH-1', 'INDEX-1'],
                      'received_by': ['DISPATCH-1', 'INDEX-1', 'RECEIPT-1']}
    for ident, key in keyed.items():
        result = rows[ident]
        proofs_expected = bool(key['answers'])
        witnesses = {role: role_witnesses[role] for role in key['answers']}
        matched = (result['kind'] == key['expected_kind'] and result['answers'] == key['answers']
                   and result['witnesses'] == witnesses
                   and result['answer_supported'] == (key['expected_kind'] == 'supported_answer')
                   and result['exact_citations'] and bool(result['citations']) == proofs_expected
                   and result['source_truth_verified'] is False)
        totals = families[key['family']]
        totals['cases'] += 1
        totals['matched'] += int(matched)
        outcomes[result['kind']] += 1
        false_support += int(result['answer_supported'] and key['expected_kind'] != 'supported_answer')
    times = sorted(row['query_ns'] / 1e6 for row in rows.values())
    return {'cases': len(rows), 'matched': sum(c['matched'] for c in families.values()),
            'native_outcomes': dict(outcomes), 'false_full_support': false_support,
            'exact_citations': sum(len(row['citations']) for row in rows.values() if row['exact_citations']),
            'families': {key: dict(value) for key, value in families.items()},
            'query_p50_ms': round(statistics.median(times), 3),
            'query_p95_ms': round(times[(len(times)*95 + 99)//100 - 1], 3),
            'replay_wall_ms': round(native['replay_wall_ns'] / 1e6, 3)}


def revision(name):
    return checked(['git', 'rev-parse', '--verify', name + '^{commit}'], cwd=ROOT,
                   capture_output=True, text=True).stdout.strip()


def install(commit, root, evaluator, fixtures):
    root.mkdir()
    archive = root/'source.zip'
    checked(['git', 'archive', '--format=zip', f'--output={archive}', commit, '--',
             'pyproject.toml', 'README.md', 'LICENSE', 'mplpb_combined', 'mplpb_answers', 'mplpb_work'], cwd=ROOT)
    source = root/'source'
    with zipfile.ZipFile(archive) as zipped:
        zipped.extractall(source)
    start = perf_counter_ns()
    wheels = root/'wheels'
    epoch = checked(['git', 'show', '-s', '--format=%ct', commit], cwd=ROOT,
                    capture_output=True, text=True).stdout.strip()
    checked([sys.executable, '-m', 'pip', 'wheel', '--no-deps', '--no-build-isolation',
             '--no-index', '--wheel-dir', str(wheels), '.'], cwd=source,
            env={**os.environ, 'SOURCE_DATE_EPOCH': epoch})
    wheel, = wheels.glob('*.whl')
    env = root/'venv'
    checked([sys.executable, '-m', 'venv', str(env)])
    python = env / ('Scripts/python.exe' if sys.platform == 'win32' else 'bin/python')
    checked([str(python), '-m', 'pip', 'install', '--no-deps', '--no-index', str(wheel)], cwd=root)
    install_ms = (perf_counter_ns() - start) / 1e6
    report = root/'native.json'
    checked([str(python), '-I', str(evaluator), '_evaluate', str(fixtures), str(report)], cwd=root)
    return {'revision': commit, 'wheel_sha256': sha256(wheel.read_bytes()).hexdigest(),
            'build_and_install_ms': round(install_ms, 3), 'native': read(report)}


def main():
    if len(sys.argv) == 4 and sys.argv[1] == '_evaluate':
        evaluate(Path(sys.argv[2]), Path(sys.argv[3]))
        return 0
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--candidate', default='HEAD')
    args = parser.parse_args()
    study = ROOT/'evaluation/d12/release-demo'
    pins = read(study/'pins.json')
    fixtures, key = (study/'fixtures.json', study/'labels.json')
    for path in (fixtures, key):
        if sha256(path.read_bytes()).hexdigest() != pins[path.name]:
            parser.error(f'Frozen input checksum differs: {path.name}')
    output = args.output.resolve()
    output.mkdir(parents=True)
    evaluator = output/'evaluate.py'
    shutil.copyfile(Path(__file__), evaluator)
    public = output/'fixtures.json'
    shutil.copyfile(fixtures, public)
    report = {'schema': 'mplpb-release-demo-v1', 'input_pins': pins,
              'environment': {'python': platform.python_version(), 'platform': platform.platform(),
                              'processor': platform.machine()}}
    for arm, commit in [('baseline', pins['baseline_git_commit']), ('candidate', revision(args.candidate))]:
        run = install(revision(commit), output/arm, evaluator, public)
        native = run.pop('native')
        report[arm] = {**run, **score(native, read(key))}
    save(output/'report.json', report)
    for arm in ('baseline', 'candidate'):
        result = report[arm]
        print(f'{arm}: {result["matched"]}/{result["cases"]} matched; '
              f'p50 {result["query_p50_ms"]} ms; p95 {result["query_p95_ms"]} ms')
    candidate = report['candidate']
    return int(candidate['matched'] != candidate['cases'] or candidate['false_full_support'] != 0)


if __name__ == '__main__':
    raise SystemExit(main())
