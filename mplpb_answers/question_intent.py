"""Finite action-question forms propose goals, never evidence or permissions.

The caller must retain the complete original question for source eligibility,
independent proof and obligation composition. No actor or source fact is inferred.
"""
import re

VERSION = 'action-question-intent-v1'


def action_request(question, past, participles):
    original = question
    q = question.strip().rstrip('? .')
    # These are request scaffolding, not a factual modality of the action.
    q = re.sub(r'^(?:can|could) you\s+(?=(?:identify|name)\b)', '', q, flags=re.I)
    q = re.sub(r'^(?:identify|name)\s+', '', q, flags=re.I)
    active = re.fullmatch(r'(?:who(?: was it that)?|which (?:person|individual))\s+('
                          + '|'.join(map(re.escape, past)) + r')\s+(.{1,240})', q, re.I)
    if active:
        action, obj = past[active[1].lower()], active[2]
    else:
        passive = re.fullmatch(r'By whom was (.{1,240}?)\s+('
                               + '|'.join(map(re.escape, participles)) + r')', q, re.I)
        if not passive:
            return None
        obj, action = passive[1], participles[passive[2].lower()]
    # Never trim an object at a condition, date, negation or extra action.
    # A retained suffix must independently match the complete proof argument;
    # otherwise the original obligation stays unresolved.
    if re.search(r'[;?!:"“”]', obj):
        return None
    return {'action': action, 'object_text': obj, 'original_clause': original,
            'normalization_is_evidence': False, 'version': VERSION}
