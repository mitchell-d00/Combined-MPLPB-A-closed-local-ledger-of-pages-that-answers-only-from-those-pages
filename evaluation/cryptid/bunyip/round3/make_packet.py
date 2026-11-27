"""Recreate the authorized synthetic diagnostic packet. Evaluator use only."""
import argparse
import hashlib
import json
from pathlib import Path

from tools.cryptid_trial_v5 import digest, save, sha

ROOT = Path(__file__).resolve().parents[4]
STUDY = Path('evaluation/cryptid/bunyip/round3')
BUDGET = dict(records=8, scan_characters=200000, units=1000, passages=12,
              characters=8000, cpu_seconds=30, wall_seconds=45, result_bytes=8388608)
HARNESS = (
    'tools/cryptid_trial_v5.py', 'tools/cryptid_adapter_v5.py',
    'tools/cryptid_worker_v5.py', 'tools/pole_worker.py', 'tools/study_sandbox.py',
    'tools/cryptid_claim_score_v5.py', 'evaluation/egyptian-gods/attribution-scope/readout.py',
    str(STUDY/'make_packet.py'), str(STUDY/'score.py'), str(STUDY/'run.py'),
    str(STUDY/'SCOPE.md'), str(STUDY/'readers.json'), str(STUDY/'preserve.py'),
    '.github/workflows/bunyip-round3.yml',
)


def ledger_source(number, paragraphs):
    return dict(id=f'SYN-{number}', title='Synthetic documentary record', origin='machine',
                external='yes', when='2026-11-27T00:00Z',
                body_html=''.join(f'<p>{p}</p>' for p in paragraphs))


def claim(paragraphs, *, text=None, proposition=None):
    return dict(quotes=paragraphs, text=text, proposition=proposition or {})


def pairs():
    place = 'Name: Feldwick Bicycle Kitchen'
    location = 'Location: Courtyard pavilion'
    opening = 'Opening time: 07:25'
    other_place = ('Name: Willow Print Cooperative', 'Location: Annex gallery')
    report = 'Dora Flint reported that Celia Reeve wrote the repair worksheet.'
    recorder = 'Report by Ezra Beck.'
    denial = 'Nora Kemp stated that Mina Tate did not write the inventory index.'
    condition = 'If the water clears'
    instruction = f'{condition}, Ada Firth instructed the bench team to reopen the wash station.'
    owner = 'Name: Ridley Lantern Workshop'
    option_one = 'Location: River stair'
    option_two = 'Location: Plaza entry'
    under = 'Location: Plaza entry or side gate'
    return (
        ('imperative-location', ('Tell me where Feldwick Bicycle Kitchen is.', ((place, location), other_place),
         'complete', [claim((place, location), text=location)], []),
         ('Tell me where Feldwick Bicycle Kitchen is.', (other_place,),
         'withhold', [], [])),
        ('ordinary-compound', ('For Feldwick Bicycle Kitchen, give its opening time and location.',
         ((place, opening, location), other_place), 'complete',
         [claim((place, opening), text=opening), claim((place, location), text=location)], []),
         ('For Feldwick Bicycle Kitchen, give its opening time and location.',
         ((place, opening), other_place), 'partial', [claim((place, opening), text=opening)], ['location'])),
        ('attribution', ('What did Dora Flint report that Celia Reeve wrote, according to the record?',
         ((recorder, report),), 'complete', [claim((recorder, report), proposition={
         'reporter': 'Dora Flint', 'author': 'Celia Reeve', 'object': 'the repair worksheet',
         'source_writer_or_unknown': 'Ezra Beck', 'actual_authorship_established': False})], []),
         ('What did Ezra Beck report that Celia Reeve wrote, according to the record?',
         ((recorder, report),), 'withhold', [], [])),
        ('negation', ('Did Nora Kemp state that Mina Tate did not write the inventory index?',
         ((denial,),), 'complete', [claim((denial,), proposition={
         'reporter': 'Nora Kemp', 'author': 'Mina Tate', 'object': 'the inventory index',
         'outer_negative': False, 'embedded_content_negative': True,
         'content_asserted_by_reporter': True, 'actual_authorship_established': False})], []),
         ('Did Nora Kemp not state that Mina Tate wrote the inventory index?',
         ((denial,),), 'withhold', [], [])),
        ('condition-modality', ('If the water clears, what did Ada Firth instruct the bench team to do?',
         ((instruction,),), 'complete', [claim((instruction,), proposition={
         'actor': 'Ada Firth', 'task_actor': 'the bench team', 'modality': 'instruction',
         'conditions': [condition], 'completion_asserted_by_source': False,
         'execution_independently_verified': False})], []),
         ('If the water clears, did the bench team reopen the wash station?',
         ((instruction,),), 'withhold', [], [])),
        ('competing-evidence', ('Where is Ridley Lantern Workshop.',
         ((owner, option_one), ('Name: Quill Lantern Shop', option_two)), 'complete',
         [claim((owner, option_one), text=option_one)], []),
         ('Where is Ridley Lantern Workshop.', ((owner, option_one), (owner, under)), 'withhold', [], [])),
    )


def bind(expected, sources, paragraphs):
    witnesses = []
    for quote in expected.pop('quotes'):
        matches = []
        for source, lines in zip(sources, paragraphs, strict=True):
            body = '\n'.join(lines)
            html = source['body_html'].encode()
            if quote in lines:
                start = body.index(quote)
                offset = html.index(quote.encode())
                matches.append(dict(source_id=source['id'], quote=quote, start=start,
                                    end=start+len(quote), start_byte=offset,
                                    end_byte=offset+len(quote.encode()),
                                    body_html_sha256=hashlib.sha256(html).hexdigest()))
        assert len(matches) == 1, quote
        witnesses.append(matches[0])
    return dict(expected, witnesses=witnesses)


def prepare(root, key_path):
    home = root/STUDY
    registry, key = [], {}
    for index, (family, a, b) in enumerate(pairs(), 1):
        for side, (question, paragraphs, decision, claims, missing) in zip('AB', (a, b), strict=True):
            ident = f'BUNYIP-R3-D{index:02d}-{side}'
            relative = STUDY/'diagnostic'/'inputs'/ident
            sources = [ledger_source(n, lines) for n, lines in enumerate(paragraphs, 1)]
            case = dict(id=ident, adapter_mode='documentary', question=question, sources=sources,
                        profile='internal', budget=BUDGET)
            save(root/relative/'case.json', case)
            registry.append(dict(id=ident, family=family, packet=str(relative),
                                 files={'case.json': sha(root/relative/'case.json')},
                                 semantic_input_hash=digest(case)))
            key[ident] = dict(decision=decision, claims=[bind(c, sources, paragraphs) for c in claims],
                              missing=missing)
    path = home/'diagnostic'/'registry.json'
    save(path, dict(schema='cryptid-case-registry-v1', family='Bunyip Round 3',
                    exposure='same-operator prospective diagnostic, public synthetic inputs', cases=registry))
    save(key_path, key)
    save(path.with_name('freeze.json'), dict(registry_sha256=sha(path), key_sha256=sha(key_path),
        harness={name: sha(root/name) for name in HARNESS}, public_raw_output=True,
        cases=len(registry), independence='NOT_RUN'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--key', type=Path, required=True)
    args = parser.parse_args()
    prepare(args.root.resolve(), args.key)
