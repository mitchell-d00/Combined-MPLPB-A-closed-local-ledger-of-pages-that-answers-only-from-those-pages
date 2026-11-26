"""Round-two packet authoring; execution/scoring stay in unchanged D% tools.

Fully enumerated same-operator development, not independent preparation.
No filtering by reader outcome. Raw text layouts differ in their actual bytes.
"""
from pathlib import Path
import argparse
from tools import dpercent as D


def prepare(public, custody):
    public, custody = Path(public), Path(custody)
    if public.exists() or custody.exists():
        raise FileExistsError('Never overwrite a frozen packet')
    public.mkdir(parents=True)
    custody.mkdir(parents=True, mode=0o700)
    keys, registry = [], []
    domains = [
        ('Maple Loom Studio', 'Iona Reed', 'Willow Court', 'a community garden', 'North Service Office', '08:25', 'Mara Finch', 'the field team', 'inspect', 'the eastern bridge'),
        ('Harbor Cycle Shop', 'Dario Vale', 'Copper House', 'a repair workshop', 'Harbor Permit Office', '10:15', 'Jonas Hill', 'the coastal crew', 'survey', 'the western quay'),
        ('Cedar Bread Bakery', 'Leena Moss', 'Orchard Hall', 'a public library', 'Meadow Advice Office', '07:40', 'Nadia Stone', 'the research group', 'review', 'the northern archive'),
    ]

    def add(family, question, body, expected, condition, layout, domain, props=None, field=None, competitor=None):
        number = len(keys) + 1
        ident = f'DP{number:05d}'
        folder = public / 'packets' / ident
        contents = [body] + ([competitor] if competitor else [])
        sources, facts = [], []
        for i, raw in enumerate(contents, 1):
            rel = f'sources/record-{i}.txt'
            path = folder / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(raw)
            source = {'path': rel, 'source_class': 'original'}
            if condition == 'retired':
                source['retired'] = True
            sources.append(source)
            facts.append({'source_id': f'SOURCE-{i:04d}', 'path': rel, 'evidence_text': raw.strip(), 'source_class': 'original', 'raw_quote': raw})
        D.save(folder / 'case.json', {'id': ident, 'question': question, 'profile': 'internal', 'sources': sources, 'budget': {'passages': 12, 'characters': 8000}})
        keys.append({'id': ident, 'family': family, 'expected': expected, 'required_propositions': props or [],
                     'reference_sources': ['SOURCE-0001'] if expected == 'answer' else [], 'source_facts': facts,
                     'structural_expectations': {}, 'automatic_answer_matcher': 'typed_proposition_v1' if props else 'literal_field_set_v1',
                     'required_field_quotes': field or [], 'features': {'question_form': question, 'field': family, 'line_ending': 'LF', 'fence': layout, 'source_count': len(sources)}})
        registry.append({'id': ident, 'stable_id': f'CRYPT-BUNYIP-R02-{number:04d}', 'family': family, 'condition': condition, 'layout': layout, 'domain': domain,
                         'original_question': question, 'source_hashes': {s['path']: D.sha((folder / s['path']).read_bytes()) for s in sources},
                         'expected': expected, 'protected_operation': 'Whole-question relation, arguments, source scope, polarity and instruction-only modality; unique task binding',
                         'origin': 'PR105 consumed transfer misses; round2 same-operator authored contrasts',
                         'diagnostics_are_not_original_question_recoveries': True})

    for domain, (entity, owner, place, category, office, time, actor, recipient, action, obj) in enumerate(domains, 1):
        canonical = {'owner': f'Who owns {entity}?', 'category': f'What is {place}?', 'time': f'When does {office} open?',
                     'instruction': f'What instruction does the record attribute to {actor} concerning {obj}?'}
        forms = {'owner': [canonical['owner'], f'Who, according to the source, owns {entity}?', f'Who, according to this record, is the owner of {entity}?'],
                 'category': [canonical['category'], f'Under what category is {place} described?', f'In this record, how would you classify {place}?'],
                 'time': [canonical['time'], f'At which time does {office} open?', f'According to this source, at which time does {office} open?'],
                 'instruction': [canonical['instruction'], f'Which task did {actor} give {recipient}?', f'What did {actor} instruct {recipient} to do?']}
        statement = {'owner': f'{owner} owns {entity}.', 'category': f'{place} is {category}.', 'time': f'Name: {office}\nOpening time: {time}',
                     'instruction': f'{actor} instructed {recipient} to {action} {obj}.'}
        other = {'owner': f'Other Person owns {entity}.', 'category': f'{place} is a railway station.', 'time': f'Name: {office}\nOpening time: 12:50',
                 'instruction': f'{actor} instructed {recipient} to inspect the southern depot.'}
        for family in forms:
            prop = {'relation': 'source_modality_assertion', 'actor': actor, 'modality': 'instruction', 'task_actor': recipient, 'task_action': action,
                    'task_object': obj, 'outer_negative': False, 'content_negative': False, 'completion_asserted_by_source': False, 'execution_independently_verified': False} if family == 'instruction' else None
            for layout in ('adjacent', 'paragraphs'):
                # Non-identical context and line separation; not repeated one-line labels.
                separator = '\n' if layout == 'adjacent' else '\n\n'
                body = 'Office inventory was updated.' + separator + statement[family] + separator + 'Paper copies remain on file.\n'
                for q in forms[family]:
                    for condition in ('unique', 'competing', 'missing', 'retired'):
                        content = 'Paper copies remain on file.\n' if condition == 'missing' else body
                        fields = [statement[family]]
                        competing = other[family]
                        if family == 'instruction' and q == canonical['instruction']:
                            competing = f'{actor} did not instruct {recipient} to {action} {obj}.'
                        add(family, q, content, 'answer' if condition == 'unique' else 'refuse', condition, layout, domain,
                            props=[prop] if prop else None, field=fields, competitor=competing + '\n' if condition == 'competing' else None)
                q = forms[family][1]
                for condition, content in [('wrong_actor', body.replace(actor if family == 'instruction' else entity if family == 'owner' else place if family == 'category' else office, 'Other Person' if family == 'instruction' else 'Other Location')),
                                           ('conditional', 'Only if the permit is approved.' + separator + statement[family] + '\n'),
                                           ('negation', (f'{actor} did not instruct {recipient} to {action} {obj}.' if family == 'instruction' else f'{owner} does not own {entity}.' if family == 'owner' else f'{place} is not {category}.' if family == 'category' else f'{office} does not open at {time}.') + '\n')]:
                    add(family, q, content, 'refuse', condition, layout, domain)
                for suffix in (' and who verified it', ' before May 2', ' if the permit is approved'):
                    add(family, q.rstrip('?') + suffix + '?', body, 'refuse', 'extra_obligation', layout, domain)
        for polarity, text in [('positive', f'{place} is {category}.'), ('negative', f'{place} is not {category}.'), ('missing', 'Paper copies remain on file.')]:
            add('classification_confirmation', f'Is {place} {category}?', text + '\n', 'refuse' if polarity == 'missing' else 'answer', polarity, 'single', domain, field=[text])
        # A different stated category is not evidence of the requested category's negation.
        add('classification_confirmation', f'Is {place} a railway station?', statement['category'] + '\n', 'refuse', 'unmentioned', 'single', domain)
    D.save(custody / 'key.json', {'schema': 'bunyip-round2-key-v1', 'cases': keys})
    D.save(custody / 'pairing.json', {'cases': registry, 'same_operator': True, 'independent_preparation': 'NOT_RUN', 'independent_scoring': 'NOT_RUN'})
    D.save(custody / 'dice.json', {'seed': None, 'rolls': [], 'sampling': 'Fully enumerated; no generated positive excluded; not random or unseen transfer'})
    D.save(public / 'protocol.json', {'schema': 'bunyip-round2-development-v1', 'mechanism': 'Question relation and argument bindings do not survive medial attribution, category/time variants or omitted task objects; literal negative classification cannot currently yield a source-scoped no.',
                                   'cases': len(keys), 'limits': D.LIMITS, 'execution': 'Unchanged tools/dpercent.py and tools/dpercent_worker.py', 'scoring': 'Unchanged tools/dpercent_expanded.py',
                                   'layout_scope': 'Actually different raw preformatted text; no structured HTML claim', 'transfer': 'NOT_PREPARED; hold back complete wording structures before implementation', 'custody': 'Same operator authored and scored; no independent preparation/blinding/adjudication'})
    seal = {'public_files': D.files(public), 'key_sha256': D.sha((custody / 'key.json').read_bytes()), 'dice_sha256': D.sha((custody / 'dice.json').read_bytes()),
            'pairing_sha256': D.sha((custody / 'pairing.json').read_bytes()), 'generator_sha256': D.sha(Path(__file__).read_bytes()), 'worker_sha256': D.sha((D.ROOT / 'tools/dpercent_worker.py').read_bytes())}
    D.save(public / 'seal.json', seal)
    D.save(custody / 'public-seal-copy.json', seal)
    return {'cases': len(keys), 'seal_sha256': D.sha((public / 'seal.json').read_bytes())}


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--custody', type=Path, required=True)
    a = p.parse_args()
    print(prepare(a.out, a.custody))
