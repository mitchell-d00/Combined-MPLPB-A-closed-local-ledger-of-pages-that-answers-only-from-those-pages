"""Verify a delegation task through reusable native signed-letter attribution."""
import re

from . import documentary_verify as kernel
from .passages import _passage_units
from .source_attribution import NAME, signed_letter, unqualified_span

_TOPIC = r'[a-z]+(?:[ -][a-z]+){0,5}'
_SINGLE = re.compile(
    rf'What task did (?P<author>{NAME}) give the (?P<topic>{_TOPIC}) delegation '
    rf'in the letter to (?P<recipient>{NAME})\?', re.I)
_PAIR = re.compile(
    rf'(?P<missing>What transition did (?P<author>{NAME}) intend (?P<possessive>his|her|their) '
    rf'approach in the letter to {NAME} to guide), and what task did (?P<pronoun>he|she|they) '
    rf'give the (?P<topic>{_TOPIC}) delegation in the letter to (?P<recipient>{NAME})\?', re.I)
_TASK = re.compile(r'^The task of (?P<delegation>[^.!?\n]{3,180}) is (?P<negative>not )?to '
                   r'(?P<task>[^.!?\n]{3,600})\.$', re.I)
_OBJECTIVE = re.compile(r'^(?:The (?:fundamental|immediate|primary) objective of [^\n]{3,120}'
                        r'|Our (?:fundamental|immediate|primary) objective) is [^\n]{3,600}\.$', re.I)
_UNSAFE = re.compile(r'\b(?:not|never|if|unless|hypothetical|example|quoted|allegedly|'
                     r'reported|draft|might|would|supposed|only|provided|assuming|when|whenever|'
                     r'until|conditional|contingent)\b|\b(?:subject to|depending on)\b', re.I)
_UNBOUND = re.compile(r'\b(?:those|such|above|aforementioned|it|them)\b', re.I)
_DECLARATION = re.compile(
    r'^(?:These are my instructions (?:for|regarding) [^.!?\n]{3,180}'
    r'|I (?:give|provide|send|convey|set out) (?:to you )?my instructions (?:for|regarding) [^.!?\n]{3,180}'
    r'|In view of [^.!?\n]{3,180}, I (?:wish|want) to address directly to you, '
    r'[^.!?\n]{3,180}, my instructions regarding [^.!?\n]{3,180})\.$')
_VOICE_SWITCH = re.compile(
    r'["“”]|\bI (?:deny|disavow|withdraw)\b|\baccording to\b|'
    r'\b(?:I|[Hh]e|[Ss]he|[Tt]hey|[A-Z][a-z]+) '
    r'(?:said|says|stated|states|reported|reports|claims?|claimed|denied)\b')


def request(question):
    q = kernel.source_question(question)
    match = _SINGLE.fullmatch(q)
    if match:
        return dict(match.groupdict(), missing=None)
    match = _PAIR.fullmatch(q)
    if not match or {'his': 'he', 'her': 'she', 'their': 'they'}[match['possessive'].lower()] != match['pronoun'].lower():
        return None
    return dict(match.groupdict(), missing=match['missing']+'?')


def _topic_matches(topic, subject):
    normalize = lambda s: ' '.join(s.casefold().replace('-', ' ').split())
    return bool(re.search(r'(?<!\w)'+re.escape(normalize(topic))+r'(?!\w)', normalize(subject)))


def _proof(record, body, attribution, goal):
    # Read complete native paragraph boundaries from the original markup. A
    # later quotation cannot be silently folded into the task or its governor.
    units = []
    for start, quote, truncated in _passage_units(record.body_html, body):
        end = start + len(quote)
        if attribution['letter_start'] <= start < end <= attribution['content_end']:
            if truncated or len(quote) > 2200:
                return None
            units.append((start, end, quote))
    tasks = [(a, b, q, _TASK.fullmatch(q)) for a, b, q in units]
    tasks = [(a, b, q, m) for a, b, q, m in tasks if m and 'delegation' in m['delegation'].casefold()
             and _topic_matches(goal['topic'], m['delegation'])]
    if len(tasks) != 1:
        return None
    start, end, directive, task = tasks[0]
    if (task['negative'] or _UNSAFE.search(directive) or _UNBOUND.search(directive)
            or _VOICE_SWITCH.search(directive)
            or not unqualified_span(record, body, start, end)):
        return None
    leads = [(a, b, q) for a, b, q in units if b <= start and _DECLARATION.fullmatch(q)]
    if (len(leads) != 1 or _UNSAFE.search(leads[0][2]) or _VOICE_SWITCH.search(leads[0][2])
            or not unqualified_span(record, body, *leads[0][:2])):
        return None
    witnesses = attribution['witnesses'] + [kernel.citation(record, body, *leads[0][:2]),
                                           kernel.citation(record, body, start, end)]
    if re.search(r'\bthese objectives\b', directive, re.I):
        previous = [unit for unit in units if unit[1] <= start][-2:]
        if len(previous) != 2 or any(not _OBJECTIVE.fullmatch(q) or _UNSAFE.search(q)
                                    or not unqualified_span(record, body, a, b) for a, b, q in previous):
            return None
        witnesses.append(kernel.citation(record, body, previous[0][0], previous[-1][1]))
    elif re.search(r'\b(?:these|this|that)\b', task['task'], re.I):
        return None
    witnesses.sort(key=lambda c: (c['body_start'], c['body_end']))
    return {
        'text': 'The letter signed '+attribution['actor']+' and addressed to '+attribution['addressee']
                +' states this instruction: '+directive,
        'proposition': {'relation': 'source_signed_letter_instruction', 'actor': attribution['actor'],
            'signer': attribution['actor'], 'action': 'instruct', 'object': task['delegation'],
            'addressee': attribution['addressee'], 'directive': directive, 'modality': 'instruction_only',
            'source_voice': attribution['source_voice'], 'polarity': 'affirmative', 'conditions': [],
            'time': {'event_date': None, 'completion_established': False,
                     'source_qualifications': re.findall(r'\b(?:before|after|by|on) '
                         r'(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b', directive)}},
        'citations': witnesses, 'source_support_established': True,
        'qualifiers': ['The source displays a salutation, full signature and instruction. '
                       'Authenticated authorship, agreement and execution remain unverified.'],
    }


def verify(index, max_passages, max_chars):
    goal = request(index.question)
    if not goal:
        return None
    if len(index.records) > 8:
        return 'abstain', 'reference_scan_budget', {}
    # The kernel constructs a new eligible index and rereads canonical bytes.
    checked = kernel.check(index, [])
    if checked['status'] != 'checked':
        return 'abstain', 'source_changed', {}
    if not checked['scan_complete']:
        return 'abstain', 'reference_scan_budget', {}
    originals = {r.path: r for r, *_ in checked['contexts']}
    paragraphs = 0
    for record in originals.values():
        for _ in _passage_units(record.body_html, kernel.body_text(record.body_html)):
            paragraphs += 1
            if paragraphs > 1000:
                return 'abstain', 'reference_scan_budget', {}
    letters = []
    for record in originals.values():
        binding = signed_letter(record, goal['author'], goal['recipient'])
        if binding:
            body, attribution = binding
            letters.append((record, _proof(record, body, attribution, goal)))
    if len(letters) != 1 or letters[0][1] is None:
        return 'abstain', 'signed_instruction_unresolved', {}
    record, proof = letters[0]
    witnesses = proof['citations']
    if len(witnesses) > max_passages or sum(len(c['quote']) for c in witnesses) > max_chars:
        return 'abstain', 'reader_budget_exceeded', {}
    if not index.unchanged():
        return 'abstain', 'source_changed', {}
    missing = [goal['missing']] if goal['missing'] else []
    return ('partial_answer' if missing else 'supported_answer'), ('partial_documentary_evidence' if missing else 'supported'), {
        'claims': [proof], 'answer_supported': not missing, 'text': proof['text'], 'missing': missing,
        'sources': [s for s in index.sources if s['path'] == record.path],
        'verification': {'structural': True, 'semantic': 'bounded_documentary_reference',
                         'truth_verified': False, 'independence_verified': False},
        'documentary_support': {'scope': 'signed_letter_instruction', 'source_support_claims': 1,
            'examined_characters': checked['examined_characters'], 'examined_units': checked['examined_units'],
            'paragraph_units': paragraphs, 'limits': checked['limits'], 'record_limit': 8},
    }
