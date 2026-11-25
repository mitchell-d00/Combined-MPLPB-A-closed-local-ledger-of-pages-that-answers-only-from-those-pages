"""Partial source proof for named advice in a two-obligation question."""
import re

from .body_text import body_text
from .documentary_verify import (META, citation, context_ranges, possible_refutation,
                                 quoted_context, source_question, units)

_NAME = r'(?-i:[A-Z][a-z]+(?: [A-Z][a-z]+){0,2})'
_TOPIC = r'[a-z]+(?:[ -][a-z]+){0,4}'
_TITLE = r'(?:Mr\. |Ms\. |Mrs\. |Dr\. |Secretary |Director |Minister )?'
_QUESTION = re.compile(
    rf'What (?P<topic>{_TOPIC}) emphasis did (?P<adviser>{_NAME}) (?:suggest|recommend) to '
    rf'(?P<recipient>{_NAME}) before (?:his|her|their) (?P<trip>{_TOPIC}) trip, '
    r'and what framework did (?P=recipient) say (?:he|she|they) '
    r'presented in (?:his|her|their) meetings\?', re.I)
_ADVICE = re.compile(
    rf'^{_TITLE}(?P<adviser>{_NAME}) (?:suggested|recommended) that '
    rf'{_TITLE}(?P<recipient>{_NAME}) (?:stress|emphasize) '
    rf"""(?P<emphasis>[\w “’”'"-]{{3,140}}?) in (?P<topic>{_TOPIC})\.""", re.I | re.M)
_DENIAL = re.compile(
    rf'^{_TITLE}(?P<adviser>{_NAME}) (?:did not (?:suggest|recommend)|never (?:suggested|recommended)) that '
    rf'{_TITLE}(?P<recipient>{_NAME}) (?:stress|emphasize) [^.\n]{{1,180}} in (?P<topic>{_TOPIC})\.',
    re.I | re.M)
_TRIP = re.compile(
    rf'(?:^|(?<=\. ))The focus of the discussion was {_TITLE}(?P<traveler>{_NAME})(?:[’\']s|(?<=s)[’\']) upcoming '
    rf'(?:(?P<descriptor>{_TOPIC}) trip|trip to (?:the )?(?P<destination>{_NAME}))\.(?=\]?$)', re.I)
_UNCERTAIN = re.compile(
    r'\b(?:allegedly|claimed|did not|if|unless|possibly|might|would|never|reported|'
    r'hypothetical|example|not|may|or|except|only)\b', re.I)
_DESTINATIONS = {'african': 'africa', 'asian': 'asia', 'european': 'europe',
                 'north american': 'north america', 'south american': 'south america',
                 'australian': 'australia', 'antarctic': 'antarctica'}
_MAX_RECORDS = 8
_MAX_CHARACTERS = 200_000
_MAX_UNITS = 1_000


def _normalized(text):
    return ' '.join(text.casefold().replace('-', ' ').split())


def _prior_trip(body, start, request):
    preceding = body[:start].rstrip()
    line = preceding.rsplit('\n', 1)[-1]
    match = _TRIP.search(line)
    if not match or _normalized(match['traveler']) != _normalized(request['recipient']):
        return None
    requested = _normalized(request['trip'])
    actual = _normalized(match['descriptor'] or match['destination'])
    if match['destination']:
        requested = _DESTINATIONS.get(requested, requested)
    if requested != actual:
        return None
    base = len(preceding) - len(line)
    return base + match.start(), base + match.end()


def _same_advice(match, request):
    return all(_normalized(match[field]) == _normalized(request[field])
               for field in ('adviser', 'recipient', 'topic'))


def _witnesses(index, request):
    if len(index.records) > _MAX_RECORDS or sum(len(r.body_html) for r in index.records) > _MAX_CHARACTERS:
        return 'reference_scan_budget', None
    matches = []
    competing = False
    remaining = _MAX_UNITS
    for record in index.records:
        body = body_text(record.body_html)
        # Record all competing native advice forms before selecting a witness.
        for _ in units(body):
            remaining -= 1
            if remaining < 0:
                return 'reference_scan_budget', None
        if record.kind != 'page' or record.derived_from or record.fields.get('corrects-field'):
            continue
        competing |= possible_refutation(body) or any(
            _same_advice(denial, request) for denial in _DENIAL.finditer(body))
        matches.extend((record, body, match) for match in _ADVICE.finditer(body)
                       if _same_advice(match, request))
    if competing or len(matches) != 1:
        return 'named_advice_unresolved', None
    record, body, advice = matches[0]
    trip = _prior_trip(body, advice.start(), request)
    if (trip is None or _UNCERTAIN.search(advice['emphasis'])
            or quoted_context(advice['emphasis']) or quoted_context(body[:trip[0]])
            or META.search(body[:advice.start()])
            or any(lo < advice.end() and hi > trip[0] for lo, hi in context_ranges(record))):
        return 'named_advice_unresolved', None
    return 'partial_documentary_evidence', (advice.groupdict(), [
        citation(record, body, *trip), citation(record, body, advice.start(), advice.end())])


def verify(index, max_passages, max_chars):
    request = _QUESTION.fullmatch(source_question(index.question))
    if not request:
        return None
    code, proof = _witnesses(index, request)
    if not proof:
        return 'abstain', code, {}
    advice, witnesses = proof
    if len(witnesses) > max_passages or sum(len(c['quote']) for c in witnesses) > max_chars:
        return 'abstain', 'reader_budget_exceeded', {}
    text = 'The record reports this advice before the trip described as upcoming. ' + witnesses[1]['quote']
    missing = 'The separately reported presentation remains unresolved.'
    claim = {'text': text, 'proposition': {'relation': 'source_named_advice_report',
        'adviser': advice['adviser'], 'recipient': advice['recipient'],
        'topic': _normalized(advice['topic']), 'emphasis': advice['emphasis'],
        'modality': 'reported_advice',
        'chronology': 'trip_upcoming_in_cited_discussion'},
        'citations': witnesses, 'source_support_established': True,
        'qualifiers': ['The document reports advice. Trip occurrence and implementation remain unresolved.']}
    return 'partial_answer', code, {
        'claims': [claim], 'answer_supported': False, 'text': text + '\n' + missing,
        'missing': [missing], 'sources': [s for s in index.sources if s['path'] == witnesses[0]['path']],
        'verification': {'structural': True, 'semantic': 'bounded_documentary_reference',
                         'truth_verified': False, 'independence_verified': False},
        'documentary_support': {'scope': 'named_advice_report', 'source_support_claims': 1},
    }
