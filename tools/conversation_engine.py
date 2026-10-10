"""Dialogue-act planning and role-aware discourse replay, separate from evidence.

Parse all clauses before choosing a response. Unknown clauses are never silently
acknowledged as understood. Source clauses use the existing environment reader.
"""
import copy
import re
from tools import deterministic_mind as M, conversation_memory as CM

VERSION='conversation-engine-v1'

def normalize(text):
    return re.sub(r'\s+',' ',text.replace('’',"'")).strip()

def clauses(text):
    text=normalize(text)
    # Quoted/repetition requests belong to their existing literal-text handler.
    if re.match(r'^(?:say|repeat|echo|when i say)\b',text,re.I):return [text]
    text=re.sub(r'\s+(?:and\s+)?(?=(?:what are you|who are you|what can you|how are you)\b)', ';',text,flags=re.I)
    parts=[s.strip(' ,') for s in re.split(r'[;!?]+|\.(?:\s+|$)|\s+and\s+(?=(?:my name|i am|i\x27m|tell me|what|who)\b)',text,flags=re.I) if s.strip(' ,')]
    return parts if len(parts)<=8 else [text]

def act(text):
    k=CM.key(text)
    if k in CM.FORGET:return {'type':'forget_name'}
    if k in CM.NAME_QUESTIONS:return {'type':'recall_name'}
    # Greeting is evidence of an introduction, not a dictionary POS lookup.
    intro=re.fullmatch(r"(?:hi|hello|hey)[, ]+i(?: am|'m) (.+)",text,re.I)
    name=CM.introduction('my name is '+intro[1]) if intro and (intro[1].split()[0].casefold() not in CM.STATES or len(intro[1])==1 and intro[1].isupper()) else CM.introduction(text)
    if name:return {'type':'introduce','value':name}
    if k in {'hi','hello','hey','so hi','hi there','hello again'}:return {'type':'greet'}
    if k in {'who are you','what are you','what is your name',"what's your name"}:return {'type':'identity'}
    if re.fullmatch(r'what (?:can|do) you (?:chat|talk) about',k) or k=='what can you do':return {'type':'abilities'}
    if k in {'talk','can we talk','can we chat','let us talk',"let's talk",'just talk'}:return {'type':'open_chat'}
    if k in {'how are you','how are you doing'}:return {'type':'wellbeing'}
    # Explicit third-party declarations; user context, never verified facts.
    p=re.fullmatch(r'(?:actually[, ]+)?my (friend|sister|brother|partner|colleague|neighbor) ([\w-]{1,40}) (likes|enjoys|dislikes) (.{1,120})',text,re.I)
    if p:return {'type':'person','relation':p[1].lower(),'person':p[2],'predicate':p[3].lower(),'value':p[4]}
    p=re.fullmatch(r'(?:actually[, ]+)?([\w-]{1,40}) (likes|enjoys|dislikes) (.{1,120})',text,re.I)
    if p:return {'type':'person_update','person':p[1],'predicate':p[2].lower(),'value':p[3]}
    p=re.fullmatch(r'what (?:does|did) ([\w-]{1,40}) (like|enjoy|dislike)',k)
    if p:return {'type':'person_query','person':p[1],'predicate':{'like':'likes','enjoy':'enjoys','dislike':'dislikes'}[p[2]]}
    p=re.fullmatch(r'(?:i want to talk about|let\x27s talk about|can we talk about) (.{1,120})',text,re.I)
    if p:return {'type':'topic','value':p[1]}
    if k in {'what were we talking about','what are we talking about'}:return {'type':'recall_topic'}
    return {'type':'unresolved','text':text}

def replay(session):
    state={'name':None,'people':{},'topic':None,'references':[]}
    for number,turn in enumerate(session.get('log',[]),1):
        for a in map(act,clauses(turn.get('payload',{}).get('question',''))):
            apply(state,a,number)
    return state

def resolve_person(state,name):
    if name.lower() in {'he','she','they','him','her','them'}:
        return next(iter(state['people'])) if len(state['people'])==1 else None
    return name.casefold() if name.casefold() in state['people'] else None

def apply(state,a,turn):
    t=a['type']
    if t=='introduce':state['name']=a['value']
    elif t=='forget_name':state['name']=None
    elif t=='topic':state['topic']=a['value']
    elif t=='person':
        person=state['people'].setdefault(a['person'].casefold(),{'name':a['person'],'attributes':{}})
        person['attributes'][a['predicate']]={'value':a['value'],'turn':turn}
    elif t=='person_update':
        person=resolve_person(state,a['person'])
        if person:state['people'][person]['attributes'][a['predicate']]={'value':a['value'],'turn':turn}

def recognize(message,session,source_reader=True,acts=None):
    parts=clauses(message);acts=copy.deepcopy(acts) if acts is not None else [act(p) for p in parts]
    if len(acts)==1 and CM.key(message)=='what can you do':return None
    if len(acts)==1 and acts[0]['type']=='topic' and (acts[0]['value'].lower() in {'nothing','anything'} or (acts[0]['value'].lower() in {'it','that','this','them'} and session.get('context'))):return None
    # Preserve legacy handlers for isolated acts that they already implement.
    dedicated={'person','person_update','person_query','open_chat','abilities','topic','recall_topic','recall_name'}
    if len(acts)==1 and acts[0]['type'] not in dedicated:
        if not ((acts[0]['type']=='introduce' and re.match(r'^(?:hi|hello|hey)\b',message,re.I)) or (acts[0]['type']=='greet' and replay(session)['name'])):return None
    if all(a['type']=='unresolved' for a in acts):return None
    unknown=[a for a in acts if a['type']=='unresolved']
    # At most one independent source question; no speculative clause dropping.
    if unknown and (len(unknown)!=1 or not source_reader or not re.match(r'^(?:what|who|when|where|how|tell me|explain)\b',unknown[0]['text'],re.I)):
        return None
    return {"parts":parts,"acts":acts,"unknown":unknown}


def handle(message,session,source_reader=None,interpretation=None):
    plan=copy.deepcopy(interpretation) if interpretation is not None else recognize(message,session,source_reader)
    if not plan:return None
    parts,acts,unknown=plan["parts"],plan["acts"],plan["unknown"]
    state=replay(session);bodies=[];units=[];refs=[];turn=len(session.get('log',[]))+1
    state['topic']=state['topic'] or session.get('mind',{}).get('idea_chat',{}).get('subject') or (session.get('context') or {}).get('title')
    for a in acts:
        if a['type']=='topic' and a['value'].lower() in {'it','that','this','them'}:
            if not state['topic']:return None
            a['value']=state['topic']
    if len(acts)==1 and acts[0]['type']=='person_update' and not state['people']:return None
    for a in acts:
        t=a['type'];apply(state,a,turn);start=len(bodies)
        if t in {'introduce','greet'}:bodies.append('Hi'+(', '+state['name'] if state['name'] else '')+'!')
        if t in {'introduce','identity'} and not any('little monster' in b for b in bodies):bodies.append('I’m MPLPB, your rule-based little monster 😈.')
        if t=='recall_name':bodies.append('You asked me to call you '+state['name']+'.' if state['name'] else 'What would you like me to call you?')
        if t=='forget_name':bodies.append('Okay; I won’t use your name. The transcript is unchanged.')
        if t=='abilities':bodies.append('We can talk about your day, explore an idea, work through a small calculation, or discuss a topic using available pages. What interests you?')
        if t=='open_chat':bodies.append('Of course'+(', '+state['name'] if state['name'] else '')+'. '+('Shall we continue with '+state['topic']+'?' if state['topic'] else 'What’s on your mind?'))
        if t=='wellbeing':bodies.append('Ready to chat and explore ideas with you.')
        if t=='topic':bodies.append('Let’s talk about '+a['value']+'. What interests you about it?')
        if t=='recall_topic':bodies.append('You wanted to talk about '+state['topic']+'.' if state['topic'] else 'We haven’t settled on a topic yet. What interests you?')
        if t in {'person','person_update','person_query'}:
            person=resolve_person(state,a['person'])
            if not person:
                bodies.append('Who do you mean'+(': '+', '.join(p['name'] for p in state['people'].values()) if state['people'] else '')+'?')
            else:
                p=state['people'][person];item=p['attributes'].get(a['predicate'])
                if item:
                    bodies.append('You told me '+p['name']+' '+a['predicate']+' '+item['value']+'.')
                    refs.append({'turn':item['turn'],'basis':'user declaration'})
                else:bodies.append('You haven’t told me what '+p['name']+' '+a['predicate']+' yet.')
        for body in bodies[start:]:
            authority=('system_description' if body=='I’m MPLPB, your rule-based little monster 😈.' or t in {'abilities','identity'}
                       else 'conversation_structure' if t in {'introduce','greet','open_chat','wellbeing'} else 'user_declaration')
            units.append({'text':body,'authority':authority,'sources':[],'act':t})
    prefix=' '.join(dict.fromkeys(bodies))
    trace={'version':VERSION,'acts':acts,'chat_references':refs,'identity_verified':False}
    if unknown:
        result=source_reader(unknown[0]['text'])
        if result is None:return None
        result=copy.deepcopy(result)
        result['claim_units']=units+[{'text':result['message'],'authority':result.get('authority','source_reader_result'),'sources':copy.deepcopy(result.get('sources',[]))}]
        result['message']=prefix+'\n\n'+result['message']
        result['dialogue_plan']=trace
        return result
    session.setdefault('mind',{})['discourse']=state
    if any(a['type']=='topic' for a in acts):
        session['mind']['idea_chat']={'subject':state['topic'],'turn':0}
    return M.reply('conversation',prefix,session.get('context'),'DIALOGUE-PLAN',authority='user_declaration',
        claim_units=units,response_structure={'intent':'chat_memory','factual_claims':False,'mplpb_supported':False,**trace},
        suggestions=['What can you chat about?','What is my name?'] if state['name'] else (['a silly question','Talk about my day','Help me brainstorm'] if any(a['type']=='open_chat' for a in acts) else ['Talk about my day','Help me brainstorm']))
