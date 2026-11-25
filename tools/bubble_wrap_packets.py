"""Additive development controls only; never opens the reserved transfer packet."""
import argparse
import hashlib
import json
from pathlib import Path


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    path.parent.mkdir(exist_ok=True, parents=True)
    with path.open('x') as stream:
        stream.write(json.dumps(value, indent=2, ensure_ascii=False) + '\n')


def prepare(folder):
    reporter, author, writer = 'Celia Duarte', 'Bram Okoye', 'Soren Malik'
    obj = 'the estuary register'
    mechanisms = {
        'affirmative': f'{reporter} reported that {author} wrote {obj}.',
        'inner_denial': f'{reporter} reported that {author} did not write {obj}.',
        'outer_denial': f'{reporter} did not report that {author} wrote {obj}.',
        'conditional': f'If asked, {reporter} would report that {author} wrote {obj}.',
    }
    questions = {
        'affirmative': f'What does {reporter} report about the writer of {obj}, without independently verifying the event?',
        'inner_denial': f'What does {reporter} report about whether {author} wrote {obj}?',
        'outer_denial': f'According to the record, did {reporter} report that {author} wrote {obj}?',
        'conditional': f'What conditional authorship statement does {reporter} report about {obj}?',
    }
    keys, cases = [], []
    for mechanism, statement in mechanisms.items():
        for purpose in ('source_attribution', 'independent_authorship'):
            for context in ('standalone', 'different_writer', 'unrelated_quote', 'conflicting_appearance'):
                ident = f'BW-RPT-{len(cases)+1:03d}'
                heading = f'From: {writer}\nTo: Archive clerk\n\n' if context == 'different_writer' else ''
                if context == 'unrelated_quote':
                    heading = 'Archive margin: “The gardener scheduled a visit.”\nThe cabinet holds reports.\n\n'
                texts = [heading + statement + '\n']
                witnesses = [statement]
                if context == 'conflicting_appearance':
                    other = (f'{reporter} reported that {author} wrote {obj}.' if mechanism in {'inner_denial', 'outer_denial'}
                             else f'{reporter} reported that {author} did not write {obj}.')
                    if mechanism == 'conditional':
                        other = f'If asked, {reporter} would report that {author} did not write {obj}.'
                    texts.append(other + '\n'); witnesses.append(other)
                question = questions[mechanism] if purpose == 'source_attribution' else (
                    f'Do these records independently establish that {author} actually wrote {obj}?')
                directory = folder / 'inputs' / ident
                sources = []
                for n, text in enumerate(texts, 1):
                    relative = f'sources/original-{n}.txt'
                    (directory / 'sources').mkdir(parents=True, exist_ok=True)
                    (directory / relative).write_bytes(text.encode())
                    sources.append({'path': relative, 'source_class': 'original', 'external': 'yes'})
                case = {'id': ident, 'question': question, 'profile': 'internal', 'sources': sources,
                        'budget': {'passages': 12, 'characters': 8000}}
                save(directory / 'case.json', case)
                expectation = ('withhold' if purpose == 'independent_authorship' else
                               'conflict' if context == 'conflicting_appearance' else 'source_answer')
                roles = {'reporter': reporter, 'author': author, 'object': obj, 'inner_action': 'write',
                         'inner_negative': False if mechanism == 'affirmative' else True if mechanism == 'inner_denial' else None,
                         'outer_negative': mechanism == 'outer_denial',
                         'content_asserted_by_reporter': mechanism in {'affirmative', 'inner_denial'},
                         'conditions': ['If asked'] if mechanism == 'conditional' else [],
                         'source_writer_or_unknown': writer if context == 'different_writer' else None,
                         'actual_authorship_established': False}
                cases.append({'id': ident, 'family': 'BW-REPORT', 'mechanism': mechanism, 'purpose': purpose,
                              'context': context, 'packet': str(directory.relative_to(folder)),
                              'files': {str(p.relative_to(directory)): digest(p) for p in directory.rglob('*') if p.is_file()}})
                keys.append({'id': ident, 'expected': expectation, 'roles': roles,
                             'eligible_complete_witnesses': witnesses,
                             'allow_claims': purpose == 'source_attribution',
                             'conflicting_roles': context == 'conflicting_appearance'})
    save(folder / 'matrix.json', {'cases': cases, 'construction': '4 mechanisms x 2 purposes x 4 contexts'})
    save(folder / 'matrix-key.json', keys)
    save(folder / 'matrix-freeze.json', {'generator_sha256': digest(Path(__file__)),
         'matrix_sha256': digest(folder / 'matrix.json'), 'key_sha256': digest(folder / 'matrix-key.json'),
         'cases': 32, 'frozen_before_native_changes': True,
         'reserved_transfer_opened': False, 'same_operator': True,
         'independent_preparation': 'NOT_RUN', 'independent_semantic_adjudication': 'NOT_RUN'})


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    prepare(p.parse_args().output)
