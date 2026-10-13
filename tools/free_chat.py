"""Ephemeral deterministic conversation experiment; never a source answer."""
import re
import uuid
from tools import casual_reasoning as D

VERSION='off-record-free-chat-v1'
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
        sid='free:'+uuid.uuid4().hex; sessions[sid]={'turn':0,'mind':{}}
    state=sessions[sid];state['turn']+=1
    response=D.respond(message,state['mind']) if key not in START else None
    if response is None:
        if key in START:
            body='Off-the-record free chat is on. I can play with wording and ideas. What shall we talk about?'
        elif re.match(r'^(?:search|import|find|remember|memory|load)\b',key):
            body='This mode does not fetch, import or save. Leave free chat to use those controls.'
        else:
            prompts=('What would you like to explore about that?','Which part should we play with as an idea?','What would you change or imagine next?')
            body='You said: «'+message[:300]+'»\n'+prompts[(state['turn']-1)%len(prompts)]
        response={'kind':'conversation','message':body,'suggestions':['tell me a story','how do you think','leave free chat']}
    response.update(context=None,sources=[],authority='conversation_structure',
        support_label='Off-the-record free chat · not source-backed',
        support_notice='Ephemeral in this running app. No transcript saved by MPLPB; no source answer or execution advice. Browser/device/network logging is outside this promise.',
        environment={'mode':'chat','corpora':[],'focus_corpus':None},
        response_structure={'factual_claims':False,'mplpb_supported':False,'intent':'free_chat'},
        response_validation={'version':VERSION,'status':'non_evidence','context_is_evidence':False,
                             'checks':['deterministic conversation templates; source, import and persistence paths disabled']})
    return {'session':sid,'corpus':data['corpus'],'profile':data.get('profile','internal'),'response':response,
            'turn':state['turn'],'turn_sha256':None,'logic_version':VERSION,'off_record':True,
            'mind':{'notes':[],'context':None},'notice':response['support_notice']}
