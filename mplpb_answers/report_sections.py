"""Locate explicit report sections and verify complete source-attributed units."""
import re

from .body_text import body_text
from .documentary_verify import citation, context_ranges, normalized, quoted_context, relationship_assertion, units


_NUMBERED = r'[ \t]*(?:[1-9][0-9]?|I)\.[ \t]*0[ \t]*'
_HEADING = re.compile(r'^' + _NUMBERED + r'\n(?:[ \t]*\n)*[ \t]*SUMMARY[ \t]*\n'
                      r'(?:[ \t]*\n)*(?P<first>[^\n]+)', re.M | re.I)
_NEXT = re.compile(r'^' + _NUMBERED + r'\n(?:[ \t]*\n)*[ \t]*[A-Z][A-Z \t]+$', re.M)
_LIMIT = 2400
_NAMED_SUMMARY = re.compile(r'According to (?:the )?(?P<report>[^,?!;]{1,120}?) summary,\s+(?P<body>.+)', re.I)
_CAUSE_RESOURCE = re.compile(
    r'why was (?P<event>[^,?!;]{2,100}) (?P<action>aborted|canceled|cancelled|halted|terminated)'
    r' and what (?:spacecraft|vehicle|equipment|resource|system) supported return to (?P<place>[^,?!;]{2,80})\?', re.I,
)


def summary_span(body):
    """Find a unique numbered summary followed by a prose line."""
    heads = [m for m in _HEADING.finditer(body)
             if len(re.findall(r'\b[a-z]{2,}\b', m['first'])) >= 6]
    if len(heads) != 1:
        return None
    start = heads[0].start('first')
    following = _NEXT.search(body, heads[0].end())
    end = min(len(body), start + _LIMIT, following.start() if following else len(body))
    return start, end


def request(question):
    named = _NAMED_SUMMARY.fullmatch(question.strip())
    if named and (goals := _CAUSE_RESOURCE.fullmatch(named['body'])):
        return {'report': named['report'], **goals.groupdict()}
    return None


def _named_report(record, body, name):
    labels = [record.title, *body[:1800].splitlines()[:36]]
    name = r'(?<!\w)' + re.escape(normalized(name)) + r'(?!\w)'
    return any(len(label) <= 150 and re.search(r'\breport\b', label, re.I)
               and re.search(name, normalized(label)) for label in labels)


def locate(index, name):
    """Return one eligible document-to-summary edge based on explicit labels."""
    owners = []
    for record in index.records:
        body = body_text(record.body_html)
        if _named_report(record, body, name):
            owners.append((record, body))
    if len(owners) == 1:
        record, body = owners[0]
        if span := summary_span(body):
            return record, body, span
    return None


def verify(index, goals):
    located = locate(index, goals['report'])
    if located is None:
        return None
    record, body, (start, end) = located
    region = body[start:end]
    blocked = context_ranges(record)
    if (record.fields.get('corrects-field') or any(lo < end and hi > start for lo, hi in blocked)
            or re.search(r'\b(?:retracted|rescinded|superseded|erratum)\b|'
                         r'\bcorrection to (?:this|the|our) (?:report|summary|record|statement)\b',
                         region, re.I)):
        return None
    cause, resource = [], []
    event = re.sub(r'^(?:the|a|an) ', '', normalized(goals['event']))
    place = normalized(goals['place'])
    report = normalized(goals['report'])
    for lo, hi, quote in units(region):
        # Exclude a unit clipped by the section window and any local quoted or
        # conditional context. The named graph edge has no bearing on support.
        if ((hi == len(region) and end < len(body)) or quoted_context(region[:lo])
                or re.search(r'\b(?:if|unless)\b', region[max(0, lo - 120):lo], re.I)):
            continue
        value = relationship_assertion(quote)
        if value is None:
            continue
        cite = citation(record, body, start + lo, start + hi)
        if value['relation'] == 'source_causal_assertion':
            subject = normalized(value['subject_text'])
            exact_event = (re.search(r'(?<!\w)' + re.escape(event) + r'(?!\w)', subject)
                           and re.search(r'(?<!\w)' + re.escape(report) + r'(?!\w)', subject))
            if exact_event and value['action_text'] == normalized(goals['action']):
                cause.append((value, cite))
        elif value['relation'] == 'source_resource_assertion':
            if re.search(r'\breturn to ' + re.escape(place) + r'(?!\w)', normalized(value['purpose_text'])):
                resource.append((value, cite))
    claims = []
    for rows in (cause, resource):
        if len(rows) == 1 and not rows[0][0]['negative']:
            value, cite = rows[0]
            claims.append({'text': cite['quote'], 'proposition': value, 'citations': [cite],
                           'source_support_established': True,
                           'qualifiers': ['Explicit statement in the named report summary.']})
    if not claims:
        return None
    missing = ['Only explicit statements within the bounded summary window were checked. '
               'Event co-reference, corrections outside this window, and independent causation remain unresolved.']
    if len(claims) < 2:
        missing.append('The summary did not establish a unique explicit statement for both requested parts.')
    return {
        'kind': 'partial_answer', 'code': 'partial_documentary_evidence',
        'answer_supported': False, 'claims': claims, 'missing': missing,
        'text': '\n'.join([*(c['text'] for c in claims), *missing]),
        'sources': [s for s in index.sources if s['path'] == record.path],
        'verification': {'structural': True, 'semantic': 'bounded_documentary_reference',
                         'truth_verified': False, 'independence_verified': False},
        'documentary_support': {
            'scope': 'named numbered report summary only', 'source_support_claims': len(claims),
            'section_edge': {'source_id': record.id, 'hash': record.hash_actual, 'start': start, 'end': end,
                             'source_support_established': False},
        },
    }
