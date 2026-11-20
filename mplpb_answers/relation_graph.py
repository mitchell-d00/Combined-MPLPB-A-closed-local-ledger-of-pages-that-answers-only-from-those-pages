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

VERSION = 'source-relation-graph-v2'
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
    ('storage_rule', rf'where should (?P<entity>{PHRASE}) be (?:stored|kept)'),
    ('code_purpose', rf'what is (?:the )?purpose of (?:bag )?code (?P<entity>{CODE})'),
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
            and re.search(r'\b(?:if|when|unless|except|provided|until|whenever|before|after|during|formerly|currently)\b',
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
        if not match:
            match = re.fullmatch(rf'(?:the )?{entity} (?:should|must) be (?:stored|kept) in (?P<value>{PHRASE})', line)
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
            {'id': fact, 'kind': 'statement', 'quote': span['quote'],
             'polarity': span.get('polarity', 'positive')},
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
    expected = manifest['text_sha256']
    if 'projection_version' in manifest:
        from .body_text import VERSION as projection_version
        if manifest['projection_version'] != projection_version or not isinstance(manifest.get('body_text_sha256'),str):
            return ''
        expected = manifest['body_text_sha256']
    if hashlib.sha256(body.encode('utf-8')).hexdigest() != expected:
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
    spans, negative_spans = [], []
    unresolved = False
    unresolved_spans = []
    for raw in re.split(r'(?<=[.!?])\s+|\n+', text):
        raw = raw.strip()
        if not raw:
            continue
        line = normalize(raw)
        # Only predicate negation, in a complete licensed sentence, is inverted
        # for recognition. The original negative quote remains the evidence.
        # Prefix conditions/time/quotation are never removed to make a match.
        positive_line = re.sub(r'(^|, )(?:do not|never) (store|keep) ', r'\1\2 ', line)
        positive_line = re.sub(r'\b(is|are|was|were|should|must) not\b', r'\1', positive_line)
        positive_line = re.sub(r'\bdoes not contain\b', 'contains', positive_line)
        is_negative = positive_line != line
        found = _evidence(frame, positive_line)
        if not found:
            # A scoped denial cannot establish an unconditional contradiction,
            # but its applicability cannot silently be assumed false either.
            scoped = re.fullmatch(r'(?:(?:if|when|unless) [^,]+|in \d{4}), (.+)', positive_line)
            if is_negative and scoped and _evidence(frame, scoped[1]):
                unresolved = True
                unresolved_spans.append({'quote': raw, 'reason': 'Denial applicability requires context.'})
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
        (negative_spans if is_negative else spans).append({'quote': raw, 'value': value,
                      'qualification': qualification,
                      'polarity': 'negative' if is_negative else 'positive'})
    # Different qualifications are different assertions, even if the numeric
    # quantities agree: never let an unconditional claim erase a condition.
    keys = {(s['value'], s['qualification']) for s in spans}
    negative_keys = {(s['value'], s['qualification']) for s in negative_spans}
    status = 'conflict' if len(keys) > 1 or keys & negative_keys else 'supported' if spans else 'unsupported'
    result = {
        'status': status, 'spans': spans, 'negative_spans': negative_spans,
        'unresolved': unresolved, 'unresolved_spans': unresolved_spans,
        'graph': _graph(frame, record, spans + negative_spans),
        'reason': 'Exact source-declared relation path; source truth and procedure execution not verified.',
    }
    from .assertions import attach
    return attach(result, frame, record)


# Exact labels are a separate bounded body grammar, not inferred field semantics.
FIELD_LINE = re.compile(r'(?m)^([A-Za-z][A-Za-z0-9 _-]{0,79}):[ \t]*(\S[^\r\n]*)$')
IDENTITY_FIELDS = {'record id', 'document id', 'event id', 'occurrence id', 'message id'}


def declared_fields(record):
    from mplpb_combined.ledger import field_name
    body = body_text(record.body_html)
    boundary=len(body)
    offset=0
    for line in body.splitlines(keepends=True):
        m=FIELD_LINE.fullmatch(line.rstrip('\r\n'))
        if not m or field_name(m[1]) in {'body','example','sample','quoted example'}:
            boundary=offset;break
        offset+=len(line)
    quoted_ranges = []
    if boundary and re.search(r'<(?:blockquote|q)\b', record.body_html, re.I):
        from .documentary_verify import context_ranges
        quoted_ranges = context_ranges(record)
    return [{'field':field_name(m[1]), 'value':m[2].strip(), 'quote':m[0],
             'source_id':record.id, 'path':record.path, 'hash':record.hash_actual,
             'body_start':m.start(), 'body_end':m.end(), 'start':m.start(), 'end':m.end(),
             'stacked_field_suspected':bool(STACKED_LABEL.search(m[2]))}
            for m in FIELD_LINE.finditer(body[:boundary])
            if not any(lo < m.end() and hi > m.start() for lo, hi in quoted_ranges)]


# plain_to_html joins the lines of one paragraph with spaces, so a header block
# "Sender: A\nRecipient: B" is served as "Sender: A Recipient: B". A later
# "Label: " inside a value means the value boundary is unknown: refuse it.
STACKED_LABEL = re.compile(r'\s[A-Za-z][A-Za-z0-9_-]{0,40}(?: [A-Za-z0-9_-]{1,40}){0,3}:[ \t]+\S')


def field_contexts(record, requested):
    """Retain competing later mentions without granting examples field authority."""
    from mplpb_combined.ledger import field_name
    headers=declared_fields(record)
    positions={f['body_start'] for f in headers}
    body=body_text(record.body_html)
    return [{'field':field_name(m[1]),'value':m[2].strip(),'quote':m[0],
             'source_id':record.id,'path':record.path,'hash':record.hash_actual,
             'body_start':m.start(),'body_end':m.end(),'start':m.start(),'end':m.end(),
             'context_only':True}
            for m in FIELD_LINE.finditer(body)
            if field_name(m[1])==requested and m.start() not in positions]


# Question syntax only. These slots never supply source evidence or field aliases.
# Full matching is essential: an unconsumed qualification/second obligation must
# not become an unconditional single-field request.
_REQUEST_FIELD = r'(?P<field>[A-Za-z][A-Za-z0-9 _-]{0,79}?)'
_REQUEST_ID = r'(?P<record>[A-Za-z0-9][A-Za-z0-9._:@/-]{0,180})'
_FIELD_REQUEST_FORMS = (
    rf'(?:tell|show|give) me (?:the )?{_REQUEST_FIELD} (?:listed|recorded|stated) (?:on|in) (?:record|event|occurrence) {_REQUEST_ID}',
    rf'(?:tell|show|give) me (?:the )?{_REQUEST_FIELD} (?:for|of) (?:record|event|occurrence) {_REQUEST_ID}',
    rf'for (?:record|event|occurrence) {_REQUEST_ID}, (?:what|which) {_REQUEST_FIELD} is (?:explicitly )?(?:stated|recorded|listed)',
    rf'looking only at {_REQUEST_ID}, (?:identify|report|show) (?:the )?{_REQUEST_FIELD} recorded there',
    rf'(?:give|show|tell) me {_REQUEST_ID}\'s (?:the )?{_REQUEST_FIELD}',
    rf'find {_REQUEST_ID} and (?:report|show|give) its {_REQUEST_FIELD}',
    rf'(?:what|which) {_REQUEST_FIELD} is (?:explicitly )?(?:recorded|stated|listed) for (?:record|event|occurrence) {_REQUEST_ID}',
    rf'in (?:record|event|occurrence) {_REQUEST_ID}, what does (?:the )?{_REQUEST_FIELD} field (?:say|state|record)',
    rf'(?:record|event|occurrence) {_REQUEST_ID}: (?:report|show|give) (?:the )?{_REQUEST_FIELD}',
)
_FIELD_QUALIFIER = re.compile(
    r'\b(?:and|or|not|never|before|after|during|unless|if|according|'
    r'allegedly|reportedly|possibly|formerly|previously|currently|now|'
    r'was|were|is|are|has|had|who|why|whether|without|except)\b', re.I)


def field_question(question):
    """Whole-question finite normalization, preserving literal field semantics."""
    q = re.sub(r'\s+', ' ', question.replace('’', "'")).strip()
    if len(q) > 400:
        return None
    q = re.sub(r'^(?:please |(?:can|could) you )', '', q, count=1, flags=re.I)
    # One terminal sentence mark is syntax; embedded punctuation is consumed
    # only by an explicitly declared form (comma or literal identifier).
    q = re.sub(r'[?.]$', '', q)
    for form in _FIELD_REQUEST_FORMS:
        match = re.fullmatch(form, q, re.I)
        if match and not _FIELD_QUALIFIER.search(match['field']):
            return {'field': match['field'].strip(), 'record_id': match['record']}
    return None


def exact_request(question, record_id=None, field=None, exact_value=None):
    from mplpb_combined.ledger import field_name
    match = re.fullmatch(r'(?i)what is (?:the )?([A-Za-z][A-Za-z0-9 _-]{0,79}) (?:for|of) '
                         r'(?:record|event|occurrence) ([A-Za-z0-9][A-Za-z0-9._:@/-]{0,180})\??', question.strip())
    if match:
        field = field or match[1]
        record_id = record_id or match[2]
    normalized = None if match else field_question(question)
    if normalized:
        if ((record_id is not None and record_id != normalized['record_id']) or
                (field is not None and field_name(field) != field_name(normalized['field']))):
            raise ValueError('Explicit selector contradicts the parsed question')
        field = field or normalized['field']
        record_id = record_id or normalized['record_id']
    if field is not None and (not isinstance(field,str) or not re.fullmatch(r'[A-Za-z][A-Za-z0-9 _-]{0,79}',field)):
        raise ValueError('Expected an explicit field label')
    if record_id is not None and (not isinstance(record_id,str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._:@/-]{0,180}',record_id)):
        raise ValueError('Invalid exact record pin')
    if exact_value is not None and (not isinstance(exact_value,dict) or set(exact_value)!={'field','value'}
            or not isinstance(exact_value['field'],str) or not isinstance(exact_value['value'],str)
            or not exact_value['value'].strip() or len(exact_value['value'])>200):
        raise ValueError('Exact value needs an explicit field/value pair')
    result = {'record_id':record_id,'field':field_name(field) if field else None,'exact_value':exact_value}
    if normalized:
        result['question_normalization'] = {
            'version': 'literal-field-question-v1', 'record_id': record_id,
            'field': result['field'], 'canonical_question': f'What is the {field} for record {record_id}?',
            'unresolved_obligations': [], 'normalization_is_evidence': False,
            'basis': 'whole_question_finite_syntax_literal_field_no_aliases'}
    return result


def exact_sources(records, question, request):
    """Route after eligibility. Shared explicit keys retain every appearance."""
    from mplpb_combined.ledger import field_name
    key=request['record_id']
    def present(value):
        return bool(re.search(r'(?<![\w:@/-])'+re.escape(value)+r'(?![\w:@/-])',question))
    keys=[key] if key else [r.id for r in records if present(r.id)]
    if not keys:
        keys=[r.hash_actual for r in records if present(r.hash_actual)]
    if not keys:
        keys=sorted({f['value'] for r in records for f in declared_fields(r)
                     if f['field'] in IDENTITY_FIELDS and present(f['value'])})
    matches=[]
    for record in records:
        fields=declared_fields(record)
        identities={f['value'] for f in fields if f['field'] in IDENTITY_FIELDS}
        identities.update(record.fields.get(k,'') for k in ('event-id','occurrence-id'))
        if any(k in {record.id, record.hash_actual, record.id+'@'+record.hash_actual} or k in identities for k in keys):
            matches.append(record)
    value=request['exact_value']
    if not keys and value:
        matches=[r for r in records if any(f['field']==field_name(value['field']) and f['value']==value['value'] for f in declared_fields(r))]
        if len(matches)!=1:
            return [], 'ambiguous_value' if matches else 'missing'
        # Retain competing appearances of the same explicit identity as well.
        shared={f['value'] for f in declared_fields(matches[0]) if f['field'] in IDENTITY_FIELDS}
        matches=[r for r in records if r in matches or any(f['field'] in IDENTITY_FIELDS and f['value'] in shared for f in declared_fields(r))]
    return matches, 'exact' if matches else 'missing' if keys or value else None


def explore(root, question, hops, profile):
    """At most two quoted forward edges; never compose an answer or cause chain."""
    from mplpb_answers.evidence_contract import pin
    from mplpb_combined.ledger import Ledger
    from mplpb_combined import provenance_gate as G
    if not isinstance(hops,list) or not 1<=len(hops)<=2:
        raise ValueError('Relation exploration accepts one or two explicit hops')
    gate=G.gather(root,question,profile)
    snapshot=pin(gate.to_dict());excluded={s['path'] for s in gate.excluded}
    lexical={s['path'] for s in gate.sources}
    records={r.id:r for r in Ledger(root).servable() if r.kind not in {'pointer','index'} and r.path not in excluded
             and (profile.prose or r.path in lexical)}
    edges=[];previous=None
    for hop in hops:
        if not isinstance(hop,dict) or not set(hop)<={'question','source_id','hash','quote'} or not isinstance(hop.get('question'),str):
            raise ValueError('A hop requires a bounded relation question and optional pinned quote')
        if len(hop['question'])>200:raise ValueError('Hop question exceeds the relation grammar budget')
        if any(k in hop and (not isinstance(hop[k],str) or len(hop[k])>limit)
               for k,limit in (('source_id',100),('hash',100),('quote',4000))):
            raise ValueError('Hop pin or quote exceeds the evidence budget')
        frame=parse(hop['question']);record=records.get(hop.get('source_id'))
        quoted=False;value=None;reason='missing_eligible_quote'
        if frame and not (len(hops)>1 and frame.relation=='cause'):
            if record and hop.get('hash')==record.hash_actual and isinstance(hop.get('quote'),str):
                hop_gate=G.gather(root,hop['question'],profile)
                allowed={s['path'] for s in hop_gate.sources}
                check=statement_support(frame,record) if record.path in allowed else {}
                spans=[s for s in check.get('spans',[]) if s['quote']==hop['quote']]
                if check.get('status')=='supported' and spans:
                    value=spans[0]['value'];quoted=previous is None or normalize(frame.entity)==normalize(previous)
                    reason='eligible_quote' if quoted else 'unlinked_subject'
        elif frame:
            reason='causal_composition_prohibited'
        start=body_text(record.body_html).find(hop['quote']) if quoted else None
        edges.append({'question':hop['question'],'status':'source_quoted_edge' if quoted else 'candidate',
                      'family':frame.relation if frame else None,'direction':'source_declared_only',
                      'quote_verified':quoted,'citation':dict(source_id=record.id,path=record.path,hash=record.hash_actual,quote=hop['quote'],
                          body_start=start,body_end=start+len(hop['quote'])) if quoted else None,
                      'reason':reason,'answer_supported':False})
        previous=value if quoted else None
    if pin(G.gather(root,question,profile).to_dict())!=snapshot:
        return {'status':'source_changed','edges':[],'answer_supported':False}
    return {'status':'source_quoted_edges' if all(e['quote_verified'] for e in edges) else 'candidate',
            'edges':edges,'answer_supported':False,'content_truth_verified':False,'multi_hop_answer_inference':False}
