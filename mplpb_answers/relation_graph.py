"""Finite, auditable question-to-body relation graph.

A graph edge is licensed by a complete declarative source sentence, never by
scope, search rank, inferred synonyms or the question alone. No multi-hop world
inference, general-language understanding or procedure execution is implied.
"""
from dataclasses import dataclass
import re

from .body_text import body_text
from .frames import normalize
from .literal_evidence import LiteralRequest

VERSION = 'source-relation-graph-v1'
WORD = r'[a-z][a-z0-9-]*'
PHRASE = rf'{WORD}(?: {WORD}){{0,7}}'
CODE = r'[a-z0-9-]{1,12}'
NUMBER = r'(?:\d+(?:\.\d+)?|a|an|one|two|three|four|five|six|ten|half|quarter)'
UNIT = r'(?:teaspoons?|tablespoons?|grams?|kilograms?|milligrams?|litres?|liters?|millilitres?|milliliters?|cups?|drops?|pinches?|scoops?)'
DURATION = rf'{NUMBER} (?:minutes?|hours?|days?|weeks?|months?)'
BAD_SOURCE = re.compile(
    r'["“”]|\b(?:imagine|suppose|assume|pretend|ignore|hypothetical|'
    r'fictional|example only|draft instruction|perhaps|maybe|possibly|'
    r'probably|allegedly|reportedly)\b', re.I
)
BAD_REQUEST = re.compile(
    r'[;"“”]|\b(?:not|never|unless|if|before repairs|after repairs|'
    r'tomorrow|yesterday|currently|formerly|possibly|maybe|allegedly)\b'
)
# Scoped before-action duration is deliberately more restrictive than a general
# how-long question. A pronoun alone cannot supply its missing subject.
QUERY_FORMS = (
    ('code_purpose', rf'what is (?:the )?(?:bag )?code (?P<entity>{CODE}) for'),
    ('additive_amount', rf'how much (?P<entity>{PHRASE})'),
    ('action_duration', rf'how long should (?:i|we) (?P<action>{WORD}) (?P<entity>{PHRASE}) before (?P<other>{WORD})'),
)


@dataclass(frozen=True)
class RelationRequest(LiteralRequest):
    def to_dict(self):
        return dict(super().to_dict(), version=VERSION, graph_type='source_body_only',
                    world_verified=False, execution_verified=False,
                    inference_permitted=False, qualified_quote_required=True)


def parse(question):
    q = normalize(question)
    if len(q) > 200 or BAD_REQUEST.search(q) or re.search(r'[?!:,.]', q):
        return None
    for relation, grammar in QUERY_FORMS:
        match = re.fullmatch(grammar, q)
        if match:
            values = match.groupdict()
            return RelationRequest(relation, values['entity'], q,
                                   values.get('other') or values.get('action') or '')
    return None


def _evidence(frame, line):
    """Return (value, qualification) only for a complete licensed assertion."""
    if frame.relation == 'code_purpose':
        code = re.escape(frame.entity)
        match = re.fullmatch(
            rf'(?P<name>{PHRASE}), (?:bag code )?{code}, is for (?P<value>.+)',
            line)
        if not match:
            match = re.fullmatch(
                rf'bag code {code} is for (?P<value>.+)', line)
        if match:
            value = match['value']
            if re.search(r'\b(?:not|never|unknown|might|could|should)\b', value):
                return None
            return value, ''
    elif frame.relation == 'additive_amount':
        entity = re.escape(frame.entity)
        # A conditional instruction may answer an amount question *only* if
        # the whole original conditional sentence is quoted. It must not be
        # restated as unconditional advice.
        pattern = (rf'(?:(?:if|when) (?P<condition>[^,;.!?]{{3,120}}), )?'
                   rf'add (?P<value>{NUMBER} {UNIT}) of {entity}'
                   rf'(?: (?P<tail>and .+|to .+|before .+))?')
        match = re.fullmatch(pattern, line)
        if match:
            return match['value'], (match['condition'] or '') + '|' + (match['tail'] or '')
    elif frame.relation == 'action_duration':
        # The entity and action must be explicitly stated in the SAME sentence;
        # "let it slake" does not establish what "it" refers to.
        action, entity, following = frame.other, re.escape(frame.entity), ''
        # "other" in LiteralRequest stores one field only: an action-specific
        # frame below uses an exact before action parsed from canonical.
        m = re.fullmatch(
            rf'how long should (?:i|we) (?P<action>{WORD}) (?P<entity>{PHRASE}) before (?P<next>{WORD})',
            frame.canonical)
        if m:
            action, following = m['action'], m['next']
        if not following:
            return None
        pattern = (rf'(?:let|leave|allow) (?:the )?{entity} '
                   rf'(?:to )?{re.escape(action)} for (?P<value>{DURATION}) '
                   rf'before {re.escape(following)}(?: (?P<tail>.+))?')
        match = re.fullmatch(pattern, line)
        if match:
            return match['value'], match['tail'] or ''
    return None


def _graph(frame, record, spans):
    """Bounded explicit proof graph. IDs are stable per evaluated page/query."""
    nodes = [
        {'id': 'q', 'kind': 'question', 'text': frame.canonical},
        {'id': 'p', 'kind': 'predicate', 'text': frame.relation},
        {'id': 's', 'kind': 'entity', 'text': frame.entity},
        {'id': 'doc', 'kind': 'source', 'record_id': record.id,
         'hash': record.hash, 'path': record.path},
    ]
    edges = [
        {'from': 'q', 'to': 'p', 'type': 'asks'},
        {'from': 'p', 'to': 's', 'type': 'targets'},
    ]
    for i, span in enumerate(spans):
        fact, value, condition = f'fact:{i}', f'value:{i}', f'qualifier:{i}'
        nodes.extend([
            {'id': fact, 'kind': 'statement', 'quote': span['quote']},
            {'id': value, 'kind': 'value', 'text': span['value']},
        ])
        edges.extend([
            {'from': 'doc', 'to': fact, 'type': 'declares'},
            {'from': fact, 'to': 'p', 'type': 'asserts_relation'},
            {'from': fact, 'to': 's', 'type': 'asserts_subject'},
            {'from': fact, 'to': value, 'type': 'supplies_value'},
        ])
        if span.get('qualification'):
            nodes.append({'id': condition, 'kind': 'qualification',
                          'text': span['qualification']})
            edges.append({'from': fact, 'to': condition,
                          'type': 'qualified_by'})
    return {'version': VERSION, 'nodes': nodes, 'edges': edges,
            'proof_kind': 'exact_source_statement',
            'independent_sources_verified': False,
            'world_verified': False, 'execution_verified': False,
            'multi_hop_inference': False}


def statement_support(frame, record):
    text = body_text(record.body_html)
    if BAD_SOURCE.search(text) or re.search(
            r'(?m)^\s*(?:if|unless|assuming|example|draft)\b[^.!?\n]{0,120}:\s*$',
            text, re.I):
        return {'status': 'unsupported', 'spans': [],
                'reason': 'Hypothetical, reported or inherited source context.'}
    spans = []
    for raw in re.split(r'(?<=[.!?])\s+|\n+', text):
        raw = raw.strip()
        if not raw:
            continue
        line = normalize(raw)
        found = _evidence(frame, line)
        if not found:
            continue
        value, qualification = found
        if not value or re.search(
                r'\b(?:unknown|not|never|perhaps|maybe|probably|reportedly)\b',
                value):
            continue
        spans.append({'quote': raw, 'value': value,
                      'qualification': qualification})
    # Different qualifications are different assertions, even if the numeric
    # quantities agree: never let an unconditional claim erase a condition.
    keys = {(s['value'], s['qualification']) for s in spans}
    status = 'conflict' if len(keys) > 1 else 'supported' if spans else 'unsupported'
    result = {
        'status': status, 'spans': spans, 'graph': _graph(frame, record, spans),
        'reason': 'Exact source-declared relation path; source truth and procedure execution not verified.',
    }
    return result
