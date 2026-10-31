"""Bounded source-declared requirements/permission conditions, never execution advice.

Match complete subjects and predicates; copy complete policy sentences, including
exceptions and negation. Necessary conditions do not establish sufficiency.
"""
from dataclasses import dataclass
import re
from .frames import normalize
from .literal_evidence import LiteralRequest
from .body_text import body_text
from mplpb_combined.record import text_of

VERSION = 'source-policy-v1'
WORDS = r'[a-z][a-z0-9-]*(?: [a-z][a-z0-9-]*){0,8}'
UNSAFE_SUBJECT = re.compile(r'\b(?:not|never|if|unless|before|after|without|except|tomorrow|yesterday|currently|formerly|and|or|it|they|this|that|these|those|my|your)\b')


@dataclass(frozen=True)
class PolicyRequest(LiteralRequest):
    def to_dict(self):
        return dict(super().to_dict(), version=VERSION, authority='source_declared_policy',
                    execution_verified=False, sufficient_conditions_proved=False)


def parse(question):
    q = normalize(question)
    q = re.sub(r'^(?:please |can you tell me |could you tell me )', '', q)
    requirements = (rf'what does (?P<entity>{WORDS}) require',
                    rf'what is required for (?P<entity>{WORDS})',
                    rf'what are the requirements for (?P<entity>{WORDS})',
                    rf'what requirements apply to (?P<entity>{WORDS})')
    for pattern in requirements:
        match = re.fullmatch(pattern, q)
        if match and not UNSAFE_SUBJECT.search(match['entity']):
            return PolicyRequest('requirements', match['entity'], q)
    match = re.fullmatch(rf'(?:under what conditions|when) (?P<modal>can|may) (?P<entity>{WORDS}) be (?P<verb>[a-z]+)', q)
    if match and not UNSAFE_SUBJECT.search(match['entity']):
        return PolicyRequest('permission_conditions', match['entity'], q, match['modal']+':'+match['verb'])
    return None


def _subject(entity):
    # Only an explicitly indefinite singular question licenses regular plural s.
    indefinite = entity.startswith(('a ', 'an '))
    entity = re.sub(r'^(?:the|an?) ', '', entity)
    return r'(?:the |an? )?'+re.escape(entity)+(r's?' if indefinite else '')


def statement_support(frame, record):
    context = text_of(record.body_html)
    if re.search(r'(?:^|[\n.!?]\s*)(?:if|unless|when|while|provided|assuming|except|only if|only when|only after|imagine|suppose|pretend|assume|ignore|example|hypothetical|draft)\b|\b(?:hypothetical|for example|example only|draft policy|fictional|not authoritative|not a policy)\b', context, re.I):
        return {'status': 'unsupported', 'spans': [], 'unresolved': True,
                'reason': 'Unresolved conditional, instructional or hypothetical source context.'}
    subject = _subject(frame.entity)
    if frame.relation == 'requirements':
        affirmative = subject+r' requires? (?P<value>.+)'
        denial = subject+r' (?:does? not|must not|never) require (?P<value>.+)'
        relevant = subject+r'\b.*\brequir'
    else:
        modal, verb = frame.other.split(':')
        predicate = r' be '+re.escape(verb)
        affirmative = subject+' '+modal+predicate+r' only (?:when|if|after) (?P<value>.+)'
        denial = subject+r' (?:cannot|can not|must not|may not|never)' +predicate+r'(?: .+)?'
        relevant = subject+r'\b.*\b'+re.escape(verb)+r'\b'
    spans, denied, unresolved, sentences = [], False, False, []
    for paragraph in body_text(record.body_html).splitlines():
        parts = re.split(r'(?<=[.!?])\s+', paragraph)
        # Imported Wiki leads may combine a neutral document description with
        # the final policy sentence. Do not drop trailing exceptions or accept
        # arbitrary preceding prose as harmless context.
        if len(parts) > 1:
            if all(re.fullmatch(affirmative, normalize(p)) or re.fullmatch(denial, normalize(p)) for p in parts):
                sentences.extend(parts)
                continue
            if not re.match(relevant, normalize(parts[-1])):
                if any(re.match(relevant, normalize(p)) for p in parts):
                    unresolved = True
                continue
            neutral = subject+r' (?:is|are) an? (?:[a-z-]+ ){0,2}(?:policy|reference|guide|document)'
            if not all(re.fullmatch(neutral, normalize(p)) for p in parts[:-1]):
                unresolved = True
                continue
        sentences.append(parts[-1])
    for raw in sentences:
        line = normalize(raw)
        if not re.match(relevant, line):
            continue
        # Never drop inherited conditions or speculative/quoted authority.
        if re.search(r'(?<=[.!?])\s+', raw) or re.search(r'["“”]|\b(?:maybe|perhaps|possibly|probably|reportedly|allegedly|might|could|would|should|unknown|claims?|says?|said|believes?)\b', line):
            unresolved = True
            continue
        if re.fullmatch(denial, line):
            denied = True
            continue
        match = re.fullmatch(affirmative, line)
        if match:
            value = match['value']
            if raw.rstrip().endswith(':') or re.search(r'\b(?:the following|as follows|see above|see below|elsewhere|unspecified|unrecorded)\b', value):
                unresolved = True
            else:
                spans.append({'quote': raw, 'value': line})
        else:
            unresolved = True
    conflict = len({s['value'] for s in spans}) > 1 or (bool(spans) and denied)
    return {'status': 'conflict' if conflict else 'supported' if spans and not unresolved else 'unsupported',
            'spans': spans, 'policy_denial': denied, 'unresolved': unresolved,
            'reason': 'Complete source-declared policy sentence; conditions and exceptions retained. Source truth, sufficiency and execution are not verified.'}
