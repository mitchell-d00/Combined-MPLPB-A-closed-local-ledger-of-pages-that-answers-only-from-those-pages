"""Compose independently checked field answers for one explicitly pinned record."""
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
                return match['record'], labels
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

    record_id, names = compound
    views = []
    checked = []
    for name in names:
        exact = relation_graph.exact_request(question, record_id, name)
        exact = field_aliases.resolve(root, question, profile, exact, as_of)
        with serving_view(as_of, exact['field']):
            result = _answer_query(root, question, profile, mode='strict', reader=None, min_confidence=0,
                                   max_passages=max_passages, max_chars=max_chars, exact=exact,
                                   relation_hops=None)
        views.append((exact, result.gate, result.contract['diagnostic']['code']))
        checked.append(result.contract)

    parts = [{'field': name, 'status': 'unresolved', 'diagnostic': item['diagnostic']}
             for name, item in zip(names, checked)]
    admitted = []
    complete = [i for i, item in enumerate(checked) if item['answer_supported']]
    conflict = any(item['kind'] == 'conflict' for item in checked)
    if len(complete) == 2 and views[0][0]['field'] == views[1][0]['field']:
        parts[1]['diagnostic'] = _diagnostic('compound_duplicate_field', 'clarification_required',
                                            'Both expressions select the same field.', 'Name two distinct field labels.')
        complete.pop()
    for i in complete.copy():
        if len(checked[i]['sources']) != 1:
            parts[i]['diagnostic'] = _diagnostic('compound_multiple_records', 'clarification_required',
                                                'The field matches multiple record appearances.',
                                                'Pin one source record by its ledger identifier.')
            complete.remove(i)
    if len(complete) == 2 and not _same_record(checked[0]['sources'][0], checked[1]['sources'][0]):
        for part in parts:
            part['diagnostic'] = _diagnostic('compound_multiple_records', 'clarification_required',
                                            'The fields resolve to different records.',
                                            'Pin one source record by its ledger identifier.')
        complete.clear()
    for i in complete:
        candidate = {'claims': admitted + checked[i]['claims'], 'missing': []}
        if output_budget(candidate, max_passages, max_chars):
            parts[i]['diagnostic'] = _diagnostic('compound_field_budget', 'index_exhaustion',
                                                'The field proof exceeds the shared evidence budget.',
                                                'Increase the evidence budget or ask for one field.')
        else:
            admitted = candidate['claims']
            parts[i]['status'] = 'verified'

    sources = {(source['id'], source['path'], source['hash']): source
               for i, part in enumerate(parts) if part['status'] == 'verified'
               for source in checked[i]['sources']}
    missing = [part['field'] for part in parts if part['status'] != 'verified']
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
