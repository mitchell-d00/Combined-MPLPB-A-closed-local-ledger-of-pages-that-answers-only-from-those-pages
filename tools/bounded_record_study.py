"""Compare native documentary outcomes across a balanced fictional query panel."""
import argparse
from collections import Counter, defaultdict
from html import escape
from itertools import product
import json
from pathlib import Path
import random
from tempfile import TemporaryDirectory

from mplpb_answers.pipeline import answer_query
from mplpb_combined.ledger import write
from mplpb_combined.reader import PROFILES

AGES = ('18–24', '25–44', '45–64', '65+')
EDUCATION = ('secondary', 'vocational', 'undergraduate', 'postgraduate')
STYLES = {
    'direct': '{}',
    'polite': 'Please answer the question using the provided records: {}',
    'scope-conscious': '{} Keep unverified matters unresolved.',
}
PARAPHRASES = {
    'Which room and which chair should we record?': 'What room and chair are confirmed?',
    'Which logging time do the records support?': 'What logging time is documented?',
    'Who signed the form?': 'Who signed the form described in the record?',
    'Was the original inspection canceled?': 'Was the first inspection canceled?',
    'Did the trucks leave from the same depot?': 'Did both trucks leave from the same depot?',
}
PEOPLE = ('Avery', 'Bennett', 'Taylor', 'Jordan', 'Drew', 'Cameron', 'Morgan', 'Reese')


def fixtures(rng):
    """Fictional text, newly worded per proof family and freely varied by seed."""
    first, second, third, fourth = rng.sample(PEOPLE, 4)
    seq = rng.randrange(100, 900)
    room_a, room_b = rng.sample(range(10, 60), 2)
    old = f'The August 12 safety briefing was listed at 8 a.m. in Room {room_a} with {first} as chair.'
    new = f'Correction to the August 12 safety briefing notice. Room {room_b} replaces Room {room_a}. The rest of the notice stands.'
    form = 'Which room and which chair should we record?'
    yield 'scoped_correction', form, [old, new], 'supported_answer', {'room': f'Room {room_b}', 'chair': first}
    yield 'different_subject_correction', form, [old, new.replace('safety', 'finance')], 'abstain', {}
    yield 'conflicting_corrections', form, [old, new, new.replace(f'Room {room_b}', 'Room 90')], 'conflict', {'chair': first}

    continued = f'The September 3 library board session adjourned and was to resume September 10 under docket LB-{seq}.'
    resumption = f'On September 10, the library board resumed LB-{seq} and later opened a special session under docket LB-{seq+1}.'
    form = 'Which September 10 meeting continued the September 3 session?'
    yield 'explicit_continuation', form, [continued, resumption], 'supported_answer', {'docket': f'LB-{seq}'}
    yield 'wrong_continuation_date', form, [continued, resumption.replace('September 10', 'September 11')], 'abstain', {}
    yield 'wrong_continuation_body', form, [continued, resumption.replace('library board', 'parks board')], 'abstain', {}

    moved = f'The March 8 permit hearing was moved to March 15. Its docket number remains PE-{seq}.'
    opened = f'Permit hearing docket PE-{seq} opened March 15.'
    form = 'Do both reports describe the same hearing?'
    yield 'rescheduled_shared_docket', form, [moved, opened], 'supported_answer', {'same_event': True, 'docket': f'PE-{seq}'}
    yield 'same_day_different_docket', form, [moved, opened.replace(f'PE-{seq}', f'PE-{seq+1}')], 'abstain', {}
    yield 'same_docket_different_proceeding', form, [moved, opened.replace('Permit', 'Budget')], 'abstain', {}
    yield 'named_scoped_docket', 'Do sources LEAF-1 and LEAF-2 describe the same event?', [moved, opened], 'supported_answer', {'same_event': True, 'docket': f'PE-{seq}'}

    logs = [f'Alarm {seq} at the annex was logged at {time}.' for time in ('14:12', '14:29')]
    form = 'Which logging time do the records support?'
    yield 'conflicting_logging_times', form, logs, 'conflict', {'recorded_times': ['14:12', '14:29']}
    yield 'consistent_logging_time', form, [logs[0]] * 2, 'supported_answer', {'recorded_times': ['14:12']}
    yield 'distinct_logging_subjects', form, [logs[0], logs[1].replace(str(seq), str(seq+1))], 'abstain', {}

    handoffs = [f'At 10 a.m., {first} handed the badge to {second}.',
                f'At 11 a.m., {second} handed it to {third}.']
    form = 'Who held the badge immediately after 11 a.m., and who returned it at 2 p.m.?'
    return_log = f'At 2 p.m., {fourth} signed the return log. The log does not name who handed back the badge.'
    yield 'unidentified_returner', form, handoffs + [return_log], 'partial_answer', {'holder': third}
    yield 'explicit_returner', form, handoffs + [f'At 2 p.m., {third} handed back the badge.'], 'supported_answer', {'holder': third, 'returned_by': third}
    yield 'broken_handoff', form, [handoffs[0], handoffs[1].replace(second, fourth), return_log], 'abstain', {}

    intro = f'Operations supervisor {first} Reed introduced {second} Vale, the compliance supervisor. The supervisor then signed the waiver form.'
    yield 'competing_role_referents', 'Who signed the form?', [intro], 'abstain', {}
    yield 'unique_role_referent', 'Who signed the form?', [intro.replace('compliance supervisor', 'compliance adviser')], 'supported_answer', {'signer': f'{first} Reed'}

    assignment = f'Case {seq} names {first} Reed as the desk clerk and {second} Vale as the courier.'
    amendment = f'Case {seq} amendment. Replace {first} Reed with {third} Lane in the desk-clerk field, effective 2026-10-05.'
    receipt = f'Case {seq} receipt dated 2026-10-06. The desk clerk signed at 2 p.m.'
    yield 'effective_role_amendment', 'Who signed at 2 p.m.?', [assignment, amendment, receipt], 'supported_answer', {'signer': f'{third} Lane'}
    yield 'undated_role_amendment', 'Who signed at 2 p.m.?', [assignment, amendment.replace(', effective 2026-10-05', ''), receipt], 'abstain', {}
    yield 'later_role_amendment', 'Who signed at 2 p.m.?', [assignment, amendment, receipt.replace('2026-10-06', '2026-10-04')], 'abstain', {}

    glossary = f'LG-{seq} log. Before February 5, “the depot” in this log refers to Cedar Depot. Beginning February 5, it refers to Willow Depot.'
    entries = [f'LG-{seq} log. February {d}. A truck left the depot.' for d in (4, 5)]
    yield 'shared_log_date_binding', 'Did the trucks leave from the same depot?', [glossary, *entries], 'supported_answer', {'same_depot': False}
    yield 'different_log_scope', 'Did the trucks leave from the same depot?', [glossary, entries[0], entries[1].replace(str(seq), str(seq+1))], 'abstain', {}

    inspection = f'Inspection SI-{seq} took place April 9. A follow-up visit was scheduled for April 16.'
    cancellation = f'The April 16 visit was canceled. The findings from SI-{seq} stand.'
    yield 'canceled_follow_up', 'Was the original inspection canceled?', [inspection, cancellation], 'supported_answer', {'inspection_date': 'April 9'}
    yield 'mismatched_cancellation', 'Was the original inspection canceled?', [inspection, cancellation.replace(str(seq), str(seq+1))], 'abstain', {}


def replay(root, question, texts):
    for i, source in enumerate(texts, 1):
        write(root, title=f'Archive leaf {i}', scope='documentary records', doc_id=f'LEAF-{i}',
              body_html='<pre>' + escape(source) + '</pre>', origin='machine',
              source_authorship='declared-machine', when='2026-11-20T00:00Z')
    return answer_query(root, question, PROFILES['internal']).contract


def result_class(contract, expected, values, texts):
    observed = contract['kind']
    union = {key: value for c in contract['claims'] for key, value in c.get('proposition', {}).items()}
    originals = {f'LEAF-{i}': body for i, body in enumerate(texts, 1)}
    witnesses = all(c['citations'] and all(
        cite['source_id'] in originals
        and cite['quote'] == originals[cite['source_id']][cite['body_start']:cite['body_end']]
        for cite in c['citations']) for c in contract['claims'])
    flags = (contract['answer_supported'] == (observed == 'supported_answer')
             and bool(contract['claims']) == (observed in {'supported_answer', 'partial_answer', 'conflict'}))
    if observed == expected and witnesses and flags and all(union.get(k) == v for k, v in values.items()):
        return 'matched'
    if contract['claims'] or (observed == 'supported_answer') or contract['answer_supported']:
        return 'unexpected_evidence'
    if expected == 'supported_answer':
        return 'missed_supported'
    if expected == 'partial_answer':
        return 'missed_partial'
    if expected == 'conflict':
        return 'missed_conflict'
    return 'wrong_unresolved_outcome'


def run(seed, repeats):
    scenarios = [list(fixtures(random.Random(seed + i))) for i in range(repeats)]
    rows = []
    with TemporaryDirectory(prefix='mplpb-fictional-panel-') as directory:
        group_counts = defaultdict(Counter)
        for i, (age, education, style, repeat) in enumerate(product(AGES, EDUCATION, STYLES, range(repeats)), 1):
            person_id = f'Fictional reader {i}'
            rng = random.Random(seed + repeat)
            for family, question, sources, expected, values in scenarios[repeat]:
                texts = list(sources)
                if family != 'named_scoped_docket':
                    rng.shuffle(texts)
                if style == 'scope-conscious':
                    question = PARAPHRASES.get(question, question)
                question = STYLES[style].format(question)
                contract = replay(Path(directory) / str(len(rows)), question, texts)
                outcome = result_class(contract, expected, values, texts)
                group_counts[(age, education, style)][outcome] += 1
                rows.append({'persona': person_id, 'family': family, 'age_band': age, 'education': education,
                             'style': style, 'expected': expected, 'observed': contract['kind'], 'result': outcome})
    groups = [{'age_band': a, 'education': e, 'style': s, 'results': dict(c)}
              for (a, e, s), c in sorted(group_counts.items())]
    return {'seed': seed, 'cases': len(rows), 'results': dict(Counter(x['result'] for x in rows)),
            'outcomes': dict(Counter(x['observed'] for x in rows)), 'groups': groups, 'cases_detail': rows}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seed', type=int, default=91)
    parser.add_argument('--repeats', type=int, default=1)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--require-pass', action='store_true')
    args = parser.parse_args()
    if not 1 <= args.repeats <= 10:
        parser.error('--repeats must be between 1 and 10')
    result = run(args.seed, args.repeats)
    if args.output:
        args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps({k: result[k] for k in ('seed', 'cases', 'results', 'outcomes')}))
    return int(args.require_pass and result['results'].get('matched', 0) != result['cases'])


if __name__ == '__main__':
    raise SystemExit(main())
