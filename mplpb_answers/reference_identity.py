"""Verify scoped documentary event keys and explicit local pronoun bindings."""
import re

from mplpb_combined.ledger import field_name

from . import relation_graph
from .body_text import body_text
from .documentary_verify import citation, context_ranges, named_actor, possible_refutation, source_question
from .evidence_contract import ReaderError
from .passages import PassageIndex

_IDENTIFIER = r'[A-Za-z0-9][A-Za-z0-9._-]{0,99}'
_PAIR = rf'sources (?P<left>{_IDENTIFIER}) and (?P<right>{_IDENTIFIER})'
_EVENT_FORMS = (
    rf'Do {_PAIR} (?:describe|refer to) the same event\?',
    rf'Are the events in {_PAIR} the same\?',
)
_PRONOUN = r'(?P<pronoun>I|he|she|they|we|it|you)'
_PRONOUN_FORMS = (
    rf'Who does (?:the pronoun )?"{_PRONOUN}" refer to in source (?P<source>{_IDENTIFIER})\?',
    rf'To whom does "{_PRONOUN}" refer in source (?P<source>{_IDENTIFIER})\?',
)
_LABELS = {'event registry', 'event id', 'occurrence id', 'different event from'}
_UNRESOLVED_NAME = {'the', 'if', 'unless', 'only', 'allegedly', 'apparently', 'reportedly',
                    'perhaps', 'possibly', 'maybe', 'probably', 'supposedly'}
_REGISTRY = re.compile(r'[A-Za-z0-9][A-Za-z0-9 ._/-]{0,79}')


def parse_request(question):
    """License only whole requests that pin the named ledger sources."""
    question = source_question(question).replace('“', '"').replace('”', '"')
    for form in _EVENT_FORMS:
        match = re.fullmatch(form, question, re.I)
        if match:
            return 'event', (match['left'], match['right']), None
    for form in _PRONOUN_FORMS:
        match = re.fullmatch(form, question, re.I)
        if match:
            return 'pronoun', (match['source'],), match['pronoun'].casefold()
    return None


def _source_body(record):
    if len(record.body_html) > 32000:
        return None
    body = body_text(record.body_html)
    return body if body and len(body) <= 4000 else None


def _event_fields(record, body):
    if possible_refutation(body):
        return {}
    headers = {row['body_start']: row for row in relation_graph.declared_fields(record)}
    restricted = context_ranges(record)
    fields = {}
    for match in relation_graph.FIELD_LINE.finditer(body):
        label = field_name(match[1])
        if label not in _LABELS:
            continue
        row = headers.get(match.start())
        if (not row or row['stacked_field_suspected'] or label in fields
                or any(a < match.end() and b > match.start() for a, b in restricted)):
            return {}
        pattern = _REGISTRY if label == 'event registry' else _IDENTIFIER
        if not re.fullmatch(pattern, row['value']):
            return {}
        fields[label] = row
    return fields


def _event_resolution(index, records):
    bodies = [_source_body(record) for record in records]
    if not all(bodies):
        return 'reference_scan_budget', None, []
    fields = [_event_fields(record, body) for record, body in zip(records, bodies)]
    if not all('event registry' in f and 'event id' in f for f in fields):
        return 'event_identity_unresolved', None, []
    left, right = [{k: v['value'] for k, v in rows.items()} for rows in fields]
    if left['event registry'] != right['event registry']:
        return 'event_identity_unresolved', None, []
    registry = left['event registry']
    same_key = left['event id'] == right['event id']
    directions = [(i, j) for i, j in ((0, 1), (1, 0))
                  if fields[i].get('different event from') and fields[j].get('occurrence id')
                  and fields[i]['different event from']['value'] == fields[j]['occurrence id']['value']]
    if same_key and directions:
        return 'event_identity_conflict', None, []
    if not same_key and not directions:
        return 'event_identity_unresolved', None, []
    refs = [(0, 'event registry'), (1, 'event registry')]
    if same_key:
        refs += [(0, 'event id'), (1, 'event id')]
    else:
        if (not left.get('occurrence id') or not right.get('occurrence id')
                or left['occurrence id'] == right['occurrence id']):
            return 'event_identity_unresolved', None, []
        if len(index.records) > 64 or sum(len(rec.body_html) for rec in index.records) > 160000:
            return 'reference_scan_budget', None, []
        # A local occurrence reference must resolve uniquely inside its declared
        # registry. Malformed duplicate declarations cannot disappear from this scan.
        for i, j in directions:
            target = fields[j]['occurrence id']['value']
            for other in index.records:
                if other.path == records[j].path:
                    continue
                other_fields = [(field_name(m[1]), m[2].strip()) for m in
                                relation_graph.FIELD_LINE.finditer(body_text(other.body_html))]
                if ('event registry', registry) in other_fields and ('occurrence id', target) in other_fields:
                    return 'event_identity_unresolved', None, []
            refs += [(i, 'different event from'), (j, 'occurrence id'), (i, 'occurrence id')]
    witnesses = [citation(records[i], bodies[i], fields[i][label]['body_start'], fields[i][label]['body_end'])
                 for i, label in dict.fromkeys(refs)]
    proposition = {'relation': 'documentary_event_identity', 'same_event': same_key,
                   'registry': registry, 'left_source_id': records[0].id,
                   'right_source_id': records[1].id}
    if same_key:
        proposition['event_id'] = left['event id']
    return 'supported_documentary_assertion', proposition, witnesses


def _pronoun_resolution(record, pronoun):
    body = _source_body(record)
    if not body:
        return 'reference_scan_budget', None, []
    if context_ranges(record):
        return 'coreference_unresolved', None, []
    text = body.replace('“', '"').replace('”', '"')
    # A complete source gloss or a single, explicitly named speech turn
    # licenses a binding confined to the selected source occurrence.
    gloss = re.fullmatch(rf'Pronoun "{_PRONOUN}" refers to (?P<name>[^\n".!?;]{{3,100}})\.', text, re.I)
    binding = 'explicit_pronoun_gloss'
    if gloss and gloss['pronoun'].casefold() == pronoun:
        name = gloss['name']
    elif pronoun == 'i':
        speech = re.fullmatch(r'"I [^"\n!?.;]{1,500}," said (?P<name>[^\n".!?;]{3,100})\.', text)
        if speech is None:
            speech = re.fullmatch(r'(?P<name>[^\n".!?;]{3,100}) said, "I [^"\n!?.;]{1,500}\."', text)
        name = speech['name'] if speech else ''
        binding = 'single_attributed_speech_turn'
    else:
        name = ''
    words = name.casefold().split()
    if not 2 <= len(words) <= 4 or not named_actor(name) or set(words) & _UNRESOLVED_NAME:
        return 'coreference_unresolved', None, []
    proposition = {'relation': 'documentary_coreference', 'pronoun': pronoun, 'referent': name,
                   'source_id': record.id, 'binding': binding}
    return 'supported_documentary_assertion', proposition, [citation(record, body, 0, len(body))]


def verify(root, question, profile, request, max_passages, max_chars):
    """Independently read currently eligible sources and certify exact spans."""
    task, ids, pronoun = request
    if len(set(ids)) != len(ids):
        return 'event_identity_unresolved', None
    try:
        index = PassageIndex(root, question, profile)
    except ReaderError as error:
        return error.code, None
    selected = {ident: [record for record in index.records if record.id == ident] for ident in ids}
    if any(len(rows) != 1 for rows in selected.values()):
        return 'no_eligible_sources', None
    records = [selected[ident][0] for ident in ids]
    code, proposition, witnesses = (_event_resolution(index, records) if task == 'event'
                                     else _pronoun_resolution(records[0], pronoun))
    if not index.unchanged():
        return 'source_changed', None
    if proposition is None:
        return code, None
    if len(witnesses) > max_passages or sum(len(c['quote']) for c in witnesses) > max_chars:
        return 'reader_budget_exceeded', None
    if task == 'event':
        prefix = ('The named sources declare the same event key under ' + proposition['registry']
                  if proposition['same_event'] else
                  'The named sources explicitly distinguish the events under ' + proposition['registry'])
    else:
        prefix = 'The selected source binds "' + pronoun + '" to ' + proposition['referent']
    claim = {'text': prefix + '.', 'proposition': proposition, 'citations': witnesses,
             'source_support_established': True,
             'qualifiers': ['This proof covers the cited documentary declarations. Historical identity and independent corroboration remain unverified.']}
    paths = {c['path'] for c in witnesses}
    return code, {'claims': [claim], 'text': claim['text'], 'answer_supported': True,
                  'sources': [source for source in index.sources if source['path'] in paths]}
