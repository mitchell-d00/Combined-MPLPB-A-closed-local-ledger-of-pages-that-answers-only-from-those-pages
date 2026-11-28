"""Verify explicit memorandum responses against one eligible earlier original."""

from datetime import date
import re

from .body_text import body_text
from .documentary_verify import MONTHS, _date_value, citation, context_ranges, source_question
from .passage_admission import Budget
from .source_attribution import unqualified_span


_DAY = rf'(?:{"|".join(MONTHS)}) [0-9]{{1,2}}(?:,? [0-9]{{4}})?'
_NAME_PART = r'[A-Z][a-z]+(?:[A-Z][a-z]+)?'
_FULL_NAME = rf'(?-i:{_NAME_PART}(?: (?:{_NAME_PART}|[A-Z]\.)){{0,3}} {_NAME_PART})'
_NAME = rf'(?:{_FULL_NAME}|(?-i:{_NAME_PART}))'
_HEADER = re.compile(r'(?:(?P<number>[0-9]{1,5})\. )?Memorandum From (?P<writer>[^\n]{2,180}?) to (?P<recipient>[^\n]{2,120})')
_DATELINE = re.compile(rf'[A-Za-z][A-Za-z .-]{{1,70}}, (?P<date>{_DAY})\.')
_REQUESTS = [
    re.compile(form, re.I) for form in (
        rf'Which (?P<target>{_DAY}) memorandum did (?P<writer>{_NAME}) explicitly respond to in (?:his|her|their) (?P<response>{_DAY}) memorandum\?',
        rf'Which memorandum dated (?P<target>{_DAY}) did (?P<writer>{_NAME}) respond to in the memorandum dated (?P<response>{_DAY})\?',
    )
]
_DESCRIPTION = rf'memorandum addressed to you by (?P<author>{_FULL_NAME}) on (?P<date>{_DAY}) (?:on|concerning) (?P<subject>[A-Za-z][A-Za-z0-9 ,’\'()\-]{{1,150}}?)'
_REPLY = re.compile(rf'I am (?:responding|replying) to the {_DESCRIPTION}\.')
_NOTICE = re.compile(rf'A {_DESCRIPTION} has just come to my attention\.')
_REACTION = re.compile(r'I (?:must )?take (?:[a-z]+ ){0,3}exception to its (?:premises|conclusions)(?: and (?:premises|conclusions))?\.')
_EDITORIAL_LINK = re.compile(r'Editorial note: Document (?P<number>[0-9]{1,5})\.')
_MAX_CHARS = 200000
_MAX_LINES = 1000


def request(question):
    question = source_question(question).strip()
    for pattern in _REQUESTS:
        if match := pattern.fullmatch(question):
            target, response = _date_value(match['target']), _date_value(match['response'])
            if target and response:
                return match['writer'], target, response
    return None


def _same_date(asked, actual):
    return all(value is None or actual[key] == value for key, value in asked.items())


def _name_key(value):
    return tuple(part.casefold() for part in value.split() if not re.fullmatch(r'[A-Z]\.', part))


def _named_writer(label, name):
    if _name_key(label) == _name_key(name):
        return True
    if len(name.split()) != 1:
        return False
    return label.endswith(' ('+name+')') or label.endswith(' '+name)


def _verified_lines(record, body, lines, ranges):
    return all(unqualified_span(record, body, *line.span(), ranges=ranges) for line in lines)


def _document(record, body):
    lines = list(re.finditer(r'[^\n]+', body))
    if len(lines) < 3 or record.kind != 'page' or record.derived_from or record.fields.get('corrects-field'):
        return None
    header = _HEADER.fullmatch(lines[0][0])
    if header is None or any(_HEADER.fullmatch(line[0]) for line in lines[1:]):
        return None
    start = 2 if lines[1][0].startswith('Editorial note: Source: ') else 1
    dateline = _DATELINE.fullmatch(lines[start][0])
    written = _date_value(dateline['date']) if dateline else None
    if written is None or written['year'] is None:
        return None
    ranges = context_ranges(record)
    head = [lines[0], lines[start]]
    if not _verified_lines(record, body, head, ranges):
        return None
    return {'record': record, 'body': body, 'header': header, 'date': written,
            'head': head, 'lines': lines[start+1:], 'ranges': ranges}


def _response(document):
    lines = document['lines']
    if not lines:
        return None
    reference = _REPLY.fullmatch(lines[0][0])
    evidence = lines[:1]
    number = None
    if reference is None:
        reference = _NOTICE.fullmatch(lines[0][0])
        if reference is None or len(lines) < 2:
            return None
        offset = 1
        if annotation := _EDITORIAL_LINK.fullmatch(lines[offset][0]):
            number = annotation['number']
            offset += 1
        if len(lines) <= offset or not _REACTION.fullmatch(lines[offset][0]):
            return None
        evidence = lines[:offset+1]
    if not _verified_lines(document['record'], document['body'], evidence, document['ranges']):
        return None
    stated = _date_value(reference['date'])
    return (reference, stated, number, evidence) if stated else None


def _target(document, response, reference, stated, number, requested):
    if (document['record'].path == response['record'].path
            or not _same_date(stated, document['date']) or not _same_date(requested, document['date'])
            or date(**document['date']) >= date(**response['date'])
            or document['header']['recipient'].casefold() != response['header']['recipient'].casefold()
            or (number is not None and document['header']['number'] != number)):
        return None
    lines = document['lines']
    if len(lines) < 2 or lines[0][0] != 'SUBJECT' or lines[1][0].casefold() != reference['subject'].casefold():
        return None
    fields = lines[:2]
    signature = []
    author = reference['author']
    label = document['header']['writer']
    if _name_key(label) != _name_key(author):
        if not label.endswith(' ('+author.split()[-1]+')'):
            return None
        signature = [line for line in lines[2:] if re.fullmatch(_FULL_NAME, line[0])
                     and _name_key(line[0]) == _name_key(author)]
        if len(signature) != 1:
            return None
    if not _verified_lines(document['record'], document['body'], fields+signature, document['ranges']):
        return None
    return [fields, signature]


def _citations(document, groups):
    return [citation(document['record'], document['body'], group[0].start(), group[-1].end())
            for group in groups if group]


def verify(index, max_passages, max_chars):
    goal = request(index.question)
    if goal is None:
        return None
    writer, target_date, response_date = goal
    support = {'scope': 'documentary_response_target', 'original_question': index.question,
               'source_support_claims': 0, 'response_stage': 'response_verification'}
    result = {'documentary_support': support}
    bodies = [(record, body_text(record.body_html)) for record in index.records]
    if (sum(len(body) for _, body in bodies) > _MAX_CHARS
            or sum(body.count('\n')+1 for _, body in bodies) > _MAX_LINES):
        support['response_stage'] = 'scan_budget'
        return 'abstain', 'reference_scan_budget', result
    documents = [doc for record, body in bodies if (doc := _document(record, body))]
    selected = [doc for doc in documents if _same_date(response_date, doc['date'])
                and _named_writer(doc['header']['writer'], writer)]
    if len(selected) != 1 or (relation := _response(selected[0])) is None:
        return 'abstain', 'documentary_response_unverified', result
    response = selected[0]
    reference, date_mentioned, number, witnesses = relation
    support['response_stage'] = 'target_verification'
    targets = [(doc, evidence) for doc in documents if
               (evidence := _target(doc, response, reference, date_mentioned, number, target_date))]
    if len(targets) != 1:
        return 'abstain', 'documentary_response_target_unverified', result
    target, fields = targets[0]
    spans = (_citations(response, [[line] for line in response['head']+witnesses]) +
             _citations(target, [[line] for line in target['head']]+fields))
    budget = Budget(index, max_passages, max_chars)
    if not budget.offer(spans, 'exact_documentary_response_witnesses'):
        support['response_stage'] = 'display_budget'
        return 'abstain', 'reader_budget_exceeded', result
    if not index.unchanged():
        return 'abstain', 'source_changed', {}
    proposition = {
        'relation': 'documentary_response_target',
        'response_source_id': response['record'].id,
        'target_source_id': target['record'].id,
        'target_date': date(**target['date']).isoformat(),
        'target_writer_as_named': reference['author'],
        'target_subject': reference['subject'],
        'historical_truth_independently_verified': False,
    }
    text = ('The cited memorandum explicitly responds to the earlier memorandum by '
            + reference['author'] + ' on ' + reference['subject'] + '.')
    qualifier = 'The cited statements identify the documentary response target. Authorship, agreement, receipt and execution remain unverified.'
    support.update(response_stage='proved', source_support_claims=1, admission=budget.report())
    result.update(answer_supported=True, text=text, missing=[],
                  claims=[{'proposition': proposition, 'citations': spans, 'text': text,
                           'source_support_established': True, 'qualifiers': [qualifier]}],
                  sources=[s for s in index.sources
                           if s['path'] in {response['record'].path, target['record'].path}],
                  verification={'structural': True, 'semantic': 'bounded_documentary_response',
                                'truth_verified': False, 'independence_verified': False})
    return 'supported_answer', 'supported_documentary_assertion', result
