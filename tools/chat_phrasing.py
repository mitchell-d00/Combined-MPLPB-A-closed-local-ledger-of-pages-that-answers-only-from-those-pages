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
