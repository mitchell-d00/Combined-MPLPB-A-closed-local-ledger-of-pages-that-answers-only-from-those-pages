"""D20: seeded synthetic owner and alias replay against disposable MPLPB ledgers."""
import argparse
from collections import Counter
from hashlib import sha256
from html import escape
import json
from pathlib import Path
from random import Random
from tempfile import TemporaryDirectory

from mplpb_answers.pipeline import answer_query
from mplpb_combined.ledger import Ledger, withdraw, write
from mplpb_work.sorter import sort_directory

VERSION = 'd20-v1'
AS_OF = '2026-01-03'
CONDITIONS = ('unique', 'competing', 'missing', 'retired')
FAMILIES = {
    'canonical-field': 'development',
    'canonical-owner-question': 'development',
    'inline-alias': 'development',
    'prose-alias': 'challenge',
    'separate-alias-register': 'challenge',
}


def digest(value):
    return sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def page(source_id, body):
    return {'id': source_id, 'body': body}


def generate(seed):
    rng = Random(seed)
    cases, key = [], []
    for index, (family, split) in enumerate(FAMILIES.items(), 1):
        canonical = f'BOX-{rng.randrange(10000, 99999)}'
        alias = f'ACCESSION-{rng.randrange(10000, 99999)}'
        owner = f'{rng.choice(("Mira", "Tobin", "Inez"))} {rng.choice(("Veil", "Morris", "Nordin"))}'
        other = f'{rng.choice(("Amara", "Sana", "Reva"))} {rng.choice(("Lee", "Khan", "Young"))}'
        alias_line = f'{canonical} is catalogued under the alias {alias}.'
        header = f'Record-ID: {canonical}'
        lookup = alias
        bridge = []
        if family.startswith('canonical'):
            lookup = canonical
        elif family == 'inline-alias':
            header += f'\nAlias: {alias}'
        elif family == 'prose-alias':
            header += f'\n{alias_line}'
        else:
            bridge = [page('REGISTER-A', alias_line)]
        question = f'What is the owner for record {lookup}?'
        if family == 'canonical-owner-question':
            question = f'Who owns record {lookup}?'
        owner_line = f'Owner: {owner}'
        for condition in CONDITIONS:
            ident = f'D20-{index:02d}-{condition}'
            body = header if condition == 'missing' else f'{header}\n{owner_line}'
            second = 'Inventory paperwork was scanned.'
            if condition == 'competing':
                second = f'{header}\nOwner: {other}'
            pages = [page('PAGE-A', body), page('PAGE-B', second), *bridge]
            cases.append({'id': ident, 'family': family, 'split': split,
                          'question': question, 'pages': pages,
                          'withdraw': ['PAGE-A'] if condition == 'retired' else []})
            required = []
            if condition == 'unique':
                required.append({'source_id': 'PAGE-A', 'quote': owner_line})
                if bridge:
                    required.append({'source_id': 'REGISTER-A', 'quote': alias_line})
            key.append({'id': ident, 'condition': condition, 'required_citations': required})
    fixtures = {'schema': VERSION, 'kind': 'synthetic_fixture', 'seed': seed, 'cases': cases}
    return fixtures, {'schema': VERSION, 'fixtures_sha256': digest(fixtures), 'cases': key}


def run(fixtures):
    if fixtures.get('schema') != VERSION or fixtures.get('kind') != 'synthetic_fixture':
        raise ValueError('Expected D20 synthetic fixtures')
    results = []
    for case in fixtures['cases']:
        pages = case['pages']
        # Source IDs also serve as filenames in the disposable sorter input.
        if any(p['id'] not in {'PAGE-A', 'PAGE-B', 'REGISTER-A'} for p in pages):
            raise ValueError('Unknown D20 source ID')
        with TemporaryDirectory(prefix='mplpb-d20-') as directory:
            root = Path(directory)
            raw = root / 'raw'
            raw.mkdir()
            for source in pages:
                (raw / (source['id'] + '.txt')).write_text(source['body'], encoding='utf-8')
            graph = sort_directory(raw, mode='compare')

            ledger = root / 'sealed'
            for source in pages:
                write(ledger, doc_id=source['id'], title='Synthetic inventory',
                      scope='inventory', body_html=f"<pre>{escape(source['body'])}</pre>",
                      source_authorship='declared-machine', when='2026-01-01')
            for source_id in case['withdraw']:
                withdraw(ledger, source_id, when='2026-01-02')
            serving = Ledger(ledger).servable()
            eligible = {record.id: record.hash_actual for record in serving}
            answer = answer_query(ledger, case['question'], mode='strict', as_of=AS_OF).contract
            results.append({
                'id': case['id'], 'family': case['family'], 'split': case['split'],
                'raw_sorter': {'graph_sha256': graph['graph_sha256'],
                               'assessment': graph['assessment'],
                               'nodes_by_kind': dict(Counter(n['kind'] for n in graph['nodes'])),
                               'issues': graph['limits_or_exclusions']},
                'eligible_sources': eligible, 'answer': answer,
            })
    return {'schema': VERSION, 'fixtures_sha256': digest(fixtures), 'as_of': AS_OF,
            'cases': results}


def score(report, key):
    if (report.get('schema') != VERSION or key.get('schema') != VERSION
            or report.get('fixtures_sha256') != key.get('fixtures_sha256')):
        raise ValueError('Run and answer key must refer to the same D20 fixtures')
    expected = {row['id']: row for row in key['cases']}
    ids = [case['id'] for case in report['cases']]
    if not ids or len(set(ids)) != len(ids) or len(expected) != len(key['cases']) or set(ids) != set(expected):
        raise ValueError('Run and key must contain the same unique case IDs')
    outcomes = []
    for case in report['cases']:
        row = expected[case['id']]
        answer = case['answer']
        required = row['required_citations']
        citations = [cite for claim in answer['claims'] for cite in claim['citations']]
        if not required:
            outcome = 'false_support' if answer['answer_supported'] else 'withheld'
        elif not answer['answer_supported']:
            outcome = 'missed'
        else:
            correct = all(any(c['source_id'] == witness['source_id'] and witness['quote'] in c['quote']
                              for c in citations) for witness in required)
            pinned = all(case['eligible_sources'].get(c['source_id']) == c['hash'] for c in citations)
            owner_claim = [claim['text'] for claim in answer['claims']] == [required[0]['quote']]
            outcome = 'supported' if correct and pinned and owner_claim else 'incorrect_support'
        outcomes.append({'id': case['id'], 'family': case['family'], 'split': case['split'],
                         'condition': row['condition'], 'outcome': outcome,
                         'kind': answer['kind'], 'diagnostic': answer['diagnostic']['code']})
    return {'totals': dict(Counter(row['outcome'] for row in outcomes)), 'cases': outcomes}


def probe_recovers(probe, witness):
    answer = probe['answer']
    return answer['answer_supported'] and any(
        claim['text'] == witness['quote'] and any(
            cite['source_id'] == witness['source_id']
            and witness['quote'] in cite['quote']
            and cite['hash'] == probe['eligible_sources'].get(cite['source_id'])
            for cite in claim['citations']
        ) for claim in answer['claims']
    )


def study(first_seed, count):
    """Repeat matched families and use literal selectors to isolate positive misses."""
    if count < 1:
        raise ValueError('D20 study requires at least one seed')
    groups = {}
    receipts = []
    for seed in range(first_seed, first_seed + count):
        fixtures, key = generate(seed)
        native = run(fixtures)
        results = score(native, key)['cases']

        # Keep pages and eligibility fixed. Change only the question to the
        # canonical field selector on each missed positive.
        misses = {row['id'] for row in results if row['outcome'] == 'missed'}
        diagnostic_cases = []
        for case in fixtures['cases']:
            if case['id'] in misses:
                canonical = case['pages'][0]['body'].splitlines()[0].removeprefix('Record-ID: ')
                canonical_case = {**case, 'question': f'What is the owner for record {canonical}?'}
                diagnostic_cases.append(canonical_case)
                if case['family'] == 'prose-alias':
                    source, *rest = case['pages']
                    identifier, prose, owner = source['body'].splitlines()
                    moved = {**source, 'body': '\n'.join((identifier, owner, prose))}
                    diagnostic_cases.append({**canonical_case, 'id': case['id'] + '-layout',
                                             'pages': [moved, *rest]})
        probes = {row['id']: row for row in run({**fixtures, 'cases': diagnostic_cases})['cases']}
        for row in results:
            group = groups.setdefault(row['family'], {}).setdefault(row['condition'], Counter())
            group[row['outcome']] += 1
            group['diagnostic/' + row['diagnostic']] += 1
            if row['id'] in probes:
                probe = probes[row['id']]
                witness = next(case['required_citations'][0] for case in key['cases'] if case['id'] == row['id'])
                label = 'canonical_probe_recovered' if probe_recovers(probe, witness) else 'canonical_probe_not_recovered'
                group[label] += 1
                layout = probes.get(row['id'] + '-layout')
                if layout is not None:
                    label = 'layout_probe_recovered' if probe_recovers(layout, witness) else 'layout_probe_not_recovered'
                    group[label] += 1
        receipts.append({'seed': seed, 'fixtures_sha256': digest(fixtures),
                         'key_sha256': digest(key), 'native_sha256': digest(native),
                         'canonical_probes_sha256': digest(probes)})
    return {'schema': VERSION, 'seeds': count, 'base_cases': count * len(FAMILIES) * len(CONDITIONS),
            'by_family_and_condition': groups, 'receipts': receipts}


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def write_new_json(path, value):
    with Path(path).open('x', encoding='utf-8') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    gen = commands.add_parser('generate')
    gen.add_argument('--seed', required=True, type=int)
    gen.add_argument('--output', required=True, type=Path)
    replay = commands.add_parser('run')
    replay.add_argument('--fixtures', required=True)
    replay.add_argument('--output', required=True)
    scoring = commands.add_parser('score')
    scoring.add_argument('--run', required=True)
    scoring.add_argument('--key', required=True)
    scoring.add_argument('--output')
    grouping = commands.add_parser('study')
    grouping.add_argument('--first-seed', required=True, type=int)
    grouping.add_argument('--count', required=True, type=int)
    grouping.add_argument('--output', required=True)
    args = parser.parse_args()
    if args.command == 'generate':
        fixtures, key = generate(args.seed)
        args.output.mkdir()
        write_new_json(args.output / 'fixtures.json', fixtures)
        write_new_json(args.output / 'answer-key.json', key)
    elif args.command == 'run':
        write_new_json(args.output, run(read_json(args.fixtures)))
    elif args.command == 'study':
        write_new_json(args.output, study(args.first_seed, args.count))
    else:
        scored = score(read_json(args.run), read_json(args.key))
        if args.output:
            write_new_json(args.output, scored)
        print(json.dumps(scored, indent=2))
        # Positive misses are measured development gaps. Unsupported claims fail the gate.
        return int(any(scored['totals'].get(kind) for kind in ('false_support', 'incorrect_support')))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
