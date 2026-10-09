"""Explicit referent clarification; branch choices never select evidence authority."""
import re
from tools import deterministic_mind as M, self_knowledge as SK

VERSION='conversation-branches-v1'
ALIASES={'mplpb':('MPLPB','mplpb','the mplpb','the ledger'),
         'monster':('little monster','the little monster','monster','your little monster')}
FOLLOWUPS={"what's that",'what is that',"what's it",'what is it','what do you mean','explain that','tell me more','more about it'}

def key(text):
    return re.sub(r'\s+',' ',text.replace('’',"'")).strip(' .?!,;').casefold()

def candidates(session):
    log=session.get('log',[])
    if not log:return []
    response=log[-1].get('payload',{}).get('response',{})
    acts=response.get('response_structure',{}).get('acts',[])
    if any(a.get('type') in {'introduce','identity'} for a in acts):
        return [{'id':'mplpb','label':'MPLPB','kind':'system'}, {'id':'monster','label':'little monster','kind':'system'}]
    # Use typed context rather than treating arbitrary assistant prose as facts.
    found=[]
    for label in [response.get('context',{}).get('title') if response.get('context') else None,
                  session.get('mind',{}).get('idea_chat',{}).get('subject')]:
        if label and label.casefold() not in {x['label'].casefold() for x in found}:
            found.append({'id':label.casefold(),'label':label,'kind':'topic'})
    return found[:4]

def clarify(session,choices,state):
    state['pending']=choices
    return M.reply('conversation','Do you mean '+ ' or '.join(x['label'] for x in choices)+'?',session.get('context'),
        'REFERENT-CLARIFY',authority='conversation_structure',suggestions=[x['label'] for x in choices],
        response_structure={'intent':'chat_memory','factual_claims':False,'mplpb_supported':False,'branch_candidates':choices,'version':VERSION})

def handle(message,session,source_reader=None):
    k=key(message);mind=session.setdefault('mind',{})
    state=mind.setdefault('conversation_branches',{'history':[]})
    choices=state.get('pending',[])
    correction=re.fullmatch(r"(?:no[,; ]+|i mean |not that[,; ]+)(.+?)(?:[,; ]+(?:what is it|what's that|what is that))?",k)
    target=correction[1] if correction else k
    target=re.sub(r'^(?:i mean |the one about )','',target)
    selected=next((x for x in choices if target==x['label'].casefold()),None)
    canonical=next((ident for ident,forms in ALIASES.items() if target in {v.casefold() for v in forms}),None)
    if canonical and (choices or correction or state.get('active')):
        selected={'id':canonical,'label':ALIASES[canonical][0],'kind':'system'}
    if choices and target in {'first','the first one','1','second','the second one','2'}:
        n=1 if target in {'second','the second one','2'} else 0
        if n<len(choices):selected=choices[n]
    if not selected and k in FOLLOWUPS:
        if k in {'tell me more','more about it'} and not choices and not state.get('active'):return None
        selected=state.get('active')
        if not selected:
            choices=choices or candidates(session)
            if len(choices)>1:return clarify(session,choices,state)
            if len(choices)==1:return None  # Existing single-page resolution owns this case.
            else:return None
    if choices and not selected and k in {'yes','no','that one','it','that'}:
        return clarify(session,choices,state)
    if not selected:
        # A new substantive turn ends the pending branch, not its audit history.
        state.pop('pending',None);state.pop('active',None)
        return None
    parent=state.get('active',{}).get('id')
    if selected['kind']=='system':
        if selected['id']=='mplpb':body=SK.CAPABILITIES['definition'][1]
        else:body='The little monster is the chat interface for MPLPB. I use explicit rules and conversation context to construct replies; I’m not an LLM. MPLPB is the underlying page ledger.'
        if k in {'tell me more','more about it'}:
            body+=' '+SK.CAPABILITIES['language' if selected['id']=='monster' else 'sources'][1]
        result=M.reply('conversation',body,session.get('context'),'REFERENT-SELECT',authority='system_description',
            suggestions=['Tell me more','What can you chat about?'],response_structure={'intent':'chat_memory','factual_claims':False,'mplpb_supported':False})
    else:
        result=source_reader('Tell me about '+selected['label']) if source_reader else None
        if result is None:return clarify(session,[selected],state)
    state['active']=dict(selected);state.pop('pending',None)
    state['history']=(state.get('history',[])+[{'turn':len(session.get('log',[]))+1,'parent':parent,'selected':selected['id'],'correction':bool(correction)}])[-32:]
    result['conversation_branch']={'version':VERSION,'selected':dict(selected),'parent':parent,'history_length':len(state['history'])}
    return result
