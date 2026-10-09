"""Shared deterministic question framing; wording normalization is not evidence."""
import re
VERSION='question-frames-v1'


def normalize(message):
    text=re.sub(r'\s+',' ',message.strip().replace('’',"'")).strip()
    text=re.sub(r"^what['’]s\b",'what is',text,flags=re.I)
    text=re.sub(r"^who['’]s\b",'who is',text,flags=re.I)
    text=re.sub(r'^(?:hey|hi|hello)[, ]+(?=(?:can|could|would|will|please|what|how|tell)\b)','',text,flags=re.I)
    text=re.sub(r'^would you mind telling me ', 'tell me ',text,flags=re.I)
    text=re.sub(r'^would you mind explaining ', 'explain ',text,flags=re.I)
    for _ in range(3):
        before=text
        text=re.sub(r'^please[, ]+','',text,flags=re.I)
        text=re.sub(r'[, ]+please[?.!]*$','',text,flags=re.I)
        text=re.sub(r'^(?:can|could|would|will) (?:you|we) (?:please )?(?=(?:tell|explain|describe|summari[sz]e|give|chat|talk|discuss|help|teach|explore)\b)','',text,flags=re.I)
        text=re.sub(r"^(?:i (?:want|would like|wish) to know|i'd like to know|i(?: am|'m| was) wondering|do you know|any idea) (?:about )?(?=(?:what|who|where|when|why|how|which)\b)",'',text,flags=re.I)
        text=re.sub(r'^(?:tell me|explain(?: to me)?|help me understand) (?=(?:what|who|where|when|why|how|which)\b)','',text,flags=re.I)
        if text==before:break
    text=re.sub(r'^(how (?:big|large|old|tall|long|wide|heavy)|where|what) (it|they|this|that) (is|are)([?.!]*)$',r'\1 \3 \2\4',text,flags=re.I)
    return text


def overview_subject(message):
    text=normalize(message)
    if re.match(r"^what about (?:its |.+?'s |the (?:size|diameter|radius|age|height|length|width|mass|distance|orbital period) of )",text,re.I):return None
    match=re.fullmatch(r"(?:(?:let's |lets |let us )?(?:(?:chat|talk)(?: to me)? about|discuss|explore(?: an idea about| an idea| the idea of)?)|tell (?:me|us)(?: more| something| a little(?: more)?| a bit(?: more)?)? (?:about|regarding)|give me (?:an overview|(?:some )?information|(?:some )?facts|a summary|(?:some )?details) (?:about|on|of)|what (?:can you tell me|do you know) about|help me (?:understand|learn about)|teach me about|(?:explain|describe|summari[sz]e)|i (?:want|would like) to (?:learn|hear|know) about|i'd like to know about|can i ask you about|do you have (?:information|info) (?:on|about)|what about|i(?: am|'m) interested in)\s+(.+?)[?.!]*",text,re.I)
    if not match:return None
    subject=match[1].strip()
    if re.match(r'^summari[sz]e ',text,re.I) and subject.casefold() in {'it','this','that','this topic','that topic'}:return None
    # Self/conversation control has dedicated rules, not remote-source intent.
    if subject.casefold() in {'nothing','yourself','you','your rules','the rules','your construction rules'}:return None
    return subject


def frame(message):
    canonical=normalize(message)
    subject=overview_subject(message)
    word=re.match(r'(what|who|where|when|why|how|which|is|are|do|does|can|should|would|will)\b',canonical,re.I)
    return {'rule':VERSION,'original':message,'canonical':canonical,
            'kind':'overview' if subject else 'question' if word or canonical.endswith('?') else 'conversation_or_command',
            'subject':subject,'normalization_is_evidence':False}
