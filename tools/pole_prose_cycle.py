"""Prepare and score the Tacitus, Douglass and Babbage Pole replays."""
import argparse
from collections import Counter
from html import escape
from pathlib import Path
import shutil
import sys
from tempfile import TemporaryDirectory

from tools import pole_authentic as A

PINS = ('FR-01', 'FR-04', 'FR-07', 'FR-10', 'FR-11', 'BT-01')
VARIANTS = {
    'FR-01': (
        'How did the Washington meeting venue change, and what meeting hours stayed the same?',
        'What changed about the Washington meeting location, and what hours did the correction retain?',
    ),
    'FR-04': (
        'What was the original Order No. 2222 compliance deadline, and what date did the correction and later notice give?',
        'Trace the original Order No. 2222 filing deadline, its correction, and the date reaffirmed by the later notice.',
    ),
    'FR-07': (
        'Which two instructions did the FEC correction amend, and did the March 1 effective date change?',
        'What two instructions did the FEC correction amend, and did the listed March 1 effective date change?',
    ),
    'FR-10': (
        'What did the January DHS notice report about the scope of the August error, and what was the intended scope?',
        'What part of paragraph (a) was replaced in August, and what part did DHS say it meant to correct?',
    ),
    'FR-11': (
        'What earlier applicability date did the January DHS correction reaffirm across the three publications?',
        'Which applicability date was preserved in the April rule, the August correction and January follow-up?',
    ),
    'BT-01': (
        'Which attribution does the B-Tests erratum withdraw, and what does it say about prior benchmark scores?',
        'What wording does the B-Tests correction withdraw, and which benchmark results does it say were unchanged?',
    ),
}


def prepare(spec_path, relations, captures, public, custody, template):
    spec = A.read(spec_path)
    expected = A.read(relations)
    public.mkdir()
    custody.mkdir(mode=0o700)
    for suite in ('tacitus', 'douglass'):
        cases = []
        local = {}
        for case in spec['cases']:
            if case['expected'] == 'withhold':
                cases.append(case)
                continue
            if case['id'] not in PINS:
                continue
            questions = (case['question'],) if suite == 'tacitus' else VARIANTS[case['id']]
            for n, question in enumerate(questions, 1):
                ident = case['id'] if suite == 'tacitus' else f"{case['id']}-{n}"
                cases.append(dict(case, id=ident, question=question))
                if case['id'] in expected:
                    local[ident] = expected[case['id']]
        case_spec = custody / (suite + '-spec.json')
        A.save(case_spec, dict(spec, cases=cases))
        A.prepare(captures, case_spec, public / suite, custody / suite)
        A.save(custody / suite / 'relations.json', local)
        A.save(public / suite / 'scoring-commitment.json',
               {'relations_sha256': A.digest((custody / suite / 'relations.json').read_bytes())})
        seal = A.read(public / suite / 'seal.json')
        seal['public_files'] = A.inventory(public / suite)
        for path in (public / suite / 'seal.json', custody / suite / 'seal-copy.json'):
            path.unlink()
            A.save(path, seal)
    shutil.copytree(template, public / 'babbage')
    A.save(public / 'babbage' / 'seal.json', {'public_files': A.inventory(public / 'babbage')})


def score(packet, custody, receipt_path, output):
    with TemporaryDirectory() as tmp:
        anchors_path = Path(tmp) / 'anchored.json'
        A.score(packet, custody, receipt_path, anchors_path)
        anchors = A.read(anchors_path)
    local = custody / 'relations.json'
    if A.digest(local.read_bytes()) != A.read(packet / 'scoring-commitment.json')['relations_sha256']:
        raise ValueError('Typed reference changed')
    expected = A.read(local)
    receipt = A.read(receipt_path)
    native = {r['id']: r['answer'] for r in receipt['cases']}
    key = {r['id']: r for r in A.read(custody / 'key.json')}
    counts = Counter()
    cases = []
    for row in anchors['cases']:
        ident = row['id']
        answer = native[ident]
        if row['expected'] == 'withhold':
            result = 'unsupported_bridge' if answer['answer_supported'] else 'control_withheld'
        elif answer['answer_supported']:
            match = expected.get(ident)
            typed = match and any(all(c.get('proposition', {}).get(k) == v for k, v in match.items())
                                  for c in answer['claims'])
            if typed and row['outcome'] == 'complete_with_all_anchors':
                result = 'bridge_formed'
            else:
                # A positive without a typed adjudication stays unverified.
                result = 'unverified_supported_bridge'
        else:
            result = 'partial' if answer['kind'] == 'partial_answer' else 'miss'
        counts[result] += 1
        if row['expected'] == 'answer' and row['complete_discovery_anchor_coverage']:
            counts['all_discovery_anchors'] += 1
        cases.append({'id': ident, 'family': key[ident]['family'], 'result': result,
                      'discovery_anchors': row['complete_discovery_anchor_coverage'],
                      'kind': row['kind'], 'diagnostic': row['diagnostic']})
    A.save(output, {'pin': receipt['revision'], 'packet_seal': receipt['source_packet_seal'],
                    'raw_sha256': A.digest(receipt_path.read_bytes()), 'counts': dict(counts), 'cases': cases})


def babbage(packet, output, implementation):
    sys.path.insert(0, str(implementation))
    from mplpb_answers.pipeline import answer_query
    from mplpb_combined.ledger import write, withdraw
    from mplpb_combined.reader import PROFILES
    from mplpb_work.sorter_v2 import sort_directory

    A.seal_for(packet)
    results = {}
    for folder in sorted((packet / 'sorter').iterdir()):
        graph = sort_directory(folder, 'compare')
        selected = [n for n in graph['nodes'] if n['kind'] == 'phrase_key'
                    and n['value'] == 'fresh sailors prepared narrow']
        results[folder.name] = {'complete': graph['complete'], 'limits': graph['limits_or_exclusions'],
                                'slots': len(selected), 'occurrences': len({n['occurrence'] for n in selected})}
    if (packet / 'linked').is_dir():
        graph = sort_directory(packet / 'linked', 'compare')
        witnesses = [n for n in graph['nodes'] if n['kind'] == 'phrase_key'
                     and n['value'] == 'fresh sailors prepared narrow']
        results['same_records_as_proof'] = {
            'slots': len(witnesses), 'occurrences': len({n['occurrence'] for n in witnesses}),
            'limits': graph['limits_or_exclusions'],
        }
    question = (packet / 'question.txt').read_text().strip()
    for name in ('eligible', 'external_denial', 'withdrawn', 'passage_cap', 'scan_cap'):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            for ident, filename in [('DOC-OLD', 'earlier.txt'), ('DOC-NEW', 'correction.txt')]:
                base = packet / 'linked' if (packet / 'linked').is_dir() else packet
                content = (base / filename).read_text()
                write(root, doc_id=ident, title=ident, scope='publication', body_html='<pre>' + escape(content) + '</pre>',
                      external='no' if name == 'external_denial' and ident == 'DOC-OLD' else 'yes')
            if name == 'withdrawn':
                withdraw(root, 'DOC-OLD')
            if name == 'scan_cap':
                for number in range(65):
                    ident = f'OTHER-{number:02d}'
                    write(root, doc_id=ident, title=ident, scope='publication', body_html='<p>Other file.</p>')
            answer = answer_query(root, question, PROFILES['external' if name == 'external_denial' else 'internal'],
                                  max_passages=1 if name == 'passage_cap' else 12).contract
            results[name] = {'answer_supported': answer['answer_supported'], 'diagnostic': answer['diagnostic']['code'],
                             'sources': sorted({c['source_id'] for claim in answer['claims'] for c in claim['citations']})}
    A.save(output, results)



def douglass_sorter(packet, output, implementation):
    sys.path.insert(0, str(implementation))
    from mplpb_answers.body_text import body_text
    from mplpb_work.sorter_v2 import sort_directory

    A.seal_for(packet)
    sources = {s['id']: s for s in A.read(packet / 'sources.json')}
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        # The sorter sees read-only projections. Proof still uses eligible originals.
        venue_case = next(r for r in A.read(packet / 'questions.json') if r['id'] == 'FR-01-1')
        for ident in venue_case['sources']:
            original = sources[ident]
            html = A.original_body((packet / original['path']).read_bytes(), original)
            (root / (ident + '.txt')).write_text(body_text(html), encoding='utf-8')
        graph = sort_directory(root, 'compare')
    names = {}
    for node in graph['nodes']:
        if node['kind'] == 'phrase_key':
            names.setdefault(node['value'], set()).add(node['occurrence'])
    A.save(output, {'source_packet_seal': A.digest((packet / 'seal.json').read_bytes()),
                    'record_occurrences': sum(node['kind'] == 'source_occurrence' for node in graph['nodes']),
                    'phrase_groups_with_both_records': sum(len(records) > 1 for records in names.values()),
                    'complete': graph['complete'], 'limits': graph['limits_or_exclusions'],
                    'proof_authority': False})

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    for command, names in {
        'prepare': ('spec', 'relations', 'captures', 'public', 'custody', 'template'),
        'score': ('packet', 'custody', 'receipt', 'output'),
        'babbage': ('packet', 'output', 'implementation'),
        'douglass-sorter': ('packet', 'output', 'implementation'),
    }.items():
        child = sub.add_parser(command)
        for name in names:
            child.add_argument('--' + name, type=Path, required=True)
    args = parser.parse_args()
    if args.command == 'prepare':
        prepare(args.spec, args.relations, args.captures, args.public, args.custody, args.template)
    elif args.command == 'babbage':
        babbage(args.packet, args.output, args.implementation)
    elif args.command == 'douglass-sorter':
        douglass_sorter(args.packet, args.output, args.implementation)
    else:
        score(args.packet, args.custody, args.receipt, args.output)


if __name__ == '__main__':
    main()
