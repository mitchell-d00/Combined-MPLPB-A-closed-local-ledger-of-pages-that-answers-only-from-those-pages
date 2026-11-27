"""Whole-question proposals with explicit relation/arguments; never evidence."""
import re
VERSION='ordinary-question-bindings-v1'
_BAD=re.compile(r'\b(?:and|or|if|unless|before|after|during|not|never|actually|false|formerly|currently|only|without|completed|happened)\b|[;:?!\n"“”]',re.I)
def slot(text):
    return isinstance(text,str) and 1<=len(text)<=240 and not _BAD.search(text)
def entity_slot(text):
    """Keep a complete singular subject proposal, including a literal name's and.

    Proof must match that entire subject in eligible bytes. This never splits or
    combines entities; plural/coordinated classification is not admitted below.
    Other argument/value slots retain the original conjunction guard.
    """
    return (isinstance(text,str) and 1<=len(text)<=240
            and not _BAD.search(re.sub(r'\band\b',' ',text,flags=re.I))
            and not re.search(r'\band\s+(?:who|what|which|when|where|why|how|is|are|does|do|did)\b',text,re.I))
def request(question):
    q=' '.join(question.strip().rstrip('?. ').split())
    if len(q)>600:return None
    q=re.sub(r'^According to (?:the|this) (?:record|source), ', '',q,flags=re.I)
    q=re.sub(r'^In (?:the|this) (?:record|source), ', '',q,flags=re.I)
    q=re.sub(r'^(Who|What|Which task|To whom|At which time), according to (?:the|this) (?:record|source), ',r'\1 ',q,flags=re.I)
    def result(kind,**fields):
        if not all((entity_slot(v) if k=='entity' and kind=='description' else slot(v))
                   for k,v in fields.items() if isinstance(v,str)):return None
        return dict(kind=kind,**fields,original_question=question,normalization_is_evidence=False,version=VERSION)
    for pattern in [r'Who owns (.+)',r'Who is the owner of (.+)',r'Who does (.+) belong to',r'To whom does (.+) belong',r'Which person owns (.+)',
                    r'Who is (.+) owned by',r'Whose property is (.+)',r'Which person is the owner of (.+)']:
        m=re.fullmatch(pattern,q,re.I)
        if m:return result('owner',entity=m[1])
    m=re.fullmatch(r'(?:What (?:kind|type) of place is|How is) (.+?)(?: described)?',q,re.I)
    if m:return result('description',entity=m[1])
    for pattern in [r'How would you classify (.+)',r'(?:What|Which) category does (.+) fall into',r'Under what category is (.+?)(?: described)?',r'What is (.+)']:
        m=re.fullmatch(pattern,q,re.I)
        if m:return result('description',entity=m[1])
    m=re.fullmatch(r'Is (.+?) ((?:a|an) .+)',q,re.I)
    if m:return result('description',entity=m[1],requested_value=m[2])
    m=re.fullmatch(r'(?:When|What time|At what time|At which time) does (.+) open',q,re.I)
    if m:return result('opening_time',entity=m[1])
    for pattern in [r'What is the opening time (?:of|for) (.+)',r'What time is listed for (.+) to open']:
        m=re.fullmatch(pattern,q,re.I)
        if m:return result('opening_time',entity=m[1])
    m=re.fullmatch(r'(?:When|On what date) was (.+) written',q,re.I)
    if m:return result('writing_date',entity=m[1])
    m=re.fullmatch(r'What (?:was|is) the date of writing of (.+)',q,re.I)
    if m:return result('writing_date',entity=m[1])
    m=re.fullmatch(r'Give the date on which (.+) was written',q,re.I)
    if m:return result('writing_date',entity=m[1])
    m=re.fullmatch(r'What did (.+?) (not )?(?:say|state|report) about (?:whether (.+?) wrote (.+)|(.+?) writing (.+))',q,re.I)
    if m:return result('reported',reporter=m[1],author=m[3] or m[5],object=m[4] or m[6],required_outer_negative=True if m[2] else None)
    m=re.fullmatch(r'What did (.+?) instruct (.+?) to do (?:concerning|about) (.+)',q,re.I)
    if not m:m=re.fullmatch(r'What task did (.+?) assign to (.+?) (?:concerning|about) (.+)',q,re.I)
    if not m:m=re.fullmatch(r'What directions did (.+?) give (.+?) (?:concerning|about) (.+)',q,re.I)
    if not m:m=re.fullmatch(r'What did (.+?) tell (.+?) to do (?:concerning|about) (.+)',q,re.I)
    if m:return result('instruction',actor=m[1],recipient=m[2],object=m[3])
    m=re.fullmatch(r'(?:Which|What) (?:task|instruction) did (.+?) give (.+)',q,re.I)
    if not m:m=re.fullmatch(r'What did (.+?) instruct (.+?) to do',q,re.I)
    if m:return result('instruction',actor=m[1],recipient=m[2],object=None)
    return None
