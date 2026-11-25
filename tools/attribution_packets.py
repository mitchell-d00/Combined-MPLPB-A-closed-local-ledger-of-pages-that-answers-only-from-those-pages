"""Deterministic synthetic source packets. Not independent preparation."""
from html import escape
import random


def statement(number, actor, team, task, first_person, quoted, transfer=False):
    imperative = task[0].upper() + task[1:]
    if transfer:
        if number == 0:
            if first_person:
                return f'The {team} is instructed by me to {task}.'
            if quoted:
                return f'The {team} received this instruction from {actor}: “{imperative}.”'
            return f'The {team} was instructed by {actor} to {task}.'
        if first_person:
            return f'“{imperative},” is my instruction to the {team}.'
        return f'“{imperative},” {actor} directed the {team}.'
    if number == 0:
        if first_person:
            return f'I instruct the {team} to {task}.'
        return (f'{actor} instructed the {team}: “{imperative}.”' if quoted
                else f'{actor} instructed the {team} to {task}.')
    if number == 1:
        if first_person:
            return f'My instruction to the {team} is to {task}.'
        return (f'The instruction from {actor} to the {team} was: “{imperative}.”' if quoted
                else f'The instruction from {actor} to the {team} was to {task}.')
    if number == 2:
        if first_person:
            return f'I order the {team} to {task}.'
        return (f'{actor} ordered the {team}: “{imperative}.”' if quoted
                else f'{actor} ordered the {team} to {task}.')
    if first_person:
        return f'To the {team}, I give this instruction: “{imperative}.”'
    return f'{actor} gave the {team} this instruction: “{imperative}.”'


def packet(seed, transfer=False):
    rng = random.Random(seed)
    actors = (['Mira Calder', 'Owen Serrano', 'Tessa Rahman', 'Bruno Leclerc',
               'Keira Danton', 'Hugo Nakamura', 'Sonia Varela', 'Felix Ortega'] if transfer else
              ['Clara Mendez', 'Jonas Akande', 'Petra Holm', 'Dario Silva',
               'Marta Kovacs', 'Emil Ortega', 'Nadia Farouk', 'Victor Chen'])
    work = ([('harbor census unit', 'reconcile the vessel register before Thursday'),
             ('botanical archive team', 'index the pressed specimens by collection date'),
             ('canal inspection crew', 'measure the lower lock and list damaged hinges'),
             ('acoustic survey group', 'calibrate the shoreline sensors before dawn'),
             ('supply audit panel', 'compare the warehouse manifests with the receipts'),
             ('glacier observation unit', 'photograph the eastern moraine before noon')] if transfer else
            [('river mapping team', 'survey the western culvert before Friday'),
             ('library catalog group', 'catalog the copper engravings by shelf'),
             ('orchard survey crew', 'inspect the southern terraces and record broken gates'),
             ('bridge safety panel', 'measure the timber supports before Tuesday'),
             ('water quality unit', 'collect the upstream samples before sunrise'),
             ('transit planning team', 'compare the morning timetables with the route maps')])
    rows, key = [], []
    for form in ['letter', 'minutes', 'report']:
        for wording in range(2 if transfer else 4):
            writer, instructor, alternate, recipient = rng.sample(actors, 4)
            team, task = rng.choice(work)
            for variant in ['valid', 'wrong_actor', 'different_quoted_speaker', 'completion']:
                ident = ('T' if transfer else 'D') + f'{len(rows)+1:03d}'
                speaker = alternate if variant == 'different_quoted_speaker' else (writer if form == 'letter' else instructor)
                first = form == 'letter' and variant != 'different_quoted_speaker'
                quoted = form == 'report' or variant == 'different_quoted_speaker'
                text = statement(wording, speaker, team, task, first, quoted, transfer)
                if form == 'letter':
                    paragraphs = [f'Dear Director {recipient}:', text, 'Respectfully,', writer]
                    layer = 'signed_letter_first_person' if first else 'letter_attributes_quotation'
                else:
                    paragraphs = (['Meeting minutes.', f'Recorded by {writer}.', text] if form == 'minutes'
                                  else ['Report.', f'Written by {writer}.', text])
                    layer = 'minutes_attributes_instruction' if form == 'minutes' else 'report_attributes_quotation'
                requested = (alternate if first else writer) if variant == 'wrong_actor' else speaker
                question = f'According to the {form}, what did {requested} instruct the {team} to do?'
                if transfer:
                    question = (f'What instruction to the {team} is attributed to {requested} in the {form}?'
                                if wording == 0 else
                                f'According to the {form}, which task did {requested} assign the {team}?')
                if variant == 'completion':
                    question = f'According to the {form}, did the {team} complete the task instructed by {requested}?'
                body = ''.join('<p>'+escape(p)+'</p>' for p in paragraphs)
                rows.append({'id': ident, 'question': question, 'sources': [{'id': 'ORIGINAL', 'body_html': body}],
                             'budget': {'passages': 12, 'characters': 8000}})
                key.append({'id': ident, 'document_form': form, 'wording': wording, 'variant': variant,
                            'supported': variant in {'valid', 'different_quoted_speaker'},
                            'requested_actor': requested, 'source_actor': speaker, 'writer': writer,
                            'recipient': 'the '+team, 'task': task, 'reporting_layer': layer,
                            'source_statement': text, 'completion_established': False})
    rng.shuffle(rows)
    by_id = {v['id']: v for v in key}
    return rows, [by_id[r['id']] for r in rows]
