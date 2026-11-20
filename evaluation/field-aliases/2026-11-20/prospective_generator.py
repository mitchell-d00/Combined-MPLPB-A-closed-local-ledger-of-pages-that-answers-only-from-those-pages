"""New post-engine-freeze development chart; not blind or independent review.

Uses the existing challenge producer with explicit replacement charts. Only the
final augmented seal is published; no earlier benchmark or key is edited.
"""
import argparse
import json
from pathlib import Path
from tools import field_alias_challenge as C
from tools import dpercent as D

PAIRS = (
    ('Accession Date', 'date of accession', '1871-04-17'),
    ('Time Of Approval', 'approval time', '11:25'),
    ('Release Location', 'location of release', 'Annex 31'),
    ('Withdrawal Date', 'date of withdrawal', '1872-03-08'),
    ('Date Of Registration', 'registration date', '1873-08-21'),
    ('Location Of Deposit', 'deposit location', 'Shelf 82'),
    ('Filing Date', 'date of filing', '1874-09-14'),
    ('Current Status', 'present state', 'Awaiting a second inspection'),
    ('Phone Number', 'telephone no', '555-0196'),
)
FORMS = (
    'What is the {alias} for record {id}?',
    'Tell me the {alias} recorded on record {id}.',
    'In occurrence {id}, what does the {alias} field record?',
    'For record {id}, which {alias} is explicitly listed?',
    'According to entry {id}, what value is listed under {alias}?',
    'Read entry {id} and tell me its {alias}.',
)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--custodian', type=Path, required=True)
    p.add_argument('--cases', type=int, default=150)
    p.add_argument('--seed', type=int)
    a = p.parse_args()
    previous = C.PAIRS, C.FORMS
    try:
        C.PAIRS, C.FORMS = PAIRS, FORMS
        seal = C.prepare(a.out, a.custodian, a.cases, a.seed)
    finally:
        C.PAIRS, C.FORMS = previous
    protocol = D.read(a.out/'protocol.json')
    protocol.update(schema='field-alias-prospective-v1',
                    implementation_frozen_before_chart='2427d80',
                    question_chart=FORMS, source_chart=PAIRS,
                    tuning_after_execution=False,
                    unseen_scope='New source vocabulary and two new question structures after engine freeze; developer authored, not independent.')
    (a.out/'protocol.json').write_text(json.dumps(protocol, indent=2)+'\n')
    seal['public_files'] = D.files(a.out)
    seal['public_files'].pop('seal.json', None)
    seal['generator_dependencies'] = {'base_producer_sha256': seal['generator_sha256']}
    seal['generator_sha256'] = D.sha(Path(__file__).read_bytes())
    (a.out/'seal.json').write_text(json.dumps(seal, indent=2)+'\n')
    (a.custodian/'public-seal-copy.json').write_text(json.dumps(seal, indent=2)+'\n')
    D.verify(a.out, a.custodian)


if __name__ == '__main__': main()
