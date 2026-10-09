"""Bounded traversal of authored phrase -> subject -> intent -> handler edges.

No actions or evidence grants are inferred by this read-only routing graph.
"""
import hashlib
import json
import re
from pathlib import Path
PATH=Path(__file__).resolve().parents[1]/'resources/chat_language_graph.json'
RAW=PATH.read_bytes()
GRAPH=json.loads(RAW)
VERSION=GRAPH['version']
SHA256=hashlib.sha256(RAW).hexdigest()

def interpret(text):
    key=re.sub(r'\s+',' ',text.replace('’',"'")).strip(' .?!').casefold()
    # Full request matching protects literal text, negation and compound requests.
    key=re.sub(r'^(?:(?:can|could|would|will) you (?:please )?|please )','',key)
    key=re.sub(r',? please$','',key)
    matches=[]
    for edge in GRAPH['edges']:
        for alias in GRAPH['subjects'][edge['subject']]:
            for form in GRAPH['forms']:
                if key==form.replace('{subject}',alias):
                    matches.append(dict(edge,phrase=key,path=[key,edge['subject'],edge['intent'],edge['command']]))
    unique={m['intent']:m for m in matches}
    if len(unique)!=1:return None
    return dict(next(iter(unique.values())),version=VERSION,sha256=SHA256)
