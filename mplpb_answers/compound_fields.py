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
