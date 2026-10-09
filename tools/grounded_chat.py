"""Conservative, topic-bound question answering over verbatim local statements.

This is a finite grammar, not semantic entailment or an LLM. A lexical page
owner alone is never sufficient for an attribute answer.
"""
import re
from mplpb_combined import reader as R, provenance_gate as G
from mplpb_combined.record import text_of
from tools import chat_logic as C
from tools import deterministic_mind as M
from tools import response_construction as N

VERSION = 'grounded-chat-v1'
NUMBER = r'\d[\d,]*(?:\.\d+)?'
SCALE = r'(?:\s+(?:thousand|million|billion|trillion))?'
LENGTH = r'(?:kilomet(?:er|re)s?|km|met(?:er|re)s?|m|centimet(?:er|re)s?|cm|miles?|feet)'
TIME = r'(?:years?|days?|hours?|minutes?|seconds?)'
MASS = r'(?:kilograms?|kg|grams?|g|tonnes?|tons?)'
APPROX = r'(?:(?:about|approximately|roughly|around|an estimated)\s+)?'
ATTRIBUTES = {
    'diameter': ('diameter', LENGTH), 'radius': ('radius', LENGTH),
    'height': ('height', LENGTH), 'length': ('length', LENGTH),
    'width': ('width', LENGTH), 'distance': ('distance', LENGTH),
    'age': ('age', TIME), 'mass': ('mass', MASS),
    'orbital period': ('orbital period', TIME),
}

def normalized(text):
    return re.sub(r'\s+', ' ', text.casefold().replace('’', "'")).strip(' ?.!')


def question_intent(message, title):
    """Full grammars only: modifiers/comparisons/conditions do not disappear."""
    q = normalized(message)
    q = re.sub(r'^(?:and|also|okay|ok)[, ]+', '', q)
    t = re.escape(normalized(title))
    subject = rf'(?:it|this topic|that topic|(?:the )?{t})'
    possessive = rf"(?:its|(?:the )?{t}'s)"
    for attribute in ATTRIBUTES:
        a = re.escape(attribute)
        if re.fullmatch(rf"(?:what is|what's|what about|tell me) (?:the {a} of {subject}|{possessive} {a})", q):
            return attribute
    for adjective, attr in [('big','diameter'),('large','diameter'),('old','age'),
                            ('tall','height'),('long','length'),('wide','width'),('heavy','mass')]:
        if re.fullmatch(rf'how {adjective} is {subject}', q): return attr
    if re.fullmatch(rf'how far (?:away )?is {subject}', q): return 'distance'
    if re.fullmatch(rf'how much does {subject} weigh', q): return 'mass'
    if re.fullmatch(rf'how long does {subject} take to orbit', q): return 'orbital period'
    if re.fullmatch(rf"(?:what is|what's|what about) {possessive} size",q):return 'diameter'
    return None


def sentences(text):
    # Keep decimal points; offsets refer to text_of(body_html), not raw HTML.
    for match in re.finditer(r'[^\n]+', text):
        for part in re.finditer(r'.+?(?:[.!?](?=\s+[A-Z]|$)|$)', match.group()):
            quote = part.group().strip()
            if quote:
                start = match.start() + part.start() + len(part.group())-len(part.group().lstrip())
                yield quote, start, start+len(quote)


def evidence(text, title, attribute):
    """Require a named subject, declarative grammar and an explicit unit."""
    t = re.escape(title.removeprefix('The ').removeprefix('the '))
    subj = rf'(?:The\s+)?{t}'
    a, unit = ATTRIBUTES[attribute]
    value = rf'{APPROX}(?P<value>{NUMBER}{SCALE}\s*{unit})'
    # Full-sentence matching avoids hypothetical, negated, quoted and injected claims.
    patterns = [rf"{subj}(?:'s|’s) {a} is {value}",
                rf'The {a} of {subj} is {value}',
                rf'{subj} has (?:a|an) {a} of {value}']
    if attribute in {'diameter','radius','height','length','width'}:
        patterns.append(rf'{subj} is {value} in {a}')
    if attribute == 'age': patterns.append(rf'{subj} is {value} old')
    if attribute == 'mass': patterns.append(rf'{subj} weighs {value}')
    if attribute == 'distance':
        patterns = [rf'{subj} is {value} (?:away from|from) (?P<reference>[^.!?\n]{{1,80}})']
    found = []
    for quote, start, end in sentences(text):
        # The existing pasted-source renderer prefixes its first paragraph with
        # the page title. Remove only that exact heading, preserving body offsets.
        prefix=title+' '
        if quote.startswith(prefix) and any(re.fullmatch(pattern+r'\.?',quote[len(prefix):],re.I) for pattern in patterns):
            quote=quote[len(prefix):];start+=len(prefix)
        for pattern in patterns:
            match = re.fullmatch(pattern+r'\.?', quote, re.I)
            if match:
                found.append({'quote':quote, 'start':start, 'end':end,
                              'value':match['value'], 'reference':match.groupdict().get('reference')})
                break
    return found


def missing(question, context, attribute=None, reason='No supported answer statement matched.'):
    topic = context['title'] if context else None
    query = (topic + (' '+attribute if attribute else '')) if topic else question.strip(' ?.!')[:160]
    return M.reply('unsupported',
        ('I’m still on “'+topic+'”, but I can’t answer that from its loaded page.' if topic else
         'I don’t have a selected local page that supports an answer to that.')+
        '\n\nWould you like to add sources? Choose a Wikipedia mode and send the search suggestion to build a new collection, '
        'or use the source-import controls to add a URL/text to your collection. Web search needs a configured crawler. Nothing has been fetched.',
        context, 'GROUND-REFUSE', authority='unsupported',
        suggestions=['search '+query, 'show my MPLPB', 'keep chatting'],
        source_offer={'query':query,'automatic_fetch':False,'search_creates_new_collection':True},
        response_structure={'intent':attribute or 'unsupported_question','topic':topic,'factual_claims':False},
        unsupported_reason=reason)


def handle(app, corpus, root, profile, message, context):
    q = normalized(message)
    # Explicit overview/source and relation commands retain their separate semantics.
    if q in {'what is it','what is this topic','what is that topic','tell me more','more','continue','show source','show page'}:
        return None
    if q.startswith(('topic ','relate ')):
        return None
    relation = re.fullmatch(r'is (.+?) (?:a|an|related to) .+',q)
    if relation:
        if context and relation[1] not in {'it',normalized(context['title'])}:
            return missing(message,context,reason='Question refers to a different subject.')
        return None
    selection = re.fullmatch(r"(?:let's talk about|lets talk about|let us talk about|talk about|discuss) (.{1,160})", q)
    if selection:
        try: return C.turn(app,corpus,root,profile,'topic '+selection[1],context)
        except ValueError: return missing(selection[1],context,reason='Requested topic is not uniquely eligible.')
    if context:
        try:
            if C.context_for(root,context['title'],profile)!=context: raise ValueError('Topic changed')
        except ValueError:
            return M.reply('clarify','The selected page changed or is withheld. Please select it again.',None,'GROUND-PIN')
    if q in {'what are we talking about','what is our topic','which topic are we on'}:
        return M.reply('conversation','We’re talking about “'+context['title']+'”.' if context else
                       'No topic is selected. We can chat casually or choose a local page.',context,'GROUND-FOCUS',
                       authority='conversation_structure',suggestions=['show source','show my MPLPB'] if context else ['just chatting','show my MPLPB'])
    is_question = bool(re.match(r"(?:what|who|whom|whose|where|when|why|how|which|is|are|was|were|can|could|does|do|did|will|would|should|tell me)\b",q)) or message.rstrip().endswith('?')
    if not is_question:
        if context and q != normalized(context['title']):
            return missing(message,context,reason='No supported question grammar matched.')
        return None
    if not context:return missing(message,None)
    attr = question_intent(message,context['title'])
    if not attr:return missing(message,context,reason='Question is outside the supported attribute grammar.')
    record = next(r for r in C.eligible(root,profile) if r.path==context['path'])
    expanded = re.sub(r'\b(it|its|this topic|that topic)\b',lambda _:context['title'],message,flags=re.I)
    gate = G.gather(root,expanded,R.PROFILES[profile]).to_dict()
    if (R.PROFILES[profile].not_for and R.terms(expanded)&R.not_for_terms(record)) or record.path not in {s['path'] for s in gate['sources']}:
        return missing(message,context,attr,'Question is excluded by source/profile rules.')
    matches = evidence(text_of(record.body_html),context['title'],attr)
    if not matches:return missing(message,context,attr)
    # No unit conversion, averaging, or resolving differing values by preference.
    values = {(normalized(m['value']),normalized(m['reference'] or '')) for m in matches}
    if len(values)>1:
        return M.reply('conflict','The selected page gives multiple '+attr+' statements. I won’t choose a value.\n\n'+
                       '\n'.join(m['quote'] for m in matches),context,'GROUND-CONFLICT',[context],evidence=matches,
                       suggestions=['show source','search '+context['title']+' '+attr])
    match=matches[0]
    result=M.reply('grounded_answer',N.source_intro(context['title'],attr)+'\n\n'+match['quote']+
                   '\n\nThis is a source statement, not independently verified truth.',context,'GROUND-QUOTE',[context],
                   evidence=[match],extractive=True,authority='source_assertion',
                   response_structure={'intent':attr,'topic':context['title'],'factual_claims':True,'generated_factual_text':False,
                   'construction':{'engine':N.VERSION,'rule':'attribute + pinned_page_title + verbatim_evidence'}},
                   suggestions=['how big is it?','how old is it?','show source'])
    result['reasoning'].insert(0,{'rule':'GROUND-CONTEXT','original_question':message,'expanded_question':expanded,'context_pin':context})
    return result
