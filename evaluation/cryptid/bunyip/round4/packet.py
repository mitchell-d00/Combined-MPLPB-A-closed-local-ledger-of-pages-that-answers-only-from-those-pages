"""Freeze authorized synthetic attribution inputs and an evaluator-only key."""
import argparse
import hashlib
from pathlib import Path

from tools.cryptid_trial_v5 import digest, save, sha

HOME = Path(__file__).resolve().parent
ROOT = HOME.parents[3]
BUDGET = dict(records=8, scan_characters=200000, units=1000, passages=12,
              characters=8000, cpu_seconds=30, wall_seconds=45, result_bytes=8388608)
HARNESS = (
    'tools/cryptid_trial_v5.py', 'tools/cryptid_adapter_v5.py',
    'tools/cryptid_worker_v5.py', 'tools/pole_worker.py', 'tools/study_sandbox.py',
    'tools/cryptid_claim_score_v5.py', 'evaluation/egyptian-gods/attribution-scope/readout.py',
    'evaluation/cryptid/bunyip/round4/packet.py', 'evaluation/cryptid/bunyip/round4/score.py',
    'evaluation/cryptid/bunyip/round4/run.py', 'evaluation/cryptid/bunyip/round4/SCOPE.md',
    '.github/workflows/bunyip-round4.yml',
)
BASE = {'commit': '39df3d14ebf4bb01c056e8b04b8da65c7303fa61',
        'zip_sha256': '464695edec5a3c44d68142dbb985e43c671da4f66eeb9264bd37ae4f55fced6d'}


def fixtures(phase):
    if phase == 'diagnostic':
        reporter, author, writer = 'Iris Brook', 'Milo Dean', 'Rosa Field'
        obj, other = 'the garden roster', 'the tool schedule'
        ordinary = f'What did {reporter} report that {author} wrote'
        generic = ordinary + ', according to the record?'
    else:
        reporter, author, writer = 'Nadia Moss', 'Lena Finch', 'Otis Clark'
        obj, other = 'the workshop bulletin', 'the exhibit checklist'
        ordinary = f'Which document did {reporter} say {author} wrote'
        generic = ordinary + ', according to this source.'
    source = (f'Report by {writer}.', f'{reporter} reported that {author} wrote {obj}.')
    competing = (f'Report by {writer}.', f'{reporter} reported that {author} wrote {other}.')
    denial = ('Report by Vera Glen.', f'{reporter} reported that {author} did not write {obj}.')
    named = (f'Report by {reporter}.', source[1])
    wrong = generic.replace(reporter, writer)
    proof = 'reported_object_unresolved'

    def claim(number, label, record, *, negative=False):
        return (number, record, dict(reporter=reporter, author=author, object=obj,
            source_writer_or_unknown=label, outer_negative=False,
            embedded_content_negative=negative, completion_established=False,
            historical_truth_independently_verified=False, actual_authorship_established=False,
            source_voice='source_reports_named_speaker'))

    yield 'bare-positive', ordinary+'?', (source,), 'complete', [claim(1, writer, source)], None
    yield 'generic-positive', generic, (source,), 'complete', [claim(1, writer, source)], None
    yield 'generic-wrong-reporter', wrong, (source,), 'withhold', [], proof
    yield 'bare-wrong-reporter', ordinary.replace(reporter, writer)+'?', (source,), 'withhold', [], proof
    yield 'named-positive', ordinary+f', according to {reporter}?', (named,), 'complete', [claim(1, reporter, named)], None
    yield 'named-wrong-source', ordinary+f', according to {writer}?', (named,), 'withhold', [], None
    yield 'generic-competing-objects', generic, (source, competing), 'withhold', [], proof
    conflict = f'What does {reporter} report about whether {author} wrote {obj}?'
    # The explicit object path uses the canonical report clause as its witness.
    yield 'opposed-content', conflict, ((source[1],), (denial[1],)), 'conflict', [
        claim(1, None, (source[1],)), claim(2, None, (denial[1],), negative=True)], 'conflicting_reported_content'


def make(phase, key_path):
    folder = HOME/phase
    registry, key = [], {}
    for i, (family, question, records, decision, allowed, proof) in enumerate(fixtures(phase), 1):
        ident = f'BUNYIP-R4-{phase[0].upper()}{i:02d}'
        sources = [dict(id=f'SYN-{i}', title='Synthetic documentary record', origin='machine',
                        external='yes', when='2026-11-27T00:00Z',
                        body_html=''.join(f'<p>{line}</p>' for line in record))
                   for i, record in enumerate(records, 1)]
        claims = []
        for n, lines, proposition in allowed:
            source = sources[n-1]
            body = '\n'.join(lines)
            html = source['body_html'].encode()
            spans = []
            for line in lines:
                lo, byte = body.index(line), html.index(line.encode())
                spans.append(dict(source_id=source['id'], quote=line, start=lo,
                                  end=lo+len(line), start_byte=byte, end_byte=byte+len(line.encode()),
                                  body_html_sha256=hashlib.sha256(html).hexdigest()))
            claims.append(dict(witnesses=spans, proposition=proposition))
        path = folder/'inputs'/ident/'case.json'
        case = dict(id=ident, question=question, adapter_mode='documentary',
                    profile='internal', sources=sources, budget=BUDGET)
        save(path, case)
        registry.append(dict(id=ident, family=family, packet=str(path.parent.relative_to(ROOT)),
                             files={'case.json': sha(path)}, semantic_input_hash=digest(case)))
        key[ident] = dict(decision=decision, claims=claims, proof_diagnostic=proof)
    path = folder/'registry.json'
    save(path, dict(schema='cryptid-case-registry-v1', family='Bunyip Round 4',
                    exposure='same-operator synthetic authoring and scoring, evaluator key outside worker',
                    cases=registry))
    save(key_path, key)
    save(folder/'freeze.json', dict(registry_sha256=sha(path), key_sha256=sha(key_path),
         baseline=BASE, harness={name: sha(ROOT/name) for name in HARNESS},
         public_raw_output=True, independence='NOT_RUN'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('phase', choices=('diagnostic','fresh'))
    parser.add_argument('--key', required=True, type=Path)
    args = parser.parse_args()
    make(args.phase, args.key)
