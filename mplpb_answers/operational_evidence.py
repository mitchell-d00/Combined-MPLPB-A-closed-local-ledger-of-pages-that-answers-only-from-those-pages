"""Two source-bound operational relations: exact conditional and separation facts.

These are finite source assertions, not procedural execution, world verification, or
a semantic fallback. In particular no scope, document title or rank is evidence.
Questions and antecedents must be complete: no synonym or pronoun guessing.
"""
from dataclasses import dataclass
import re

from .body_text import body_text
from .frames import normalize
from .literal_evidence import LiteralRequest

VERSION = 'operational-relations-v1'

_NOUN = r'[a-z][a-z0-9-]*(?: [a-z][a-z0-9-]*){0,2}'
_UNSAFE_QUESTION = re.compile(r'[;"“”]|\b(?:perhaps|maybe|possibly|probably|supposedly|allegedly)\b')
_UNSAFE_SOURCE = re.compile(
    r'(^|[.!?]\s+|\n)(?:imagine|suppose|assume|pretend|ignore|'
    r'example|hypothetical|draft|perhaps|maybe|possibly|probably)\b|["“”]', re.I
)
_UNSAFE_CONSEQUENT = re.compile(
    r'\b(?:perhaps|possibly|maybe|probably|allegedly|reportedly|'
    r'supposedly|unknown|unrecorded|hypothetical)\b', re.I
)


@dataclass(frozen=True)
class OperationalRequest(LiteralRequest):
    def to_dict(self):
        return dict(super().to_dict(), version=VERSION,
                    answer_kind='source_declaration', world_verified=False,
                    execution_verified=False, entailment_general=False)


def parse(question):
    q = normalize(question)
    if _UNSAFE_QUESTION.search(q):
        return None
    match = re.fullmatch(r'(?:what does it mean|what happens) if (?P<condition>.+)', q)
    if match:
        condition = match['condition']
        if not 4 <= len(condition) <= 140 or not re.search(r'[a-z]', condition):
            return None
        if re.search(r'[?!:,.]|\b(?:or else|as an example)\b', condition):
            return None
        return OperationalRequest('conditional_outcome', condition, q)
    match = re.fullmatch(
        rf'which (?P<entity>{_NOUN}) (?:must|should) be kept in separate (?P<other>{_NOUN})',
        q)
    if match and len(q) <= 160 and not re.search(r'\b(?:not|never|except)\b', q):
        return OperationalRequest('separate_storage', match['entity'], q, match['other'])
    return None


def _condition_key(text):
    # A missing initial article ("guard" / "the guard") is the only
    # normalized variation. Do not delete negation, time, or modal terms.
    return re.sub(r'^the ', '', normalize(text))


def statement_support(frame, record):
    context = body_text(record.body_html)
    if _UNSAFE_SOURCE.search(context) or re.search(r'(?m)^\s*if [^\n.!?]{0,100}:\s*
        return {'status': 'unsupported', 'spans': [],
                'reason': 'Hypothetical/instructional or quoted page context.'}
    spans = []
    unresolved = False
    for raw in re.split(r'(?<=[.!?])\s+|\n+', context):
        raw = raw.strip()
        if not raw:
            continue
        line = normalize(raw)
        if frame.relation == 'conditional_outcome':
            # Every bit of the antecedent must be present. In particular:
            # if the alarm is ON != if the alarm is NOT on.
            match = re.fullmatch(r'if (?P<condition>[^,;:]+), (?P<outcome>.+)', line)
            if not match or _condition_key(match['condition']) != _condition_key(frame.entity):
                continue
            outcome = match['outcome']
            if len(outcome) < 4 or _UNSAFE_CONSEQUENT.search(outcome):
                unresolved = True
                continue
            spans.append({'quote': raw, 'value': outcome})
        elif frame.relation == 'separate_storage':
            entity, container = map(re.escape, (frame.entity, frame.other))
            match = re.fullmatch(
                rf'(?:keep|store) (?P<value>[a-z0-9-]+(?: [a-z0-9-]+){{0,12}}) '
                rf'{entity} in separate {container}(?:[;,] .+)?', line)
            if not match:
                continue
            # Full sentence is returned: even a semicolon qualification remains.
            value = match['value']
            if re.search(r'\b(?:no|not|never|maybe|possibly|hypothetical)\b', value):
                unresolved = True
                continue
            spans.append({'quote': raw, 'value': value})
    values = {span['value'] for span in spans}
    status = ('conflict' if len(values) > 1 else
              'supported' if spans and not unresolved else 'unsupported')
    return {'status': status, 'spans': spans, 'unresolved': unresolved,
            'reason': 'Complete body conditional or separation instruction, quoted as a source declaration; not certified advice.'}
, context, re.I):
        return {'status': 'unsupported', 'spans': [],
                'reason': 'Hypothetical/instructional or quoted page context.'}
    spans = []
    unresolved = False
    for raw in re.split(r'(?<=[.!?])\s+|\n+', context):
        raw = raw.strip()
        if not raw:
            continue
        line = normalize(raw)
        if frame.relation == 'conditional_outcome':
            # Every bit of the antecedent must be present. In particular:
            # if the alarm is ON != if the alarm is NOT on.
            match = re.fullmatch(r'if (?P<condition>[^,;:]+), (?P<outcome>.+)', line)
            if not match or _condition_key(match['condition']) != _condition_key(frame.entity):
                continue
            outcome = match['outcome']
            if len(outcome) < 4 or _UNSAFE_CONSEQUENT.search(outcome):
                unresolved = True
                continue
            spans.append({'quote': raw, 'value': outcome})
        elif frame.relation == 'separate_storage':
            entity, container = map(re.escape, (frame.entity, frame.other))
            match = re.fullmatch(
                rf'(?:keep|store) (?P<value>[a-z0-9-]+(?: [a-z0-9-]+){{0,12}}) '
                rf'{entity} in separate {container}(?:[;,] .+)?', line)
            if not match:
                continue
            # Full sentence is returned: even a semicolon qualification remains.
            value = match['value']
            if re.search(r'\b(?:no|not|never|maybe|possibly|hypothetical)\b', value):
                unresolved = True
                continue
            spans.append({'quote': raw, 'value': value})
    values = {span['value'] for span in spans}
    status = ('conflict' if len(values) > 1 else
              'supported' if spans and not unresolved else 'unsupported')
    return {'status': status, 'spans': spans, 'unresolved': unresolved,
            'reason': 'Complete body conditional or separation instruction, quoted as a source declaration; not certified advice.'}
