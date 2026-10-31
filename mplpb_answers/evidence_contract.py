"""Domain-independent proposed claims and separate semantic review contracts.

Schema validity and exact citations are structural checks, never truth proofs.
"""
import hashlib
import json
import math
import re

VERSION = 'answer-contract-v1'


class ReaderError(ValueError):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False)


def pin(value):
    return 'sha256:'+hashlib.sha256(canonical(value).encode()).hexdigest()


def loads(raw):
    def pairs(items):
        out = {}
        for key, value in items:
            if key in out:
                raise ReaderError('invalid_reader_output', 'Duplicate JSON field')
            out[key] = value
        return out
    try:
        result = json.loads(raw, object_pairs_hook=pairs, parse_constant=lambda _: (_ for _ in ()).throw(ValueError()))
        canonical(result)
        return result
    except (ValueError, TypeError, RecursionError) as exc:
        raise ReaderError('invalid_reader_output', 'Reader output must be bounded, strict JSON') from exc


def text(value, limit=2000, empty=False):
    if not isinstance(value, str) or len(value) > limit or (not empty and not value.strip()):
        raise ReaderError('invalid_reader_output', 'Expected bounded text')


def strings(value, limit=12):
    if not isinstance(value, list) or len(value) > limit:
        raise ReaderError('invalid_reader_output', 'Expected a bounded text list')
    for item in value:
        text(item)


def shape(value, fields):
    if not isinstance(value, dict) or set(value) != set(fields.split()):
        raise ReaderError('invalid_reader_output', 'Missing or unexpected evidence fields')


def confidence(value):
    if type(value) not in (int, float) or not math.isfinite(value) or not 0 <= value <= 1:
        raise ReaderError('invalid_reader_output', 'Confidence must be a finite number from zero to one')


def validate_proposal(doc, question, passages):
    shape(doc, 'question outcome claims missing clarification confidence')
    if doc['question'] != question:
        raise ReaderError('question_changed', 'Reader did not preserve the complete original question')
    if doc['outcome'] not in {'answer', 'partial', 'clarify', 'conflict', 'abstain'}:
        raise ReaderError('invalid_reader_output', 'Unknown reader outcome')
    confidence(doc['confidence']); strings(doc['missing']); text(doc['clarification'], empty=True)
    if not isinstance(doc['claims'], list) or len(doc['claims']) > 12:
        raise ReaderError('invalid_reader_output', 'Expected at most twelve atomic claims')
    if doc['outcome'] in {'answer', 'partial', 'conflict'} and not doc['claims']:
        raise ReaderError('missing_evidence', 'An answer needs cited claims')
    if doc['outcome'] in {'clarify', 'abstain'} and doc['claims']:
        raise ReaderError('invalid_reader_output', 'Nonanswers must not contain answer claims')
    if doc['outcome'] == 'clarify' and not doc['clarification'].strip():
        raise ReaderError('invalid_reader_output', 'Clarification must name the missing context')
    if doc['outcome'] == 'partial' and not doc['missing']:
        raise ReaderError('invalid_reader_output', 'Partial answers must identify what remains unanswered')
    lookup = {p['id']: p for p in passages}
    result = []
    for claim in doc['claims']:
        shape(claim, 'text qualifiers citations')
        text(claim['text']); strings(claim['qualifiers'])
        if not isinstance(claim['citations'], list) or not 1 <= len(claim['citations']) <= 6:
            raise ReaderError('missing_evidence', 'Every claim needs exact passage citations')
        citations = []
        for cite in claim['citations']:
            shape(cite, 'passage quote')
            if not isinstance(cite['passage'], str) or cite['passage'] not in lookup:
                raise ReaderError('invalid_citation', 'Citation does not identify a supplied eligible passage')
            p = lookup[cite['passage']]
            text(cite['quote'], 5000)
            begin = p['text'].find(cite['quote'])
            if begin < 0:
                raise ReaderError('invalid_citation', 'Citation must match an exact source substring')
            if p['text'].find(cite['quote'], begin+1) >= 0:
                raise ReaderError('ambiguous_citation', 'Expand the quote to identify one unique location in the passage')
            end = begin+len(cite['quote'])
            citations.append(dict(cite, start=begin, end=end, source_id=p['source_id'], path=p['path'], hash=p['hash'],
                                  body_start=p['body_start']+begin, body_end=p['body_start']+end))
        # This limited guard catches fabricated numeric literals, not subject,
        # relation, unit or qualifier entailment. Those require semantic review.
        numbers = lambda s: set(re.findall(r'(?<!\w)\d+(?:[,.]\d+)*(?!\w)', s))
        evidence_numbers = numbers(' '.join(lookup[c['passage']]['text'] for c in citations))
        if not numbers(claim['text']+' '+' '.join(claim['qualifiers'])) <= evidence_numbers:
            raise ReaderError('unsupported_numeric_literal', 'A proposed numeric literal is absent from its cited context')
        result.append(dict(claim, citations=citations))
    return result


def validate_review(doc, question, claims):
    shape(doc, 'question verdict checks complete missing confidence')
    if doc['question'] != question or doc['verdict'] not in {'accept', 'reject', 'conflict', 'clarify'}:
        raise ReaderError('invalid_review', 'Review must preserve the question and a known verdict')
    confidence(doc['confidence']); strings(doc['missing'])
    if type(doc['complete']) is not bool or not isinstance(doc['checks'], list) or len(doc['checks']) != len(claims):
        raise ReaderError('invalid_review', 'Review must assess every proposed claim')
    seen = set()
    for check in doc['checks']:
        shape(check, 'claim supported subject_matches relation_matches constraints_preserved reason')
        index = check['claim']
        if type(index) is not int or not 0 <= index < len(claims) or index in seen:
            raise ReaderError('invalid_review', 'Claim review indices must be unique and complete')
        seen.add(index); text(check['reason'], 1000)
        if any(type(check[key]) is not bool for key in ('supported', 'subject_matches', 'relation_matches', 'constraints_preserved')):
            raise ReaderError('invalid_review', 'Review decisions must be explicit booleans')
    return sorted(doc['checks'], key=lambda item: item['claim'])


def obj(properties):
    return {'type': 'object', 'properties': properties, 'required': list(properties), 'additionalProperties': False}


S = {'type': 'string'}
B = {'type': 'boolean'}
N = {'type': 'number', 'minimum': 0, 'maximum': 1}
STRINGS = {'type': 'array', 'items': S, 'maxItems': 12}
CITATION_SCHEMA = obj({'passage': S, 'quote': S})
CLAIM_SCHEMA = obj({'text': S, 'qualifiers': STRINGS, 'citations': {'type': 'array', 'items': CITATION_SCHEMA, 'minItems': 1, 'maxItems': 6}})
PROPOSAL_SCHEMA = obj({'question': S, 'outcome': {'type': 'string', 'enum': ['answer', 'partial', 'clarify', 'conflict', 'abstain']},
                       'claims': {'type': 'array', 'items': CLAIM_SCHEMA, 'maxItems': 12}, 'missing': STRINGS, 'clarification': S, 'confidence': N})
REVIEW_SCHEMA = obj({'question': S, 'verdict': {'type': 'string', 'enum': ['accept', 'reject', 'conflict', 'clarify']},
                     'checks': {'type': 'array', 'items': obj({'claim': {'type': 'integer'}, 'supported': B, 'subject_matches': B,
                     'relation_matches': B, 'constraints_preserved': B, 'reason': S}), 'maxItems': 12}, 'complete': B, 'missing': STRINGS, 'confidence': N})
PLAN_SCHEMA = obj({'question': S, 'queries': {'type': 'array', 'items': S, 'maxItems': 3}})
