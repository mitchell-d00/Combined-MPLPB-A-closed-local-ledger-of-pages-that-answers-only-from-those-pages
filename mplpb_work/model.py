"""Closed work-record schema. Working assessments are never truth certificates."""
import json
import re
from .errors import WorkError

KINDS = {'task', 'evidence', 'claim', 'attempt', 'decision', 'action', 'review'}
OPERATIONS = {verb+':'+kind for verb in ('create', 'revise') for kind in KINDS} | {'execute', 'transfer', 'resolve_review'}
ASSESSMENTS = {'proposed', 'supported_under_scope', 'contested', 'withdrawn', 'needs_recheck'}
FIELDS = {
    'task': {'goal', 'criteria', 'review_budget', 'state', 'acceptance'},
    'evidence': {'task', 'corpus', 'source_id', 'source_hash', 'quote', 'query'},
    'claim': {'task', 'proposition', 'basis', 'assessment', 'assumptions', 'alternatives', 'revisit_when'},
    'attempt': {'task', 'method', 'result', 'failure', 'retry_when', 'artifact'},
    'decision': {'task', 'choice', 'alternatives', 'reason', 'assessment', 'recheck_when', 'failed_attempts'},
    'action': {'task', 'task_revision', 'operation', 'arguments', 'side_effect', 'executor_seat', 'state', 'retry_of', 'retry_reason'},
    'review': {'task', 'target', 'target_variable', 'regime', 'finding', 'outcome', 'resolution'},
}


def identifier(value):
    if not isinstance(value, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._:-]{0,99}', value):
        raise WorkError('Invalid identifier')
    return value


def words(value, limit=4000):
    if not isinstance(value, str) or not value.strip() or len(value) > limit:
        raise WorkError('Expected bounded, nonempty text')
    return value


def strings(value, empty=True):
    if not isinstance(value, list) or len(value) > 100 or (not empty and not value):
        raise WorkError('Expected a bounded text list')
    for item in value:
        words(item)
    if len(set(value)) != len(value):
        raise WorkError('Repeated list item')


def pins(value):
    if not isinstance(value, dict) or len(value) > 100:
        raise WorkError('Expected revision-pinned references')
    for key, revision in value.items():
        identifier(key)
        if type(revision) is not int or revision < 1:
            raise WorkError('References require positive integer revisions')


def validate(kind, payload):
    if kind not in KINDS or not isinstance(payload, dict) or set(payload) != FIELDS[kind]:
        raise WorkError('Unknown kind or missing/extra record fields')
    # Strict JSON, including nested arguments; reject NaN, huge/unserializable input.
    if len(json.dumps(payload, allow_nan=False)) > 32000:
        raise WorkError('Record exceeds 32 KB')
    if kind != 'task':
        identifier(payload['task'])
    if kind == 'task':
        words(payload['goal']); strings(payload['criteria'], empty=False)
        if type(payload['review_budget']) is not int or not 1 <= payload['review_budget'] <= 100:
            raise WorkError('Review budget must be 1–100')
        if payload['state'] not in {'open', 'done', 'cancelled'}:
            raise WorkError('Invalid task state')
        pins(payload['acceptance'])
    elif kind == 'evidence':
        for field in ('corpus', 'source_id', 'source_hash', 'quote', 'query'):
            words(payload[field])
    elif kind == 'claim':
        words(payload['proposition']); words(payload['revisit_when'])
        if payload['basis'] not in {'observation', 'inference'} or payload['assessment'] not in ASSESSMENTS:
            raise WorkError('Invalid claim basis or revisable assessment')
        strings(payload['assumptions']); strings(payload['alternatives'])
    elif kind == 'attempt':
        for field in ('method', 'failure', 'retry_when', 'artifact'):
            words(payload[field])
        if payload['result'] not in {'failed', 'inconclusive'}:
            raise WorkError('Passing attempts require a host execution receipt')
    elif kind == 'decision':
        pins(payload['failed_attempts'])
        for field in ('choice', 'reason', 'recheck_when'):
            words(payload[field])
        strings(payload['alternatives'])
        if payload['assessment'] not in {'proposed', 'accepted', 'withdrawn'}:
            raise WorkError('Invalid decision assessment')
    elif kind == 'action':
        pins(payload['retry_of'])
        if len(payload['retry_of']) > 1 or not isinstance(payload['retry_reason'], str):
            raise WorkError('Retry needs at most one prior attempt and a reason')
        if payload['retry_of']:
            words(payload['retry_reason'])
        if type(payload['task_revision']) is not int or payload['task_revision'] < 1:
            raise WorkError('Action requires a pinned task revision')
        identifier(payload['operation']); identifier(payload['executor_seat'])
        if payload['state'] not in {'proposed', 'cancelled'} or payload['side_effect'] not in {'local', 'external'}:
            raise WorkError('Invalid action state or effect class')
        if not isinstance(payload['arguments'], dict):
            raise WorkError('Action arguments must be an object')
    elif kind == 'review':
        pins(payload['target'])
        if len(payload['target']) != 1:
            raise WorkError('A review requires exactly one pinned claim target')
        for field in ('target_variable', 'regime', 'finding'):
            words(payload[field])
        if payload['outcome'] not in {'challenge', 'support', 'inconclusive', 'resolved'}:
            raise WorkError('Invalid review outcome')
        if not isinstance(payload['resolution'], str) or (payload['outcome'] == 'resolved' and not payload['resolution'].strip()):
            raise WorkError('Resolved challenges require an explicit resolution')


def references(record):
    """All references for visibility; only dependencies form the prerequisite DAG."""
    result = dict(record['dependencies'])
    payload = record['payload']
    if record['kind'] != 'task':
        result.setdefault(payload['task'], None)
    if record['kind'] == 'task':
        result.update(payload['acceptance'])
    if record['kind'] == 'decision':
        result.update(payload['failed_attempts'])
    if record['kind'] == 'action':
        result.update(payload['retry_of'])
    if record['kind'] == 'review':
        result.update(payload['target'])
    return result
