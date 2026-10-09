"""Deterministic discourse planning and bounded surface realization.

Source sentences, quotations, qualifications and proofs are immutable payloads.
This is a finite grammar, not a semantic entailment or unrestricted NLP engine.
"""
import hashlib
import re
from tools import question_frames as F

VERSION = 'language-planner-v1'
PRONOUNS = {'it', 'this', 'that', 'they', 'them', 'this topic', 'that topic'}


def parse(message, memory, context=None):
    frame = F.frame(message)
    text = frame['canonical']
    subject = frame['subject']
    compound = re.fullmatch(r'(?:say (?:hi|hello)|give a greeting) to (.{1,100}?) and (?:tell (?:them|everyone)|talk) about (.{1,160}?)[?.!]*', text, re.I)
    if compound:subject = compound[2]
    prior = memory.get('idea_chat', {}).get('subject') or (context or {}).get('title')
    reference = subject.casefold() in PRONOUNS if subject else False
    if reference:subject = prior
    key = text.casefold().strip(' ?!.')
    followup = key in {'tell me more', 'more', 'go on', 'continue', 'why', 'how', 'how so'}
    if followup:subject = prior
    imagined = bool(re.match(r'^(?:explore an idea|imagine|suppose|what if)\b', text, re.I))
    negation = bool(re.search(r"\b(?:not|never|no|don't|dont|do not|can't|cannot|without)\b", text, re.I))
    actions = []
    if compound:actions.append('greet')
    actions.append('explore_idea' if imagined else 'continue' if followup else 'overview' if subject else frame['kind'])
    return {'version': VERSION, 'canonical': text, 'actions': actions,
            'subject': subject, 'audience': compound[1] if compound else None,
            'reference': 'resolved' if reference and subject else 'unresolved' if reference else None,
            'negation_present': negation, 'imagined': imagined,
            'question_word': (re.match(r'(what|who|where|when|why|how|which)\b', text, re.I) or [''])[0],
            'normalization_is_evidence': False}


def label(result):
    kind = result.get('kind')
    structure = result.get('response_structure', {})
    if kind in {'unsupported','not_in_corpus','unknown_relation'}:return 'No supporting answer'
    if kind in {'ambiguous','clarify','conflict'}:return 'Needs clarification'
    if structure.get('intent') == 'casual_idea_exploration':return 'Idea · not source-backed'
    if result.get('authority') == 'lexical_reference':return 'Dictionary reference'
    if result.get('sources'):return 'Sources below'
    if result.get('support_notice') or result.get('determination',{}).get('basis') == 'conversation':return 'Conversation · not source-backed'
    return 'System guidance'


def choice(values, turn, offset=0):
    return values[(max(1, turn)-1+offset) % len(values)]


def topic_clause(subject, turn, continuing=False, count=1):
    # Clause construction uses bound slots; user text cannot supply grammar rules.
    lead = choice(('For', 'About'), turn)
    subject_clause = lead+' '+subject+', '
    plural=count!=1
    determiner = choice(('the', 'these' if plural else 'this'), turn, 1)
    noun='pages' if plural else 'page'
    predicate = choice(('say', 'tell us') if plural else ('says', 'tells us'), turn//2+1)
    return subject_clause+'here’s what '+determiner+' '+noun+' '+predicate+(' next' if continuing else '')+':'


def finish(result, parsed, memory, turn):
    """Called after evidence gates on every chat path, before transcript hashing."""
    structure = result.get('response_structure', {})
    subject = structure.get('subject') or parsed.get('subject')
    body = result.get('message', '')
    rules = ['preserve_validated_payload']
    # Only the engine-owned framing slots can be regenerated. No paraphrasing
    # source quotations, negation, numbers, units, qualifiers or relation proofs.
    if structure.get('intent') == 'source_exploration' and result.get('sources') and not result.get('source_exhausted') and subject:
        parts = body.split('\n\n')
        offset = 1 if result.get('composition') else 0
        if len(parts) >= offset+3 and parts[offset].startswith(('Let’s talk about ', 'Here’s more about ', 'Here’s what I found.')) and parts[-1] == 'What part interests you most?':
            parts[offset] = topic_clause(subject, turn, parsed['actions'][-1] == 'continue',len(result['sources']))
            listening = memory.get('emotional', {}).get('style') == 'listen'
            parts[-1] = '' if listening else choice(('Which part of '+subject+' would you like to explore?', 'What would you like to ask about '+subject+'?'), turn)
            result['message'] = '\n\n'.join(p for p in parts if p)
            rules += ['topic_clause + immutable_source_spans + contextual_followup']
    elif structure.get('intent') == 'casual_idea_exploration' and parsed['imagined'] and subject:
        result['message'] = 'Let’s '+choice(('explore','develop'),turn)+' '+subject+' as an idea. '+choice(('What would you like it to do?', 'Which assumption should we examine first?'),turn//2+1)
        rules += ['invitation + bound_subject + hypothetical_frame + open_question']
    # Existing echo, emotion, explanation, dictionary and proof realizers retain
    # their contracts. The common plan records their construction rules.
    construction = structure.get('construction') or {}
    rules.extend(construction.get('rules', []))
    candidate = parsed.get('subject')
    query = None
    if candidate and not parsed['imagined'] and not parsed['negation_present'] and ('overview' in parsed['actions'] or result.get('source_exhausted')):
        if candidate.casefold() not in PRONOUNS and 1 <= len(candidate) <= 160:query = candidate
    result['language_plan'] = {**parsed, 'subject': subject, 'realization_rules': rules,
        'response_act': structure.get('intent') or result.get('kind'),
        'acquisition': {'query': query, 'order': ['eligible_local_pages','enabled_remote_capture'],
                        'search_snippets_are_evidence': False, 'automatic_network_requires_setting': True},
        'payload_sha256': hashlib.sha256(body.encode()).hexdigest(),
        'surface_changed': result.get('message','') != body,
        'source_paraphrasing': False, 'rules_are_not_evidence': True}
    result['support_label'] = label(result)
    return result
