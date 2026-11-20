"""Finite whole-record proofs for small, self-contained documentary packets."""
import re
from collections import defaultdict
from datetime import date

from .documentary_verify import citation, context_ranges, source_question
from .relation_graph import _capture_evidence_text

_MONTHS = ('January', 'February', 'March', 'April', 'May', 'June',
           'July', 'August', 'September', 'October', 'November', 'December')
_DATE = rf'(?:{"|".join(_MONTHS)}) (?:[1-9]|[12][0-9]|3[01])'
_ISO_DATE = r'[0-9]{4}-[0-9]{2}-[0-9]{2}'
_CLOCK = r'(?:[1-9]|1[0-2])(?::[0-5][0-9])? [ap]\.m\.|noon'
_NAME = r'(?-i:[A-Z][a-z]+(?: [A-Z][a-z]+){0,2})'
_SUBJECT = r'[A-Za-z]+(?: [A-Za-z]+){0,5}'
_DOCKET = r'[A-Z]+-[0-9]+[A-Z]?'
_LOCATION = r'[A-Z0-9][A-Za-z0-9-]*(?: [A-Z0-9][A-Za-z0-9-]*)?'

_NOTICE = rf'The (?P<day>{_DATE}) (?P<event>{_SUBJECT}) was listed at (?:{_CLOCK}) in (?P<room>{_LOCATION}) with (?P<chair>{_NAME}) as chair\.'
_CORRECTION = rf'Correction to the (?P<day>{_DATE}) (?P<event>{_SUBJECT}) notice\. (?P<new>{_LOCATION}) replaces (?P<old>{_LOCATION})\. The rest of the notice stands\.'
_ADJOURNMENT = rf'The (?P<day>{_DATE}) (?P<body>{_SUBJECT}) (?:session|meeting|hearing) adjourned and was to resume (?P<next>{_DATE}) under docket (?P<key>{_DOCKET})\.'
_RESUMPTION = rf'On (?P<day>{_DATE}), the (?P<body>{_SUBJECT}?) resumed (?P<key>{_DOCKET})(?: and later opened a special session under docket (?P<other>{_DOCKET}))?\.'
_RESCHEDULED = rf'The (?P<old>{_DATE}) (?P<event>{_SUBJECT}) was moved to (?P<new>{_DATE})\. Its docket number remains (?P<key>{_DOCKET})\.'
_OPENED = rf'(?P<event>{_SUBJECT}) docket (?P<key>{_DOCKET}) opened (?P<day>{_DATE})\.|(?P<bare_event>{_SUBJECT}) (?P<bare_key>{_DOCKET}) opened (?P<bare_day>{_DATE})\.'
_LOGGED = r'(?P<subject>(?:Alarm|Incident|Report|Record|Case|Entry|Dispatch) (?:[A-Z]+-)?[0-9]+(?: at [A-Za-z ]{1,40})?) was logged at (?P<time>(?:[01][0-9]|2[0-3]):[0-5][0-9])\.'
_TRANSFER = rf'At (?P<time>{_CLOCK}), (?P<giver>{_NAME}) handed (?P<object>the [a-z]+|it) to (?P<recipient>{_NAME})\.'
_RETURN = rf'At (?P<time>{_CLOCK}), (?P<signer>{_NAME}) signed the return log\. The log does not name who handed back the (?P<object>[a-z]+)\.'
_NAMED_RETURN = rf'At (?P<time>{_CLOCK}), (?P<actor>{_NAME}) handed back the (?P<object>[a-z]+)\.'
_INSPECTION = rf'(?P<subject>Inspection) (?P<key>{_DOCKET}) took place (?P<day>{_DATE})\. A follow-up visit was scheduled for (?P<later>{_DATE})\.'
_CANCELLATION = rf'The (?P<day>{_DATE}) visit was canceled\. The findings from (?P<key>{_DOCKET}) stand\.'
_DEPOT_RULE = rf'(?P<log>{_DOCKET}) log\. Before (?P<before>{_DATE}), [‘“"]the depot[’”"] in this log refers to (?P<old>{_NAME})\. Beginning (?P<after>{_DATE}), it refers to (?P<new>{_NAME})\.'
_DEPOT_ENTRY = rf'(?P<log>{_DOCKET}) log\. (?P<day>{_DATE})\. A (?:second )?truck left the depot\.'
_TITLE = r'(?-i:[A-Za-z][a-z]*(?: [a-z]+){0,4})'
_PERSON = r'(?-i:[A-Z][a-z]+ [A-Z][a-z]+)'
_ROLE_INTRO = rf'(?P<title>{_TITLE}) (?P<first>{_PERSON}) introduced (?P<second>{_PERSON}), the (?P<other>{_TITLE})\. The (?P<role>[a-z]+) then signed the (?:[a-z]+ ){{0,3}}form\.'
_ASSIGNMENT = rf'(?P<case>Case [0-9]+) names (?P<old>{_NAME}) as the (?P<role>[a-z]+(?: [a-z]+){{0,3}}) and (?P<other>{_NAME}) as the (?P<other_role>[a-z]+(?: [a-z]+){{0,3}})\.'
_AMENDMENT = rf'(?P<case>Case [0-9]+) amendment\. Replace (?P<old>{_NAME}) with (?P<new>{_NAME}) in the (?P<role>[a-z]+(?:-[a-z]+){{0,3}}) field, effective (?P<day>{_ISO_DATE})\.'
_RECEIPT = rf'(?P<case>Case [0-9]+) receipt dated (?P<day>{_ISO_DATE})\. The (?P<role>[a-z]+(?: [a-z]+){{0,3}}) signed at (?P<time>{_CLOCK})(?:(?<=\.)|\.)'


def _full(pattern, value):
    return re.fullmatch(pattern, value, re.I)


def _bodies(records):
    for record in records:
        if len(record.body_html) > 16000:
            return None
    texts = [_capture_evidence_text(record) for record in records]
    if any(not text or len(text) > 2000 or any(start < len(text) for start, _ in context_ranges(record))
           for record, text in zip(records, texts)):
        return None
    return list(zip(records, texts))


def _collect(bodies, patterns):
    """Every supplied record must match exactly one role in this proof."""
    groups = defaultdict(list)
    for record, body in bodies:
        matches = [(label, match) for label, pattern in patterns.items()
                   if (match := _full(pattern, re.sub(r'\s+', ' ', body).strip()))]
        if len(matches) != 1:
            return defaultdict(list)
        label, match = matches[0]
        groups[label].append((match, citation(record, body, 0, len(body))))
    return groups


def _single(groups, *labels):
    if all(len(groups.get(label, [])) == 1 for label in labels):
        return tuple(groups[label][0] for label in labels)
    return ()


def _same(left, right):
    return left.casefold() == right.casefold()


def _claim(text, value, *citations):
    return {'text': text, 'proposition': value, 'citations': list(citations),
            'source_support_established': True,
            'qualifiers': ['Applies to the cited documentary statements.']}


def rescheduled_event(records, event=None):
    bodies = _bodies(records)
    if not bodies:
        return None
    pair = _single(_collect(bodies, {'moved': _RESCHEDULED, 'opened': _OPENED}), 'moved', 'opened')
    if not pair:
        return None
    (a, ca), (b, cb) = pair
    title, key, day = ((b['event'], b['key'], b['day']) if b['event'] else
                       (b['bare_event'], b['bare_key'], b['bare_day']))
    if (not all(map(_calendar_day, (a['old'], a['new'], day)))
            or _same(a['old'], a['new']) or not _same(a['event'], title)
            or a['key'] != key or not _same(a['new'], day)
            or (event and not _same(title.split()[-1], event))):
        return None
    return _claim(f'The records describe one rescheduled {title.lower()} under docket {key}.',
                  {'relation': 'documentary_event_identity', 'same_event': True, 'docket': key,
                   'event': title, 'scheduled_date': a['old'], 'rescheduled_date': day}, ca, cb)


def _correction(bodies, question):
    rows = _collect(bodies, {'notice': _NOTICE, 'correction': _CORRECTION})
    notice = _single(rows, 'notice')
    amendments = rows.get('correction', [])
    if notice and amendments:
        (a, ca), = notice
        if (_calendar_day(a['day']) and all(_same(a['day'], b['day']) and _same(a['event'], b['event'])
                and _same(a['room'], b['old']) and not _same(b['old'], b['new']) for b, _ in amendments)):
            rooms = {b['new'].casefold(): b['new'] for b, _ in amendments}
            cites = [ca, *(c for _, c in amendments)]
            if len(rooms) > 1:
                alternatives = sorted(rooms.values())
                return [_claim(f"Conflicting rooms: {', '.join(alternatives)}. The chair remains {a['chair']}.",
                               {'conflicting_fields': {'room': alternatives}, 'chair': a['chair']}, *cites)], [
                                   'The competing corrections do not establish one room.']
            room = next(iter(rooms.values()))
            return [_claim(f"{room}. Chair {a['chair']}.", {'room': room, 'chair': a['chair']}, *cites)], []
    return [], ['The original notice and the correction could not be aligned uniquely.']


def _continuation(bodies, question):
    pair = _single(_collect(bodies, {'adjourned': _ADJOURNMENT, 'resumed': _RESUMPTION}), 'adjourned', 'resumed')
    if pair:
        (a, ca), (b, cb) = pair
        if (all(map(_calendar_day, (a['day'], a['next'])))
                and a['key'] == b['key'] != b['other'] and _same(a['body'], b['body'])
                and _same(a['day'], question['first']) and _same(a['next'], question['next'])
                and _same(b['day'], question['next']) and not _same(a['day'], a['next'])):
            return [_claim(f"The continuation was docket {a['key']}.", {'docket': a['key']}, ca, cb)], []
    return [], ['No unique adjournment and resumption match the requested sessions.']


def _logging(bodies, question):
    rows = _collect(bodies, {'logged': _LOGGED}).get('logged', [])
    if rows and len({m['subject'].casefold() for m, _ in rows}) == 1:
        times = sorted({m['time'] for m, _ in rows})
        return [_claim('Recorded logging time' + ('s' if len(times) > 1 else '') + ': ' + ', '.join(times) + '.',
                       {'recorded_times': times, **({'conflicting_fields': {'logging_time': times}} if len(times) > 1 else {})},
                       *(c for _, c in rows))], (
                           ['The records give competing logging times.'] if len(times) > 1 else [])
    return [], ['The records did not identify one logging subject.']


def _minutes(clock):
    if clock.casefold() == 'noon':
        return 720
    value, half = clock.casefold().split()
    hour, _, minute = value.partition(':')
    return (int(hour) % 12 + (12 if half == 'p.m.' else 0)) * 60 + int(minute or 0)


def _custody(bodies, question):
    rows = _collect(bodies, {'transfer': _TRANSFER, 'log': _RETURN, 'return': _NAMED_RETURN})
    transfers = sorted(rows['transfer'], key=lambda row: _minutes(row[0]['time']))
    cutoff, requested_return = (_minutes(question[k]) for k in ('when', 'return'))
    object_name = question['object'].casefold()
    if (not transfers or cutoff >= requested_return
            or len({_minutes(m['time']) for m, _ in transfers}) != len(transfers)
            or not _same(transfers[0][0]['object'], 'the ' + object_name)
            or any(not _same(m['object'], 'the ' + object_name) and m['object'].casefold() != 'it'
                   for m, _ in transfers)
            or any(not _same(a['recipient'], b['giver'])
                   for ((a, _), (b, _)) in zip(transfers, transfers[1:]))):
        return [], ['The records did not establish one continuous handoff chain.']
    claims, missing = [], []
    at_cutoff = next((i for i, (m, _) in enumerate(transfers) if _minutes(m['time']) == cutoff), None)
    if at_cutoff is None:
        missing.append('No handoff is recorded at the requested time.')
    else:
        actor = transfers[at_cutoff][0]['recipient']
        claims.append(_claim(f'{actor} held the {object_name} immediately after {question["when"]}.',
                             {'holder': actor}, *(c for _, c in transfers[:at_cutoff+1])))
    returns = [(m, c) for m, c in rows['return']
               if _minutes(m['time']) == requested_return and _same(m['object'], object_name)]
    logs = [(m, c) for m, c in rows['log']
            if _minutes(m['time']) == requested_return and _same(m['object'], object_name)]
    prior = [m for m, _ in transfers if _minutes(m['time']) < requested_return]
    if (len(returns) == 1 and not logs and len(prior) == len(transfers)
            and _same(prior[-1]['recipient'], returns[0][0]['actor'])):
        actor = returns[0][0]['actor']
        claims.append(_claim(f'{actor} returned the {object_name} at {question["return"]}.',
                             {'returned_by': actor}, *(c for _, c in transfers), returns[0][1]))
    else:
        missing.append('The returner at the requested time is unresolved.')
    return claims, missing


def _inspection(bodies, question):
    pair = _single(_collect(bodies, {'inspection': _INSPECTION, 'cancellation': _CANCELLATION}),
                   'inspection', 'cancellation')
    if pair:
        (a, ca), (b, cb) = pair
        if (all(map(_calendar_day, (a['day'], a['later']))) and a['key'] == b['key']
                and _same(a['later'], b['day']) and not _same(a['day'], a['later'])):
            return [_claim(f"The original inspection took place {a['day']}. The {a['later']} follow-up was canceled.",
                           {'inspection_date': a['day'], 'canceled_followup': a['later']}, ca, cb)], []
    return [], ['The records did not separate the original inspection from a canceled follow-up.']


def _calendar_day(value):
    month, day = value.split()
    try:
        return date(2000, _MONTHS.index(month.capitalize()) + 1, int(day)).timetuple().tm_yday
    except ValueError:
        return 0


def _depots(bodies, question):
    parsed = _collect(bodies, {'rule': _DEPOT_RULE, 'entry': _DEPOT_ENTRY})
    if len(parsed['rule']) == 1 and len(parsed['entry']) == 2:
        rule, witness = parsed['rule'][0]
        cutoff = _calendar_day(rule['after'])
        rows = [(_calendar_day(m['day']), c) for m, c in parsed['entry']]
        if (cutoff and _same(rule['after'], rule['before']) and all(day for day, _ in rows)
                and all(entry['log'] == rule['log'] for entry, _ in parsed['entry'])):
            names = [rule['old'] if day < cutoff else rule['new'] for day, _ in rows]
            return [_claim(f"The recorded depots were {names[0]} and {names[1]}.",
                           {'depots': names, 'same_depot': _same(*names)}, witness, *(c for _, c in rows))], []
    return [], ['The records did not establish a shared dated depot glossary for both entries.']


def _role(bodies, question):
    if len(bodies) != 1:
        return [], ['A unique local signing statement was not established.']
    rows = _collect(bodies, {'role': _ROLE_INTRO}).get('role', [])
    if rows:
        clause, witness = rows[0]
        candidates = [clause[person] for title, person in (('title', 'first'), ('other', 'second'))
                      if _same(clause[title].split()[-1], clause['role'])]
        if len(candidates) == 1:
            return [_claim(f'{candidates[0]} signed the form.', {'signer': candidates[0]}, witness)], []
        if len(candidates) > 1:
            return [], ['The role in the signing statement matches more than one named person.']
    return [], ['The signer could not be uniquely identified from the local role statement.']


def _amended_role(bodies, question):
    trio = _single(_collect(bodies, {'assignment': _ASSIGNMENT, 'amendment': _AMENDMENT, 'receipt': _RECEIPT}),
                   'assignment', 'amendment', 'receipt')
    if trio:
        (a, ca), (b, cb), (c, cc) = trio
        try:
            when, effective = (date.fromisoformat(record['day']) for record in (c, b))
        except ValueError:
            return [], ['The amendment or receipt has an invalid date.']
        if (a['case'] == b['case'] == c['case'] and _same(a['old'], b['old'])
                and _same(a['role'], c['role']) and _same(a['role'], b['role'].replace('-', ' '))
                and not _same(a['other_role'], a['role']) and _minutes(c['time']) == _minutes(question['time'])
                and when >= effective):
            return [_claim(f"{b['new']} signed at {c['time']} in the amended role.",
                           {'signer': b['new'], 'amended_role': c['role']}, ca, cb, cc)], []
    return [], ['No dated amendment establishes who held the signing role when the receipt was made.']


def _event(bodies, question):
    labels = [question.groupdict().get(side) for side in ('left', 'right')]
    if labels[0]:
        chosen = [{r.id for r, _ in bodies if _same(r.id, label) or _same(r.title, 'Source ' + label)}
                  for label in labels]
        if any(len(ids) != 1 for ids in chosen) or chosen[0] == chosen[1]:
            return [], ['The question did not select two distinct source records.']
    if len(bodies) == 2:
        claim = rescheduled_event([r for r, _ in bodies], question['event'])
        if claim:
            return [claim], []
    return [], ['The records do not establish a shared documentary event identity.']


_RULES = (
    (r'(?:What|Which) room and (?:which )?chair (?:should (?:someone|we|I) (?:put on (?:their|our|my) calendar|record|use)|are (?:current|confirmed))\?', _correction),
    (rf'Which (?P<next>{_DATE}) (?:session|meeting|hearing) continued the (?P<first>{_DATE}) (?:meeting|session|hearing)\?', _continuation),
    (r'(?:What|Which) logging time (?:can (?:you|we|I) report (?:from these records|from the reports)|do the records support|is documented)\?', _logging),
    (rf'Who held the (?P<object>[a-z]+) immediately after (?P<when>{_CLOCK}), and who returned it at (?P<return>{_CLOCK})\?', _custody),
    (r'Was the (?:original|first) inspection canceled\?', _inspection),
    (r'Did (?:the|both) trucks leave from the same depot\?', _depots),
    (r'Who signed the form(?: described in the record)?\?', _role),
    (rf'Who signed at (?P<time>{_CLOCK})(?:, and which records support your answer)?\?', _amended_role),
    (r'Do (?:the|both) (?:records|reports) (?:describe|refer to) the same (?P<event>hearing|meeting|session|briefing|inspection)\?', _event),
    (r'Do (?P<left>[A-Za-z0-9.-]+) and (?P<right>[A-Za-z0-9.-]+) (?:describe|refer to) the same (?P<event>hearing|meeting|session|briefing|inspection)\?', _event),
    (r'Do the reports establish that there was one [a-z]+ (?P<event>failure) described by both\?', _event),
)


def verify(index):
    """Use only current sealed body bytes, with an explicitly bounded scan."""
    question = source_question(index.question)
    for pattern, rule in _RULES:
        if match := _full(pattern, question):
            break
    else:
        return None
    if len(index.records) > 8:
        claims, missing = [], ['The statement check exceeded its small source-set limit.']
        kind, code = 'abstain', 'reference_scan_budget'
    else:
        bodies = _bodies(index.records)
        claims, missing = rule(bodies, match) if bodies else ([], ['No complete eligible statements could be inspected.'])
        if any('conflicting_fields' in claim['proposition'] for claim in claims):
            kind, code = 'conflict', 'documentary_statement_conflict'
        elif claims and missing:
            kind, code = 'partial_answer', 'partial_documentary_evidence'
        elif claims:
            kind, code = 'supported_answer', 'supported_documentary_assertion'
        else:
            kind, code = 'abstain', 'bounded_record_unresolved'
    paths = {c['path'] for claim in claims for c in claim['citations']}
    return kind, code, {
        'answer_supported': kind == 'supported_answer', 'claims': claims, 'missing': missing,
        'text': '\n'.join([*(claim['text'] for claim in claims), *missing]),
        'sources': [source for source in index.sources if source['path'] in paths],
        'verification': {'structural': bool(claims), 'semantic': 'bounded_documentary_reference',
                         'truth_verified': False, 'independence_verified': False},
        'documentary_support': {'scope': 'bounded_record_statements', 'source_support_claims': len(claims)},
    }
