"""Freeze, replay and score a public documentary packet with separate key custody."""
import argparse
from collections import Counter, defaultdict
from hashlib import sha256
from html import escape
import json
from pathlib import Path
import re
import subprocess
import sys
from tempfile import TemporaryDirectory

MAX_SOURCE_BYTES = 2 * 1024**2
BUDGET = {'passages': 12, 'characters': 8000}
ROOT = Path(__file__).resolve().parents[1]


def digest(raw):
    return sha256(raw).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def save(path, value):
    with path.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False, allow_nan=False)
        stream.write('\n')


def inventory(root):
    return {p.relative_to(root).as_posix(): digest(p.read_bytes())
            for p in sorted(root.rglob('*')) if p.is_file() and p.name != 'seal.json'}


def seal_for(packet):
    seal = read(packet / 'seal.json')
    if inventory(packet) != seal['public_files']:
        raise ValueError('Operator packet changed')
    return seal


def anchor(source, packet, quote):
    raw = (packet / source['path']).read_bytes()
    token = quote.encode(source['encoding'])
    start = raw.find(token)
    if start < 0:
        raise ValueError(f'Anchor absent in {source["path"]}: {quote!r}')
    begin = len(raw[:start].decode(source['encoding']))
    return {'id': source['id'], 'path': source['path'], 'sha256': source['sha256'],
            'byte_span': [start, start + len(token)], 'character_span': [begin, begin + len(quote)],
            'quote': quote}


def prepare(captures, spec_path, packet, custody):
    packet, custody = packet.resolve(), custody.resolve()
    if packet == custody or packet in custody.parents or custody in packet.parents:
        raise ValueError('Keep operator packet and custody disjoint')
    if packet.exists() or custody.exists():
        raise FileExistsError('Use new packet and custody directories')
    spec = read(spec_path)
    packet.mkdir(parents=True)
    custody.mkdir(parents=True, mode=0o700)
    (packet / 'sources').mkdir()
    sources = {}
    for item in spec['sources']:
        ident, filename = item['id'], item['filename']
        if not re.fullmatch(r'[A-Z0-9-]{2,35}', ident) or Path(filename).name != filename or ident in sources:
            raise ValueError('Invalid source identity')
        raw = (captures / filename).read_bytes()
        if not 0 < len(raw) <= MAX_SOURCE_BYTES or digest(raw) != item['sha256']:
            raise ValueError(f'Capture length or pinned digest invalid for {filename}')
        raw.decode(item['encoding'])
        relative = 'sources/' + ident + Path(filename).suffix
        (packet / relative).write_bytes(raw)
        sources[ident] = dict(item, path=relative, bytes=len(raw))
    public, key = [], []
    for case in spec['cases']:
        case_id = case['id']
        selected = case['sources']
        public.append({'id': case_id, 'question': case['question'], 'sources': selected,
                       'budget': BUDGET})
        anchors = [anchor(sources[ident], packet, quote) for ident, quote in case['anchors']]
        if any(row['id'] not in selected for row in anchors):
            raise ValueError('Anchor references a source excluded from the question')
        key.append({'id': case_id, 'family': case['family'], 'expected': case['expected'],
                    'local_reference': case['local_reference'], 'anchors': anchors})
    save(packet / 'sources.json', list(sources.values()))
    save(packet / 'questions.json', public)
    save(custody / 'key.json', key)
    (custody / 'key.json').chmod(0o600)
    save(packet / 'seal.json', {'public_files': inventory(packet),
                                'key_sha256': digest((custody / 'key.json').read_bytes()),
                                'spec_sha256': digest(spec_path.read_bytes())})
    save(custody / 'seal-copy.json', read(packet / 'seal.json'))


def original_body(raw, source):
    text = raw.decode(source['encoding'])
    if source['media_type'] == 'text/html':
        match = re.search(r'<pre>([\s\S]*?)</pre>', text, re.I)
        if not match:
            raise ValueError('GovInfo original lacks the expected preformatted document')
        # Keep original bytes in the packet. Clear publisher layout NULs only
        # from the native HTML body, never from the original anchor coordinates.
        return '<pre>' + match[1].replace('\0', '') + '</pre>'
    return '<pre>' + escape(text) + '</pre>'


def run(packet, output, implementation, *, project_source=original_body):
    packet, output, implementation = (p.resolve() for p in (packet, output, implementation))
    seal_for(packet)
    sys.path.insert(0, str(implementation))
    from mplpb_answers.body_text import body_text
    from mplpb_answers.passages import PassageIndex
    from mplpb_answers.pipeline import answer_query
    from mplpb_combined.ledger import write
    from mplpb_combined.reader import PROFILES
    from tools.unprepared_challenge import code_pins

    sources = {row['id']: row for row in read(packet / 'sources.json')}
    initial_pins = code_pins(implementation)
    profile = PROFILES['internal']
    rows = []
    for case in read(packet / 'questions.json'):
        with TemporaryDirectory(prefix='pole-authentic-') as directory:
            ledger = Path(directory)
            receipts = []
            for ident in case['sources']:
                source = sources[ident]
                body = project_source((packet / source['path']).read_bytes(), source)
                if source.get('retain_capture_manifest'):
                    projection = digest(body_text(body).encode())
                    manifest = {'source_url': source['url'], 'source_sha256': source['sha256'],
                                'text_sha256': projection, 'transport': 'frozen_public_capture'}
                    body += '<p>' + escape('Source capture: ' + json.dumps(manifest, sort_keys=True)) + '</p>'
                record = write(ledger, doc_id=ident, title=ident, scope='public documentary originals',
                               origin='machine', body_html=body, external='yes', when='2026-11-24T00:00Z')
                receipts.append({'id': ident, 'original_path': source['path'],
                                 'original_sha256': source['sha256'], 'ledger_hash': record.hash_actual,
                                 'ledger_path': record.path, 'body': body_text(record.body_html)})
            question, budget = case['question'], case['budget']
            answer = answer_query(ledger, question, profile, max_passages=budget['passages'],
                                  max_chars=budget['characters']).contract
            discovery = PassageIndex(ledger, question, profile).retrieve(
                [question], budget['passages'], budget['characters'])
            rows.append({'id': case['id'], 'answer': answer, 'receipts': receipts,
                         'discovery': discovery['passages'],
                         'discovery_search_complete': discovery['search_complete']})
    if initial_pins != code_pins(implementation):
        raise ValueError('Runtime changed during execution')
    seal_for(packet)
    revision = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=implementation, text=True,
                              capture_output=True).stdout.strip() or None
    save(output, {'source_packet_seal': digest((packet / 'seal.json').read_bytes()),
                  'revision': revision, 'runtime_sha256': initial_pins,
                  'os_isolated': False, 'custody_path_passed': False, 'cases': rows})


def normal(text):
    return ' '.join(text.replace('\0', '').split()).casefold()


def score(packet, custody, receipt_path, output):
    seal = seal_for(packet)
    if seal != read(custody / 'seal-copy.json') or digest((custody / 'key.json').read_bytes()) != seal['key_sha256']:
        raise ValueError('Custody commitment changed')
    by_id = {row['id']: row for row in read(custody / 'key.json')}
    receipt = read(receipt_path)
    if receipt['source_packet_seal'] != digest((packet / 'seal.json').read_bytes()):
        raise ValueError('Execution used a different packet')
    if len(receipt['cases']) != len(by_id) or set(by_id) != {row['id'] for row in receipt['cases']}:
        raise ValueError('Incomplete or duplicate execution coverage')
    source_index = {row['id']: row for row in read(packet / 'sources.json')}
    public_cases = {row['id']: row for row in read(packet / 'questions.json')}
    groups = defaultdict(Counter)
    scores = []
    for row in receipt['cases']:
        key = by_id[row['id']]
        records = {source['id']: source for source in row['receipts']}
        if set(records) != set(public_cases[row['id']]['sources']):
            raise ValueError('Worker source coverage differs from the sealed case')
        for ident, source in records.items():
            original = source_index[ident]
            if (source['original_path'], source['original_sha256']) != (original['path'], original['sha256']):
                raise ValueError('Worker source identity differs from the sealed original')
        witnesses = [c for claim in row['answer']['claims'] for c in claim['citations']]
        for cite in witnesses:
            source = records[cite['source_id']]
            a, b = cite['body_start'], cite['body_end']
            if (source['ledger_hash'] != cite['hash'] or source['ledger_path'] != cite['path']
                    or not 0 <= a < b <= len(source['body']) or source['body'][a:b] != cite['quote']):
                raise ValueError(f'Cited span changed: {row["id"]}')
        for ref in key['anchors']:
            original = source_index[ref['id']]
            if anchor(original, packet, ref['quote']) != ref:
                raise ValueError(f'Original anchor changed: {row["id"]}')
        kept = row['answer']['answer_supported']
        anchored = bool(key['anchors']) and all(any(
            c['source_id'] == ref['id'] and normal(ref['quote']) in normal(c['quote'])
            for c in witnesses) for ref in key['anchors'])
        if key['expected'] == 'withhold':
            outcome = 'supported_on_withhold' if kept else 'expected_withhold'
        else:
            outcome = ('complete_with_all_anchors' if kept and anchored else
                       'supported_without_all_anchors' if kept else 'over_refusal')
        groups[key['family']][outcome] += 1
        scores.append({'id': row['id'], 'family': key['family'], 'outcome': outcome,
                       'expected': key['expected'], 'kind': row['answer']['kind'],
                       'diagnostic': row['answer']['diagnostic']['code'],
                       'complete_discovery_anchor_coverage': bool(key['anchors']) and all(any(
                           p['source_id'] == ref['id'] and normal(ref['quote']) in normal(p['text'])
                           for p in row['discovery']) for ref in key['anchors']),
                       'discovery_search_complete': row['discovery_search_complete']})
    save(output, {'receipt_sha256': digest(receipt_path.read_bytes()),
                  'source_packet_seal': receipt['source_packet_seal'], 'revision': receipt['revision'],
                  'counts': dict(Counter(row['outcome'] for row in scores)),
                  'families': {name: dict(outcomes) for name, outcomes in groups.items()},
                  'independent_historical_accuracy': 'NOT RUN',
                  'scope': 'Local authored anchors on authentic original publications. Semantic accuracy was not independently scored.',
                  'cases': scores})


def compare(before, after, output):
    left, right = read(before), read(after)
    if left['source_packet_seal'] != right['source_packet_seal']:
        raise ValueError('Comparison requires the same source packet seal')
    a, b = left['cases'], right['cases']
    if [row['id'] for row in a] != [row['id'] for row in b]:
        raise ValueError('Comparison requires identical ordered case coverage')
    correct = {'complete_with_all_anchors', 'expected_withhold'}
    changes = []
    for first, second in zip(a, b):
        if first['expected'] != second['expected']:
            raise ValueError('Scoring obligation changed')
        if first != second:
            changes.append({'id': first['id'], 'before': first['outcome'],
                            'after': second['outcome']})
    result = {'source_packet_seal': left['source_packet_seal'], 'before': left['counts'],
              'after': right['counts'], 'changes': changes,
              'new_false_support': [row['id'] for row in changes
                                    if row['before'] != 'supported_on_withhold' and row['after'] == 'supported_on_withhold'],
              'lost_correct_outcomes': [row['id'] for row in changes
                                        if row['before'] in correct and row['after'] not in correct]}
    save(output, result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    for name, paths in {'prepare': ('captures', 'spec', 'packet', 'custody'),
                        'run': ('packet', 'output', 'implementation'),
                        'score': ('packet', 'custody', 'receipt', 'output'),
                        'compare': ('before', 'after', 'output')}.items():
        command = commands.add_parser(name)
        for path in paths:
            command.add_argument('--' + path, required=True, type=Path)
    args = parser.parse_args()
    if args.command == 'prepare':
        prepare(args.captures, args.spec, args.packet, args.custody)
    elif args.command == 'run':
        run(args.packet, args.output, args.implementation)
    elif args.command == 'score':
        score(args.packet, args.custody, args.receipt, args.output)
    else:
        result = compare(args.before, args.after, args.output)
        return int(bool(result['new_false_support'] or result['lost_correct_outcomes']))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
