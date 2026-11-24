"""Finite proof of explicitly linked statements in selected documentary sources."""
import re

from mplpb_combined.ledger import field_name
from .body_text import body_text
from .documentary_verify import citation, context_ranges

SOURCE_ID = r'[A-Za-z0-9][A-Za-z0-9._-]{0,99}'
_TRIO = rf'sources (?P<first>{SOURCE_ID}), (?P<second>{SOURCE_ID}),? and (?P<third>{SOURCE_ID})'
_CHAIN_FORMS = (
    rf'Trace the request, dispatch,? and reported receipt in {_TRIO}[?.]',
    rf'What request, dispatch,? and reported receipt do {_TRIO} explicitly link\?',
)
_CORRECTION_FORMS = (
    rf'What did source (?P<second>{SOURCE_ID}) change in source (?P<first>{SOURCE_ID}),? and what did it retain\?',
    rf'In source (?P<second>{SOURCE_ID}), what was corrected in source (?P<first>{SOURCE_ID}) and what remained unchanged\?',
)
_PERSON = r"[A-Z][a-z]+(?: [A-Z][a-z]+){1,3}"
_PHRASE = r'[A-Za-z0-9][A-Za-z0-9 -]{1,119}'
_FIELD = r'[A-Za-z][A-Za-z0-9 -]{0,63}'
_CHAIN_QUALIFIER = re.compile(
    r'\b(?:if|unless|except|maybe|perhaps|probably|possibly|not|never|and|or|'
    r'would|could|without|either|then|from|to|at)\b', re.I)
_CORRECTION_QUALIFIER = re.compile(
    _CHAIN_QUALIFIER.pattern + r'|\b(?:reported|reportedly|pending|proposed|allegedly|hypothetical|example)\b',
    re.I)
_NONDECLARATION_FIELDS = {'body', 'draft', 'example', 'notes', 'quote', 'quoted example', 'sample'}
_REQUEST = re.compile(rf'(?P<requester>{_PERSON}) requested that (?P<sender>{_PERSON}) send (?P<object>{_PHRASE}) to (?P<destination>{_PHRASE})\.')
_DISPATCH = re.compile(rf'In response to request source (?P<reference>{SOURCE_ID}), (?P<sender>{_PERSON}) sent (?P<object>{_PHRASE}) to (?P<destination>{_PHRASE})\.')
_RECEIPT = re.compile(rf'Referring to dispatch source (?P<reference>{SOURCE_ID}), (?P<reported_by>{_PERSON}) reported receiving (?P<object>{_PHRASE}) at (?P<destination>{_PHRASE}) from (?P<sender>{_PERSON})\.')
_CORRECTION = re.compile(
    rf'Correction to source (?P<reference>{SOURCE_ID}): (?P<changed>{_FIELD}) should read (?P<replacement>{_PHRASE})\.'
    rf' (?P<retained>{_FIELD}) remains (?P<value>{_PHRASE})\.', re.I)
_DECLARATION = re.compile(rf'(?P<label>{_FIELD}):[ \t]+(?P<value>{_PHRASE})')


def parse(question):
    for task, forms in (('documentary_chain', _CHAIN_FORMS), ('partial_correction', _CORRECTION_FORMS)):
        for form in forms:
            match = re.fullmatch(form, question, re.I)
            if match:
                groups = ('first', 'second', 'third') if task == 'documentary_chain' else ('first', 'second')
                return task, tuple(match[name] for name in groups), None
    return None


def whole_source(record, budget):
    if record is None or len(record.body_html) > budget * 8 + 10000:
        return None
    body = body_text(record.body_html)
    if not body.strip() or len(body) > budget:
        return None
    return citation(record, body, 0, len(body))


def chain(records, source_ids, max_passages, max_chars):
    steps, witnesses = [], []
    required = ('recorded request', 'dispatch linked to the request', 'reported receipt linked to the dispatch')
    for position, (ident, form) in enumerate(zip(source_ids, (_REQUEST, _DISPATCH, _RECEIPT))):
        record = records.get(ident)
        witness = whole_source(record, max_chars)
        if not witness or context_ranges(record):
            break
        match = form.fullmatch(' '.join(witness['quote'].split()))
        if not match or any(_CHAIN_QUALIFIER.search(match[name]) for name in ('object', 'destination')):
            break
        values = match.groupdict()
        if position and (values['reference'] != source_ids[position - 1] or any(
                values[key] != steps[0][key] for key in ('sender', 'object', 'destination'))):
            break
        if len(witnesses) >= max_passages or sum(len(c['quote']) for c in witnesses) + len(witness['quote']) > max_chars:
            break
        steps.append(dict(values, source_id=ident, role=('request', 'dispatch', 'reported_receipt')[position]))
        witnesses.append(witness)
    return {'steps': steps, 'citations': witnesses, 'missing': list(required[len(steps):])}


def correction(records, source_ids, max_chars):
    witnesses = [whole_source(record, min(max_chars, 4000)) for record in records]
    if not all(witnesses) or any(context_ranges(record) for record in records):
        return None
    changes = _CORRECTION.fullmatch(' '.join(witnesses[1]['quote'].split()))
    if not changes or changes['reference'] != source_ids[0]:
        return None
    earlier = {}
    for line in witnesses[0]['quote'].splitlines():
        match = _DECLARATION.fullmatch(line)
        if not match or _CORRECTION_QUALIFIER.search(match['value']):
            return None
        name = field_name(match['label'])
        if name in earlier or name in _NONDECLARATION_FIELDS:
            return None
        earlier[name] = match['value']
    changed, retained = (field_name(changes[name]) for name in ('changed', 'retained'))
    if (changed == retained or not {changed, retained} <= earlier.keys()
            or any(_CORRECTION_QUALIFIER.search(changes[name]) for name in ('replacement', 'value'))
            or earlier[retained] != changes['value']
            or earlier[changed].casefold() == changes['replacement'].casefold()):
        return None
    return {
        'relation': 'documentary_partial_correction', 'earlier_source_id': source_ids[0],
        'correction_source_id': source_ids[1], 'changed_field': changed,
        'previous_value': earlier[changed], 'replacement_value': changes['replacement'],
        'retained_field': retained, 'retained_value': earlier[retained],
    }, witnesses


def resolve(task, records, ids, max_chars):
    if task == 'partial_correction':
        result = correction(records, ids, max_chars)
        if not result:
            return None
        proposition, witnesses = result
        text = (f"Source {ids[1]} changes {proposition['changed_field']} from "
                f"{proposition['previous_value']} to {proposition['replacement_value']} "
                f"and explicitly retains {proposition['retained_field']} as {proposition['retained_value']}.")
    else:
        result = chain(dict(zip(ids, records)), ids, len(ids), max_chars)
        if result['missing']:
            return None
        request, _, receipt = result['steps']
        proposition = {'relation': 'documentary_request_dispatch_receipt', 'steps': result['steps'],
                       **{key: request[key] for key in ('sender', 'object', 'destination')},
                       'reported_by': receipt['reported_by']}
        witnesses = result['citations']
        text = (f"Source {ids[0]} records {request['requester']}'s request to "
                f"{request['sender']} to send {request['object']} to {request['destination']}. "
                f"Source {ids[1]} reports the dispatch in response to that request. "
                f"In source {ids[2]}, {receipt['reported_by']} reports receipt and names that dispatch.")
    return {'text': text, 'proposition': proposition, 'citations': witnesses,
            'source_support_established': True,
            'qualifiers': ['The proof covers the cited source statements only.']}
