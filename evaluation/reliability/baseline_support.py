"""Finite, conservative statement support. Not general entailment or truth checking.

Scope/title metadata never supplies an answer. Unsupported grammar abstains.
"""
import re
from mplpb_combined.record import text_of

VERSION = 'statement-support-v2'


def normalize(text):
    return re.sub(r'\s+', ' ', text.casefold().replace('’', "'")).strip(' .?!')


def statement_support(question, record):
    q=normalize(question)
    q=re.sub(r'^(?:please |can you |could you )', '', q)
    patterns=[]
    subject=''
    negative=False
    # An exact subject phrase is required; do not drop entity or temporal words.
    match=re.fullmatch(r"(?:what is|what are|what's) (.+)",q)
    if match:
        subject=re.sub(r'^the ', '', match[1])
        patterns.append(r'(?:the )?'+re.escape(subject)+r' (?:is|are) (?P<value>.+)')
    match=re.fullmatch(r'which socket does (.+) listen on',q)
    if match:
        patterns.append(re.escape(match[1])+r' listens on socket (?P<value>\d{1,5})')
    # Relation-specific question slots retain the whole entity and direction.
    # These are sentence grammars, not topic-keyword matches.
    relations = (
        (r'when did (.+) open', r'{entity} opened in (?P<value>\d{{4}})'),
        (r'who owns (.+)', r'(?P<value>.+) owns {entity}'),
        (r'how long is (.+)', r'{entity} is (?P<value>\d+(?:\.\d+)? (?:meters?|metres?|centimeters?|kilometers?|feet|inches)) long'),
        (r'which colou?r was chosen for (.+)', r'(?P<value>.+) was chosen for {entity}'),
        (r'why did (.+) close', r'{entity} closed because (?P<value>.+)'),
    )
    for question_pattern, statement_pattern in relations:
        relation = re.fullmatch(question_pattern, q)
        if relation:
            entity = re.escape(relation[1])
            patterns.append(statement_pattern.format(entity=entity))
    if not patterns:return {'status':'unsupported','reason':'Question is outside the supported statement grammar.','spans':[]}
    spans=[]
    # Only body sentences, never declared scope or when-to-use. Whole sentence
    # matches reject quoted instructions, hypothetical prefixes and other subjects.
    body=re.sub(r'<h[1-6]\b[^>]*>.*?</h[1-6]>','\n',record.body_html,flags=re.I|re.S)
    for sentence in re.split(r'(?<=[.!?])\s+|\n+',text_of(body)):
        raw=sentence.strip();line=normalize(raw)
        if re.match(r'^(?:say|write|claim|imagine|suppose|assume|pretend|if|perhaps|possibly|maybe)\b', line):
            continue
        fact=re.fullmatch(r'fact: (.+?) \| (instance_of|subclass_of) \| (.+)',line)
        if fact and subject and fact[1]==subject:
            spans.append({'quote':raw,'value':fact[3]})
        for pattern in patterns:
            m=re.fullmatch(pattern,line)
            if not m:continue
            value=m['value']
            if re.search(r'\bnot\b',value):negative=True
            if re.search(r'\b(?:port|socket)$',subject):
                if not re.fullmatch(r'\d{1,5}',value) or not 0<int(value)<65536:continue
            if re.search(r'\b(not|unknown|unrecorded|unspecified|unavailable|missing|maybe|perhaps|possibly|reportedly|if|unless|might|could|should|would|either|or)\b',value):continue
            # Avoid presenting a future/conditional statement as an unconditional fact.
            if any(c in value for c in ['"','“','”',';']):continue
            spans.append({'quote':raw,'value':value})
    values={s['value'] for s in spans}
    if len(values)>1 or (spans and negative):return {'status':'conflict','reason':'Conflicting matching statements in the candidate page.','spans':spans}
    if not spans:return {'status':'unsupported','reason':'No affirmative statement answers the complete requested subject.','spans':[]}
    return {'status':'supported','reason':'Exact affirmative statement under a finite grammar; source truth is not verified.','spans':spans}


from dataclasses import dataclass, field
from mplpb_combined.reader import Answer, RETURN

@dataclass
class SupportedAnswer(Answer):
    support: dict = field(default_factory=dict)

    @property
    def text(self):
        if self.kind != RETURN or not self.record:return ''
        if self.support.get('status')=='supported':
            return '\n'.join(s['quote'] for s in self.support['spans'])
        return self.record.text

    def to_dict(self):
        result=super().to_dict();result['answer_support']=self.support
        return result

def supported_answer(root, question, profile=None):
    """Public answer path: eligibility/lexical selection, then statement support.

    `answer` remains the legacy candidate-retrieval API for inspection/evaluation.
    Candidate metadata is retained on refusal, but never a return body/citation.
    """
    from mplpb_combined.reader import answer, RETURN, AMBIGUOUS, NOT_IN_CORPUS
    out=SupportedAnswer(**answer(root,question,profile).__dict__)
    if out.kind != RETURN or not out.record:
        out.support={'status':'not_selected','version':VERSION,'spans':[]}
        return out
    # Bare topic lookup is source inspection, never a supported answer claim.
    import re
    if '?' not in question and not re.match(r'^(?:what|which|who|where|when|why|how|is|are|does|do|did|can|could|would|should|will)\b',question.strip(),re.I):
        out.support={'status':'candidate_only','version':VERSION,'spans':[],
                     'reason':'Topic/source inspection; this page is not certified to answer a question.'}
        return out
    out.support=statement_support(question,out.record)
    out.support['version']=VERSION
    if out.support['status']!='supported':
        out.kind=AMBIGUOUS if out.support['status']=='conflict' else NOT_IN_CORPUS
        out.reason='A lexical candidate was found, but answer support was not established. '+out.support['reason']
        out.record=None
    return out
