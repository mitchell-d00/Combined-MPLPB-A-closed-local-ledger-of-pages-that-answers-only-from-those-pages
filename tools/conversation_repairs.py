"""Deterministic discourse frames, with no evidence authority.

Scores rank a closed grammar; they are not probabilities. Only the temporal slot
of a complete wellbeing question is spelling-tolerant. No arbitrary clause loss.
"""
import re

TIMES = ('today', 'tonight', 'this morning', 'this afternoon', 'this evening', 'lately')
BASE = (r"how (?:are you(?: doing| feeling)?|have you been)|"
        r"how(?: is|'s) (?:it|everything) going|how(?: is|'s) your day(?: going)?|how r u|how are u")

# Behavior classes are separate from sentence realizations. These guards are
# also emitted in the interpretation trace for per-class evaluation.
POLICY = {
    'bounded_social_frame': {'reaction': 'social_reply', 'requires': 'complete_social_grammar_and_unique_slot',
                             'forbids': ['source_claim', 'network_acquisition']},
    'temporal_social_repair': {'reaction': 'repair_social_reply', 'requires': 'recent_social_frame',
                              'forbids': ['source_claim', 'reuse_source_question']},
    'attribute_slot_repair': {'reaction': 'route_corrected_question', 'requires': 'recent_matching_context_pin',
                             'forbids': ['answer_without_evidence', 'change_entity']},
    'attribute_followup': {'reaction': 'route_followup_question', 'requires': 'recent_matching_context_pin',
                           'forbids': ['answer_without_evidence', 'change_entity']},
}


def one_edit(a, b):
    if a == b:
        return True
    if abs(len(a)-len(b)) > 1:
        return False
    if len(a) == len(b):
        indexes = [i for i, (x, y) in enumerate(zip(a, b)) if x != y]
        return len(indexes) == 1 or (len(indexes) == 2 and indexes[1] == indexes[0]+1
                                    and a[indexes[0]] == b[indexes[1]] and a[indexes[1]] == b[indexes[0]])
    short, long = (a, b) if len(a) < len(b) else (b, a)
    return any(long[:i]+long[i+1:] == short for i in range(len(long)))


def temporal_candidates(text):
    if not re.fullmatch(r'[a-z ]{3,24}', text):
        return []
    compact = text.replace(' ', '')
    ranked = []
    for value in TIMES:
        score = 100 if text == value else 95 if compact == value.replace(' ', '') else 85 if one_edit(compact, value.replace(' ', '')) else 0
        if score:
            ranked.append({'value': value, 'score': score})
    return sorted(ranked, key=lambda x: (-x['score'], x['value']))


def unique_time(text):
    ranked = temporal_candidates(text)
    return (ranked[0]['value'] if ranked and (len(ranked) == 1 or ranked[0]['score'] > ranked[1]['score']) else None), ranked


def wellbeing_frame(text):
    text = re.sub(r'\s+', ' ', text.replace('’', "'")).casefold().strip(' .!?')
    greeting = re.match(r'^(hi|hello|hey)[,! ]+(.+)$', text)
    body = greeting[2] if greeting else text
    match = re.fullmatch(r'('+BASE+r')(?: (.+))?', body)
    if not match:
        return None
    temporal, ranked = unique_time(match[2]) if match[2] else (None, [])
    if match[2] and not temporal:
        return None
    base = 'how are you' if match[1] in {'how r u', 'how are u'} else match[1]
    return {'canonical': (text[:greeting.start(2)] if greeting else '')+base+(' '+temporal if temporal else '')+'?',
            'intent': 'wellbeing', 'time': temporal, 'candidates': ranked,
            'rule': 'bounded_social_frame', 'scores_are_probabilities': False}


def attribute_slot(text):
    """Exact grammatical slots only: never repair entity names or factual values."""
    aliases = {'size': 'diameter', 'old': 'age', 'heavy': 'mass', 'tall': 'height',
               'wide': 'width', 'long': 'length'}
    from tools.grounded_chat import ATTRIBUTES
    aliases.update({a: a for a in ATTRIBUTES})
    return aliases.get(re.sub(r'^(?:its|the) ', '', text))


def interpret(text, session):
    current = wellbeing_frame(text)
    if current:
        return current
    correction = re.fullmatch(r"(?:(?:sorry|actually|no)[, ]+)?i (?:meant|mean) (.{1,40})[.!?]*", text, re.I)
    followup = re.fullmatch(r'(?:and|what about|how about) (.{1,40})[.!?]*', text, re.I)
    if not correction and not followup:return None
    fragment = (correction or followup)[1].casefold().strip(' .!?')
    state = session.get('mind', {}).get('continuity', {})
    attribute = attribute_slot(fragment)
    if attribute:
        if followup and session.get('context'):
            from tools.grounded_chat import question_intent
            if question_intent(text,session['context']['title']):return None
        saved = state.get('attribute_frame')
        trace = {'rule': 'attribute_slot_repair' if correction else 'attribute_followup',
                 'attribute': attribute, 'scores_are_probabilities': False,
                 'candidates': [{'value': attribute, 'score': 100}]}
        if (saved and 0 <= len(session.get('log', []))-saved['turn'] <= 2
                and saved['context'] == session.get('context')):
            trace.update(canonical='What is the '+attribute+' of '+saved['context']['title']+'?',
                         intent='source_question', source_turn=saved['turn'],
                         context_pin=saved['context'], evidence_required=True)
        else:
            trace.update(needs_clarification=True, reason='No recent pinned attribute question')
        return trace
    if not correction:return None
    target, ranked = unique_time(fragment)
    if not target:
        return None
    saved = state.get('social_frame')
    trace = {'rule': 'temporal_social_repair', 'candidates': ranked,
             'scores_are_probabilities': False, 'time': target}
    if saved and 0 <= len(session.get('log', []))-saved['turn'] <= 2:
        # The remembered intent is social only; never reuse a source question.
        trace.update(canonical='how are you '+target+'?', intent='wellbeing',
                     source_turn=saved['turn'], repaired=True)
    else:
        trace.update(needs_clarification=True, reason='No recent unambiguous social frame')
    return trace


def remember(frame, session):
    state = session['mind'].setdefault('continuity', {})
    repair = frame.get('conversational_repair') or {}
    if repair.get('intent') == 'wellbeing':
        state['social_frame'] = {'turn': len(session.get('log', []))+1, 'intent': 'wellbeing'}
    elif frame['original'].casefold().strip(' .!?') not in {'thanks', 'thank you', 'hi', 'hello', 'hey'}:
        state.pop('social_frame', None)
        state.pop('attribute_frame', None)
        context = session.get('context')
        if context:
            from tools.grounded_chat import question_intent
            attribute = question_intent(frame['resolved'], context['title'])
            if attribute:
                state['attribute_frame'] = {'turn': len(session.get('log', []))+1,
                                            'attribute': attribute, 'context': dict(context)}
