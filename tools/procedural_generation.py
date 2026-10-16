"""Bounded idea grammar. Output is conversation, never ledger evidence.

Enumerate a Cartesian product with mixed-radix indices. No random state, clocks,
network calls, Python hash(), or previously generated prose enter the seed.
"""
import hashlib
import json

VERSION = 'idea-grammar-v1'
OPERATIONS = (
    ('simplify', 'Imagine a smaller version of {topic}'),
    ('combine', 'Imagine combining two parts of {topic}'),
    ('perspective', 'Imagine introducing {topic} to a newcomer'),
    ('reverse', 'Imagine reversing one assumption about {topic}'),
    ('constraint', 'Imagine giving {topic} one playful limitation'),
    ('prototype', 'Imagine a rough prototype of {topic}'),
)
LENSES = (
    ('first-step', 'Focus on the first step someone could try.'),
    ('collaboration', 'Focus on how two people could participate.'),
    ('adaptation', 'Focus on what someone could change to make it their own.'),
    ('discovery', 'Focus on something someone could discover through trying it.'),
)
FORMS = (
    ('sketch', 'Sketch one possible scene, then mark an unanswered question.'),
    ('sequence', 'Describe three possible steps, then mark an assumption to check.'),
    ('contrast', 'Describe two possible versions, then name a trade-off to explore.'),
    ('trial', 'Outline a small trial, then say what you would want to learn.'),
)


def canonical(value):
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(',', ':'))


def digest(value):
    return hashlib.sha256(canonical(value).encode('utf-8')).hexdigest()


GRAMMAR_SHA256 = digest({'version': VERSION, 'operations': OPERATIONS,
                         'lenses': LENSES, 'forms': FORMS})
SPACE_SIZE = len(OPERATIONS) * len(LENSES) * len(FORMS)


def construct(subject, turn):
    """Return three proposals and a replay recipe for a 1-based turn.

    Each consecutive group has distinct operations. The 96 slot combinations
    are exhausted before any combination repeats (32 groups of three).
    Subject bytes are preserved as data, never parsed as grammar instructions.
    """
    if not isinstance(subject, str) or not subject.strip() or len(subject) > 180:
        raise ValueError('subject must contain 1 to 180 characters')
    if type(turn) is not int or turn < 1:
        raise ValueError('turn must be a positive integer')
    seed = digest({'subject': subject, 'grammar_sha256': GRAMMAR_SHA256})
    offset = int(seed, 16) % SPACE_SIZE
    choices = []
    lines = []
    for position in range(3):
        index = (offset + (turn - 1) * 3 + position) % SPACE_SIZE
        remaining, op = divmod(index, len(OPERATIONS))
        form, lens = divmod(remaining, len(LENSES))
        operation, template = OPERATIONS[op]
        lens_id, lens_text = LENSES[lens]
        form_id, form_text = FORMS[form]
        lines.append(template.format(topic=subject)+'. '+lens_text+' '+form_text)
        choices.append({'index': index, 'operation': operation,
                        'lens': lens_id, 'form': form_id})
    return lines, {'version': VERSION, 'grammar_sha256': GRAMMAR_SHA256,
                   'input_sha256': seed, 'subject': subject, 'turn': turn,
                   'rules': ['operation + user_topic + lens + exploratory_form'],
                   'operations': [choice['operation'] for choice in choices],
                   'choices': choices, 'space_size': SPACE_SIZE,
                   'cycle': (turn - 1) // (SPACE_SIZE // 3),
                   'deterministic': True, 'mplpb_supported': False}
