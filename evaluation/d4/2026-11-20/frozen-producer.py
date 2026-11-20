"""Event identity, co-reference D4. Sealed mixed D% generation and acceptance."""
import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
import json
from pathlib import Path
import secrets

from tools import dpercent as D
from tools import dpercent_weaknesses as W

TITLE = 'Event identity, co-reference D4'
VERSION = 'd4-v1'
EVENT = (
    'd4_event_shared_key', 'd4_event_declared_distinct',
    'd4_event_cross_registry', 'd4_event_different_keys', 'd4_event_same_wording',
    'd4_event_contradiction', 'd4_event_quoted', 'd4_event_withheld',
    'd4_event_budget', 'd4_event_ambiguous_occurrence', 'd4_event_late_conflict',
)
COREFERENCE = (
    'd4_coref_explicit', 'd4_coref_direct_speech', 'd4_coref_ambiguous',
    'd4_coref_quoted', 'd4_coref_reported', 'd4_coref_conditional',
    'd4_coref_nearby_names', 'd4_coref_wrong_pronoun', 'd4_coref_withdrawn',
)
FOCUS = EVENT + COREFERENCE
CONTROLS = (
    'exact_anchor', 'direct_action', 'passive_action', 'explicit_cause',
    'subject_identity', 'ambiguous_pronoun', 'embedded_identifier',
    'reported_execution', 'restricted_source', 'corrupted_source',
    'field_literal', 'field_synonym', 'field_compound', 'field_same_subject',
    'field_conflict', 'field_quoted_only', 'alias_role_date', 'alias_collision',
)
ANSWERS = {'d4_event_shared_key', 'd4_event_declared_distinct',
           'd4_coref_explicit', 'd4_coref_direct_speech'}
REGISTRIES = ('Harbor Ledger', 'Maple Register', 'Quarry Index', 'Transit Archive')
SPEAKERS = ('Ada Moreno', 'Ravi Das', 'Élodie Tennant', 'Lina Park', 'Nicolás Chen', 'Luan Öberg')
TOPICS = ('repair ledger', 'orchard map', 'arrival register', 'clay inventory')
EVENT_FORMS = ('Do sources {a} and {b} describe the same event?',
               'Are the events in sources {a} and {b} the same?',
               'Do sources {a} and {b} refer to the same event?')
COREF_FORMS = ('Who does "{pronoun}" refer to in source {a}?',
               'Who does the pronoun "{pronoun}" refer to in source {a}?',
               'To whom does "{pronoun}" refer in source {a}?')


def material(number, family, dice):
    if family not in FOCUS:
        return W.material(number, family, dice)
    registry = dice.choose('d4_registry', REGISTRIES)
    index = REGISTRIES.index(registry)
    actor, rival = dice.choose('d4_speakers', [(a, b) for a in SPEAKERS for b in SPEAKERS if a != b])
    topic = dice.choose('d4_topic', TOPICS)
    token = str(dice.choose('d4_document_number', tuple(range(100, 200))))
    newline = dice.choose('d4_newline', ('\n', '\r\n'))
    fence = dice.choose('d4_quote_style', ('quote', 'backtick', 'tilde'))
    reverse = dice.choose('d4_source_order', (False, True))
    profile = dice.choose('d4_profile', ('internal', 'lab'))
    form = dice.choose('d4_question_form', (0, 1, 2))
    suffix = dice.choose('d4_question_scaffolding', ('none', 'prefix', 'suffix'))
    document = lambda i: 'SOURCE-%04d' % i
    profile_flags = {}
    max_passages = 12
    witnesses = {}
    required = {}
    if family in EVENT:
        key = 'ENTRY-' + token
        first, second = 'LEAF-' + token + 'A', 'LEAF-' + token + 'B'
        left = [f'Event Registry: {registry}', f'Occurrence ID: {first}', f'Event ID: {key}']
        right = [f'Event Registry: {registry}', f'Occurrence ID: {second}', f'Event ID: {key}']
        if family == 'd4_event_cross_registry':
            right[0] = f'Event Registry: {REGISTRIES[(index+1) % len(REGISTRIES)]}'
        if family in {'d4_event_declared_distinct', 'd4_event_different_keys', 'd4_event_ambiguous_occurrence'}:
            right[2] += 'B'
        if family in {'d4_event_declared_distinct', 'd4_event_contradiction', 'd4_event_ambiguous_occurrence'}:
            left.append(f'Different Event From: {second}')
        if family == 'd4_event_same_wording':
            left.clear()
            right.clear()
        primary = [left, right]
        order = (1, 0) if reverse else (0, 1)
        a, b = (document(order.index(i)+1) for i in (0, 1))
        asked = (a, b) if form != 2 else (b, a)
        question = EVENT_FORMS[form].format(a=asked[0], b=asked[1])
        bodies = ['\n'.join(primary[i] + [f'The {topic} was moved to the annex.']) for i in order]
        if family == 'd4_event_late_conflict':
            bodies[order.index(0)] += f'\n\nEvent ID: ENTRY-{token}Z'
        if family == 'd4_event_quoted':
            bodies[order.index(1)] = _quote(bodies[order.index(1)], fence)
        if family == 'd4_event_withheld':
            profile = 'external'
            profile_flags = {0: {'external': 'yes'}, 1: {'external': 'yes'}}
            profile_flags[order.index(1)] = {'external': 'no'}
        if family == 'd4_event_budget':
            max_passages = 1
        if family == 'd4_event_ambiguous_occurrence':
            bodies.append('\n'.join(right + ['An additional occurrence uses the same local identifier.']))
        if family in ANSWERS:
            shared = family == 'd4_event_shared_key'
            required = {'relation': 'documentary_event_identity', 'same_event': shared,
                        'left_source_id': asked[0], 'right_source_id': asked[1], 'registry': registry}
            if shared:
                required['event_id'] = key
                witnesses = {a: [left[0], left[2]], b: [right[0], right[2]]}
            else:
                witnesses = {a: [left[0], left[3]], b: [right[0], right[1]]}
    else:
        pronoun = dice.choose('d4_pronoun', ('she', 'he', 'they'))
        if family == 'd4_coref_direct_speech':
            pronoun = 'I'
            body = (
                f'“I filed the {topic},” said {actor}.',
                f'{actor} said, “I filed the {topic}.”',
                f'"I filed the {topic}," said {actor}.',
            )[form]
        else:
            body = f'Pronoun "{pronoun}" refers to {actor}.'
            if family == 'd4_coref_ambiguous':
                body += f'\nPronoun "{pronoun}" refers to {rival}.'
            if family == 'd4_coref_quoted':
                body = _quote(body, fence)
            if family == 'd4_coref_reported':
                body = f'{rival} suspected that "{pronoun}" referred to {actor}.'
            if family == 'd4_coref_conditional':
                body = f'If this is the revised text, pronoun "{pronoun}" refers to {actor}.'
            if family == 'd4_coref_nearby_names':
                body = f'{actor} met {rival} near the annex. {pronoun.capitalize()} filed the {topic}.'
            if family == 'd4_coref_wrong_pronoun':
                pronoun = 'it'
        if reverse:
            bodies = [f'{rival} indexed the {topic}.', body]
        else:
            bodies = [body, f'{rival} indexed the {topic}.']
        chosen = int(reverse)
        source = document(chosen+1)
        question = COREF_FORMS[form].format(a=source, pronoun=pronoun)
        if family == 'd4_coref_withdrawn':
            profile_flags[chosen] = {'retired': True}
        if family in ANSWERS:
            required = {'relation': 'documentary_coreference', 'pronoun': pronoun.casefold(),
                        'referent': actor, 'source_id': source}
            witnesses = {source: [body]}
    if suffix == 'prefix':
        question = 'Please assess this from the provided records: ' + question
    if suffix == 'suffix':
        question += ' Keep unknown matters unresolved.'
    docs = []
    for i, body in enumerate(bodies, 1):
        source = {'path': f'sources/leaf-{i:02d}.txt', 'source_class': 'original',
                  **profile_flags.get(i-1, {})}
        docs.append((source, (body.replace('\n', newline)+'\n').encode('utf-8')))
    ident = f'DP{number:05d}'
    case = {'id': ident, 'question': question, 'profile': profile, 'sources': [s for s, _ in docs],
            'budget': {'passages': max_passages, 'characters': 8000}}
    key = {'id': ident, 'family': family, 'expected': 'answer' if required else 'refuse',
           'required_propositions': [required] if required else [],
           'reference_sources': list(witnesses), 'required_witnesses': witnesses,
           'structural_expectations': {}, 'automatic_answer_matcher': 'typed_proposition_v1',
           'features': {'d4_task': 'event_identity' if family in EVENT else 'coreference',
                        'd4_question_form': form, 'd4_scaffolding': suffix,
                        'd4_source_order': 'reverse' if reverse else 'forward',
                        'd4_line_ending': 'CRLF' if newline == '\r\n' else 'LF',
                        'd4_profile': profile, 'd4_source_count': len(docs)}}
    return case, docs, key


def _quote(body, style):
    if style == 'quote':
        return '\n'.join('> '+line for line in body.splitlines())
    fence = '```' if style == 'backtick' else '~~~'
    return f'{fence}text\n{body}\n{fence}'


def prepare(public, custody, count=4096, seed=2026112004, shard_size=256, mix='study'):
    public, custody = Path(public).resolve(), Path(custody).resolve()
    if (public == custody or public in custody.parents or custody in public.parents
            or D.ROOT == custody or D.ROOT in custody.parents):
        raise ValueError('Use separate packet and scoring directories outside source custody')
    if not 1 <= count <= 8192 or not 1 <= shard_size <= 512 or not 0 <= seed < 2**128:
        raise ValueError('Use 1–8192 cases, 1–512 cases per shard and an unsigned 128-bit seed')
    public.mkdir(parents=True, exist_ok=False)
    custody.mkdir(parents=True, mode=0o700, exist_ok=False)
    catalog = FOCUS + CONTROLS if mix == 'gate' else FOCUS * 4 + W.FAMILIES
    dice = D.Dice(seed)
    schedule = dice.shuffle('d4_class_schedule', [catalog[i % len(catalog)] for i in range(count)])
    shards = []
    dependencies = {f'tools/{name}.py': D.sha((D.ROOT / f'tools/{name}.py').read_bytes())
                    for name in ('dpercent', 'dpercent_expanded', 'dpercent_weaknesses')}
    for start in range(0, count, shard_size):
        name = 'shard-%04d' % (start//shard_size+1)
        packet, private = public/name, custody/name
        private.mkdir(mode=0o700)
        keys = []
        before = len(dice.rolls)
        for i in range(start, min(start+shard_size, count)):
            case, sources, key = material(i+1, schedule[i], dice)
            folder = packet/'packets'/case['id']
            D.save(folder/'case.json', case)
            for source, raw in sources:
                path = folder/source['path']
                path.parent.mkdir(exist_ok=True)
                path.write_bytes(raw)
            keys.append(key)
        D.save(private/'key.json', {'schema': VERSION+'-key', 'cases': keys})
        D.save(private/'dice.json', {'seed': str(seed), 'rolls': dice.rolls[before:]})
        D.save(packet/'protocol.json', {'schema': VERSION, 'title': TITLE, 'cases': len(keys)})
        seal = {'public_files': D.files(packet), 'key_sha256': D.sha((private/'key.json').read_bytes()),
                'dice_sha256': D.sha((private/'dice.json').read_bytes()),
                'generator_sha256': D.sha(Path(__file__).read_bytes()), 'generator_dependencies': dependencies,
                'worker_sha256': D.sha((D.ROOT/'tools/dpercent_worker.py').read_bytes())}
        D.save(packet/'seal.json', seal)
        D.save(private/'public-seal-copy.json', seal)
        shards.append({'name': name, 'cases': len(keys), 'seal_sha256': D.sha((packet/'seal.json').read_bytes())})
    D.save(custody/'schedule-dice.json', {'seed': str(seed), 'rolls': dice.rolls})
    manifest = {'schema': VERSION, 'title': TITLE, 'mix': mix, 'cases': count, 'shards': shards,
                'seed_commitment': D.sha(str(seed).encode()),
                'schedule_dice_sha256': D.sha((custody/'schedule-dice.json').read_bytes()),
                'family_counts': dict(Counter(schedule))}
    D.save(public/'study.json', manifest)
    D.save(custody/'study-copy.json', manifest)
    return manifest


def _run_shard(public, output, implementation):
    Path(output).parent.mkdir(exist_ok=True)
    return D.run(public, output, implementation=implementation)


def run(public, output, implementation, workers):
    """Execute without reading custody or mounting a scorer."""
    public, output = Path(public).resolve(), Path(output).resolve()
    manifest = D.read(public/'study.json')
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futures = []
        for shard in manifest['shards']:
            name = shard['name']
            packet = public/name
            if D.sha((packet/'seal.json').read_bytes()) != shard['seal_sha256']:
                raise ValueError('Shard seal differs from the study manifest')
            futures.append(pool.submit(_run_shard, packet, output/name, implementation))
        for future in futures:
            future.result()


def score(public, custody, run_dir, output, baseline=None):
    public, custody, run_dir, output = map(Path, (public, custody, run_dir, output))
    study = D.read(public/'study.json')
    if (study != D.read(custody/'study-copy.json')
            or D.sha((custody/'schedule-dice.json').read_bytes()) != study['schedule_dice_sha256']):
        raise ValueError('Frozen study or draw commitment changed')
    output.mkdir(exist_ok=False)
    rows = {}
    revisions = set()
    for shard in study['shards']:
        name = shard['name']
        packet, private, native = public/name, custody/name, run_dir/name
        if D.sha((packet/'seal.json').read_bytes()) != shard['seal_sha256']:
            raise ValueError('Shard seal differs from the study manifest')
        receipt = D.read(native/'run.json')
        if (not receipt['network_isolated'] or receipt['scoring_key_mounted']
                or receipt['generator_mounted']):
            raise ValueError('Native worker isolation was not established')
        revisions.add(receipt['checkout_revision'])
        base = W.score_shard(packet, private, native, output/(name+'-score.json'))
        keys = {k['id']: k for k in D.read(private/'key.json')['cases']}
        for row in base['cases']:
            ident = row['id']
            key = keys[ident]
            if row['outcome'] == 'detected_answer' and row['family'] in FOCUS:
                result = D.read(native/ident/'result.json')
                proof = result['answer']['claims']
                required = {(sid, quote) for sid, quotes in key['required_witnesses'].items() for quote in quotes}
                actual = {(c['source_id'], c['quote']) for claim in proof for c in claim['citations']}
                if (len(proof) != 1 or not required <= actual
                        or {sid for sid, _ in actual} != set(key['required_witnesses'])
                        or result['answer']['verification']['truth_verified']):
                    row['outcome'] = 'incorrect_supported_answer'
            rows[ident] = {field: row.get(field) for field in (
                'family', 'outcome', 'execution', 'kind', 'answer_supported', 'features')}
    if len(revisions) != 1 or len(rows) != study['cases']:
        raise ValueError('A complete report requires one implementation revision and every planned result')
    groups = {}
    for row in rows.values():
        strata = [('family', row['family'])]
        if row['family'] in FOCUS:
            strata += [(name, str(value)) for name, value in row['features'].items()]
            strata.append(('family_by_question_form', row['family']+'/'+str(row['features']['d4_question_form'])))
        for feature, value in strata:
            groups.setdefault(feature, {}).setdefault(value, Counter())[row['outcome']] += 1
    focus = Counter(row['outcome'] for row in rows.values() if row['family'] in FOCUS)
    mixed = Counter(row['outcome'] for row in rows.values() if row['family'] not in FOCUS)
    findings = None
    seal = D.sha((public/'study.json').read_bytes())
    if baseline:
        prior = D.read(baseline)
        if prior['study_sha256'] != seal or rows.keys() != prior['rows'].keys():
            raise ValueError('Before/after reports must share frozen inputs')
        findings = [ident for ident, row in rows.items() if row['family'] not in FOCUS
                    and row != prior['rows'][ident]]
    summary = {'schema': VERSION+'-results', 'title': TITLE, 'mix': study['mix'],
               'revision': revisions.pop(), 'study_sha256': seal, 'focus': focus, 'mixed': mixed,
               'cohorts': groups, 'mixed_changes_from_baseline': findings, 'rows': rows,
               'independent_semantic_review': 'NOT RUN'}
    passing = {'detected_answer', 'appropriate_refusal'}
    summary['strict_gate_passed'] = (set(focus) <= passing and
        (set(mixed) <= passing if study['mix'] == 'gate' else findings == []))
    D.save(output/'summary.json', summary)
    print(json.dumps({k: v for k, v in summary.items() if k not in {'rows', 'cohorts'}}, indent=2))
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    prep = sub.add_parser('prepare')
    prep.add_argument('--cases', type=int, default=4096)
    prep.add_argument('--seed', type=int, default=2026112004)
    prep.add_argument('--shard-size', type=int, default=256)
    prep.add_argument('--mix', choices=('gate', 'study'), default='study')
    prep.add_argument('--custody', required=True, type=Path)
    replay = sub.add_parser('run')
    replay.add_argument('--implementation', type=Path, default=D.ROOT)
    replay.add_argument('--workers', type=int, choices=range(1, 5), default=4)
    scoring = sub.add_parser('score')
    scoring.add_argument('--custody', required=True, type=Path)
    scoring.add_argument('--run', required=True, type=Path)
    scoring.add_argument('--baseline', type=Path)
    scoring.add_argument('--require-pass', action='store_true')
    for command in (prep, replay, scoring):
        command.add_argument('--public', type=Path, required=True)
        command.add_argument('--output', type=Path, required=command is not prep)
    args = parser.parse_args()
    if args.command == 'prepare':
        print(json.dumps(prepare(args.public, args.custody, args.cases, args.seed, args.shard_size, args.mix)))
    elif args.command == 'run':
        run(args.public, args.output, args.implementation, args.workers)
    else:
        result = score(args.public, args.custody, args.run, args.output, args.baseline)
        return int(args.require_pass and not result['strict_gate_passed'])
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
