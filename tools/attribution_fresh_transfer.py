"""Fresh transfer structures after documented development/control overlap. Not independent preparation."""
from html import escape
import random


def statement(number, actor, team, task, first_person, quoted, transfer=False):
    assert transfer
    imperative = task[0].upper() + task[1:]
    if number == 0:
        if first_person:
            return f'For the {team}, my instruction is to {task}.'
        return (f'For the {team}, the instruction from {actor} was: “{imperative}.”' if quoted
                else f'For the {team}, the instruction from {actor} was to {task}.')
    if first_person:
        return f'My instruction is for the {team} to {task}.'
    return (f"{actor}'s instruction for the {team} was “{imperative}.”" if quoted
            else f"{actor}'s instruction was for the {team} to {task}.")


def packet(seed, transfer=False):
    rng = random.Random(seed)
    actors = (['Livia Benton', 'Anton Seifert', 'Rina Okeke', 'Mateo Galvez',
               'Iris Demir', 'Stefan Petrov', 'Amara Holt', 'Julien Costa'] if transfer else
              ['Clara Mendez', 'Jonas Akande', 'Petra Holm', 'Dario Silva',
               'Marta Kovacs', 'Emil Ortega', 'Nadia Farouk', 'Victor Chen'])
    work = ([('reservoir survey team', 'mark the spillway gauges before Wednesday'),
             ('observatory maintenance crew', 'align the rooftop instruments before sunset'),
             ('ceramic archive unit', 'catalog the glazed fragments by excavation layer'),
             ('grain inspection panel', 'weigh the northern silo samples and log moisture readings'),
             ('wetland mapping group', 'trace the reed beds along the southern embankment'),
             ('railway inventory team', 'count the signal lamps before Saturday')] if transfer else
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
                ident = ('F' if transfer else 'D') + f'{len(rows)+1:03d}'
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


if __name__ == '__main__':
    import argparse
    import hashlib
    import json
    from pathlib import Path
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['custody','freeze','rule']:
        p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--seed',required=True);a=p.parse_args()
    a.custody.mkdir(mode=0o700)
    rows,key=packet(a.seed,True)
    def save(path,value):
        with path.open('x') as f:f.write(json.dumps(value,indent=2,ensure_ascii=False)+'\n')
    def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
    save(a.custody/'inputs.json',rows);save(a.custody/'key.json',key)
    save(a.freeze,{'baseline_commit':'28b8feb871cd0c2eb29440f2ab46623e410622b6','seed':a.seed,
        'cohorts':{'transfer':{'input_sha256':sha(a.custody/'inputs.json'),'key_sha256':sha(a.custody/'key.json'),'cases':24}},
        'generator_sha256':sha(Path(__file__)),'harness_sha256':sha(Path(__file__).with_name('attribution_trial.py')),
        'rule_sha256':sha(a.rule),'custody':{'preparer':'Betty, same operator','scorer':'Betty, same operator',
            'generator_templates_seen_by_implementer':True,'instance_bytes_opened_before_candidate_freeze':False,
            'worker_receives_key_path':False,'independent_preparation':'NOT_RUN','blinding':'NOT_RUN',
            'independent_semantic_adjudication':'NOT_RUN','independent_historical_accuracy':'NOT_RUN',
            'outside_custodian_scoring':'NOT_RUN','native_oocc':'NOT_RUN'},
        'protocol_correction':'First transfer overlapped supplementary development syntax and is retained as consumed development. Fresh recipient-fronted nominal and possessive argument-order constructions differ from all prior development examples.',
        'budgets':{'records':8,'scan_characters':200000,'units':1000,'passages':12,'output_characters':8000}})
    print('Fresh 24 transfer instances and keys sealed, templates visible; no instance bytes printed.')
