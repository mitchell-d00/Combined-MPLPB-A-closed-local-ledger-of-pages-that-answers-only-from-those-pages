"""Dice Bag live USGS acquisition, blind native replay, and separate scoring."""
import argparse
from collections import Counter, defaultdict
from contextlib import ExitStack
from datetime import datetime, timezone
from hashlib import sha256
import json
import math
from pathlib import Path
from random import Random
import re
from secrets import token_hex
from tempfile import TemporaryDirectory
from urllib.request import Request, urlopen

from test_tools.generate_open_data_seeds import generate

LEXICON = Path(__file__).resolve().parents[1] / 'evaluation/dice-bag/lexicon.json'
SCHEMA = 'mplpb-dice-bag-v1'
TERMS = 'https://www.usgs.gov/information-policies-and-instructions/copyrights-and-credits'
UNLISTED_WORDING = {'Event Magnitude': 'What measured strength did the catalog assign to',
                    'Depth Kilometers': 'How far below the surface was'}
FIELDS = {
    'Event Magnitude': ('How strong was', 'What quake magnitude was recorded for', 'How large was'),
    'Depth Kilometers': ('How deep was', 'What depth in km was recorded for', 'What quake depth was recorded for'),
}


def json_bytes(value):
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False) + '\n').encode()


def digest(raw):
    return sha256(raw).hexdigest()


def put(path, value):
    with Path(path).open('xb') as stream:
        stream.write(json_bytes(value))


def read(path):
    return json.loads(Path(path).read_bytes())


def fetch(url):
    request = Request(url, headers={'User-Agent': 'MPLPB-DiceBag/1.0 open-data evaluation'})
    with urlopen(request, timeout=12) as reply:
        if reply.geturl() != url:
            raise ValueError('Catalog request redirected')
        raw = reply.read(4_000_001)
    if len(raw) > 4_000_000:
        raise ValueError('Catalog response exceeded byte limit')
    return raw


def usable(feature, used):
    prop = feature.get('properties') or {}
    geo = feature.get('geometry') or {}
    coords = geo.get('coordinates') or []
    ident, place = feature.get('id'), prop.get('place')
    return (
        isinstance(ident, str) and re.fullmatch(r'[a-zA-Z0-9_-]{1,50}', ident)
        and ident not in used and prop.get('type') == 'earthquake'
        and isinstance(place, str) and 3 <= len(place) <= 160 and place == place.strip()
        and all(c.isprintable() for c in place)
        and len(coords) >= 3
        and all(type(value) in (float, int) and math.isfinite(value)
                for value in (prop.get('mag'), coords[2]))
    )


def collect(draws, captures):
    sources, receipts, used = [], [], set()
    for draw in draws:
        entry = {'draw': draw['draw'], 'requests': [], 'status': 'unfilled'}
        receipts.append(entry)
        for url in draw['candidates']:
            request = {'url': url}
            entry['requests'].append(request)
            try:
                raw = fetch(url)
                raw_hash = digest(raw)
                (captures / f'{draw["draw"]}-{len(entry["requests"])}.json').write_bytes(raw)
                request.update(sha256=raw_hash, retrieved_at=datetime.now(timezone.utc).isoformat())
                features = json.loads(raw)['features']
                choices = [(i, f) for i, f in enumerate(features) if usable(f, used)]
            except (OSError, ValueError, KeyError, TypeError) as exc:
                request['error'] = f'{type(exc).__name__}: {exc}'
                continue
            request['usable_records'] = len(choices)
            if not choices:
                continue
            selected, feature = min(choices, key=lambda item: digest(
                f'{draw["selection_key"]}:{item[1]["id"]}'.encode()))
            ident = feature['id']
            used.add(ident)
            prop = feature['properties']
            source = {
                'id': f'DB-{len(sources) + 1:04d}', 'place': prop['place'], 'event_id': ident,
                'url': f'https://earthquake.usgs.gov/earthquakes/eventpage/{ident}/executive',
                'source_sha256': raw_hash, 'reuse_terms': TERMS,
                'pointers': {key: f'/features/{selected}/{value}' for key, value in {
                    'place': 'properties/place', 'magnitude': 'properties/mag',
                    'depth': 'geometry/coordinates/2', 'event_id': 'id',
                }.items()},
                'fields': {'Event Magnitude': str(prop['mag']),
                           'Depth Kilometers': str(feature['geometry']['coordinates'][2])},
            }
            sources.append(source)
            entry.update(status='filled', event_id=ident)
            break
    return sources, receipts


def make_questions(seed, sources):
    rng = Random(int(seed, 16))
    cases, expected = [], []

    def add(question, family, source=None, field=None):
        ident = f'{rng.getrandbits(64):016x}'
        cases.append({'id': ident, 'question': question})
        key = {'id': ident, 'family': family}
        if source:
            key.update(source=source['id'], field=field,
                       quote=f'{field}: {source["fields"][field]}')
        expected.append(key)

    # Only ask a positive natural question when the source gives a unique
    # place description. Repeated places become explicit ambiguity controls.
    locations = Counter(source['place'].casefold() for source in sources)
    for number, source in enumerate(sources):
        field = rng.choice(list(FIELDS))
        place = source['place']
        template = rng.choice(FIELDS[field])
        natural = f'{template} the earthquake catalogued as {place}?'
        add(f'What is the {field.lower()} for record {source["id"]}?', 'direct', source, field)
        unlisted = f'{UNLISTED_WORDING[field]} the earthquake catalogued as {place}?'
        if locations[place.casefold()] > 1:
            add(natural, 'ambiguous')
            add(unlisted, 'ambiguous')
        else:
            add(natural, 'natural', source, field)
            add(unlisted, 'unlisted_wording', source, field)
        add(natural[:-1] + ' before its first catalog revision?', 'qualified')
        add(f'How long did shaking last for the earthquake catalogued as {place}?', 'missing')
        if len(sources) > 1:
            other = sources[(number + 1) % len(sources)]
            add(f'{template} the earthquake catalogued as {place} or {other["place"]}?', 'ambiguous')
    rng.shuffle(cases)
    rng.shuffle(expected)
    return cases, expected


def prepare(inputs, custody, seed, count):
    if inputs.resolve().is_relative_to(custody.resolve()) or custody.resolve().is_relative_to(inputs.resolve()):
        raise ValueError('Input and custodian directories must be separate')
    if inputs.exists() or custody.exists():
        raise ValueError('Use two fresh directories')
    plan = generate(seed, count * 2)
    draws = [draw for draw in plan['draws'] if draw['catalog'] == 'USGS earthquake catalog']
    custody.mkdir(mode=0o700)
    captures = custody / 'captures'
    captures.mkdir()
    sources, receipts = collect(draws, captures)
    put(custody / 'draws.json', {'seed': seed, 'draws': receipts})
    if not sources:
        raise ValueError('No live records acquired. See custodian draw receipts.')
    cases, expected = make_questions(seed, sources)
    packet = {'schema': SCHEMA, 'sources': sources, 'cases': cases, 'lexicon': read(LEXICON),
              'draw_counts': dict(Counter(row['status'] for row in receipts))}
    packet_hash = digest(json_bytes(packet))
    key = {'packet_sha256': packet_hash, 'seed': seed, 'cases': expected}
    put(custody / 'key.json', key)
    inputs.mkdir()
    put(inputs / 'packet.json', packet)
    put(inputs / 'seal.json', {'packet_sha256': packet_hash, 'key_sha256': digest(json_bytes(key))})


def packet_with_seal(inputs):
    raw = (inputs / 'packet.json').read_bytes()
    seal = read(inputs / 'seal.json')
    if seal['packet_sha256'] != digest(raw):
        raise ValueError('Dice Bag packet checksum mismatch')
    packet = json.loads(raw)
    if packet.get('schema') != SCHEMA:
        raise ValueError('Expected Dice Bag packet')
    return packet, seal


def seal_ledger(root, sources):
    from html import escape
    from mplpb_combined.ledger import Ledger, write

    for source in sources:
        lines = [f'Record-ID: {source["id"]}', f'Event ID: {source["event_id"]}',
                 f'Place: {source["place"]}']
        lines.extend(f'{field}: {value}' for field, value in source['fields'].items())
        write(root, doc_id=source['id'], title=source['place'], scope='USGS earthquake catalog',
              body_html='<pre>' + escape('\n'.join(lines)) + '</pre>', origin='machine',
              when='2026-01-01')
    return {rec.id: rec for rec in Ledger(root).servable()}


def run(inputs, graph_db=None):
    from mplpb_answers.pipeline import answer_query
    from mplpb_answers.synonym_graph import open_index
    from test_tools.synonym_index import SynonymIndex

    packet, seal = packet_with_seal(inputs)
    rows = []
    catalog = {'schema': 'mplpb-synonym-index-v1', 'collections': {'earthquakes': {
        'records': {source['id']: [source['place']] for source in packet['sources']},
        'fields': packet['lexicon'],
    }}}
    with ExitStack() as stack:
        root = stack.enter_context(TemporaryDirectory(prefix='mplpb-dice-bag-'))
        index = (stack.enter_context(open_index(graph_db)) if graph_db is not None
                 else SynonymIndex(catalog))
        seal_ledger(root, packet['sources'])
        for case in packet['cases']:
            question = case['question']
            rows.append({'id': case['id'],
                         'answer': answer_query(root, question, mode='strict').contract,
                         'lookup': index.lookup('earthquakes', question)})
    return {'schema': SCHEMA, **seal, 'cases': rows}


def rows_by_id(rows):
    result = {row['id']: row for row in rows}
    if len(result) != len(rows):
        raise ValueError('Duplicate Dice Bag case ID')
    return result


def score(inputs, run_path, key_path):
    from mplpb_answers.pipeline import answer_query
    from test_tools.persona_corpus_transfer import classify

    packet, seal = packet_with_seal(inputs)
    key_raw = key_path.read_bytes()
    key = json.loads(key_raw)
    report = read(run_path)
    if (report.get('schema') != SCHEMA or any(report.get(k) != v for k, v in seal.items())
            or key.get('packet_sha256') != seal['packet_sha256'] or digest(key_raw) != seal['key_sha256']):
        raise ValueError('Run and key do not match the frozen Dice Bag batch')
    questions = rows_by_id(packet['cases'])
    outcomes = rows_by_id(report['cases'])
    labels = rows_by_id(key['cases'])
    if set(questions) != set(outcomes) or set(questions) != set(labels):
        raise ValueError('Score must cover every frozen question')
    totals, cases = defaultdict(Counter), []
    with TemporaryDirectory(prefix='mplpb-dice-score-') as root:
        sources = seal_ledger(root, packet['sources'])
        for ident, label in labels.items():
            answer, lookup = (outcomes[ident][k] for k in ('answer', 'lookup'))
            question = questions[ident]['question']
            expected = {**label, 'expected': 'answer' if 'quote' in label else 'withhold'}
            base = classify(expected, answer, sources)
            candidate = lookup['status']
            proof = None
            if candidate == 'candidate' and expected['expected'] == 'answer':
                if set(lookup['records']) == {label['source']} and set(lookup['fields']) == {label['field']}:
                    candidate = 'correct_selector'
                    approved = answer_query(root, question, mode='strict',
                                            record_id=label['source'], field=label['field']).contract
                    proof = classify(expected, approved, sources)
                else:
                    candidate = 'incorrect_selector'
            group = totals[label['family']]
            group.update(['baseline_' + base, 'lookup_' + candidate])
            if proof is not None:
                group['confirmed_proof_' + proof] += 1
            cases.append({'id': ident, 'family': label['family'], 'baseline': base,
                          'lookup': candidate, 'confirmed_proof': proof})
    return {'schema': SCHEMA, **seal, 'draw_counts': packet['draw_counts'],
            'questions': len(cases), 'summary': dict(totals), 'cases': cases}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_subparsers(dest='mode', required=True)
    preparation = modes.add_parser('prepare')
    preparation.add_argument('--custody', type=Path, required=True)
    preparation.add_argument('--seed', help='1–32 hexadecimal digits. Omit for a fresh draw.')
    preparation.add_argument('--count', type=int, default=12)
    replay = modes.add_parser('run')
    grading = modes.add_parser('score')
    for mode in (preparation, replay, grading):
        mode.add_argument('--inputs', type=Path, required=True)
    for mode in (replay, grading):
        mode.add_argument('--output', type=Path, required=True)
    replay.add_argument('--graph-db', type=Path, help='Use a reviewed SQLite synonym graph')
    grading.add_argument('--run', type=Path, required=True)
    grading.add_argument('--key', type=Path, required=True)
    args = parser.parse_args()
    if args.mode == 'prepare':
        seed = args.seed or token_hex(16)
        if not re.fullmatch(r'[0-9a-fA-F]{1,32}', seed) or not 1 <= args.count <= 30:
            parser.error('Use a hexadecimal seed and 1–30 draws')
        prepare(args.inputs, args.custody, seed.lower().zfill(32), args.count)
    elif args.mode == 'run':
        put(args.output, run(args.inputs, args.graph_db))
    else:
        result = score(args.inputs, args.run, args.key)
        put(args.output, result)
        print(json.dumps(result['summary'], indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
