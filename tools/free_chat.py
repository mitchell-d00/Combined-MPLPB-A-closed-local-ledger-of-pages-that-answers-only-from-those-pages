"""Ephemeral local conversation and verified bundled references; no persistence."""
import re
import uuid
from tools import casual_reasoning as D
from tools import idea_chat as I, topic_dialogue as TD, general_reference as GR
from tools import structured_requests as SR, conversation_memory as CM, dialogue_rules as DR
from tools import social_chat as S, reference_resources as F, language_planner as LP
from tools.response_validation import validate_response

VERSION='off-record-free-chat-v3'
START={'off the record','off-the-record','off the record mode','off-the-record free chat','free chat'}
STOP={'leave off the record','leave free chat','serious mode','chat mode'}


def active(data):
    return (data.get('off_record') is True or str(data.get('session','')).startswith('free:') or
            str(data.get('message','')).casefold().strip(' .?!') in START)


def respond(app,data):
    message=data['message'].strip(); key=message.casefold().strip(' .?!')
    sid=data.get('session'); sessions=app.free_sessions
    if sid not in sessions:
        if len(sessions)>=32: raise ValueError('Ephemeral session limit reached; restart the application to clear these sessions.')
        sid='free:'+uuid.uuid4().hex; sessions[sid]={'turn':0,'mind':{},'log':[],'context':None,'environment':{'mode':'free','corpora':[],'focus_corpus':None}}
    state=sessions[sid]
    if len(state['log'])>=1000:raise ValueError('1000-turn ephemeral limit reached; leave free chat to discard this session.')
    state['turn']+=1
    response=None
    if key in {'browse library','main index','library'} or key.startswith('library '):
        response={'kind':'clarify','message':'Leave free chat to browse or answer from the local library. This mode does not read ledger collections.','authority':'conversation_structure','sources':[]}
    elif key not in START:
        frame=SR.parse(message,state)
        if frame['action'] not in {'select_activity','calculation_input'}:state['mind'].pop('pending_activity',None)
        if frame['action'] not in {'select_sense','lexical_followup','lexical_nuance'} and not TD.recognize(message,state):state['mind'].pop('lexical_discussion',None)
        response=SR.handle(message,state,app.roots())
        if response is None:response=TD.handle(app,data,state,message,data['corpus'],data.get('profile','internal'))
        if response is None:response=GR.handle(message,state,allow_all_modes=True)
        if response is None:response=CM.handle(message,state)
        if response is None:response=DR.handle(message,state)
        if response is None and F.topic_request(message,state):response=F.topic(message,state)
        if response is None:response=SR.lexical(message,state,frame)
        if response is None:response=I.brainstorm(message,state['mind'])
        if response is None:response=D.respond(message,state['mind'])
        if response is None:response=S.handle(message,None,state['mind'])
    if response is None:
        if key in START:
            body='Off-the-record free chat is on. I can play with wording and ideas. What shall we talk about?'
        elif re.match(r'^(?:search|import|find|remember|memory|load)\b',key):
            body='This mode does not fetch, import or save. Leave free chat to use those controls.'
        else:
            prompts=('What would you like to explore about that?','Which part should we play with as an idea?','What would you change or imagine next?')
            body='You said: «'+message[:300]+'»\n'+prompts[(state['turn']-1)%len(prompts)]
        response={'kind':'conversation','message':body,'suggestions':['tell me a story','how do you think','leave free chat']}
    response.setdefault('context',None)
    response.setdefault('sources',[])
    response.setdefault('authority','conversation_structure')
    response.setdefault('response_structure',{'factual_claims':False,'mplpb_supported':False,'intent':'free_chat'})
    response['environment']=state['environment']
    response['support_notice']='Ephemeral in this running app. No transcript saved by MPLPB; no remote fetching. Bundled dictionary references are separately attributed. Browser/device/network logging is outside this promise.'
    response=validate_response(app,response,data.get('profile','internal'),data['corpus'],response['message'])
    response['support_label']='Off-the-record free chat · '+LP.label(response)
    response.setdefault('support_notice','Ephemeral in this running app; no transcript saved by MPLPB.')
    response.setdefault('structured_request',SR.parse(message,state))
    if not response.get('response_structure',{}).get('intent','').startswith('social_'):state['mind'].pop('social',None)
    # In-memory user turns support replay without touching the persistent store.
    state['log'].append({'payload':{'question':message,'response':response}})
    return {'session':sid,'corpus':data['corpus'],'profile':data.get('profile','internal'),'response':response,
            'turn':state['turn'],'turn_sha256':None,'logic_version':VERSION,'off_record':True,
            'mind':{'notes':[],'context':None},'notice':response['support_notice']}
