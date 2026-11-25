"""Check native proposition admission for the existing FRUS comparison packet."""
import argparse
from pathlib import Path
from tempfile import TemporaryDirectory

from mplpb_answers import documentary, documentary_verify as kernel
from mplpb_answers.passages import PassageIndex
from mplpb_combined.ledger import write
from mplpb_combined.reader import PROFILES
from tools import pole_authentic as A
from tools.pole_focus_extend import frus_rendered


def probe(packet, question, witnesses, sources, work):
    records = {}
    for ident in question['sources']:
        source = sources[ident]
        raw = (packet / source['path']).read_bytes()
        records[ident] = write(work, doc_id=ident, title=ident, scope='public documentary originals',
                               origin='machine', body_html=frus_rendered(raw, source),
                               external='yes', when='2026-11-24T00:00Z')
    index = PassageIndex(work, question['question'], PROFILES['internal'])
    if {record.path for record in index.records} != {record.path for record in records.values()}:
        raise ValueError('Source eligibility differs from the frozen pair')
    budget = question['budget']
    discovery = index.retrieve([question['question']], budget['passages'], budget['characters'])
    native = documentary.propose(index, discovery['passages'])
    proposed, units = [], []
    for witness in witnesses:
        record = records[witness['id']]
        if (record.path, record.hash_actual) != (witness['ledger_path'], witness['ledger_sha256']):
            raise ValueError('The native proof input differs from the frozen witnessed appearance')
        body = kernel.body_text(record.body_html)
        lo, hi = witness['projected_character_span']
        enclosing = [(a, b, q) for a, b, q in kernel.units(body) if a <= lo < hi <= b]
        if len(enclosing) != 1:
            raise ValueError('A frozen anchor has no unique enclosing native unit')
        start, stop, text = enclosing[0]
        if stop - start > 2200:
            raise ValueError('A frozen unit exceeds the current native proposal span limit')
        kinds = ('action_statement', 'relationship_statement')
        proposed.extend({'kind': kind, 'source_id': record.id, 'path': record.path,
                         'hash': record.hash_actual, 'start': start, 'end': stop, 'quote': text}
                        for kind in kinds)
        units.append({
            'source_id': record.id,
            'enclosing_unit_span': [start, stop],
            'native_action_shape': (kernel.action_assertion(text) or {}).get('relation'),
            'native_relationship_shape': (kernel.relationship_assertion(text) or {}).get('relation'),
            'letter_instruction_proposed': any(p['kind'] == 'letter_instruction'
                                               and p['source_id'] == record.id for p in native),
            'probe_kinds': list(kinds),
        })
    if len(proposed) > budget['passages'] or sum(len(p['quote']) for p in proposed) > budget['characters']:
        raise ValueError('Kernel proposals exceed the frozen output budgets')
    result = kernel.check(index, proposed)
    if result['status'] != 'checked':
        raise ValueError('Native checker could not finish its bounded reread')
    if result['proofs'] or any(unit['letter_instruction_proposed'] for unit in units):
        raise ValueError('A potential certificate requires explicit attribution review before admission')
    return {
        'units': units,
        'proposals': len(proposed),
        'rejected': result['rejected'],
        'certified_required_propositions': 0,
        'scan_complete': result['scan_complete'],
        'examined_characters': result['examined_characters'],
        'examined_units': result['examined_units'],
        'limits_reached': result['limits_reached'],
        'limits': result['limits'],
    }


def audit(packet, custody, rule, freeze, previous, receipt, output):
    seal = A.seal_for(packet)
    held = A.read(freeze)
    commits = {
        'packet_seal_sha256': A.digest((packet / 'seal.json').read_bytes()),
        'custody_key_sha256': A.digest((custody / 'key.json').read_bytes()),
        'candidate_rule_sha256': A.digest(rule.read_bytes()),
        'prior_evaluation_sha256': A.digest(previous.read_bytes()),
    }
    if any(held[key] != value for key, value in commits.items()) or seal['key_sha256'] != commits['custody_key_sha256']:
        raise ValueError('Frozen FRUS commitments changed')
    last, worker = A.read(previous), A.read(receipt)
    if last['native_runtime_sha256'] != worker['runtime_sha256']:
        raise ValueError('The evaluation rule requires the same native runtime')
    questions = A.read(packet / 'questions.json')
    if any([row['id'] for row in rows] != held['ordered_case_ids']
           for rows in (questions, last['rows'], worker['cases'])):
        raise ValueError('Use only the same eight ordered frozen cases')
    sources = {source['id']: source for source in A.read(packet / 'sources.json')}
    rows = []
    with TemporaryDirectory(prefix='frus-proposition-') as scratch:
        temporary = Path(scratch)
        scores = temporary / 'native-score.json'
        A.score(packet, custody, receipt, scores)
        raw = A.read(scores)
        for question, previous_row, strict_row, score in zip(
                questions, last['rows'], worker['cases'], raw['cases'], strict=True):
            ident = question['id']
            answer = strict_row['answer']
            if (score['outcome'] != previous_row['outcome'] or answer['claims']
                    or answer['answer_supported'] or score['kind'] != previous_row['strict_after']):
                raise ValueError(f'Existing Strict Ask decision changed: {ident}')
            positive = score['expected'] == 'answer'
            if positive != bool(previous_row['exact_witness_coordinates']):
                raise ValueError(f'Frozen witness obligations changed: {ident}')
            if positive and not score['complete_discovery_anchor_coverage']:
                raise ValueError(f'Discovery lost a frozen witness: {ident}')
            diagnostic = (probe(packet, question, previous_row['exact_witness_coordinates'],
                                sources, temporary / ident) if positive else None)
            rows.append({
                'id': ident,
                'discovery_before': previous_row['discovery_after'],
                'discovery_after': score['complete_discovery_anchor_coverage'] if positive else None,
                'strict_before': previous_row['strict_after'],
                'strict_after': score['kind'],
                'outcome': score['outcome'],
                'native_diagnostic': score['diagnostic'],
                'decision': 'withhold_missing_proposition_admission' if positive else 'correct_withhold',
                'kernel_probe': diagnostic,
            })
    A.save(output, {
        **commits, 'baseline_commit': held['baseline_commit'], 'worker_revision': worker['revision'],
        'native_receipt_sha256': A.digest(receipt.read_bytes()), 'runtime_unchanged': True,
        'before': last['after'], 'after': raw['counts'], 'false_supported_bridges': 0,
        'outside_custodian_scoring': 'NOT_RUN', 'independent_historical_accuracy': 'NOT_RUN',
        'independent_semantic_adjudication': 'NOT_RUN', 'native_oocc': 'NOT_RUN',
        'rows': rows,
    })


if __name__ == '__main__':
    cli = argparse.ArgumentParser(description=__doc__)
    for field in ('packet', 'custody', 'rule', 'freeze', 'previous', 'receipt', 'output'):
        cli.add_argument('--' + field, required=True, type=Path)
    audit(**vars(cli.parse_args()))
