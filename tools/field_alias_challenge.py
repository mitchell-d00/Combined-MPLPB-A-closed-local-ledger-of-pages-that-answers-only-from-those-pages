"""Seal a new synthetic alias challenge; execute via the unchanged D% sandbox.

Authored development holdout, not independent or context-blind validation.
Some new question structures are intentionally outside current grammar.
"""
import argparse
from pathlib import Path
import secrets
from tools import dpercent as D

PAIRS = (
    ('Inspection Date', 'date of inspection', '1884-06-11'),
    ('Observation Time', 'time of observation', '09:30'),
    ('Loan Location', 'location of loan', 'North repository'),
    ('Telephone Number', 'phone number', '020-555-0171'),
    ('Postal Code', 'postcode', 'AB4 7XY'),
    ('Present Status', 'current state', 'Provisional; subject to review'),
    ('Date Of Expiration', 'expiration date', '1885-07-13'),
    ('Location Of Assembly', 'assembly location', 'West hall'),
    ('Time Of Reception', 'reception time', '15:40'),
)
FORMS = (
    'What is the {alias} for record {id}?',
    'Please show me the {alias} for record {id}.',
    'In record {id}, what does the {alias} field state?',
    'Record {id}: give the {alias}.',
    'For entry {id}, state its {alias}.',
    'Which value does {id} give under {alias}?',
)
FAMILIES = ('alias', 'alias', 'alias', 'exact', 'ambiguous', 'conflict',
            'quoted', 'conditional', 'restricted', 'withdrawn', 'corrupt',
            'missing_id', 'qualified_question', 'temporal_role', 'geographic_state')


def prepare(out, custodian, count=240, seed=None):
    out, custodian = Path(out).resolve(), Path(custodian).resolve()
    if type(count) is not int or not 1 <= count <= 4096:
        raise ValueError('Cases must be 1–4096')
    if (out == custodian or out in custodian.parents or custodian in out.parents
            or custodian == D.ROOT or D.ROOT in custodian.parents):
        raise ValueError('Keep custody disjoint and outside repository')
    seed = secrets.randbits(128) if seed is None else seed
    if type(seed) is not int or not 0 <= seed < 2**128:
        raise ValueError('Invalid seed')
    out.mkdir(parents=True, exist_ok=False)
    custodian.mkdir(parents=True, mode=0o700, exist_ok=False)
    dice = D.Dice(seed)
    schedule = dice.shuffle('family_schedule', [FAMILIES[i % len(FAMILIES)] for i in range(count)])
    keys = []; total = 0; files = 0
    for i, family in enumerate(schedule, 1):
        field, alias, value = dice.choose('field_language', PAIRS)
        form = dice.choose('question_structure', tuple(range(len(FORMS))))
        ending = dice.choose('line_ending', ('\n', '\r\n'))
        ident = f'LEAF-{73000+i}'
        body = f'Record-ID: {ident}\n{field}: {value}\nNote: Clerk wrote this entry — Zoë.'
        question = FORMS[form].format(alias=alias, id=ident)
        expected = 'answer' if family in {'alias', 'exact'} else 'refuse'
        if family == 'exact':
            question = FORMS[0].format(alias=field.lower(), id=ident)
        if family == 'ambiguous':
            field, alias, value = 'Telephone Number', 'telephone no', '020-555-0171'
            body = f'Record-ID: {ident}\nTelephone Number: {value}\nPhone Number: 020-555-0199'
            question = FORMS[0].format(alias=alias, id=ident)
        elif family == 'conflict':
            body += f'\n{field}: conflicting value'
        elif family == 'quoted':
            body = f'Record-ID: {ident}\nExample:\n```text\n{field}: {value}\n```'
        elif family == 'conditional':
            body = f'Record-ID: {ident}\nIf approved:\n{field}: {value}'
        elif family == 'missing_id':
            question = question.replace(ident, ident+'-ABSENT')
        elif family == 'qualified_question':
            question = FORMS[0].format(alias=alias, id=ident)[:-1]+' before the revision?'
        elif family == 'temporal_role':
            body = f'Record-ID: {ident}\nReceipt Date: 1884-08-12'
            question = FORMS[0].format(alias='sending date', id=ident)
        elif family == 'geographic_state':
            body = f'Record-ID: {ident}\nCurrent State: Maine'
            question = FORMS[0].format(alias='current status', id=ident)
        source = {'path': 'sources/leaf.txt', 'source_class': 'original'}
        if family == 'restricted': source['external'] = 'no'
        if family == 'withdrawn': source['retired'] = True
        if family == 'corrupt': source['corrupt'] = True
        raw = (body.replace('\n', ending)+'\n').encode()
        total += len(raw); files += 1
        folder = out/'packets'/f'DP{i:05d}'
        (folder/'sources').mkdir(parents=True)
        (folder/source['path']).write_bytes(raw)
        D.save(folder/'case.json', {'id': folder.name, 'question': question,
              'profile': 'external' if family == 'restricted' else 'internal',
              'sources': [source], 'budget': {'passages': 12, 'characters': 8000}})
        keys.append({'id': folder.name, 'family': 'holdout_'+family, 'expected': expected,
            'required_propositions': [], 'reference_sources': ['SOURCE-0001'] if expected == 'answer' else [],
            'source_facts': [], 'structural_expectations': {},
            'automatic_answer_matcher': 'literal_field_set_v1', 'required_field_quotes': [f'{field}: {value}'],
            'features': {'question_form': form, 'field': field, 'line_ending': 'LF' if ending=='\n' else 'CRLF', 'fence': 'none', 'source_count': 1}})
    D.save(custodian/'key.json', {'schema': 'field-alias-holdout-v1-key', 'cases': keys})
    (custodian/'key.json').chmod(0o600)
    D.save(custodian/'dice.json', {'seed': str(seed), 'rolls': dice.rolls})
    D.save(out/'protocol.json', {'schema': 'field-alias-holdout-v1', 'cases': count,
        'source_kind': 'New developer-authored synthetic materials, prepared before alias implementation',
        'independent_review': 'NOT RUN', 'context_blind': False,
        'unseen_scope': 'New source vocabulary and two new language structures relative to previous frozen benchmarks; not unseen to the developer.',
        'families': list(dict.fromkeys(FAMILIES)), 'limits': D.LIMITS,
        'no_language_acceptance_filter': True, 'negative_keys_do_not_require_a_specific_refusal_diagnostic': True})
    seal = {'public_files': D.files(out), 'key_sha256': D.sha((custodian/'key.json').read_bytes()),
        'dice_sha256': D.sha((custodian/'dice.json').read_bytes()),
        'generator_sha256': D.sha(Path(__file__).read_bytes()),
        'worker_sha256': D.sha((D.ROOT/'tools/dpercent_worker.py').read_bytes()),
        'seed_commitment': D.sha(str(seed).encode()), 'source_bytes': total, 'source_files': files}
    D.save(out/'seal.json', seal)
    D.save(custodian/'public-seal-copy.json', seal)
    return seal


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--custodian', type=Path, required=True)
    p.add_argument('--cases', type=int, default=240)
    p.add_argument('--seed', type=int)
    a = p.parse_args()
    prepare(a.out, a.custodian, a.cases, a.seed)


if __name__ == '__main__': main()
