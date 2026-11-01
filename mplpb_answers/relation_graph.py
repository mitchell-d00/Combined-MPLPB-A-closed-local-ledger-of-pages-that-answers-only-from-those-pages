"""Finite, auditable question-to-body relation graph.

A graph edge is licensed by a complete declarative source sentence, never by
scope, search rank, inferred synonyms or the question alone. No multi-hop world
inference, general-language understanding or procedure execution is implied.
"""
from dataclasses import dataclass
import hashlib
import json
import re
from datetime import date

from .body_text import body_text
from .frames import normalize
from .literal_evidence import LiteralRequest

VERSION = 'source-relation-graph-v1'
WORD = r'[a-z][a-z0-9-]*'
PHRASE = rf'{WORD}(?: {WORD}){{0,7}}'
CODE = r'[a-z0-9-]{1,12}'
NUMBER = r'(?:\d+(?:\.\d+)?|a|an|one|two|three|four|five|six|ten|fifteen|twenty|thirty|forty|fifty|sixty|half|quarter)'
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
    ('storage_rule', rf'where should (?:i|we) store (?P<entity>{PHRASE})'),
    ('responsibility', rf'who is responsible for (?P<entity>{PHRASE})'),
    ('due_date', rf'when is (?P<entity>{PHRASE}) due'),
    ('recorded_status', rf'(?:what is the status of|what status is recorded for) (?P<entity>{PHRASE})'),
    ('storage_rule', rf'where (?:do|should) (?:i|we) (?:store|keep) (?P<entity>{PHRASE})'),
    ('storage_rule', rf'where should (?P<entity>{PHRASE}) be stored'),
    ('responsibility', rf'who has responsibility for (?P<entity>{PHRASE})'),
    ('due_date', rf'what is the due date for (?P<entity>{PHRASE})'),
    ('due_date', rf'what date is (?P<entity>{PHRASE}) due'),
    ('location', rf'where is (?P<entity>{PHRASE}) located'),
    ('contents', rf'what does (?P<entity>{PHRASE}) contain'),
    ('scheduled_date', rf'when is (?P<entity>{PHRASE}) scheduled'),

    ('cause', rf'what causes (?P<entity>{PHRASE})'),
    ('inspection_method', rf'how do i check (?:the )?(?P<entity>{PHRASE}) with (?:a |the )?(?P<other>{PHRASE})'),
    ('required_time', rf'how long does (?P<entity>{PHRASE}) need'),
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
    q = re.sub(r'^(?:please,? |can you tell me |could you tell me )', '', normalize(question))
    if len(q) > 200 or BAD_REQUEST.search(q) or re.search(r'[?!:,.]', q):
        return None
    alternatives = re.fullmatch(
        r"(?P<left>[a-z][a-z' -]{1,39}) or (?P<right>[a-z][a-z' -]{1,39})",
        q)
    if alternatives:
        left, right = alternatives['left'].strip(), alternatives['right'].strip()
        if left != right and len(left.split()) <= 4 and len(right.split()) <= 4:
            return RelationRequest('alternative_context', left, q, right)
    for relation, grammar in QUERY_FORMS:
        match = re.fullmatch(grammar, q)
        if match:
            values = match.groupdict()
            entity = re.sub(r'^the ', '', values['entity'])
            return RelationRequest(relation, entity, q,
                                   values.get('other') or values.get('action') or '')
    return None


def _evidence(frame, line):
    """Return (value, qualification) only for a complete licensed assertion."""
    # Unqualified inventory, responsibility and storage questions cannot
    # license an assertion that holds only under a stated condition.
    if (frame.relation in {'storage_rule', 'responsibility', 'due_date',
                           'recorded_status', 'location', 'contents',
                           'scheduled_date'}
            and re.search(r'\b(?:if|unless|except|provided|until|whenever)\b',
                          line)):
        return None
    if frame.relation == 'alternative_context':
        left, right = map(re.escape, (frame.entity, frame.other))
        match = re.fullmatch(
            rf'{left} for (?P<leftcase>[^,;]+), {right} for (?P<rightcase>[^,;]+)',
            line)
        if match and not re.search(
                r'\b(?:not|never|possibly|perhaps|might|could|unknown)\b',
                line):
            return match['leftcase'] + ' | ' + match['rightcase'], ''
    elif frame.relation == 'inspection_method':
        entity, tool = map(re.escape, (frame.entity, frame.other))
        match = re.fullmatch(
            rf'(?:the )?{entity} (?:should|must|is) [^:;]{{3,160}}: '
            rf'(?P<method>[^:;]+) with (?:a |the )?{tool} to check',
            line)
        if match and not re.search(
                r'\b(?:not|never|possibly|perhaps|unknown|might|could)\b',
                match['method']):
            return match['method'], ''
    elif frame.relation == 'storage_rule':
        entity = re.escape(frame.entity)
        match = re.fullmatch(rf'(?:store|keep) (?:the )?{entity} in (?P<value>{PHRASE})', line)
        if match:
            return match['value'], ''
    elif frame.relation == 'responsibility':
        entity = re.escape(frame.entity)
        match = re.fullmatch(
            rf'(?P<value>{PHRASE}) is responsible for (?:the )?{entity}', line)
        if match:
            return match['value'], ''
    elif frame.relation == 'due_date':
        entity = re.escape(frame.entity)
        match = re.fullmatch(
            rf'(?:the )?{entity} is due (?:on|by) (?P<value>\d{{4}}-\d{{2}}-\d{{2}})',
            line)
        if not match:
            match = re.fullmatch(rf'(?:the )?due date for (?:the )?{entity} is (?P<value>\d{{4}}-\d{{2}}-\d{{2}})', line)
        if match:
            return match['value'], ''
    elif frame.relation == 'recorded_status':
        entity = re.escape(frame.entity)
        match = re.fullmatch(
            rf'(?:the )?status of (?:the )?{entity} is (?P<value>{PHRASE})',
            line)
        if not match:
            match = re.fullmatch(rf'(?:the )?{entity} has status (?P<value>{PHRASE})', line)
        if match:
            return match['value'], ''
    elif frame.relation == 'location':
        entity = re.escape(frame.entity)
        match = re.fullmatch(
            rf'(?:the )?{entity} is located in (?P<value>{PHRASE})', line)
        if match:
            return match['value'], ''
    elif frame.relation == 'contents':
        entity = re.escape(frame.entity)
        match = re.fullmatch(
            rf'(?:the )?{entity} contains (?P<value>[^;:.]+)', line)
        if match and len(match['value']) <= 180:
            return match['value'], ''
    elif frame.relation == 'scheduled_date':
        entity = re.escape(frame.entity)
        match = re.fullmatch(
            rf'(?:the )?{entity} is scheduled for (?P<value>\d{{4}}-\d{{2}}-\d{{2}})', line)
        if match:
            return match['value'], ''
    elif frame.relation == 'cause':
        subject = re.escape(frame.entity)
        match = re.fullmatch(
            rf'{subject} (?:comes? from|is caused by|are caused by) (?P<value>.+)',
            line)
        if match and not re.search(
                r'\b(?:not|never|could|might|perhaps|unknown)\b', match['value']):
            return match['value'], ''
    elif frame.relation == 'required_time':
        subject = re.escape(frame.entity)
        match = re.fullmatch(
            rf'{subject} needs (?P<value>{DURATION})(?:, not (?P<contrast>{DURATION}))?',
            line)
        if match:
            return match['value'], match['contrast'] or ''
    elif frame.relation == 'code_purpose':
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


def _capture_evidence_text(record):
    """Keep captured source text separate from its appended JSON audit manifest.

    The browser import store appends 'Source capture: {manifest}' to the
    record's body. That JSON is provenance, not an answer sentence and not
    part of the captured text. Strip it *only* if a machine-origin page has
    exactly one correctly pinned, well-formed capture manifest. Never turn
    an unverified or hand-written suffix into a source quotation.
    """
    text = body_text(record.body_html)
    marker = '\nSource capture: '
    if marker not in text:
        return text
    if getattr(record, 'origin', '') != 'machine' or text.count(marker) != 1:
        return ''
    body, raw = text.split(marker, 1)
    if not body or len(raw) > 15000:
        return ''
    try:
        manifest = json.loads(raw)
    except (ValueError, TypeError):
        return ''
    if not isinstance(manifest, dict) or not all(
            isinstance(manifest.get(key), str) and manifest[key]
            for key in ('source_url', 'source_sha256', 'text_sha256', 'transport')):
        return ''
    if hashlib.sha256(body.encode('utf-8')).hexdigest() != manifest['text_sha256']:
        # Refuse on a body projection that no longer matches captured text.
        return ''
    return body


def statement_support(frame, record):
    text = _capture_evidence_text(record)
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
        if frame.relation in {'due_date', 'scheduled_date'}:
            try:
                date.fromisoformat(value)
            except ValueError:
                continue
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
