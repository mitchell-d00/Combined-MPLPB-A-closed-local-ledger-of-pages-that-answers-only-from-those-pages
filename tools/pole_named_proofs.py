"""Seeded Pole checks for named-source correction and linked documentary chains."""
import argparse
from pathlib import Path

from tools import dpercent as D, pole


def correction(dice, variant, variant_number):
    old, new, site, other = dice.choose('archival quantities', (
        ('six barrels', 'four barrels', 'east quay', 'west quay'),
        ('eight cartons', 'three cartons', 'upper depot', 'lower depot'),
        ('seven bundles', 'five bundles', 'north wharf', 'south wharf'),
    ))
    field, retained = dice.choose('declared fields', (
        ('Cargo Count', 'Destination'), ('Load Total', 'Landing Place'), ('Bundle Count', 'Depot Name')
    ))
    target = 'SOURCE-0001' if variant != 'wrong_target' else 'OTHER-1'
    final_site = other if variant == 'changed_retention' else site
    tail = ' if authorized' if variant == 'conditional' else ''
    question = 'What did source SOURCE-0002 change in source SOURCE-0001, and what did it retain?'
    if variant_number % 2:
        question = 'In source SOURCE-0002, what was corrected in source SOURCE-0001 and what remained unchanged?'
    lhs = f'{field}: {old}\n{retained}: {site}'
    rhs = f'Correction to source {target}: {field} should read {new}. {retained} remains {final_site}{tail}.'
    key = {'relation': 'documentary_partial_correction', 'previous_value': old,
           'replacement_value': new, 'retained_value': site}
    return question, (lhs, rhs), key


def chain(dice, variant, variant_number):
    requester, sender, reporter, obj, place = dice.choose('action actors and destination', (
        ('Ada Moss', 'Jan Ash', 'Ina Bell', 'the tide chart', 'the lower quay'),
        ('Rita Gale', 'Ted Ford', 'Uma Dean', 'the port ledger', 'the west depot'),
        ('Eva Park', 'Ian Hall', 'Lea Holt', 'the grain list', 'the north wharf'),
    ))
    target = 'SOURCE-0002' if variant != 'wrong_target' else 'OTHER-2'
    received = 'the wrong ledger' if variant == 'wrong_object' else obj
    question = 'Trace the request, dispatch and reported receipt in sources SOURCE-0001, SOURCE-0002 and SOURCE-0003.'
    if variant_number % 2:
        question = 'What request, dispatch and reported receipt do sources SOURCE-0001, SOURCE-0002 and SOURCE-0003 explicitly link?'
    a = f'{requester} requested that {sender} send {obj} to {place}.'
    b = f'In response to request source SOURCE-0001, {sender} sent {obj} to {place}.'
    if variant == 'conditional':
        b = 'If authorized, ' + b
    c = f'Referring to dispatch source {target}, {reporter} reported receiving {received} at {place} from {sender}.'
    key = {'relation': 'documentary_request_dispatch_receipt', 'sender': sender,
           'object': obj, 'destination': place, 'reported_by': reporter}
    return question, (a, b, c), key


def prepare(packets, custody, seed):
    packets, custody = pole.paths_separate(packets, custody)
    if packets.exists() or custody.exists():
        raise FileExistsError('Use new output directories')
    packets.mkdir(parents=True)
    custody.mkdir(parents=True, mode=0o700)
    dice = D.Dice(seed)
    cases, keys = {}, []
    families = [
        ('named_partial_correction', correction, ('wrong_target', 'changed_retention', 'conditional')),
        ('named_dispatch_chain', chain, ('wrong_target', 'wrong_object', 'conditional')),
    ]
    for family, material, negatives in families:
        for n, variant in enumerate(dice.shuffle(family, ('unqualified',) * 6 + negatives * 2), 1):
            number = len(keys) + 1
            ident = f'DOCUMENTARY-{seed}-{number:03d}'
            question, bodies, proposition = material(dice, variant, n)
            folder = packets / 'packets' / ident
            sources = []
            for index, body in enumerate(bodies, 1):
                source = f'sources/witness-{index:02d}.txt'
                path = folder / source
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(body + '\n', encoding='utf-8')
                sources.append({'path': source, 'source_class': 'original'})
            positive = variant == 'unqualified'
            keys.append({'id': ident, 'family': family, 'expected': 'answer' if positive else 'refuse',
                         'automatic_answer_matcher': 'typed_proposition_v1',
                         'required_propositions': [proposition] if positive else [], 'source_facts': [],
                         'reference_sources': [f'SOURCE-{i:04d}' for i in range(1, len(bodies) + 1)] if positive else [],
                         'structural_expectations': {}, 'features': {'contrast': variant}})
            D.save(folder / 'case.json', {'id': ident, 'question': question, 'sources': sources,
                                          'profile': 'internal', 'budget': {'passages': 12, 'characters': 8000}})
            cases[ident] = {'level': 'hard', 'cohort': 'fresh'}
    D.save(packets / 'protocol.json', {'schema': pole.SCHEMA, 'cases': cases})
    D.save(custody / 'key.json', {'schema': pole.SCHEMA, 'cases': keys})
    D.save(custody / 'dice.json', {'seed': seed, 'rolls': dice.rolls})
    for name in ('key.json', 'dice.json'):
        (custody / name).chmod(0o600)
    seal = {'public_files': D.files(packets),
            'key_sha256': D.sha((custody / 'key.json').read_bytes()),
            'dice_sha256': D.sha((custody / 'dice.json').read_bytes()),
            'generator_sha256': D.sha(Path(__file__).read_bytes())}
    D.save(packets / 'seal.json', seal)
    D.save(custody / 'seal-copy.json', seal)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--packets', required=True, type=Path)
    ap.add_argument('--custody', required=True, type=Path)
    ap.add_argument('--seed', required=True, type=int)
    options = ap.parse_args()
    prepare(options.packets, options.custody, options.seed)
