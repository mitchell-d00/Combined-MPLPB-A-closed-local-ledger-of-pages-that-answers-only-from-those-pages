"""Verify scoped documentary event keys and explicit local pronoun bindings."""
import re

from mplpb_combined.ledger import field_name

from . import documentary_errata, documentary_links, publication_corrections, relation_graph
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

EVENT_GAP_GUIDANCE = {
    'named_sources_needed': (
        'The strict reader has not checked event identity for this question form.',
        'Name two ledger source IDs and ask: Do sources SOURCE-A and SOURCE-B describe the same event?',
    ),
    'distinct_source_ids_needed': (
        'The question repeats the same source ID.',
        'Choose two distinct ledger source IDs for comparison.',
    ),
    'event_declaration_unverified': (
        'The comparison could not verify an Event Registry and Event ID in both eligible sources.',
        'Look for records that explicitly declare the event registry and event ID, or record the same proceeding being rescheduled and opened.',
    ),
    'registry_mismatch': (
        'The verified event declarations refer to different registries.',
        'Look for eligible declarations in the same registry. Event IDs are scoped to their registry.',
    ),
    'event_relationship_unverified': (
        'The event IDs differ within the registry, and no verified declaration links their occurrences as distinct.',
        'For agreement, look for a shared event ID. For distinction, look for an explicit Different Event From declaration and the matching occurrence ID in the same registry.',
    ),
    'occurrence_identity_unverified': (
        'The distinction needs two separately identifiable occurrences.',
        'Look for distinct Occurrence ID declarations in the two records.',
    ),
    'occurrence_target_ambiguous': (
        'The declared occurrence target does not resolve uniquely in the eligible registry records.',
        'Check which eligible record the declaration points to and whether the occurrence ID is unique.',
    ),
}


def unnamed_event_question(question):
    """Recognize comparison wording solely to offer an admitted next question."""
    return bool(re.fullmatch(
        r'Do the (?:records|reports|documents) establish that (?:both|they) '
        r'(?:describe|refer to) the same (?:event|incident|failure|occurrence)\?',
        source_question(question), re.I))


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
    return (documentary_links.parse(question) or publication_corrections.parse(question)
            or documentary_errata.parse(question))


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
        return 'reference_scan_budget', None, [], None
    fields = [_event_fields(record, body) for record, body in zip(records, bodies)]
    if not all('event registry' in f and 'event id' in f for f in fields):
        return 'event_identity_unresolved', None, [], 'event_declaration_unverified'
    left, right = [{k: v['value'] for k, v in rows.items()} for rows in fields]
    if left['event registry'] != right['event registry']:
        return 'event_identity_unresolved', None, [], 'registry_mismatch'
    registry = left['event registry']
    same_key = left['event id'] == right['event id']
    directions = [(i, j) for i, j in ((0, 1), (1, 0))
                  if fields[i].get('different event from') and fields[j].get('occurrence id')
                  and fields[i]['different event from']['value'] == fields[j]['occurrence id']['value']]
    if same_key and directions:
        return 'event_identity_conflict', None, [], None
    if not same_key and not directions:
        return 'event_identity_unresolved', None, [], 'event_relationship_unverified'
    refs = [(0, 'event registry'), (1, 'event registry')]
    if same_key:
        refs += [(0, 'event id'), (1, 'event id')]
    else:
        if (not left.get('occurrence id') or not right.get('occurrence id')
                or left['occurrence id'] == right['occurrence id']):
            return 'event_identity_unresolved', None, [], 'occurrence_identity_unverified'
        if len(index.records) > 64 or sum(len(rec.body_html) for rec in index.records) > 160000:
            return 'reference_scan_budget', None, [], None
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
                    return 'event_identity_unresolved', None, [], 'occurrence_target_ambiguous'
            refs += [(i, 'different event from'), (j, 'occurrence id'), (i, 'occurrence id')]
    witnesses = [citation(records[i], bodies[i], fields[i][label]['body_start'], fields[i][label]['body_end'])
                 for i, label in dict.fromkeys(refs)]
    proposition = {'relation': 'documentary_event_identity', 'same_event': same_key,
                   'registry': registry, 'left_source_id': records[0].id,
                   'right_source_id': records[1].id}
    if same_key:
        proposition['event_id'] = left['event id']
    return 'supported_documentary_assertion', proposition, witnesses, None


def _pronoun_resolution(record, pronoun):
    if len(record.body_html) > 32000:
        return 'reference_scan_budget', None, []
    body = relation_graph._capture_evidence_text(record)
    if len(body) > 4000:
        return 'reference_scan_budget', None, []
    if not body or any(lo < len(body) and hi > 0 for lo, hi in context_ranges(record)):
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
        return 'event_identity_unresolved', None, 'distinct_source_ids_needed'
    try:
        index = PassageIndex(root, question, profile)
    except ReaderError as error:
        return error.code, None, None
    selected = {ident: [record for record in index.records if record.id == ident] for ident in ids}
    if any(len(rows) != 1 for rows in selected.values()):
        return 'no_eligible_sources', None, None
    records = [selected[ident][0] for ident in ids]
    gap = None
    claim = None
    if task == 'event':
        code, proposition, witnesses, gap = _event_resolution(index, records)
    elif task == 'pronoun':
        code, proposition, witnesses = _pronoun_resolution(records[0], pronoun)
    elif task in {'publication_correction', 'erratum_report'}:
        prover = publication_corrections if task == 'publication_correction' else documentary_errata
        code, claim = prover.prove(index, pronoun) if profile.prose else ('no_eligible_sources', None)
        proposition, witnesses = (claim['proposition'], claim['citations']) if claim else (None, [])
    else:
        claim = documentary_links.resolve(task, records, ids, max_chars) if profile.prose else None
        code = 'supported_documentary_assertion' if claim else 'documentary_link_unverified'
        proposition, witnesses = (claim['proposition'], claim['citations']) if claim else (None, [])
    if task == 'event' and code == 'event_identity_unresolved' and profile.prose:
        from .bounded_records import rescheduled_event
        claim = rescheduled_event(records)
        if claim:
            code = 'supported_documentary_assertion'
            proposition, witnesses = claim['proposition'], claim['citations']
            proposition.update(left_source_id=records[0].id, right_source_id=records[1].id)
    if not index.unchanged():
        return 'source_changed', None, None
    if proposition is None:
        return code, None, gap
    if len(witnesses) > max_passages or sum(len(c['quote']) for c in witnesses) > max_chars:
        return 'reader_budget_exceeded', None, None
    if claim is None:
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
                  'sources': [source for source in index.sources if source['path'] in paths]}, None
