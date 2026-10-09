"""Deterministic bidirectional conversation index, separate from source evidence.

Forward replay applies explicit corrections; reverse lookup finds recent relevant
turns. User declarations, assistant text and source pointers retain their roles.
This index does not rewrite executable rules or promote repetition into truth.
"""
import hashlib
import json
import re
from tools import deterministic_mind as M

VERSION='context-index-v1'

def key(text):
    return re.sub(r'\s+',' ',text.replace('’',"'")).strip(' .!?').casefold()

def terms(text):
    return sorted({w[:-1] if len(w)>3 and w.endswith('s') and not w.endswith('ss') else w
                   for w in re.findall(r'[^\W_]+',key(text))
                   if w not in {'the','a','an','my','our','about','what','did','we','i','say','said','you'}})[:40]

def declarations(text):
    """Explicit possessive slots, not inferred personal attributes."""
    text=re.sub(r'^(?:actually|correction|no)[,; ]+','',text.strip(),flags=re.I)
    match=re.fullmatch(r"my ([\w][\w '-]{0,60}?) (is|are) (.{1,160})[.!]?",text,re.I)
    if not match or '?' in text:return []
    slot,copula,value=match.groups();value=value.rstrip('.!')
    if re.search(r'\b(?:what|who|how|where|when|why)\b',value,re.I):return []
    return [{'slot':key(slot),'value':value,'copula':copula.casefold(),'negated':bool(re.match(r'not\b',value,re.I))}]

def prepare(session):
    log=session.get('log',[])
    entries=[]
    for number,turn in enumerate(log,1):
        p=turn.get('payload',{});r=p.get('response',{})
        entries.append({'turn':number,'user':p.get('question',''),'assistant':r.get('message','')[:1200],
                        'source_pointers':r.get('sources',[])[:16]})
    fingerprint=hashlib.sha256(json.dumps(entries,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
    mind=session.setdefault('mind',{})
    previous=mind.get('context_index',{})
    if previous.get('fingerprint')==fingerprint and previous.get('version')==VERSION:return previous
    # Replaying oldest-to-newest makes corrections reproducible after reload.
    slots={};postings={};vocabulary={}
    for entry in entries:
        command=key(entry['user'])
        definition=re.fullmatch(r'when i say (.{1,50}?) i mean (.{1,160})',command)
        if definition:vocabulary[definition[1]]={'meaning':definition[2],'turn':entry['turn']}
        forgotten=re.fullmatch(r'forget my (.{1,60})',command)
        if forgotten:slots.pop(forgotten[1],None)
        for item in declarations(entry['user']):
            old=slots.get(item['slot'])
            slots[item['slot']]={**item,'turn':entry['turn'],'supersedes':old['turn'] if old else None,'basis':'user_declaration'}
        for word in terms(entry['user']):postings.setdefault(word,[]).append(entry['turn'])
    index={'version':VERSION,'fingerprint':fingerprint,'turn_count':len(entries),'slots':slots,'vocabulary':vocabulary,'postings':postings,'entries':entries}
    mind['context_index']=index
    return index

def result(session,body,refs,**extra):
    return M.reply('conversation',body,session.get('context'),'CONTEXT-REPLAY',authority='user_declaration',
        suggestions=extra.pop('suggestions',[]),response_structure={'intent':'chat_memory','factual_claims':False,
        'mplpb_supported':False,'identity_verified':False,'chat_references':refs,'version':VERSION,**extra})

def handle(message,session):
    index=prepare(session);command=key(message)
    definition=re.fullmatch(r'when i say (.{1,50}?) i mean (.{1,160})',command)
    if definition:
        return result(session,'In our conversation, I’ll use “'+definition[1]+'” to mean “'+definition[2]+'”.',[{'turn':len(session.get('log',[]))+1,'basis':'user-defined wording'}])
    meaning=re.fullmatch(r'what does (.{1,50}?) mean',command)
    if meaning and meaning[1] in index['vocabulary']:
        item=index['vocabulary'][meaning[1]]
        return result(session,'You defined “'+meaning[1]+'” as “'+item['meaning']+'”.',[{'turn':item['turn'],'basis':'user-defined wording'}])
    pronoun=re.fullmatch(r"(?:what is|what's) (?:its|their) (.{1,40})",command)
    if pronoun:
        candidates=[slot for slot in index['slots'].values() if slot['slot'].endswith("'s "+pronoun[1])]
        if len(candidates)==1:
            slot=candidates[0]
            return result(session,'You told me your '+slot['slot']+' is '+slot['value']+'.',[{'turn':slot['turn'],'basis':'unique user-declared referent'}])
        if len(candidates)>1:
            return result(session,'Which do you mean: '+', '.join(slot['slot'] for slot in candidates)+'?',[],ambiguous=True)
    # Questions about user-declared values must not become external source searches.
    query=re.fullmatch(r"(?:what (?:is|are)|what's|do you remember|remind me (?:of|about)) my (.{1,60})",command)
    if query and query[1]!='name':
        slot=index['slots'].get(query[1])
        if slot:
            return result(session,'You told me your '+slot['slot']+' '+slot['copula']+' '+slot['value']+'.',
                          [{'turn':slot['turn'],'basis':'user declaration','supersedes':slot['supersedes']}])
        return result(session,'I don’t have a clear statement from you about your '+query[1]+'. What would you like me to remember?',[])
    forgotten=re.fullmatch(r'forget my (.{1,60})',command)
    if forgotten and forgotten[1]!='name' and forgotten[1] in index['slots']:
        return result(session,'Okay; I won’t use that saved detail about your '+forgotten[1]+'. Your transcript is unchanged.',[])
    new=declarations(message)
    if new and new[0]['slot']!='name':
        item=new[0];old=index['slots'].get(item['slot'])
        body=('Thanks for the correction; ' if old else 'Got it; ')+'your '+item['slot']+' '+item['copula']+' '+item['value']+'.'
        return result(session,body,[{'turn':len(session.get('log',[]))+1,'basis':'user declaration'}],
                      suggestions=['What is my '+item['slot']+'?'])
    recall=re.fullmatch(r'(?:what did we (?:discuss|talk about)|what have we discussed|go back to|return to) (.{1,120})',command)
    if recall:
        topic=re.sub(r'^about ','',recall[1]);wanted=terms(topic)
        sets=[set(index['postings'].get(word,[])) for word in wanted]
        hits=sorted(set.intersection(*sets),reverse=True)[:3] if sets else []
        if not hits:return result(session,'I can’t find an earlier exchange about '+topic+'. Where would you like to start?',[])
        selected=[index['entries'][n-1] for n in sorted(hits)]
        if command.startswith(('go back to ','return to ')):
            session['mind']['idea_chat']={'subject':topic,'turn':0}
        body='Here’s our earlier conversation about '+topic+':\n\n'+'\n\n'.join(
            'You: “'+e['user'][:400]+'”\nMy reply: “'+e['assistant'][:600]+'”' for e in selected)
        return result(session,body,[{'turn':e['turn'],'basis':'historical conversation; not a fresh source check'} for e in selected],historical=True)
    return None
