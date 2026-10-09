"""Shared deterministic question framing; wording normalization is not evidence."""
import re
VERSION='question-frames-v2'


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
        text=re.sub(r'^(?:can|could|would|will) (?:you|we) (?:please )?(?=(?:tell|explain|describe|summari[sz]e|give|chat|talk|discuss|help|teach|explore|walk|share|say|introduce)\b)','',text,flags=re.I)
        text=re.sub(r"^(?:i (?:want|would like|wish) to know|i'd like to know|i(?: am|'m| was) wondering|do you know|any idea) (?:about )?(?=(?:what|who|where|when|why|how|which)\b)",'',text,flags=re.I)
        text=re.sub(r'^(?:tell me|explain(?: to me)?|help me understand) (?=(?:what|who|where|when|why|how|which)\b)','',text,flags=re.I)
        if text==before:break
    text=re.sub(r'^(how (?:big|large|old|tall|long|wide|heavy)|where|what) (it|they|this|that) (is|are)([?.!]*)$',r'\1 \3 \2\4',text,flags=re.I)
    return text


def overview_subject(message):
    text=normalize(message)
    if re.match(r"^what about (?:its |.+?'s |the (?:size|diameter|radius|age|height|length|width|mass|distance|orbital period) of )",text,re.I):return None
    match=re.fullmatch(r"(?:(?:let's |lets |let us )?(?:(?:chat|talk)(?: to me)? about|discuss|explore(?: an idea about| an idea| the idea of)?)|tell (?:me|us)(?: more| something| a little(?: more)?| a bit(?: more)?)? (?:about|regarding)|give me (?:an overview|(?:some )?information|(?:some )?facts|a summary|(?:some )?details) (?:about|on|of)|what (?:can you tell me|do you know) about|help me (?:understand|learn about)|teach me about|(?:explain|describe|summari[sz]e)|i (?:want|would like) to (?:learn|hear|know) about|i'd like to know about|can i ask you about|do you have (?:information|info) (?:on|about)|walk me through|fill me in on|bring me up to speed on|share (?:some )?(?:facts|information|details) (?:about|on)|(?:a quick )?overview of|what can (?:we|i) learn about|i(?: would|'d) (?:like|love) to hear about|what about|i(?: am|'m) interested in)\s+(.+?)[?.!]*",text,re.I)
    if not match:
        # A short topic question is an overview request, not evidence or a command.
        short=re.fullmatch(r"([A-Za-z][A-Za-z -]{0,59})\?",text)
        stop={'hi','hello','hey','yes','no','okay','ok','sure','why','how','what','who','when','where','which','really','again','more','continue','you','me','it','this','that','help','thanks','thank you','bored','sad','happy','tired','sorry','please','so hi','and you','what about you','how about you'}
        if short and len(short[1].split())==1 and short[1].casefold() not in stop and not re.match(r'^(?:what|who|where|when|why|how|which|is|are|can|could|do|does|will|would|should|say|repeat|load|clear|show|search|find)\b',short[1],re.I):return short[1]
        return None
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


def definition_subject(message):
    """A definition request, excluding follow-up pronouns and attribute questions."""
    match=re.fullmatch(r"(?:what is|what are|who is) (?:a |an |the )?([a-z][a-z0-9 -]{0,99})[?.!]*",normalize(message),re.I)
    if not match:return None
    subject=match[1].strip()
    if subject.casefold() in {'it','this','that','they','you','rules','your name','your purpose'}:return None
    if re.search(r"\b(?:of|your|my|its|their)\b",subject,re.I):return None
    return subject
