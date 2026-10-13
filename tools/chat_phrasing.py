"""Finite, anchored paraphrase normalization for personal-memory questions.

No synonym expansion of source queries; this grammar is only used by chat memory.
"""
import re

VERSION="chat-phrasing-v1"

def memory_question(text):
    text=re.sub(r'\s+',' ',text.replace('’',"'")).strip(' .!?').casefold()
    text=re.sub(r'^please\s+','',text)
    text=re.sub(r'^(?:can|could|would) you (?:please )?(?:tell me|remember) my ', 'what is my ',text)
    # The shared request normalizer may already have removed "can you".
    text=re.sub(r'^tell me my ', 'what is my ',text)
    match=re.fullmatch(r'tell me what my (.{1,60}) (?:is|are)',text)
    if match:text='what is my '+match[1]
    return text


def conversational_request(text):
    """Remove bounded social lead-ins only before an explicit request.

    Preserve the request bytes, including names, negation and quoted material.
    Ordinary adjectives, bare acknowledgements and literal-repeat requests are
    not rewritten. The caller retains the original message for the transcript.
    """
    lead = r'(?:cool|great|nice|awesome|neat|okay|ok|alright|all right|sure|thanks|thank you|hey|right|got it|well)'
    request = (r'(?:please\s+)?(?:tell me\b|explain\b|describe\b|summari[sz]e\b|teach me\b|show me\b|help me\b|'
               r'what\b|who\b|where\b|when\b|why\b|how\b|which\b|'
               r'can you\b|could you\b|would you\b|can we\b|give me\b|walk me\b|look up\b|search\b|find\b|define\b)')
    match = re.fullmatch(r'(?P<prefix>(?:'+lead+r'(?:\s*[,!.;:]\s*|\s+)){1,3})'
                         r'(?P<request>'+request+r'.*)', text, re.I | re.S)
    if not match:
        return text, None
    return match['request'], match['prefix'].strip()


def request_form(text):
    """Bounded request paraphrases. Captured topic bytes are never rewritten."""
    original=text
    from tools import self_knowledge as SK, question_frames as QF, chat_tutor as T
    if SK.recognize(text) or T.local_phrase(text)!=text:return text,None
    if re.fullmatch(r'switch to (?:chat|serious|focus|casual)(?: mode)?[?.!]*',text,re.I):return text,None
    if re.match(r'^(?:i want to learn about|i would like to learn about) ',text,re.I):return text,None
    # Do not convert a restricted request into an executable search command.
    if re.search(r"\b(?:not|never|without|don't|do not)\b",text,re.I):return text,None
    if re.match(r'^what about\b',text,re.I) and QF.overview_subject(text) is None:return text,None
    if re.match(r'^help me understand (?:what|who|when|where|why|how|which)\b',text,re.I):return text,None
    # Only unwrap politeness when the remainder is a recognized request.
    wrapper=re.fullmatch(r'(?:please\s+|(?:can|could|would|will) you (?:please )?)(.+)',text,re.I)
    candidate=wrapper[1] if wrapper else text
    patterns=[
        (r'(?:tell me (?:a bit|a little|something|more details) about|give me (?:an overview|some information|a quick overview) (?:of|about)|walk me through|help me understand) (.+)', 'Tell me about '),
        (r"(?:i(?:'d| would) like to (?:learn|know)(?: more)? about|i want to (?:learn|know)(?: more)? about|can we (?:talk|learn) about|let(?:'s| us) (?:talk|learn) about|what do you know about) (.+)", 'Tell me about '),
        (r'(?:switch (?:the topic )?to|new topic[: ]+|how about|what about)\s*(.+)', 'Tell me about '),
        (r'(?:look up|look into|search for|find information (?:on|about)) (.+)', 'search '),
        (r'(?:give me (?:the )?definition of|what is the meaning of) (.+)', 'define '),
        (r'(?:another word for|other words for|give me synonyms for) (.+)', 'synonyms '),
    ]
    for pattern,prefix in patterns:
        match=re.fullmatch(pattern,candidate,re.I)
        if match and match[1].strip():
            subject=match[1].strip(' ?!.').casefold()
            if subject in {'you','yourself','nothing','something else','it','this','that','them'}:return original,None
            if candidate.lower().startswith('help me understand ') and re.match(r'^(?:what|who|when|where|why|how|which)\b',match[1],re.I):return candidate,None
            return prefix+match[1], 'request_paraphrase'
    aliases={
        'keep going':'tell me more','go into more detail':'tell me more',
        'a bit more please':'tell me more','more details please':'tell me more',
        'anything else':'tell me more','what else':'tell me more',
        'where did you get that':'show source','where is that from':'show source',
        'show me the source':'show source','show me your sources':'show source',
        "let's change the subject":'change the subject','something else please':'change the subject',
    }
    key=candidate.casefold().strip(' ?!.')
    if key in aliases:return aliases[key], 'request_paraphrase'
    if wrapper and re.match(r'(?:tell me|explain|describe|summari[sz]e|show|search|find|define|synonyms|what|who|when|where|why|how)\b',candidate,re.I):
        return candidate,'polite_request'
    return original,None
