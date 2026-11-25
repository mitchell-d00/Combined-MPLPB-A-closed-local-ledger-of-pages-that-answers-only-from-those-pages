"""Native source-voice verification for instructions across documentary forms."""
import re

from . import documentary_verify as kernel
from .passages import _passage_units
from .source_attribution import FULL_NAME, instruction_roles, source_frame, unqualified_span

_FORM = r'(?P<form>letter|minutes|report)'
_ACTOR = rf'(?P<actor>{FULL_NAME})'
_TEAM = r'(?P<recipient>the [a-z]+(?:[ -][a-z]+){0,7})'
_REQUESTS = [
    rf'According to the {_FORM}, what did {_ACTOR} instruct {_TEAM} to do\?',
    rf'In the {_FORM}, what instruction did {_ACTOR} give {_TEAM}\?',
    rf'What instruction to {_TEAM} is attributed to {_ACTOR} in the {_FORM}\?',
    rf'According to the {_FORM}, which task did {_ACTOR} assign {_TEAM}\?',
]
_REQUESTS = [re.compile(p) for p in _REQUESTS]
_COMPLETION = re.compile(rf'According to the {_FORM}, did {_TEAM} complete the task instructed by {_ACTOR}\?')


def request(question):
    for pattern in _REQUESTS:
        if match := pattern.fullmatch(question.strip()):
            return dict(match.groupdict(), completion=False)
    if match := _COMPLETION.fullmatch(question.strip()):
        return dict(match.groupdict(), completion=True)
    return None


def _proof(record, body, frame, goal):
    assertions = []
    for start, text, truncated in _passage_units(record.body_html, body):
        end = start + len(text)
        if not (frame['start'] <= start < end <= frame['end']):
            continue
        if truncated or len(text) > 2200:
            return None
        if re.search(r'\b(?:if|unless|conditional|provided|assuming|denied|hypothetical|'
                     r'example|fictional|draft|might|would)\b|\bsubject to\b', text, re.I):
            return None
        roles = instruction_roles(text)
        if not roles:
            # A nearby denied, qualified or unsupported instruction cannot be
            # silently pruned in favour of another superficially positive one.
            if re.search(r'\b(?:instruct\w*|order\w*|directed)\b', text, re.I):
                return None
            continue
        if not unqualified_span(record, body, start, end):
            return None
        if roles['first_person']:
            if frame['form'] != 'letter':
                return None
            actor = frame['writer']
            layer = 'signed_letter_first_person'
        else:
            actor = roles['speaker']
            layer = {'minutes': 'minutes_attributes_instruction',
                     'report': 'report_attributes_quotation' if roles['quotation'] else 'report_attributes_instruction',
                     'letter': 'letter_attributes_quotation' if roles['quotation'] else 'letter_attributes_instruction'}[frame['form']]
        assertions.append(dict(roles, actor=actor, source_voice=layer,
                               statement=text, citation=kernel.citation(record, body, start, end)))
    relevant = [v for v in assertions if v['actor'] == goal['actor'] and v['recipient'] == goal['recipient']]
    if len(relevant) != 1:
        return None
    value = relevant[0]
    proposition = {'relation': 'source_attributed_instruction', 'actor': value['actor'],
        'writer': frame['writer'], 'recipient': value['recipient'], 'task': value['task'],
        'source_voice': value['source_voice'], 'source_form': frame['form'],
        'quoted_instruction': value['quotation'], 'modality': 'instruction_only',
        'polarity': 'affirmative', 'conditions': [], 'completion_established': False,
        'historical_truth_independently_verified': False,
        'reporting_chain': [{'role': 'document_writer', 'actor': frame['writer']},
                            {'role': 'attributed_instructor', 'actor': value['actor']}],
        'directive': value['statement']}
    text = ('The '+frame['form']+' attributed to '+frame['writer']+' attributes this instruction to '
            +value['actor']+' for '+value['recipient']+': '+value['task']+'.')
    return {'text': text, 'proposition': proposition,
            'citations': sorted(frame['witnesses']+[value['citation']], key=lambda c: c['body_start']),
            'source_support_established': True,
            'qualifiers': ['Source-attributed instruction only. Authenticated authorship, '
                           'occurrence, agreement and execution remain unverified.']}


def verify(index, max_passages, max_chars):
    goal = request(index.question)
    if not goal:
        return None
    if goal['completion']:
        return 'abstain', 'instruction_does_not_establish_completion', {}
    if len(index.records) > 8:
        return 'abstain', 'reference_scan_budget', {}
    checked = kernel.check(index, [])
    if checked['status'] != 'checked':
        return 'abstain', 'source_changed', {}
    if not checked['scan_complete']:
        return 'abstain', 'reference_scan_budget', {}
    records = {r.path: r for r, *_ in checked['contexts']}
    count = 0
    candidates = []
    for record in records.values():
        for _ in _passage_units(record.body_html, kernel.body_text(record.body_html)):
            count += 1
            if count > 1000:
                return 'abstain', 'reference_scan_budget', {}
        framed = source_frame(record, goal['form'])
        if framed:
            body, frame = framed
            candidates.append((record, _proof(record, body, frame, goal)))
        else:
            body = kernel.body_text(record.body_html)
            if (goal['actor'] in body and goal['recipient'] in body
                    and re.search(r'\b(?:instruct\w*|order\w*|directed)\b', body, re.I)):
                candidates.append((record, None))
    proofs = [(r, p) for r, p in candidates if p]
    # Every framed document is inspected; an unresolved competing document
    # cannot disappear because another document supplies a convenient witness.
    if len(candidates) != 1 or len(proofs) != 1:
        return 'abstain', 'instruction_attribution_unresolved', {}
    record, proof = proofs[0]
    witnesses = proof['citations']
    if len(witnesses) > max_passages or sum(len(c['quote']) for c in witnesses) > max_chars:
        return 'abstain', 'reader_budget_exceeded', {}
    if not index.unchanged():
        return 'abstain', 'source_changed', {}
    return 'supported_answer', 'supported', {
        'claims': [proof], 'answer_supported': True, 'text': proof['text'], 'missing': [],
        'sources': [s for s in index.sources if s['path'] == record.path],
        'verification': {'structural': True, 'semantic': 'bounded_source_attribution',
                         'truth_verified': False, 'independence_verified': False},
        'documentary_support': {'scope': 'source_attributed_instruction', 'source_support_claims': 1,
            'examined_characters': checked['examined_characters'], 'examined_units': checked['examined_units'],
            'paragraph_units': count, 'limits': checked['limits'], 'record_limit': 8}}
