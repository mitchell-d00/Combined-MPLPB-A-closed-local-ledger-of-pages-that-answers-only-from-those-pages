"""Finite, anchored paraphrase normalization for personal-memory questions.

No synonym expansion of source queries; this grammar is only used by chat memory.
"""
import re

VERSION="chat-phrasing-v1"

def memory_question(text):
    text=re.sub(r'\s+',' ',text.replace('’',"'")).strip(' .!?').casefold()
    text=re.sub(r'^please\s+','',text)
    text=re.sub(r'^(?:can|could|would) you (?:please )?(?:tell me|remember) my ', 'what is my ',text)
    match=re.fullmatch(r'tell me what my (.{1,60}) (?:is|are)',text)
    if match:text='what is my '+match[1]
    return text


def conversational_request(text):
    """Remove bounded social lead-ins only before an explicit request.

    Preserve the request bytes, including names, negation and quoted material.
    Ordinary adjectives, bare acknowledgements and literal-repeat requests are
    not rewritten. The caller retains the original message for the transcript.
    """
    lead = r'(?:cool|great|nice|awesome|neat|okay|ok|alright|all right|sure|thanks|thank you)'
    request = (r'(?:please\s+)?(?:tell me\b|explain\b|describe\b|summari[sz]e\b|teach me\b|show me\b|help me\b|'
               r'what\b|who\b|where\b|when\b|why\b|how\b|which\b|'
               r'can you\b|could you\b|would you\b|search\b|find\b|define\b)')
    match = re.fullmatch(r'(?P<prefix>(?:'+lead+r'(?:\s*[,!.;:]\s*|\s+)){1,3})'
                         r'(?P<request>'+request+r'.*)', text, re.I | re.S)
    if not match:
        return text, None
    return match['request'], match['prefix'].strip()
