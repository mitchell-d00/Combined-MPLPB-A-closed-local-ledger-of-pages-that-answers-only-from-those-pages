"""Pole, the Frederick Douglass experiment's seeded documentary test runner."""
import argparse
from collections import Counter
from pathlib import Path
import secrets
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory

from tools import dpercent as D
from tools import dpercent_weaknesses as W
from tools.unprepared_challenge import code_pins

SCHEMA = 'mplpb-pole-v1'
ROOT = D.ROOT
TIERS = ('easy', 'medium', 'hard')
FIELD_FAMILIES = ('field_recorded_value', 'field_recorded_value_qualified',
                  'field_recorded_value_conflict')
FOCUS = {
    'easy': FIELD_FAMILIES[:2],
    'medium': FIELD_FAMILIES[:2] + ('field_synonym', 'date_roles', 'reported_statement'),
    'hard': FIELD_FAMILIES[1:] + ('field_compound', 'wording_change', 'partial_correction',
                                  'explicit_chain', 'missing_bridge', 'chronology_causation'),
}
HARD = {
    'field_compound', 'date_roles', 'wording_change', 'partial_correction',
    'earliest_observed', 'explicit_chain', 'identical_wording', 'editorial_competition',
    'embedded_identifier', 'subject_identity', 'ambiguous_pronoun', 'missing_bridge',
    'ambiguous_correction', 'competing_accounts', 'historical_priority',
    'sorter_partial_correction', 'sorter_ambiguous_target', 'sorter_concatenated_records',
    'sorter_fenced_example', 'sorter_changed_body', 'sorter_same_body_different_ids',
}
EASY = {'exact_anchor', 'direct_action', 'absent_anchor', 'header_location',
        'restricted_source', 'withdrawn_source', 'corrupted_source', 'negated_execution',
        'sorter_duplicate_appearance', 'sorter_same_subject', 'sorter_unique_correction'}
EASY.update(name for name in W.FAMILIES if name.startswith('alias_role_'))
CLASS_TIERS = {name: ('hard' if name in HARD else 'easy' if name in EASY else 'medium')
               for name in W.FAMILIES}


def recorded_value(number, family, level, dice):
    label, value, contrary = dice.choose('field', (
        ('Custody Location', 'North vault', 'South vault'),
        ('Catalog Number', '218-B', '281-C'),
        ('Accession Date', '1853-06-19', '1853-07-19'),
        ('Review Status', 'Pending', 'Approved'),
    ))
    record = f'LOG-{1000 + number}'
    noun = dice.choose('record_noun', ('record', 'event', 'occurrence'))
    verb = dice.choose('recording_verb', ('listed', 'recorded', 'stated'))
    selector = f'{noun} {record}'
    templates = (
        f'What is the value {verb} for {label.lower()} in {selector}',
        f'What value is {verb} for {label.lower()} on {selector}',
    )
    question = dice.choose('question_structure', templates)
    if family == 'field_recorded_value_qualified':
        question += dice.choose('qualification', (
            ' before the revision', ' according to the courier',
            ' and who verified it', ' if the permit was granted',
        ))
    expected = 'answer' if family == 'field_recorded_value' else 'refuse'
    documents = []

    def add(body):
        source = {'path': f'sources/item-{len(documents) + 1:02d}.txt', 'source_class': 'original'}
        documents.append((source, (body + '\n').encode()))

    add(f'Record-ID: {record}\n{label}: {value}')
    if level != 'easy':
        add(f'Record-ID: OTHER-{number}\n{label}: {contrary}')
    if family == 'field_recorded_value_conflict':
        add(f'Record-ID: {record}\n{label}: {contrary}')
    case = {'question': question + '?', 'profile': 'internal', 'sources': [s for s, _ in documents],
            'budget': {'passages': 12, 'characters': 8000}}
    key = {'family': family, 'expected': expected, 'required_propositions': [], 'source_facts': [],
           'reference_sources': ['SOURCE-0001'] if expected == 'answer' else [],
           'automatic_answer_matcher': 'literal_field_set_v1',
           'required_field_quotes': [f'{label}: {value}'], 'structural_expectations': {},
           'features': {'source_count': len(documents), 'recording_verb': verb, 'record_noun': noun}}
    return case, documents, key


def paths_separate(*paths):
    resolved = [Path(path).resolve() for path in paths]
    for index, left in enumerate(resolved):
        for right in resolved[index + 1:]:
            if left == right or left in right.parents or right in left.parents:
                raise ValueError('Use disjoint paths for packets, custody and outputs')
    return resolved


def load_keys(custody):
    rows = D.read(custody / 'key.json')['cases']
    return {row['id']: row for row in rows}


def load_packet(packets, custody=None):
    seal = D.verify(packets, custody)
    protocol = D.read(packets / 'protocol.json')
    if protocol['schema'] != SCHEMA:
        raise ValueError('Expected a Pole packet')
    ids = set(protocol['cases'])
    if ids != {entry.name for entry in (packets / 'packets').iterdir()}:
        raise ValueError('Packet inventory differs from its protocol')
    if custody is not None:
        if seal != D.read(custody / 'seal-copy.json'):
            raise ValueError('Packet differs from custody seal')
        if ids != set(load_keys(custody)):
            raise ValueError('Key coverage differs from its protocol')
    return seal, protocol


def families_for(level, suite):
    if suite == 'focus':
        return FOCUS[level]
    return tuple(family for family, assigned in CLASS_TIERS.items() if assigned == level)


def prepare(packets, custody, *, seed, count, levels, suite, pinned=None, families=()):
    packets, custody = paths_separate(packets, custody)
    if not 1 <= count <= 65536 or not 0 <= seed < 2**128:
        raise ValueError('Use 1 to 65536 cases and a seed in the unsigned 128-bit range')
    if not levels or len(set(levels)) != len(levels) or set(levels) - set(TIERS):
        raise ValueError('Select each difficulty at most once')
    if suite not in ('focus', 'catalog'):
        raise ValueError('Unknown Pole suite')
    schedules = {level: tuple(name for name in families_for(level, suite)
                              if not families or name in families) for level in levels}
    schedules = {level: names for level, names in schedules.items() if names}
    if not schedules or set(families) - {name for names in schedules.values() for name in names}:
        raise ValueError('Requested families must be available in the selected suite and levels')
    if packets.exists() or custody.exists():
        raise FileExistsError('Use new packet and custody directories')
    if pinned is not None:
        old_packets, old_custody, selections = pinned
        paths_separate(packets, custody, old_packets, old_custody)
        _, old_protocol = load_packet(old_packets, old_custody)
        old_keys = load_keys(old_custody)
        if not selections or len(set(selections)) != len(selections) or set(selections) - old_keys.keys():
            raise ValueError('Select distinct case IDs from the sealed prior packet')
    dice = D.Dice(seed)
    keys = []
    cases = {}
    packets.mkdir(parents=True)
    custody.mkdir(parents=True, mode=0o700)
    case_root = packets / 'packets'
    case_root.mkdir()
    if pinned is not None:
        origin = D.sha((old_packets / 'seal.json').read_bytes())
        for case_id in selections:
            shutil.copytree(old_packets / 'packets' / case_id, case_root / case_id)
            cases[case_id] = {'level': old_protocol['cases'][case_id]['level'],
                              'cohort': 'pinned', 'origin_seal_sha256': origin}
            keys.append(old_keys[case_id])
    for level, pool in schedules.items():
        namespace_seed = f'{seed}/{suite}/{level}'
        if families:
            namespace_seed += '/' + ','.join(pool)
        namespace = D.sha(namespace_seed.encode())[:16]
        schedule = []
        while len(schedule) < count:
            schedule.extend(dice.shuffle(level + '_families', pool))
        for number, family in enumerate(schedule[:count], 1):
            if family in FIELD_FAMILIES:
                case, documents, key = recorded_value(number, family, level, dice)
            else:
                case, documents, key = W.material(number, family, dice)
            case_id = f'POLE-{namespace}-{number:05d}'
            if case_id in cases:
                raise ValueError(f'Fresh draw duplicates pinned case {case_id}; choose another seed')
            case['id'] = key['id'] = case_id
            folder = case_root / case_id
            for source, raw in documents:
                path = folder / source['path']
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(raw)
            D.save(folder / 'case.json', case)
            keys.append(key)
            cases[case_id] = {'level': level, 'cohort': 'fresh'}
    D.save(packets / 'protocol.json', {'schema': SCHEMA, 'cases': cases})
    D.save(custody / 'key.json', {'schema': SCHEMA, 'cases': keys})
    (custody / 'key.json').chmod(0o600)
    D.save(custody / 'dice.json', {'seed': str(seed), 'suite': suite, 'rolls': dice.rolls})
    (custody / 'dice.json').chmod(0o600)
    seal = {'public_files': D.files(packets),
            'key_sha256': D.sha((custody / 'key.json').read_bytes()),
            'dice_sha256': D.sha((custody / 'dice.json').read_bytes()),
            'tools': tool_pins()}
    D.save(packets / 'seal.json', seal)
    D.save(custody / 'seal-copy.json', seal)
    return cases


def tool_pins():
    files = ('tools/pole.py', 'tools/pole_worker.py', 'tools/dpercent.py',
             'tools/dpercent_expanded.py', 'tools/dpercent_weaknesses.py')
    return {name: D.sha((ROOT / name).read_bytes()) for name in files}


def run(packets, output, implementation):
    packets, output = paths_separate(packets, output)
    implementation = Path(implementation).resolve()
    seal, protocol = load_packet(packets)
    pins = code_pins(implementation)
    if not pins:
        raise ValueError('Expected an MPLPB source checkout or extracted archive')
    worker = ROOT / 'tools/pole_worker.py'
    revision = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=implementation,
                              capture_output=True, text=True).stdout.strip() or None
    output.mkdir(parents=True)
    files_by_case = {}
    for name, digest in seal['public_files'].items():
        if name.startswith('packets/'):
            _, case_id, relative = name.split('/', 2)
            files_by_case.setdefault(case_id, {})[relative] = digest
    rows = []
    for case_id in protocol['cases']:
        destination = output / case_id
        destination.mkdir()
        with TemporaryDirectory(prefix='pole-case-') as temp:
            scratch = Path(temp)
            case_input = scratch / 'input'
            shutil.copytree(packets / 'packets' / case_id, case_input)
            if D.files(case_input) != files_by_case[case_id]:
                raise ValueError(f'Frozen case changed: {case_id}')
            result = destination / 'result.json'
            try:
                with (destination / 'worker.log').open('wb') as log:
                    finished = subprocess.run(
                        [sys.executable, '-I', '-B', str(worker), str(implementation),
                         str(case_input), str(scratch / 'ledger'), str(scratch / 'result.json')],
                        cwd=scratch, stdout=log, stderr=subprocess.STDOUT,
                        timeout=D.LIMITS['wall_seconds'])
                if finished.returncode:
                    raise ValueError(f'Worker exited {finished.returncode}')
                raw = (scratch / 'result.json').read_bytes()
                if len(raw) > D.LIMITS['result_bytes']:
                    raise ValueError('Worker output exceeded its case limit')
                result.write_bytes(raw)
                rows.append({'case_id': case_id, 'execution': 'completed', 'sha256': D.sha(raw)})
            except (OSError, ValueError, subprocess.TimeoutExpired) as error:
                rows.append({'case_id': case_id, 'execution': 'failed', 'error': str(error)})
    load_packet(packets)
    if pins != code_pins(implementation):
        raise ValueError('Native implementation changed during replay')
    receipt = {'schema': SCHEMA, 'checkout_revision': revision, 'runtime_sha256': pins,
               'worker_sha256': D.sha(worker.read_bytes()),
               'packet_seal_sha256': D.sha((packets / 'seal.json').read_bytes()),
               'os_isolated': False, 'partial': False, 'cases': rows}
    D.save(output / 'run.json', receipt)
    return receipt


def score(packets, custody, output, report_path):
    packets, custody, output = paths_separate(packets, custody, output)
    _, protocol = load_packet(packets, custody)
    receipt = D.read(output / 'run.json')
    expected_ids = list(protocol['cases'])
    if [row['case_id'] for row in receipt['cases']] != expected_ids:
        raise ValueError('Replay coverage or order differs from the frozen packet')
    with TemporaryDirectory(prefix='pole-score-') as temporary:
        base = W.score_shard(packets, custody, output, Path(temporary) / 'score.json')
    keys = load_keys(custody)
    groups = {}
    for row in base['cases']:
        row.update(protocol['cases'][row['id']])
        group = (row['cohort'], row['level'], row['family'], row['expected'])
        groups.setdefault(group, Counter())[row['outcome']] += 1
        if row['execution'] == 'completed':
            result = D.read(output / row['id'] / 'result.json')
            key = keys[row['id']]
            checks = W.graph_checks(result['sorter'], key['structural_expectations'])
            row['graph_failures'] = sorted(name for name, passed in checks.items() if not passed)
            row['diagnostic'] = result['answer'].get('diagnostic')
            row['discovered_all_required_statements'] = (
                row['retrieval']['native_facets']['complete_statement_coverage'] == 1
                if key.get('source_facts') and key['reference_sources'] else None)
    report = {'schema': SCHEMA, 'packet_seal_sha256': receipt['packet_seal_sha256'],
              'run_sha256': base['run_sha256'], 'checkout_revision': receipt['checkout_revision'],
              'worker_sha256': receipt['worker_sha256'], 'metrics': base['metrics'],
              'groups': [{'cohort': cohort, 'level': level, 'family': family,
                          'expected': expected, 'cases': sum(outcomes.values()), 'outcomes': dict(outcomes)}
                         for (cohort, level, family, expected), outcomes in sorted(groups.items())],
              'cases': base['cases']}
    D.save(report_path, report)
    return report


def compare(before, after, output):
    earlier, later = D.read(before), D.read(after)
    for key in ('schema', 'packet_seal_sha256', 'worker_sha256'):
        if earlier[key] != later[key]:
            raise ValueError(f'Cannot compare replays with different {key}')
    ids = [row['id'] for row in earlier['cases']]
    if ids != [row['id'] for row in later['cases']] or len(set(ids)) != len(ids):
        raise ValueError('Cannot compare different case coverage')
    transitions = []
    for first, second in zip(earlier['cases'], later['cases']):
        fields = ('outcome', 'kind', 'graph_failures')
        if any(first.get(field) != second.get(field) for field in fields):
            transitions.append({'id': first['id'], 'level': first['level'], 'family': first['family'],
                                'cohort': first['cohort'], 'before': first['outcome'],
                                'after': second['outcome'], 'kind_before': first.get('kind'),
                                'kind_after': second.get('kind'),
                                'new_graph_failures': sorted(set(second.get('graph_failures', []))
                                                             - set(first.get('graph_failures', [])))})
    correct = {'detected_answer', 'appropriate_refusal'}
    report = {'schema': SCHEMA, 'packet_seal_sha256': earlier['packet_seal_sha256'],
              'before_run_sha256': earlier['run_sha256'], 'after_run_sha256': later['run_sha256'],
              'cases': len(ids), 'transitions': transitions,
              'recovered': sum(row['before'] not in correct and row['after'] in correct for row in transitions),
              'regressions': sum((row['before'] in correct and row['after'] not in correct)
                                 or bool(row['new_graph_failures']) for row in transitions),
              'new_false_alarms': sum(row['after'] == 'false_alarm' and row['before'] != 'false_alarm'
                                      for row in transitions),
              'false_alarms_before': earlier['metrics']['false_alarms'],
              'false_alarms_after': later['metrics']['false_alarms'],
              'execution_failures_before': earlier['metrics']['execution_failures'],
              'execution_failures_after': later['metrics']['execution_failures']}
    D.save(output, report)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('catalog')
    prep = commands.add_parser('prepare')
    prep.add_argument('--packets', type=Path, required=True)
    prep.add_argument('--custody', type=Path, required=True)
    prep.add_argument('--seed', type=int)
    prep.add_argument('--cases-per-level', type=int, default=12)
    prep.add_argument('--level', choices=TIERS, action='append')
    prep.add_argument('--suite', choices=('focus', 'catalog'), default='focus')
    prep.add_argument('--family', action='append', help='include only the named class, repeatable')
    prep.add_argument('--pin-from', type=Path)
    prep.add_argument('--pin-custody', type=Path)
    prep.add_argument('--pin-case', action='append')
    run_parser = commands.add_parser('run')
    run_parser.add_argument('--packets', type=Path, required=True)
    run_parser.add_argument('--out', type=Path, required=True)
    run_parser.add_argument('--implementation', type=Path, default=ROOT)
    scorer = commands.add_parser('score')
    scorer.add_argument('--packets', type=Path, required=True)
    scorer.add_argument('--custody', type=Path, required=True)
    scorer.add_argument('--run', type=Path, required=True)
    scorer.add_argument('--out', type=Path, required=True)
    differ = commands.add_parser('compare')
    differ.add_argument('--before', type=Path, required=True)
    differ.add_argument('--after', type=Path, required=True)
    differ.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == 'catalog':
            import json
            print(json.dumps({'focus': FOCUS, 'catalog': CLASS_TIERS, 'unmeasured': W.PENDING},
                             indent=2))
        elif args.command == 'prepare':
            pins = (args.pin_from, args.pin_custody, args.pin_case)
            if any(pins) and not all(pins):
                raise ValueError('Pinning requires --pin-from, --pin-custody and --pin-case')
            seed = args.seed if args.seed is not None else secrets.randbits(128)
            levels = tuple(level for level in TIERS if not args.level or level in args.level)
            if args.level and len(args.level) != len(levels):
                raise ValueError('Select each level at most once')
            cases = prepare(args.packets, args.custody, seed=seed, count=args.cases_per_level,
                            levels=levels, suite=args.suite, pinned=pins if all(pins) else None,
                            families=args.family or ())
            print(f'Sealed {len(cases)} cases. Seed: {seed}')
        elif args.command == 'run':
            receipt = run(args.packets, args.out, args.implementation)
            return int(any(row['execution'] != 'completed' for row in receipt['cases']))
        elif args.command == 'score':
            report = score(args.packets, args.custody, args.run, args.out)
            return int(bool(report['metrics']['execution_failures']))
        else:
            report = compare(args.before, args.after, args.out)
            return int(bool(report['regressions'] or report['execution_failures_after']
                            or report['new_false_alarms']))
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as error:
        parser.exit(2, str(error) + '\n')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
