"""Finite question grammar. Canonicalization never establishes evidence."""
from dataclasses import dataclass, asdict
import re

VERSION = 'support-frames-v1'

@dataclass(frozen=True)
class QuestionFrame:
    relation: str
    entity: str
    canonical: str
    statement: str
    negative_statement: str = ''
    time_constraint: str = ''
    polarity: str = 'affirmative'

    def to_dict(self):
        return dict(asdict(self), version=VERSION, normalization_is_evidence=False)


def normalize(text):
    return re.sub(r'\s+', ' ', text.casefold().replace('’', "'")).strip(' .?!')


def parse(question):
    q = normalize(question)
    q = re.sub(r'^(?:please |can you |could you )', '', q)
    # These modifiers are not licensed by this finite grammar. Do not remove them.
    if re.search(r'\b(?:not|never|before|after|during|unless|if|possibly|maybe|currently|formerly|now)\b', q):
        return None
    # Alternative surface forms bind the same relation and whole entity slot.
    rules = (
        ('opening_year', r'(?:when|in what year|in which year) did (.+) open',
         'when did {e} open', r'{e} opened in (?P<value>\d{{4}})', r'{e} did not open in (?P<value>\d{{4}})'),
        ('owner', r'(?:who owns|who is the owner of) (.+)',
         'who owns {e}', r'(?P<value>.+) owns {e}', r'(?P<value>.+) does not own {e}'),
        ('length', r'how long is (.+)', 'how long is {e}',
         r'{e} is (?P<value>\d+(?:\.\d+)? (?:meters?|metres?|centimeters?|kilometers?|feet|inches)) long',
         r'{e} is not (?P<value>\d+(?:\.\d+)? (?:meters?|metres?|centimeters?|kilometers?|feet|inches)) long'),
        ('chosen_colour', r'which colou?r was chosen for (.+)', 'which color was chosen for {e}',
         r'(?P<value>.+) was chosen for {e}', r'(?P<value>.+) was not chosen for {e}'),
        ('closure_cause', r'why did (.+) close', 'why did {e} close',
         r'{e} closed because (?P<value>.+)', r'{e} did not close because (?P<value>.+)'),
        ('socket', r'which socket does (.+) listen on', 'which socket does {e} listen on',
         r'{e} listens on socket (?P<value>\d{{1,5}})', r'{e} does not listen on socket (?P<value>\d{{1,5}})'),
        ('description', r"(?:what is|what are|what's) (.+)", 'what is {e}',
         r'(?:the )?{e} (?:is|are) (?P<value>.+)', r'(?:the )?{e} (?:is|are) not (?P<value>.+)'),
    )
    for relation, grammar, canonical, statement, negative in rules:
        m = re.fullmatch(grammar, q)
        if not m: continue
        entity = m[1]
        if relation == 'description': entity = re.sub(r'^the ', '', entity)
        # Reject clause suffixes, quotes and punctuation rather than dropping them.
        if re.search(r'[;?!."“”]', entity): return None
        return QuestionFrame(relation, entity, canonical.format(e=entity),
                             statement.format(e=re.escape(entity)), negative.format(e=re.escape(entity)))
    return None
