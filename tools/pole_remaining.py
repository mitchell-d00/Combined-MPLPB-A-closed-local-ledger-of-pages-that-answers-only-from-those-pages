"""Freeze and replay Herodotus-DHS, Polybius and Lovelace-Limit."""
import argparse
import json
from collections import Counter
from html import escape
from pathlib import Path
import shutil
import tarfile
from tempfile import TemporaryDirectory
from unittest.mock import patch

from tools import pole_authentic as A, pole_open_items as P
from tools.sorter_first_study import FAMILIES

HERODOTUS = {'FR-10', 'FR-11', 'FR-12', 'BT-01', 'BT-03'}
LITERAL = 'Which source contains the exact words “the French Foreign Office extended an invitation”?'


def prepare(spec, captures, public, custody, babbage):
    if public.exists() or custody.exists():
        raise FileExistsError('Use new operator and custody directories')
    public.mkdir()
    custody.mkdir(mode=0o700)
    source = A.read(spec)
    cases = [c for c in source['cases'] if c['id'] in HERODOTUS]
    for key, question, ref in (
        ('DHS-C01', 'Across the March rule, August correction and January follow-up, what earlier applicability date is reaffirmed?',
         'The original rule was published in April, not March.'),
        ('DHS-C02', 'Across the April rule, August correction and January follow-up, what earlier applicability date is reaffirmed for every application without exception?',
         'The correction explicitly describes an exception.'),
    ):
        cases.append({'id': key, 'family': 'correction_scope_control', 'expected': 'withhold',
                      'question': question, 'local_reference': ref, 'anchors': [],
                      'sources': ['DHS-OLD', 'DHS-ERR', 'DHS-NEW']})
    spec_copy = custody / 'herodotus-spec.json'
    A.save(spec_copy, dict(source, cases=cases))
    A.prepare(captures, spec_copy, public / 'herodotus-dhs', custody / 'herodotus-dhs')

    P.check_scout()
    poly = public / 'polybius'
    shutil.copytree(P.SCOUT / 'inputs', poly / 'inputs')
    local = custody / 'polybius'
    local.mkdir(mode=0o700)
    review = [r for r in A.read(P.SCOUT / 'custody/key.json')
              if r['family'] in {'relationship', 'missing'}]
    old_questions = A.read(poly / 'inputs/questions.json')
    questions = [q for q in old_questions if q['id'] in {r['id'] for r in review}]
    (poly / 'inputs/questions.json').unlink()
    A.save(poly / 'inputs/questions.json', questions)
    A.save(local / 'key.json', review)
    (local / 'key.json').chmod(0o600)
    A.save(poly / 'seal.json', {'public_files': A.inventory(poly),
                              'key_sha256': A.digest((local / 'key.json').read_bytes())})

    limit = public / 'lovelace-limit'
    limit.mkdir()
    shutil.copytree(babbage, limit / 'babbage')
    geo = limit / 'extra'
    geo.mkdir()
    extra = ('USDA-OLD', 'USDA-NEW', 'FERC-ERR', 'FERC-NEW', 'FEC-NEW', 'DHS-NEW', 'DHS-ERR', 'FERC-OLD')
    sources = {r['id']: r for r in A.read(public / 'herodotus-dhs/sources.json')}
    manifests = []
    for ident in extra:
        row = sources[ident]
        path = geo / (ident + '.html')
        shutil.copyfile(public / 'herodotus-dhs' / row['path'], path)
        manifests.append(dict(row, path='extra/' + path.name))
    pins = {}
    for folder in (P.SCOUT, P.SOLO):
        for name in ('inputs.sha256', 'inputs/sources.json'):
            path = folder / name
            pins[str(path.relative_to(P.ROOT))] = A.digest(path.read_bytes())
    for folder, seal in FAMILIES.values():
        for name in (seal, 'corpus-manifest.json'):
            path = P.ROOT / folder / name
            pins[str(path.relative_to(P.ROOT))] = A.digest(path.read_bytes())
    A.save(limit / 'protocol.json', {
        'extra': manifests, 'retained_inputs': pins, 'literal': LITERAL,
        'controlled_filler_pages': 39, 'short_units': 1, 'long_words': 1000,
        'many_units': 40, 'passages': 12, 'characters': 8000,
    })
    A.save(limit / 'seal.json', {'public_files': A.inventory(limit)})


def polybius(packet, output):
    A.seal_for(packet)
    rows = P.historical_rows(packet, discover=True)
    A.save(output, {'seal': A.digest((packet / 'seal.json').read_bytes()), 'cases': rows})


def score_polybius(packet, custody, receipt, output):
    seal = A.seal_for(packet)
    key_path = custody / 'key.json'
    if A.digest(key_path.read_bytes()) != seal['key_sha256']:
        raise ValueError('Reference key changed')
    run = A.read(receipt)
    if run['seal'] != A.digest((packet / 'seal.json').read_bytes()):
        raise ValueError('Replay input seal changed')
    expected = {row['id']: row for row in A.read(key_path)}
    if set(expected) != {row['id'] for row in run['cases']}:
        raise ValueError('Case coverage changed')
    counts = Counter()
    rows = []
    for result in run['cases']:
        row = {k: v for k, v in result.items() if k != 'discovery'}
        ref = expected[row['id']]
        row['family'] = ref['family']
        row['anchors'] = {name: all(
            any(a['source'] == p['source_id'] and a['quote'] in p['text'] for p in passages)
            for a in ref['anchors']) for name, passages in result['discovery'].items()}
        if ref['family'] == 'missing':
            result_type = 'unsupported_bridge' if row['supported'] else 'control_withheld'
        else:
            for method, matched in row['anchors'].items():
                counts[method + '_all_anchors'] += matched
            # Rehearsal measures bridge admission. The local key does not
            # independently adjudicate an unexpected complete bridge.
            result_type = ('unverified_supported_bridge' if row['supported'] else
                           'partial' if row['kind'] == 'partial_answer' else 'withheld')
        counts[result_type] += 1
        row['result'] = result_type
        rows.append(row)
    A.save(output, {'seal': run['seal'], 'counts': dict(counts), 'cases': rows})


def lovelace(packet, output):
    from mplpb_answers import documentary_verify as K
    from mplpb_answers.pipeline import answer_query
    from mplpb_combined.ledger import write
    from tools.pole_prose_cycle import babbage

    A.seal_for(packet)
    protocol = A.read(packet / 'protocol.json')
    for name, digest in protocol['retained_inputs'].items():
        if A.digest((P.ROOT / name).read_bytes()) != digest:
            raise ValueError('Retained original inventory changed')
    observed = []
    original_probe = P.scale_probe
    kernel = K.check

    def trace(index, proposals, **kwargs):
        checked = kernel(index, proposals, **kwargs)
        if K.literal_request(index.question):
            observed.append({
                'limits_reached': checked.get('limits_reached', []),
                'limits': checked.get('limits', {}),
                'examined_characters': checked.get('examined_characters'),
                'examined_units': checked.get('examined_units'),
                'literal_proofs': len(checked['proofs']),
                'complete_witnesses': sum(bool(p['proposition'].get('question_obligations_verified'))
                                          for p in checked['proofs']),
            })
        return checked

    added = []

    def probe(ledger, questions, stage, types=None):
        start = len(observed)
        row = original_probe(ledger, questions, stage, types)
        row['literal_scan'] = observed[start:]
        if stage == 'add_original_collection_2':
            for n, source in enumerate(protocol['extra'], 1):
                raw = (packet / source['path']).read_bytes()
                if A.digest(raw) != source['sha256']:
                    raise ValueError('Additional original changed')
                ident = 'ADDED-' + source['id']
                write(ledger, doc_id=ident, title=ident, scope='public documentary originals',
                      body_html=A.original_body(raw, source), origin='machine')
                if n in (4, len(protocol['extra'])):
                    begin = len(observed)
                    item = original_probe(ledger, questions, f'add_{n}_publications')
                    item['literal_scan'] = observed[begin:]
                    added.append(item)
        return row

    controlled = {}
    with patch.object(K, 'check', side_effect=trace), patch.object(P, 'scale_probe', side_effect=probe):
        ladder = P.volume_ladder()['stages'] + added
        for kind, filler in (
            ('small', '<p>Quiet neutral material.</p>'),
            ('characters', '<p>' + 'woven material ' * protocol['long_words'] + '.</p>'),
            ('units', '<p>The cedar shelf stood empty.</p>' * protocol['many_units']),
        ):
            with TemporaryDirectory() as tmp:
                root = Path(tmp)
                write(root, doc_id='ITEM-00', title='Original anchor', scope='control',
                      body_html='<p>The cobalt lantern burns quietly.</p>')
                for n in range(protocol['controlled_filler_pages']):
                    ident = f'ITEM-{n + 1:02d}'
                    write(root, doc_id=ident, title=ident, scope='control', body_html=filler)
                begin = len(observed)
                query = 'Which source contains the exact words “cobalt lantern burns quietly”?'
                answer = answer_query(root, query, max_passages=protocol['passages'],
                                      max_chars=protocol['characters']).contract
                controlled[kind] = {'kind': answer['kind'], 'diagnostic': answer['diagnostic']['code'],
                                    'supported': answer['answer_supported'], 'scan': observed[begin:]}
    with TemporaryDirectory() as tmp:
        strip = Path(tmp) / 'sorter.json'
        babbage(packet / 'babbage', strip, P.ROOT)
        sorter = A.read(strip)
    A.save(output, {'seal': A.digest((packet / 'seal.json').read_bytes()),
                    'authentic_ladder': ladder, 'controlled_caps': controlled, 'sorter': sorter})


def komnene_ship(bundle, prior_receipt, custody, delivery, output):
    package_digest = A.digest(bundle.read_bytes())
    if A.read(prior_receipt)['komnene_outside']['package_sha256'] != package_digest:
        raise ValueError('The existing sealed outside package changed')
    packet_hashes = {}
    arms = {'A': set(), 'B': set()}
    with tarfile.open(bundle) as archive:
        for entry in archive:
            if not entry.isfile():
                continue
            path = Path(entry.name)
            if path.name == 'key.json' or 'crosswalk' in path.name.casefold():
                raise ValueError('Custody files in the public delivery')
            if path.parent.as_posix() == 'review-packet/packets' and path.suffix == '.json':
                if path.stem in packet_hashes:
                    raise ValueError('Duplicate anonymous packet')
                packet_hashes[path.stem] = A.digest(archive.extractfile(entry).read())
            if path.parent.name in arms and path.name.endswith('.packet.json'):
                ident = path.name.removesuffix('.packet.json')
                if ident in arms[path.parent.name]:
                    raise ValueError('Duplicate anonymous arm')
                arms[path.parent.name].add(ident)
        status = json.load(archive.extractfile('review-packet/STATUS.json'))
    merged = set(packet_hashes)
    if len(merged) != 22 or any(arm != merged for arm in arms.values()) or status['questions'] != 22:
        raise ValueError('Anonymous question or arm coverage changed')
    if status['independent_human_review'] != 'NOT RUN' or status['metrics'] is not None:
        raise ValueError('Expected blank outside review accounting')
    matching = []
    for candidate in custody.rglob('crosswalk.json'):
        cases = A.read(candidate)['cases']
        if {k: v['packet_sha256'] for k, v in cases.items()} == packet_hashes:
            matching.append(candidate)
    if len(matching) != 1:
        raise ValueError('Expected exactly one separately held matching crosswalk')
    with delivery.open('xb') as stream:
        stream.write(bundle.read_bytes())
    if A.digest(delivery.read_bytes()) != package_digest:
        raise ValueError('Delivery copy differs')
    with delivery.with_name(delivery.name + '.sha256').open('x', encoding='utf-8') as stream:
        stream.write(package_digest + '  ' + delivery.name + '\n')
    A.save(output, {'baseline_sha256': package_digest, 'delivery_sha256': package_digest,
                    'paired_questions': 22, 'anonymous_arms': 44,
                    'packet_hashes_matching_concealed_mapping': 22,
                    'keys_in_delivery': 0, 'delivered_to_outside_judge': False,
                    'independent_scoring': 'NOT_RUN'})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    for name, fields in {
        'prepare': ('spec', 'captures', 'public', 'custody', 'babbage'),
        'polybius': ('packet', 'output'),
        'score-polybius': ('packet', 'custody', 'receipt', 'output'),
        'lovelace-limit': ('packet', 'output'),
        'komnene-ship': ('bundle', 'prior-receipt', 'custody', 'delivery', 'output'),
    }.items():
        child = commands.add_parser(name)
        for field in fields:
            child.add_argument('--' + field, required=True, type=Path)
    args = vars(parser.parse_args())
    command = args.pop('command')
    {'prepare': prepare, 'polybius': polybius, 'score-polybius': score_polybius,
     'lovelace-limit': lovelace, 'komnene-ship': komnene_ship}[command](**args)


if __name__ == '__main__':
    main()
