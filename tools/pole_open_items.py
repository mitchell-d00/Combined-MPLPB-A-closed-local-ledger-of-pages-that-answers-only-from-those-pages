"""Seven follow-up tests for the Frederick Douglass experiment."""
import argparse
from collections import Counter
from hashlib import sha256
from html import escape
from pathlib import Path
import shutil
import tarfile
from tempfile import TemporaryDirectory
from time import perf_counter

from test_tools import four_score_twenty as historical
from tools import blind_archival_packets, dpercent as D, pole
from tools.sorter_first_study import FAMILIES
from tools.unprepared_challenge import code_pins
from tools.unprepared_sources import import_corpus, verify

ROOT = D.ROOT
SCOUT = ROOT / 'evaluation/d12/scout'
SOLO = ROOT / 'evaluation/d12/solo-post-freeze'
ARCHIVAL = ROOT / 'evaluation/archival-inspection/2026-11-19'
SUITES = {
    'herodotus': 'Historical reconstruction on sealed authentic originals',
    'ida-b-wells': 'Known focus gaps with exact pins and fresh seeded cases',
    'ada-lovelace': 'Sorter span diversity and completeness budget',
    'zora-neale-hurston': 'Unfamiliar wording and multi-document proof',
    'anna-komnene': 'Anonymous semantic review packet and citation audit',
    'al-biruni': 'Outside-custodian protocol rehearsal and matched budgets',
    'sima-qian': 'Mixed authentic source volume ladder',
}


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def check_scout():
    from evaluation.d12.scout.run import verify_files

    for manifest in ('protocol.sha256', 'inputs.sha256'):
        verify_files(SCOUT, manifest)


def prepare(public, custody):
    public, custody = pole.paths_separate(public, custody)
    if public.exists() or custody.exists():
        raise FileExistsError('Choose new public and custody directories')
    public.mkdir(parents=True)
    custody.mkdir(parents=True, mode=0o700)
    original = ROOT / 'evaluation/pole'
    focus = D.read(original / 'focus-after.json')['cases']
    misses = [row['id'] for row in focus if row['outcome'] == 'over_refusal']
    if len(misses) != 12:
        raise ValueError('Expected the 12 retained Pole focus misses')
    fresh = {row['family'] for row in focus if row['id'] in misses}
    fresh.update(('missing_bridge', 'chronology_causation'))
    with TemporaryDirectory(prefix='pole-followup-preparation-') as tmp:
        old = Path(tmp)
        for name in ('packets.tar.gz', 'development-custody.tar.gz'):
            with tarfile.open(original / name) as archive:
                archive.extractall(old, filter='data')
        pole.prepare(public / 'ida-b-wells', custody / 'ida-b-wells', seed=1862, count=10,
                     levels=('medium', 'hard'), suite='focus',
                     families=tuple(sorted(fresh)),
                     pinned=(old / 'pole-focus', old / 'pole-focus-key', misses))
        pole.prepare(public / 'zora-neale-hurston', custody / 'zora-neale-hurston', seed=1935,
                     count=12, levels=pole.TIERS, suite='catalog',
                     families=('field_synonym', 'field_compound', 'reported_statement',
                               'explicit_chain', 'missing_bridge', 'ambiguous_pronoun',
                               'conditional_execution', 'chronology_causation'))
        shutil.copytree(old / 'pole-transfer' / 'packets' / 'POLE-82adc1f4f7ae9efd-00008' / 'sources',
                        public / 'ada-lovelace' / 'frozen-pole-chain')
    sorter = public / 'ada-lovelace'
    phrase = 'Fresh sailors prepared narrow canvas.'
    for name, repeat, owner in (('balanced', 1, True), ('crowded', 8, True), ('single-owner', 8, False),
                                ('many-owners', 8, True)):
        folder = sorter / name
        folder.mkdir()
        (folder / 'first.txt').write_text('Message-ID: BOAT-17\n\n' + '\n\n'.join([phrase] * repeat) + '\n')
        if owner:
            (folder / 'second.txt').write_text('Message-ID: BOAT-22\n\n' + phrase + '\n')
        if name == 'many-owners':
            for number in range(8):
                (folder / f'witness-{number}.txt').write_text(f'Message-ID: BOAT-{40 + number}\n\n' + phrase + '\n')
    check_scout()
    outside = public / 'al-biruni'
    shutil.copytree(SCOUT / 'inputs', outside / 'inputs')
    private = custody / 'al-biruni'
    private.mkdir(mode=0o700)
    shutil.copyfile(SCOUT / 'custody/key.json', private / 'key.json')
    (private / 'key.json').chmod(0o600)
    D.save(outside / 'protocol.json', {
        'status': 'local_rehearsal', 'runs': ['native', 'overlap'],
        'passage_budget': 12, 'character_budget': 8000,
        'key_sha256': digest(private / 'key.json'),
        'outside_trial': 'Before a new run, an independent custodian selects fresh originals, freezes sources and concealed keys, and commissions blinded review.',
        'review_obligations': ['source attribution', 'event identity', 'false links', 'appropriate abstentions'],
        'required_review': 'Two independent assessments and explicit adjudication of disagreements.',
    })
    D.save(public / 'seal.json', {'public_files': D.files(public), 'suites': SUITES})


def verify_study(public):
    seal = D.read(public / 'seal.json')
    files = D.files(public)
    files.pop('seal.json')
    if files != seal['public_files']:
        raise ValueError('Frozen study bytes changed')
    return digest(public / 'seal.json')


def historical_rows(packet, *, discover=False):
    from mplpb_answers.passages import PassageIndex
    from mplpb_answers.pipeline import answer_query
    from evaluation.d12.scout.run import search

    sources, cases = (D.read(packet / 'inputs' / filename)
                      for filename in ('sources.json', 'questions.json'))
    rows = []
    with TemporaryDirectory(prefix='pole-authentic-') as tmp:
        for pair in sources:
            ledger = Path(tmp) / pair['id']
            historical.import_packet(packet, pair['sources'], ledger)
            for case in cases:
                if case['packet'] != pair['id']:
                    continue
                question = case['question']
                result = answer_query(ledger, question, historical.PROFILE, max_passages=12,
                                      max_chars=8000).contract
                row = {'id': case['id'], 'kind': result['kind'],
                       'diagnostic': result['diagnostic']['code'],
                       'supported': result['answer_supported'],
                       'citations': sum(len(claim['citations']) for claim in result['claims'])}
                if discover:
                    index = PassageIndex(ledger, question, historical.PROFILE)
                    row['discovery'] = {name: [{'source_id': passage['source_id'], 'text': passage['text']}
                                               for passage in passages]
                                        for name, passages in search(index, question, 12).items()}
                rows.append(row)
    return rows


def reconstruction():
    check_scout()
    rows = historical_rows(SCOUT)
    retained = {row['id']: row['strict'] for row in D.read(SCOUT / 'native.json')['cases']}
    matches = sum((r['kind'], r['diagnostic'], r['supported']) ==
                  (retained[r['id']]['kind'], retained[r['id']]['diagnostic']['code'],
                   retained[r['id']]['answer_supported']) for r in rows)
    return {'cases': rows, 'matching_retained_decisions': matches,
            'native_outcomes': dict(Counter(r['kind'] for r in rows)),
            'independent_historical_accuracy': None}


def sorter_test(public):
    from mplpb_work.sorter_v2 import sort_directory

    rows = {}
    for folder in sorted((public / 'ada-lovelace').iterdir()):
        raw = sort_directory(folder)
        compared = sort_directory(folder, 'compare')
        phrase_nodes = [node for node in compared['nodes']
                        if node['kind'] == 'phrase_key' and node['value'] == 'fresh sailors prepared narrow']
        phrase_ids = {node['id'] for node in phrase_nodes}
        rows[folder.name] = {
            'complete': compared['complete'],
            'limits': compared['limits_or_exclusions'],
            'raw_nodes_preserved': raw['nodes'] == compared['nodes'],
            'phrase_occurrences': len({node['occurrence'] for node in phrase_nodes}),
            'phrase_nodes': len(phrase_nodes),
            'non_authoritative_reviews': sum(
                edge['kind'] == 'repeated_phrase_review' and edge['comparison_only']
                and set(edge['evidence_nodes']) <= phrase_ids for edge in compared['edges']),
            'explicit_reference_count': sum(
                edge['kind'] == 'explicit_reference_candidate' for edge in compared['edges']),
        }
    return {'cases': rows, 'phrase_occurrence_cap': 8, 'phrase_group_limit_unchanged': True}


def package_review(output, custody):
    count = blind_archival_packets.prepare(ARCHIVAL / 'baseline-originals',
                                            ARCHIVAL / 'final/originals',
                                            output / 'review-packet', custody)
    return {'paired_questions': count, 'issued_to_reviewers': False,
            'independent_review': 'NOT RUN', 'semantic_metrics': None}


def custody_rehearsal(public, custody, output):
    packet = public / 'al-biruni'
    protocol = D.read(packet / 'protocol.json')
    rows = historical_rows(packet, discover=True)
    D.save(output / 'operator-results.json', rows)
    key = custody / 'al-biruni' / 'key.json'
    if digest(key) != protocol['key_sha256']:
        raise ValueError('Custody key differs from its commitment')
    outcomes = D.read(key)
    by_id = {row['id']: row for row in rows}
    if set(by_id) != {row['id'] for row in outcomes}:
        raise ValueError('Key and operator case coverage differs')
    coverage, supported_gaps = Counter(), 0
    for expected in outcomes:
        result = by_id[expected['id']]
        if set(result['discovery']) != set(protocol['runs']):
            raise ValueError('Missing matched discovery arm')
        for name, passages in result['discovery'].items():
            if len(passages) > protocol['passage_budget'] or sum(
                    len(p['text']) for p in passages) > protocol['character_budget']:
                raise ValueError('Discovery exceeded the matched budget')
            if expected['family'] != 'missing':
                coverage[name] += all(
                    any(anchor['source'] == p['source_id'] and anchor['quote'] in p['text'] for p in passages)
                    for anchor in expected['anchors'])
        if expected['family'] == 'missing':
            supported_gaps += result['supported']
    return {'operator_receipt_sha256': digest(output / 'operator-results.json'),
            'cases': len(rows), 'answerable_according_to_local_key': sum(
                row['family'] != 'missing' for row in outcomes),
            'complete_anchor_coverage': dict(coverage), 'supported_on_missing_evidence': supported_gaps,
            'outside_custody': 'NOT RUN', 'independent_scoring': 'NOT RUN'}


def volume_ladder():
    from mplpb_combined.ledger import Ledger, write

    check_scout()
    historical.verify_inputs(SOLO)
    probe = D.read(SCOUT / 'inputs/questions.json')[0]['question']
    quote = 'Which source contains the exact words “the French Foreign Office extended an invitation”?'
    questions = {'direct': probe, 'literal': quote}
    started = perf_counter()
    stages = []
    with TemporaryDirectory(prefix='pole-mixed-originals-') as directory:
        root = Path(directory)
        ledger = root / 'mixed'
        for folder in (SCOUT, SOLO):
            pairs = D.read(folder / 'inputs/sources.json')
            for pair in pairs:
                for row in pair['sources']:
                    source = folder / 'inputs/sources' / (row['id'] + '.txt')
                    if digest(source) != row['text_sha256']:
                        raise ValueError('FRUS projection hash changed')
                    ident = ('SCOUT-' if folder == SCOUT else 'SOLO-') + row['id']
                    write(ledger, doc_id=ident, title='Frozen FRUS projection ' + ident,
                          scope='public historical records', body_html='<pre>' + escape(source.read_text()) + '</pre>',
                          origin='machine', when='2026-11-23T00:00Z')
                if pair == pairs[0] and folder == SCOUT:
                    stages.append(scale_probe(ledger, questions, 'two_frus_projections'))
        stages.append(scale_probe(ledger, questions, 'two_frus_draws'))
        for index, (folder, _) in enumerate(FAMILIES.values(), 1):
            original = ROOT / folder
            manifest = verify(original)
            imported = root / f'import-{index}'
            import_corpus(original, imported)
            for record in Ledger(imported).servable():
                ident = f'ORIG-{index}-{record.id}'
                write(ledger, doc_id=ident, title=f'{ident} {record.title}',
                      scope='documentary records', body_html=record.body_html,
                      origin='machine', when='2026-11-23T00:00Z')
            stages.append(scale_probe(ledger, questions, f'add_original_collection_{index}',
                                      Counter(row['media_type'] for row in manifest['sources'])))
    return {'stages': stages, 'seconds': perf_counter() - started, 'large_authentic_corpus_accuracy': None}


def scale_probe(ledger, questions, stage, types=None):
    from mplpb_answers.pipeline import answer_query
    from mplpb_combined.ledger import Ledger

    records = list(Ledger(ledger).servable())
    outcomes = {}
    for name, question in questions.items():
        started = perf_counter()
        reply = answer_query(ledger, question, historical.PROFILE, max_passages=12, max_chars=8000).contract
        outcomes[name] = {'kind': reply['kind'], 'diagnostic': reply['diagnostic']['code'],
                          'supported': reply['answer_supported'], 'seconds': perf_counter() - started}
    return {'stage': stage, 'eligible_pages': len(records),
            'ledger_body_html_bytes': sum(len(record.body_html.encode()) for record in records),
            'new_original_media_types': dict(types or {}), 'outcomes': outcomes}


def run(suite, public, custody, output):
    public, custody, output = pole.paths_separate(public, custody, output)
    seal = verify_study(public)
    output.mkdir(parents=True)
    started = perf_counter()
    if suite == 'herodotus':
        result = reconstruction()
    elif suite in ('ida-b-wells', 'zora-neale-hurston'):
        raw = output / 'native'
        pole.run(public / suite, raw, ROOT)
        report = pole.score(public / suite, custody / suite, raw, output / 'score.json')
        result = {'metrics': report['metrics'], 'groups': report['groups']}
    elif suite == 'ada-lovelace':
        result = sorter_test(public)
    elif suite == 'anna-komnene':
        name = 'anna-komnene-' + sha256(str(output).encode()).hexdigest()[:12]
        result = package_review(output, custody / name)
    elif suite == 'al-biruni':
        result = custody_rehearsal(public, custody, output)
    else:
        result = volume_ladder()
    if seal != verify_study(public):
        raise ValueError('Frozen study changed during replay')
    report = {'suite': suite, 'scope': SUITES[suite], 'study_seal_sha256': seal,
              'runtime_sha256': code_pins(ROOT), 'seconds': perf_counter() - started,
              'result': result}
    D.save(output / 'report.json', report)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    preparation = commands.add_parser('prepare')
    replay = commands.add_parser('run')
    for command in (preparation, replay):
        command.add_argument('--public', required=True, type=Path)
        command.add_argument('--custody', required=True, type=Path)
    replay.add_argument('suite', choices=tuple(SUITES))
    replay.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    if args.command == 'prepare':
        prepare(args.public, args.custody)
    else:
        run(args.suite, args.public, args.custody, args.out)


if __name__ == '__main__':
    main()
