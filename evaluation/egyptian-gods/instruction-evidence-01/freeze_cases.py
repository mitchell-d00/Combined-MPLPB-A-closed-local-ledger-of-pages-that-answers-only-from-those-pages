"""Prepare two synthetic draws and separate evaluator material."""
import json
import sys
from pathlib import Path

MECHANISMS = (
    'dated', 'unresolved-date', 'fictional-false', 'wrong-reporter',
    'unlinked', 'withdrawn', 'no-grant', 'other-resource',
)


def save(path, data):
    with path.open('x') as output:
        json.dump(data, output, ensure_ascii=False, indent=2)
        output.write('\n')


def prepare(draw):
    fresh = draw == 'F'
    writer, reporter, actor, other = (
        ('Leona Mills', 'Mara Lin', 'Hugo Santos', 'Ida Nel') if fresh else
        ('Mina Vale', 'Nora Bell', 'Owen Reed', 'Tessa Dale')
    )
    team = 'the loading crew' if fresh else 'the intake team'
    task = 'Inspect the brass latch' if fresh else 'Move the blue crates'
    date = '2024-06-12' if fresh else '2023-04-18'
    citation_statement = (f'{team.capitalize()} was instructed by {actor} to {task.lower()}.' if fresh
                          else f'{actor} instructed {team} to {task.lower()}.')
    date_statement = (f'The instruction to {task.lower()} was given on {date}.' if fresh
                      else f'{actor} gave that instruction on {date}.')
    cases, key, oracle = [], {}, {}
    for number, mechanism in enumerate(MECHANISMS, 1):
        ident = f'IE01-{draw}{number:02}'
        base_question = (f'In the report, what instruction did {actor} give {team}?' if fresh else
                         f'According to the report, what did {actor} instruct {team} to do?')
        units = ['Report.', f'Written by {writer}.', citation_statement]
        question = base_question
        if number in (1, 2):
            date_question = ('On what date was that instruction given?' if fresh
                             else 'When did the instructor give that instruction?')
            question = base_question[:-1] + ', and ' + date_question[0].lower() + date_question[1:]
        if number == 1:
            units.append(date_statement)
        if number == 4:
            units[2] = f'{reporter} reported that {citation_statement[0].lower() + citation_statement[1:]}'
            question = (f'According to {writer}, what did {actor} instruct {team} to do, '
                        f'and who reported the instruction as written by {writer}?')
        if number == 5:
            units[2:] = [f'{reporter} told {other} that the spare latch was in storage.',
                         citation_statement]
            question = f'What instruction did {actor} give {team} according to {reporter} in the report?'
        cases.append({'id': ident, 'question': question, 'withdraw_before_reread': number == 6,
                      'sources': [{'id': 'REPORT', 'body_html': ''.join(f'<p>{u}</p>' for u in units)}],
                      'budget': {'passages': 12, 'characters': 8000}})
        support = number not in (4, 5)
        key[ident] = {
            'mechanism': mechanism, 'candidate_attempts': int(number <= 3),
            'candidate_durable_completions': int(number <= 3),
            'initial_native': 'partial_answer' if number == 2 else
                              'supported_answer' if support else 'abstain',
            'final_native': 'abstain' if number == 6 or not support else
                            'partial_answer' if number == 2 else 'supported_answer',
            'role_claim': {'writer': writer, 'actor': actor, 'recipient': team,
                           'task': task.lower(), 'polarity': 'affirmative', 'conditions': [],
                           'modality': 'instruction_only'} if support else None,
            'witnesses': [f'Written by {writer}.', citation_statement] if support else [],
            'requested_instruction_date': date if number == 1 else 'unresolved' if number == 2 else None,
            'date_witness': date_statement if number == 1 else None,
            'grant': 'absent' if number == 7 else 'different-resource' if number == 8 else 'exact',
        }
        if number == 3:
            oracle[ident] = {'holds': False, 'actor': actor, 'team': team, 'instruction': task.lower()}
    return cases, key, oracle


if __name__ == '__main__':
    draw, inputs, evaluator = sys.argv[1:]
    data, key, oracle = prepare(draw)
    save(Path(inputs), data)
    save(Path(evaluator) / f'{draw}-key.json', key)
    save(Path(evaluator) / f'{draw}-oracle.json', oracle)
