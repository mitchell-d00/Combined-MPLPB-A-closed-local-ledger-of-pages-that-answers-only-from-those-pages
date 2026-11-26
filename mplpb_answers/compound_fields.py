"""Compose independently checked field answers for explicitly pinned records."""
import re

from mplpb_combined import provenance_gate as G
from mplpb_combined.ledger import serving_view

from . import field_aliases, relation_graph
from .passage_admission import output_budget

_LABEL = r'[A-Za-z][A-Za-z0-9 _-]{0,79}?'
_FIELDS = rf'(?:the )?(?P<first>{_LABEL}) and (?:the )?(?P<second>{_LABEL})'
_RECORD = rf'record {relation_graph._REQUEST_ID}'
_SCOPE = re.compile(r'\b(?:as of|until|since|subject to|provided|including|excluding)\b', re.I)
_FORMS = (
    rf'for {_RECORD}, (?:report|show|list) (?:its )?{_FIELDS}',
    rf'what are {_FIELDS} (?:for|of) {_RECORD}',
    rf'(?:report|show|list) {_FIELDS} (?:for|of) {_RECORD}',
)
_OTHER_RECORD = _RECORD.replace('?P<record>', '?P<other>')
_RECORD_PAIR = rf'compare (?:the )?(?P<label>{_LABEL}) (?:for|of) {_RECORD} and {_OTHER_RECORD}'


def parse_question(question):
    question = re.sub(r'\s+', ' ', question).strip()
    if len(question) > 400:
        return None
    question = re.sub(r'[?.]$', '', question)
    for form in _FORMS:
        match = re.fullmatch(form, question, re.I)
        if match:
            labels = [name.strip() for name in (match['first'], match['second'])]
            if not any(relation_graph._FIELD_QUALIFIER.search(name) or _SCOPE.search(name) for name in labels):
                return [(match['record'], label) for label in labels]
    pair = re.fullmatch(_RECORD_PAIR, question, re.I)
    if pair:
        label = pair['label'].strip()
        if not (relation_graph._FIELD_QUALIFIER.search(label) or _SCOPE.search(label)):
            return [(pair['record'], label), (pair['other'], label)]
    return None


def parse_named_fields(question):
    """Bind one complete request to an entity and its explicit field obligations."""
    from .ordinary_questions import slot

    text = ' '.join(question.split())
    if text.endswith(('?', '.')):
        text = text[:-1].rstrip()
    if text.endswith(('?', '.')):
        return None
    compound = ('opening time', 'location')
    forms = (
        (r'(?:When|What time|At which time|At what time) does (.+?) open,? and where is it located', compound),
        (r'For (.+?), (?:give|report|show|list) its opening time and location', compound),
        (r'What is the opening time and location (?:of|for|at) (.+)', compound),
        (r'Where is (.+)', ('location',)),
        (r'Tell me where (.+?) is', ('location',)),
    )
    for pattern, labels in forms:
        match = re.fullmatch(pattern, text, re.I)
        if not match:
            continue
        entity = match[1]
        if (slot(entity) and not re.search(r'[.,]', entity)
                and not re.search(r'\b(?:according to|says?|said|reported|where|is)\b', entity, re.I)):
            return entity, labels
    return None


def answer_named_fields(root, gate, entity, fields, max_passages, max_chars):
    """Admit each field from the original question's eligible source set."""
    from mplpb_combined.ledger import Ledger
    from .body_text import body_text
    from .documentary_verify import units
    from .frames import QuestionFrame, normalize
    from .ordinary_evidence import named_fields

    if any(s['reason'] == 'correction scope unclear' for s in gate.excluded):
        return 'abstain', 'correction_scope_unclear', {'missing': list(fields)}
    allowed = {(s['id'], s['path'], s['hash']) for s in gate.sources}
    records = [r for r in Ledger(root).servable() if (r.id, r.path, r.hash_actual) in allowed]
    if len(records) != len(allowed):
        return 'abstain', 'source_changed', {}
    if (len(records) > 8 or sum(len(r.body_html) for r in records) > 200000
            or sum(sum(1 for _ in units(body_text(r.body_html))) for r in records) > 1000):
        return 'abstain', 'reference_scan_budget', {'missing': list(fields)}
    frame = QuestionFrame('named_fields', normalize(entity), entity, '')
    parts = []
    admitted = []
    proved_pins = set()
    conflict = False
    for label in fields:
        checks = [(r, v) for r in records
                  if r.kind == 'page' and not r.derived_from
                  and (v := named_fields(frame, r, label, exact_offsets=True))]
        supported = [(r, check) for r, check in checks if check['status'] == 'supported']
        competing = len(supported) > 1 or any(v['status'] == 'conflict' for _, v in checks)
        unresolved = any(v.get('unresolved') for _, v in checks)
        conflict |= competing
        part = {'field': label, 'status': 'conflict' if competing else 'unresolved'}
        parts.append(part)
        if competing or unresolved or len(supported) != 1:
            continue
        record, proof = supported[0]
        pin = (record.id, record.path, record.hash_actual)
        proved_pins.add(pin)
        citations = [{'source_id': pin[0], 'path': pin[1], 'hash': pin[2],
                      'quote': span['quote'], 'body_start': span['body_start'],
                      'body_end': span['body_end'], 'start': span['body_start'],
                      'end': span['body_end']} for span in proof['spans']]
        statement = next(c['quote'] for span, c in zip(proof['spans'], citations)
                         if span['field'] == label)
        claim = {'text': statement, 'citations': citations,
                 'qualifiers': ['Source-declared field; source truth is unverified.']}
        if output_budget({'claims': [c for _, c in admitted] + [claim], 'missing': []},
                         max_passages, max_chars):
            part['status'] = 'budget'
            continue
        admitted.append((pin, claim))
        part['status'] = 'verified'
    pins = dict.fromkeys(pin for pin, _ in admitted)
    if len(proved_pins) > 1:
        return 'conflict', 'compound_field_incomplete', {'missing': list(fields),
                    'question_parts': [dict(p, status='unresolved') for p in parts]}
    claims = [claim for _, claim in admitted]
    missing = [p['field'] for p in parts if p['status'] != 'verified']
    kind = ('supported_answer' if not missing else 'partial_answer' if claims
            else 'conflict' if conflict else 'abstain')
    code = ('supported' if not missing else 'compound_field_budget' if any(
        p['status'] == 'budget' for p in parts) else 'compound_field_incomplete')
    return kind, code, {'answer_supported': not missing,
                        'question_parts': parts, 'missing': missing, 'claims': claims,
                        'sources': [{'id': source_id, 'path': path, 'hash': hash_} for source_id, path, hash_ in pins],
                        'text': '\n'.join(c['text'] for c in claims),
                        'verification': {'structural': bool(claims), 'semantic': 'bounded_named_compound_fields',
                                         'truth_verified': False, 'independence_verified': False}}


def _diagnostic(code, category, message, next_step):
    return {'code': code, 'category': category, 'stage': 'compound_field_verification',
            'message': message, 'next_steps': [next_step], 'corpus_answerability': 'not_established'}


def _same_record(left, right):
    if left['path'] == right['path'] and left['hash'] == right['hash']:
        return True
    # These are the exact, gated sources supplied by the two field serving
    # views. Only a pinned supersession can connect different revisions.
    return (left['id'] + '@' + left['hash'] in right['supersedes']
            or right['id'] + '@' + right['hash'] in left['supersedes'])


def answer_fields(root, question, profile, as_of, compound, max_passages, max_chars):
    from .pipeline import _answer_query

    across_records = compound[0][0] != compound[1][0]
    views = []
    checked = []
    for record_id, name in compound:
        exact = relation_graph.exact_request(question, record_id, name)
        exact = field_aliases.resolve(root, question, profile, exact, as_of)
        with serving_view(as_of, exact['field']):
            result = _answer_query(root, question, profile, mode='strict', reader=None, min_confidence=0,
                                   max_passages=max_passages, max_chars=max_chars, exact=exact,
                                   relation_hops=None)
        views.append((exact, result.gate, result.contract['diagnostic']['code']))
        checked.append(result.contract)

    parts = [{'field': name, 'status': 'unresolved', 'diagnostic': item['diagnostic']}
             for (_, name), item in zip(compound, checked)]
    if across_records:
        for part, (record_id, _) in zip(parts, compound):
            part['record_id'] = record_id
    admitted = []
    complete = [i for i, item in enumerate(checked) if item['answer_supported']]
    conflict = any(item['kind'] == 'conflict' for item in checked)
    if len(complete) == 2 and not across_records and views[0][0]['field'] == views[1][0]['field']:
        parts[1]['diagnostic'] = _diagnostic('compound_duplicate_field', 'clarification_required',
                                            'Both expressions select the same field.', 'Name two distinct field labels.')
        complete.pop()
    for i in complete.copy():
        if len(checked[i]['sources']) != 1:
            parts[i]['diagnostic'] = _diagnostic('compound_multiple_records', 'clarification_required',
                                                'The field matches multiple record appearances.',
                                                'Pin one source record by its ledger identifier.')
            complete.remove(i)
    if len(complete) == 2 and _same_record(checked[0]['sources'][0], checked[1]['sources'][0]) == across_records:
        for part in parts:
            part['diagnostic'] = _diagnostic('compound_multiple_records', 'clarification_required',
                'Both identifiers resolve to the same record or revision chain.' if across_records
                else 'The fields resolve to different records.',
                'Pin two distinct ledger records.' if across_records else 'Pin one source record by its ledger identifier.')
        complete.clear()
    for i in complete:
        claims = checked[i]['claims']
        if across_records:
            claims = [dict(claim, text=f"{compound[i][0]}: {claim['text']}") for claim in claims]
        candidate = {'claims': admitted + claims, 'missing': []}
        if output_budget(candidate, max_passages, max_chars):
            parts[i]['diagnostic'] = _diagnostic('compound_field_budget', 'index_exhaustion',
                                                'The field proof exceeds the shared evidence budget.',
                                                'Increase the evidence budget or ask for one field.')
        else:
            admitted = candidate['claims']
            parts[i]['status'] = 'verified'

    if across_records:
        for i, item in enumerate(checked):
            if item['kind'] != 'conflict':
                continue
            parts[i]['status'] = 'conflict'
            if item['diagnostic']['code'] != 'conflicting_or_multiple_owners' or not item['claims']:
                continue
            witness = {
                'text': f"{compound[i][0]}: " + '; '.join(claim['text'] for claim in item['claims']),
                'citations': [cite for claim in item['claims'] for cite in claim['citations']],
                'qualifiers': ['Competing field passages. No unique value was selected.'],
            }
            candidate = {'claims': admitted + [witness], 'missing': []}
            if not output_budget(candidate, max_passages, max_chars):
                admitted = candidate['claims']
            else:
                parts[i]['diagnostic'] = _diagnostic(
                    'contradictory_passages_pruned', 'known_source_conflict',
                    'The competing passages do not fit together in the shared budget.',
                    'Increase the evidence budget to inspect both witnesses.')

    sources = {(cite['source_id'], cite['path'], cite['hash']):
               {'id': cite['source_id'], 'path': cite['path'], 'hash': cite['hash']}
               for claim in admitted for cite in claim['citations']}
    missing = [f"{part['record_id']}: {part['field']}" if across_records else part['field']
               for part in parts if part['status'] != 'verified']
    kind = ('supported_answer' if not missing else 'conflict' if conflict
            else 'partial_answer' if admitted else 'clarify' if any(
                part['diagnostic']['category'] == 'clarification_required' for part in parts)
            else 'abstain')
    return {'kind': kind, 'question_parts': parts, 'missing': missing, 'claims': admitted,
            'sources': list(sources.values()), 'text': '\n'.join(c['text'] for c in admitted),
            'answer_supported': not missing,
            'verification': {'structural': bool(admitted), 'semantic': 'bounded_compound_fields',
                             'truth_verified': False, 'independence_verified': False}}, views


def recheck(root, question, profile, as_of, views):
    sources = {}
    for exact, expected, code in views:
        if code == 'source_changed':
            return False, []
        resolution = exact.get('alias_resolution')
        if resolution and not field_aliases.unchanged(root, question, profile, resolution):
            return False, []
        with serving_view(as_of, exact['field']):
            fresh = G.gather(root, question, profile).to_dict()
        if fresh != expected:
            return False, []
        for source in fresh['sources']:
            sources[source['id'], source['path'], source['hash']] = source
    return True, list(sources.values())
