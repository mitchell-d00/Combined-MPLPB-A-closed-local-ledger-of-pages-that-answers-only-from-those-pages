"""Fail-closed source support for a finite, unconditional status grammar.

This is independent of specialist assessments and reviews, not general entailment.
Unsupported language, assumptions and inference chains require rechecking.
"""
import re

VERSION = 'work-source-status-v1'
OPPOSITE = {'available': 'discontinued', 'discontinued': 'available',
            'active': 'inactive', 'inactive': 'active',
            'enabled': 'disabled', 'disabled': 'enabled'}
STATUS = re.compile(r'([A-Z][A-Za-z0-9_-]*(?: [A-Za-z0-9_-]+){0,7}) '
                    r'(?:is|remains) (not )?(available|discontinued|active|inactive|enabled|disabled)\.?')


def assertion(text):
    match = STATUS.fullmatch(text.strip())
    if not match:
        return None
    subject, negative, value = match.groups()
    if set(subject.lower().split()) & {'if', 'when', 'unless', 'and', 'or', 'not', 'said', 'claims'}:
        return None
    return subject, value, bool(negative)


def check(payload, evidence):
    """Evidence contains coordinator-loaded full bodies and pinned exact quotes."""
    claim = assertion(payload['proposition'])
    if not claim or payload['assumptions'] or not evidence:
        return 'needs_recheck'
    supported, unknown_context = False, False
    for body, quote in evidence:
        # Whole sentences only: substrings cannot discard a condition or negation.
        for sentence in re.split(r'(?<=[.!?])\s+', body.strip()):
            source = assertion(sentence)
            if source is None:
                unknown_context = True
                continue
            if source[0] != claim[0]:
                continue
            if ((source[1] == claim[1] and source[2] != claim[2])
                    or (source[1] == OPPOSITE[claim[1]] and not source[2] and not claim[2])):
                return 'contested'
            if source == claim and sentence.strip() in quote:
                supported = True
    return 'supported_under_scope' if supported and not unknown_context else 'needs_recheck'
