"""Source-attributed reading of an explicit, named statutory lease clause."""
import re

from .body_text import body_text
from .documentary_verify import citation, context_ranges, normalized, source_question, units


_NAME = r'(?P<name>[a-z0-9][a-z0-9 \-]{1,79}?)'
_QUESTIONS = (
    rf'Does the {_NAME} (?:law|act|statute) make leasing compulsory, or grant discretion subject to a term limit\?',
    rf'Is leasing mandatory under the {_NAME} (?:law|act|statute), or discretionary with a maximum term\?',
)
_CLAUSE = re.compile(
    r'The [a-z ]{1,60} may,? in (?:his|her|its|their) discretion,? grant leases '
    r'for [a-z ]{1,100}? for terms (?:not exceeding|of no more than) '
    r'(?P<limit>[a-z0-9-]{1,30} (?:years|months))(?=[ ,.\;])[^.!?]*\.',
    re.I,
)


def request(question):
    for shape in _QUESTIONS:
        match = re.fullmatch(shape, source_question(question), re.I)
        if match:
            return normalized(match['name'])
    return None


def _named_act(record, body, name):
    # Imported records can have neutral wrapper titles. Admit a document label
    # from its early body lines too, including an explicit navigation title.
    labels = [record.title, *body[:1200].splitlines()[:32]]
    key = r'(?<!\w)' + re.escape(name) + r'(?!\w)'
    for label in labels:
        label = normalized(label.removeprefix('Home > '))
        if (len(label) <= 140 and not re.search(r'[;:!?]', label)
                and re.search(r'\b(?:act|law|statute)\b', label) and re.search(key, label)):
            return True
    return False


def verify(index, name):
    candidates = []
    for record in index.records:
        body = body_text(record.body_html)
        if _named_act(record, body, name):
            candidates.append((record, body))
    if len(candidates) != 1:
        return None
    record, body = candidates[0]
    if len(body) > 100000:
        return None
    regions = context_ranges(record)
    headings = list(re.finditer(r'^Transcript[ \t]*\n', body[:6000], re.I | re.M))
    if len(headings) > 1:
        return None
    offset = headings[0].end() if headings else 0
    matches = []
    for start, end, text in units(body[offset:]):
        start, end = start + offset, end + offset
        if end - start > 1600 or any(lo < end and hi > start for lo, hi in regions):
            continue
        clause = _CLAUSE.fullmatch(' '.join(text.split()))
        if clause:
            matches.append((clause['limit'], citation(record, body, start, end)))
    rival = r'\b(?:shall|must|may not|shall not) (?:grant|issue) leases\b'
    if len(matches) != 1 or re.search(rival, body, re.I):
        return None
    limit, cite = matches[0]
    claim = {'text': 'The cited clause grants discretion to issue the specified leases, with terms not exceeding '
             + limit + '.', 'qualifiers': ['The conclusion applies to the permission in the cited clause.'],
             'proposition': {'relation': 'source_discretionary_lease_with_term_ceiling', 'term_ceiling_text': limit},
             'source_support_established': True, 'citations': [cite]}
    return {
        'kind': 'supported_answer', 'code': 'supported_documentary_assertion',
        'answer_supported': True, 'text': claim['text'], 'claims': [claim],
        'sources': [s for s in index.sources if s['path'] == record.path],
        'verification': {'structural': True, 'semantic': 'bounded_documentary_reference',
                         'truth_verified': False, 'independence_verified': False},
        'documentary_support': {'scope': 'one named statute and one explicit clause',
                                'source_support_claims': 1},
    }
