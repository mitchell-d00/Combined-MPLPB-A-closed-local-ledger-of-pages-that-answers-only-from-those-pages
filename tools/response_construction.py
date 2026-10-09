"""Finite surface grammar: compose social language, never invent ledger facts.

WordNet supplies sense/part-of-speech checks, not conversation rules or truth.
Rules and pragmatic word restrictions below are deliberately authored and auditable.
"""
import re
from tools import reference_resources as L
from tools import reduction as R

VERSION = 'response-construction-v1'
# Exact sense pins avoid mixing unrelated meanings of the same headword.
LEXICAL_SLOTS = {
    'frustrated': ('frustrating', '00871066-s', ('frustrating',)),
    'tired': ('exhausting', '00840788-s', ('exhausting', 'tiring', 'wearying')),
    'sad': ('disappointing', '02089757-s', ('disappointing', 'unsatisfying')),
    'good': ('pleasant', '01805299-a', ('pleasant',)),
}


def choose(items, turn, offset=0):
    return R.wording(items,'equivalent phrase slot',max(1,turn)+offset)[0]


def sentence(*parts, question=False):
    text = ' '.join(p for p in parts if p).strip()
    return text[:1].upper()+text[1:]+('?' if question else '.')


def adjective(category, turn):
    """Only approved predicative adjectives in one defined WordNet sense."""
    if category not in LEXICAL_SLOTS:
        return None, None
    headword, sense_id, allowed = LEXICAL_SLOTS[category]
    try:
        senses, manifest = L.lookup(headword)
        sense = next(s for s in senses if s['id'] == sense_id
                     and s['part_of_speech'] in {'a', 's'} and s['definitions'])
        words = [word for word in allowed if word in sense['synonyms']]
        if not words:
            return None, None
        word = choose(words, turn)
        return word, {'headword': headword, 'word': word, 'sense': sense_id,
                      'definition': sense['definitions'][0], 'part_of_speech': 'adjective',
                      'resource_sha256': manifest['resources'][0]['sha256']}
    except (OSError, ValueError, KeyError, StopIteration):
        # Missing or altered resources may not silently authorize lexical expansion.
        return None, None


def social(message, category, turn, listening=False, previous=''):
    word, lexical = adjective(category, turn) if not listening else (None, None)
    # A quote is user testimony, not an asserted event or new ledger evidence.
    # Never truncate a long statement: its qualification may be at the end.
    detail = re.sub(r'\s+', ' ', message).strip()
    quotable = bool(detail) and len(detail) <= 180 and not any(c in detail for c in '<>«»')
    def render(index):
        clauses = []
        rules = []
        if quotable and not listening:
            clauses.append('You said: «'+detail+'»')
            rules.append('attributed_user_quote')
        if word:
            clauses.append(sentence(choose(('that', 'what you described'), index),
                                    choose(('sounds', 'seems'), index//2+1), word))
            rules.append('subject + linking_verb + sense_checked_adjective')
        else:
            clauses.append(sentence('I’m', choose(('following', 'listening'), index)))
            rules.append('subject + auxiliary + participle')
        if listening:
            clauses.append(sentence(choose(('take', 'use'), index), 'your time'))
            rules.append('imperative + object')
        else:
            clauses.append(sentence(choose(('would you like to', 'do you want to'), index),
                                    choose(('tell me more', 'say a little more'), index//2+1),
                                    choose(('about that', 'about how it felt'), index//3+1), question=True))
            rules.append('question_auxiliary + subject + verb_phrase + prepositional_phrase')
        return ' '.join(clauses), rules
    body, rules = render(turn)
    if body == previous:
        body, rules = render(turn+1)
    return body, {'engine': VERSION, 'rules': rules, 'lexical_choice': lexical,
                  'user_quote': detail if quotable and not listening else None,
                  'user_quote_is_evidence': False, 'deterministic': True}


def source_intro(title, attribute):
    """Build only the framing. The caller must validate and attach an exact quote."""
    return sentence('For', attribute+',', 'the loaded page', '“'+title+'”', 'says')[:-1]+':'
