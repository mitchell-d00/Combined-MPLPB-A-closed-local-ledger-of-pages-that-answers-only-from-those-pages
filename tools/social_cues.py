"""Complete social phrases and deterministic variation; never evidence or diagnostics."""
import re


def key(text):
    return re.sub(r'\s+', ' ', text.casefold().replace('’', "'")).strip(' .!?,')


def wellbeing(text):
    k = key(text)
    return bool(re.fullmatch(
        r"(?:how (?:are you(?: doing| feeling)?|have you been)|"
        r"how(?: is|'s) (?:it|everything) going|how(?: is|'s) your day(?: going)?)"
        r"(?: today| tonight| this morning| this afternoon| this evening| lately)?", k))


def cue(text, session):
    k = key(text)
    if k in {'good morning', 'good afternoon', 'good evening', 'nice to meet you', 'nice talking to you'}:
        return 'greeting'
    if wellbeing(k):
        return 'wellbeing'
    if k in {'thanks', 'thank you', 'thanks a lot', 'thank you so much',
             'thanks that helps', 'thanks, that helps', 'thank you that helps', 'cheers'}:
        # Keep an active listening conversation's existing acknowledgement.
        if not session.get('mind', {}).get('social', {}).get('active'):
            return 'thanks'
    if k in {'bye', 'goodbye', 'bye for now', 'see you later', 'talk later', 'take care', 'good night'}:
        if not session.get('mind', {}).get('social', {}).get('active'):
            return 'farewell'
    log = session.get('log', [])
    last = log[-1].get('payload', {}).get('response', {}) if log else {}
    structure = last.get('response_structure') or {}
    recent = structure.get('social_cue') == 'wellbeing' or any(
        (a == 'wellbeing' or isinstance(a, dict) and a.get('type') == 'wellbeing') for a in last.get('dialogue_plan', {}).get('acts', structure.get('acts', []))
    )
    if recent:
        if k in {'and you', 'you', 'what about you', 'how about you'}:
            return 'reciprocal'
        if k in {'good', 'good thanks', "i'm good thanks", 'fine thanks', 'not bad',
                 'pretty good', 'doing well', 'all good', "i'm fine thanks"}:
            return 'positive'
        if k in {'okay', 'ok', 'so so', 'so-so', 'hanging in there', 'could be better'}:
            return 'mixed'
    return None


def wording(kind, memory):
    if kind == 'reciprocal':
        kind = 'wellbeing'
    state = memory.setdefault('social_cues', {})
    count = state.get(kind, 0)
    state[kind] = count + 1
    if kind in {'wellbeing', 'reciprocal'}:
        starts = ("I’m functional, thanks!", "Ready to chat, thanks for asking!",
                  "Little monster reporting for conversation duty!")
        endings = ("How’s your day going?", "How are things with you?", "What’s on your mind?")
        return starts[count % len(starts)] + ' ' + endings[(count + count // len(starts)) % len(endings)]
    options = {
        'greeting': ('Hello! What’s on your mind?', 'Hi there! What would you like to chat about?'),
        'thanks': ("You’re welcome!", "Glad that helped.", "Anytime. We can keep going whenever you like."),
        'farewell': ("Take care! Talk whenever you’re ready.", "See you later!", "Bye for now!"),
        'positive': ("Good to hear! What have you been up to?", "Nice! Want to chat about your day or something else?"),
        'mixed': ("We can take it easy. Want to talk, or keep things light?", "I’m here to chat. What’s on your mind?"),
    }
    return options[kind][count % len(options[kind])]
