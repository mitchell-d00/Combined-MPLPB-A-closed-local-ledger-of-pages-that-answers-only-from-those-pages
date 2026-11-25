"""Freeze and replay the BT-Erratum and expanded Polybius-Prose sets."""
import argparse
from collections import Counter
from pathlib import Path
import shutil

from test_tools import four_score_twenty as historical
from tools import pole_authentic as A, pole_open_items as P, pole_remaining as R


def prepare(spec, captures, retained, public, custody, typed_reference):
    if public.exists() or custody.exists():
        raise FileExistsError('Use new packet and custody directories')
    public.mkdir()
    custody.mkdir(mode=0o700)
    original = A.read(spec)
    questions = {r['id']: r for r in original['cases']}
    base = questions['BT-01']
    cases = [base, questions['BT-03']]
    for ident, sources, question, rationale in (
        ('BT-C01', ['BTESTS-ERR'], base['question'], 'The earlier version is missing.'),
        ('BT-C02', ['BTESTS-OLD'], base['question'], 'The erratum is missing.'),
        ('BT-C03', base['sources'], 'According to the Other-Probe erratum, what attribution was withdrawn and what happened to the earlier benchmark scores?',
         'Neither capture belongs to that repository.'),
        ('BT-C04', base['sources'], 'According to the B-Tests erratum, who actually ran M6 and which earlier benchmark scores changed?',
         'Neither the withdrawn claim nor the verification limit establishes an execution or score change.'),
    ):
        cases.append(dict(base, id=ident, sources=sources, question=question,
                          expected='withhold', anchors=[], local_reference=rationale))
    sources = [dict(row, retain_capture_manifest=True) for row in original['sources']
               if row['id'] in base['sources']]
    authored = custody / 'erratum-spec.json'
    A.save(authored, dict(original, sources=sources, cases=cases))
    bt = public / 'bt-erratum'
    bt_key = custody / 'bt-erratum'
    A.prepare(captures, authored, bt, bt_key)
    private_typed = bt_key / 'typed.json'
    shutil.copyfile(typed_reference, private_typed)
    private_typed.chmod(0o600)
    seal = A.read(bt / 'seal.json')
    A.save(bt / 'typed-commitment.json', {'sha256': A.digest(private_typed.read_bytes())})
    seal['public_files'] = A.inventory(bt)
    for path in (bt / 'seal.json', bt_key / 'seal-copy.json'):
        path.unlink()
        A.save(path, seal)

    previous = retained / 'polybius'
    A.seal_for(previous)
    shutil.copytree(previous, public / 'polybius-retained')
    historical.verify_inputs(P.SOLO)
    added = public / 'polybius-added'
    shutil.copytree(P.SOLO / 'inputs', added / 'inputs')
    positive = {'P02-2', 'P03-2', 'P04-2', 'P05-2'}
    negative = {'P02-4', 'P04-4', 'P05-4', 'P06-4'}
    ids = positive | negative
    refs = [r for r in A.read(P.SOLO / 'custody/key.json') if r['id'] in ids]
    old = A.read(added / 'inputs/questions.json')
    selected = [q for q in old if q['id'] in ids]
    if ({r['id'] for r in refs} != ids or {q['id'] for q in selected} != ids
            or {r['id'] for r in refs if r['family'] == 'missing'} != negative):
        raise ValueError('Expected the frozen relation and missing-evidence families')
    (added / 'inputs/questions.json').unlink()
    A.save(added / 'inputs/questions.json', selected)
    key = custody / 'polybius-added'
    key.mkdir(mode=0o700)
    A.save(key / 'key.json', refs)
    (key / 'key.json').chmod(0o600)
    A.save(added / 'seal.json', {'public_files': A.inventory(added),
                                'key_sha256': A.digest((key / 'key.json').read_bytes())})
    A.seal_for(retained / 'lovelace-limit')
    shutil.copytree(retained / 'lovelace-limit', public / 'scan-phrase')


def score_erratum(packet, custody, receipt, output):
    expected = A.read(custody / 'typed.json')
    if A.digest((custody / 'typed.json').read_bytes()) != A.read(packet / 'typed-commitment.json')['sha256']:
        raise ValueError('Typed reference changed')
    from tempfile import TemporaryDirectory
    with TemporaryDirectory() as tmp:
        scored = Path(tmp) / 'anchors.json'
        A.score(packet, custody, receipt, scored)
        score = A.read(scored)
    native = {r['id']:r['answer'] for r in A.read(receipt)['cases']}
    totals = Counter()
    for row in score['cases']:
        ident = row['id']
        answer = native[ident]
        if answer['answer_supported'] and row['expected'] == 'answer':
            match = expected.get(ident)
            if not match or not any(all(claim['proposition'].get(k) == v for k, v in match.items())
                                for claim in answer['claims']):
                row['outcome'] = 'unverified_supported_bridge'
        totals[row['outcome']] += 1
    score['counts'] = dict(totals)
    A.save(output, score)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest='command', required=True)
    for name, fields in {
        'prepare': ('spec', 'captures', 'retained', 'public', 'custody', 'typed-reference'),
        'score-erratum': ('packet', 'custody', 'receipt', 'output'),
    }.items():
        command = subs.add_parser(name)
        for field in fields:
            command.add_argument('--' + field, type=Path, required=True)
    args = vars(parser.parse_args())
    command = args.pop('command')
    {'prepare': prepare, 'score-erratum': score_erratum}[command](**args)


if __name__ == '__main__':
    main()
