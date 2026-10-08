"""Frozen multi-domain evaluation: python -m mplpb_combined.evaluate MANIFEST.

Fixtures created with this module are developer tests, not independent evidence.
An external manifest can reference real corpora and separately authored probes.
"""
import argparse
import hashlib
import json
import tempfile
from pathlib import Path

from .baselines import LexicalIndex
from .killtest import Result, score, run_top1
from .ledger import Ledger, write
from .reader import RETURN, NOT_IN_CORPUS, answer, terms


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(manifest_path):
    path = Path(manifest_path).resolve()
    spec = json.loads(path.read_text(encoding='utf-8'))
    domains = []
    with tempfile.TemporaryDirectory(prefix='mplpb-eval-') as tmp:
        for number, domain in enumerate(spec['domains']):
            root = path.parent / domain['root'] if 'root' in domain else Path(tmp) / str(number)
            if 'root' not in domain:
                root.mkdir()
                for page in domain['pages']:
                    write(root, **page, when='2026-01-01T00:00Z')
            led = Ledger(root)
            probes_path = path.parent / domain['probes']
            if digest(probes_path) != domain['sha256']:
                raise ValueError('probe hash mismatch: ' + domain['name'])
            probes = json.loads(probes_path.read_text(encoding='utf-8'))['probes']
            ids = {r.path: r.id for r in led.records}
            pools = {'stripped': {r.path: r.text for r in led.records if r.kind != 'index'},
                     'current': {r.path: r.text for r in led.servable()
                                 if r.kind == 'page' and led.depth(r) <= 1}}
            indexes = {name: LexicalIndex(pages) for name, pages in pools.items()}
            arms = ['ledger'] + [method + '_' + pool for pool in pools
                                 for method in ('overlap', 'bm25', 'tfidf')]
            tally = {arm: {'correct': 0, 'wrong_return': 0, 'wrong_refusal': 0,
                           'returns': 0, 'correct_returns': 0} for arm in arms}
            rows = []
            for probe in probes:
                if probe['expect'] not in ('return', 'ambiguous', 'not_in_corpus'):
                    raise ValueError('invalid expected outcome')
                if probe['expect'] == RETURN:
                    targets = led.by_id.get(probe.get('doc'), [])
                    evidence = probe.get('evidence', '')
                    if len(targets) != 1 or not evidence or evidence not in targets[0].text:
                        raise ValueError('return label requires one document and a verbatim evidence span')
                elif not probe.get('rationale'):
                    raise ValueError('refusal label requires rationale')
                a = answer(root, probe['q'])
                got = {'ledger': Result(a.kind, a.record.id if a.record else None)}
                for pool, index in indexes.items():
                    prose = {key: terms(text) for key, text in pools[pool].items()}
                    got['overlap_' + pool] = run_top1(prose, ids, probe['q'])
                    for method in ('bm25', 'tfidf'):
                        key = index.top(probe['q'], method)
                        got[method + '_' + pool] = Result(RETURN if key else NOT_IN_CORPUS,
                                                        ids[key] if key else None)
                row = {'id': probe['id'], 'q': probe['q'], 'expect': probe['expect'],
                       'doc': probe.get('doc'), 'arms': {}}
                for arm, result in got.items():
                    outcome = score(probe['expect'], probe.get('doc'), result)
                    tally[arm][outcome] += 1
                    tally[arm]['returns'] += result.kind == RETURN
                    tally[arm]['correct_returns'] += outcome == 'correct' and result.kind == RETURN
                    row['arms'][arm] = {'kind': result.kind, 'doc': result.doc, 'score': outcome}
                rows.append(row)
            for stats in tally.values():
                stats['accuracy'] = stats['correct'] / len(probes) if probes else None
                stats['return_precision'] = stats['correct_returns'] / stats['returns'] if stats['returns'] else None
                stats['return_rate'] = stats['returns'] / len(probes) if probes else None
            by_outcome = {}
            for outcome in ('return', 'ambiguous', 'not_in_corpus'):
                selected = [row for row in rows if row['expect'] == outcome]
                by_outcome[outcome] = {'n': len(selected), 'arms': {
                    arm: {label: sum(row['arms'][arm]['score'] == label for row in selected)
                          for label in ('correct', 'wrong_return', 'wrong_refusal')}
                    for arm in arms}}
            domains.append({'name': domain['name'], 'n': len(probes), 'by_outcome': by_outcome,
                            'probe_sha256': digest(probes_path),
                            'corpus_hashes': {r.path: r.hash_actual for r in led.records},
                            'arms': tally, 'rows': rows})
    return {'manifest_sha256': digest(path), 'provenance': spec.get('provenance', {}),
            'independence_verified': False, 'domains': domains,
            'limitations': ['Authorship declarations are not independently verified.',
                            'Top-one baselines cannot produce ambiguity; compare per outcome.',
                            'No refusal thresholds were tuned on the evaluation probes.']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest')
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    result = json.dumps(run(args.manifest), indent=2, sort_keys=True) + '\n'
    if args.out:
        args.out.write_text(result, encoding='utf-8')
    else:
        print(result, end='')


if __name__ == '__main__':
    main()
