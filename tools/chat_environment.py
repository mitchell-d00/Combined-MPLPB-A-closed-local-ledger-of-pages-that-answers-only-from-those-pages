"""Explicit empty/chat and federated/focus scopes; never merge ledger evidence."""
import re
import copy
from tools import casual_reasoning as D
from tools import reduction as RD
from tools import emotional_rules as EM
from tools import idea_chat as IC
from tools import chat_logic as C, chat_tutor as T, deterministic_mind as M
from tools import social_chat as S, grounded_chat as Q, reference_resources as F

VERSION = 'chat-environment-v4'


def reply(body, context=None, **extra):
    return M.reply('conversation', body, context, 'ENVIRONMENT-1',
                   authority='conversation_structure', **extra)


def load(app, session, keys):
    roots = app.roots()
    if keys == 'all': keys = sorted(roots)
    if not isinstance(keys, list) or len(keys) > 64 or any(not isinstance(k,str) or k not in roots for k in keys) or len(set(keys)) != len(keys):
        raise ValueError('Choose distinct available MPLPB collections (up to 64), or none.')
    session['environment'] = {'mode': 'focus' if keys else 'chat', 'corpora': list(keys), 'focus_corpus': None}
    session['context'] = None
    mind = session['mind']
    mind.pop('idea_chat', None); mind.pop('topic_offer', None); mind.pop('guide', None); mind.pop('chat_discourse',None); mind.pop('emotional',None)
    mind['casual_active'] = not keys
    mind['social'] = {'active': not keys, 'stage': 'story', 'turns': 0, 'style': 'chat'}
    return reply(('Serious mode; '+str(len(keys))+' MPLPB collections loaded. Each keeps its own evidence and delivery boundaries.' if keys else
                  'Just chat; 0 MPLPB collections loaded. The active MPLPB topic is unloaded; your saved pages and notes are retained. What’s on your mind?'),
                 response_structure={'intent':'scope_load' if keys else 'social_start','mode':'focus' if keys else 'casual','factual_claims':False},
                 suggestions=['show loaded MPLPB','show my MPLPB','just chat'] if keys else ['how do you think?','I had a bad day','load all MPLPB'])


def pages(app, keys, profile):
    entries=[]; blocked=[]
    for key in keys:
        try:
            root=app.root(key)
            for record in C.eligible(root,profile):
                try: pin=C.context_for(root,record.title,profile)
                except ValueError: continue
                entries.append((key,pin))
        except (OSError,ValueError,KeyError) as exc:
            blocked.append({'corpus':key,'reason':str(exc)})
    return entries,blocked


def general(message, session):
    mind=session['mind'];key=T.casual_key(message)
    if IC.topic_request(message):return IC.handle(message,mind)
    if mind.get('idea_chat') and key in {'tell me more','go on','why','how','how so','why not','any ideas','yes','sure','explore an idea'}:
        return IC.handle(message,mind)
    emotional=EM.handle(message,mind)
    if emotional:return emotional
    conversational=D.respond(message,mind)
    if conversational:return conversational
    if key in {'how do you think','how do you work','can you think','how does your mind work','what are you thinking','what are you'}:
        return reply('I use explicit rules to recognize a request, track our conversation and assemble a reply. My dictionary and thesaurus help with wording. I don’t use an LLM or have private thoughts. In focus mode, factual answers must come from the loaded MPLPB pages.', suggestions=['I had a bad day','load all MPLPB','language resources'])
    definition=re.fullmatch(r"(?:what is|what's|what are) (?:a |an |the )?([a-z][a-z '-]{0,79})[?.!]*",message.casefold().strip())
    if definition and definition[1] not in {'it','this','that','your name','your purpose'}:
        senses,_=F.lookup(definition[1])
        if senses:return F.handle('define '+definition[1],None)
    exploration=IC.handle(message,mind)
    if exploration:return exploration
    social=S.handle(message,None,mind)
    if social:return social
    help_reply=M.help_reply(message,None)
    if help_reply:return help_reply
    reference=F.handle(message,None)
    if reference:return reference
    if T.smalltalk_candidate(message,mind):return T.smalltalk(message,None,mind,[], 'chat-empty')
    if key in {'what can we talk about','what should we talk about','what do you want to talk about'}:
        return reply('Your day, an idea, something you enjoy, or a question you’re working through. Where would you like to start?',suggestions=['I had a bad day','tell me a joke'])
    if re.match(r'^(?:what|why|who|where|when|how|which|is|are|can|could|do|does|will|would|should)\b',key) or message.endswith('?'):
        return reply('We can talk that through. I don’t have a general-knowledge model, so I can’t supply a factual answer to every question with 0 MPLPB loaded. Tell me what you already know, or load saved pages to explore it with sources.',suggestions=['can we talk','load all MPLPB','language resources'])
    mind.setdefault('social',{}).update(active=True,stage='story',style='chat')
    return S.handle(message,None,mind) or reply('Tell me a little more about what you have in mind.',suggestions=['can we talk','load all MPLPB'])


def explore_sources(app,data,session,message,corpus,profile):
    """Read saved pages with their normal gates; never activate serious state."""
    request=IC.topic_request(message)
    if not request and (D.respond(message,copy.deepcopy(session['mind'])) or T.smalltalk_candidate(message,session['mind'])):return None
    subject=request[1].strip() if request else session['mind'].get('idea_chat',{}).get('subject')
    if request:
        IC.handle(message,session['mind'])
        query='tell me about '+subject
    else:
        query=message
    if not request and not re.match(r'^(?:what|who|when|where|how|is|are|does|do|can|will|tell me about|summarize|explain)\b',message,re.I):return None
    keys=sorted(app.roots())
    shadow=copy.deepcopy(session)
    shadow['environment']={'mode':'focus','corpora':keys,'focus_corpus':None}
    shadow['context']=None
    entries,_=pages(app,keys,profile)
    candidates=[(k,p) for k,p in entries if subject and p['title'].casefold()==subject.casefold()]
    # Resolve pronouns per page, preserving duplicate-title results independently.
    if not request and candidates and Q.question_intent(message,subject):
        responses=[]
        for k,p in candidates:
            answer=Q.handle(app,k,app.root(k),profile,message,p)
            if answer and answer.get('sources'):responses.append({'corpus':k,'response':answer})
        if responses:
            result=M.reply('federated_answers','From saved MPLPB pages:\n\n'+'\n\n'.join(x['corpus']+' :: '+x['response']['message'] for x in responses),None,'CHAT-SOURCES',authority='separate_source_results',scope_results=responses,sources=[dict(s,corpus=x['corpus']) for x in responses for s in x['response'].get('sources',[])])
        else:return None
    else:
        result=handle(app,data,shadow,query,corpus,profile)
    if not result or not result.get('sources'):return None
    result['context']=None
    result['message']+='\n\nWe can explore these pages conversationally, or choose Serious mode to focus on their evidence.'
    result['support_notice']='Chat exploration; cited passages come from saved MPLPB pages. Conversation is not additional evidence.'
    result['suggestions']=['tell me more','serious mode','just chat']
    result['response_structure']={'intent':'source_exploration','mode':'chat','factual_claims':True,'mplpb_supported':True}
    return result


def handle(app, data, session, message, corpus, profile):
    key=T.casual_key(message)
    if key in {'just chatting','chat mode','stay casual','keep chatting'}:return load(app,session,[])
    # An explicit casual request can leave serious mode; topic alone cannot.
    if IC.topic_request(message) and key not in {"let's talk about it",'lets talk about it','talk about it','talk about this'}:
        if session.get('environment',{}).get('mode') == 'focus':
            result=IC.handle(message,session['mind'])
            result['context']=session['context']
            return result
        if not session.get('environment'):load(app,session,[])
        return explore_sources(app,data,session,message,corpus,profile) or general(message,session)
    if key in {'load all mplpb','load saved mplpb'}:return load(app,session,'all')
    if key in {'load mplpb','focus mode','serious mode'}:
        return load(app,session,data.get('loaded_corpora',[corpus]))
    env=session.get('environment')
    if not env:
        if not data.get('default_chat',False) and key not in {'how do you think','how does your mind work'}:
            return None
        # Old browser saves may have no environment despite displaying Just chat.
        # Preserve explicit source/management commands and existing selected topics.
        command=bool(re.match(r'^(?:topic|relate|focus|summarize|explain|compare|teach|show|clear|forget|remember|memory|search|find|import|guide|next|back|finish|define|dictionary|synonyms|thesaurus|language)\b',key))
        relation=bool(re.fullmatch(r'is .+? (?:a|an|related to) .+',key))
        selection=bool(re.fullmatch(r"(?:let's talk about|lets talk about|let us talk about|talk about|discuss) .+",key))
        if session['context'] or command or relation or selection or key in T.LIST:
            return None
        # Migrate without clearing notes, transcript, or an in-progress social turn.
        session['environment']={'mode':'chat','corpora':[],'focus_corpus':None}
        session['mind'].pop('topic_offer',None)
        session['mind']['casual_active']=True
        env=session['environment']
    if key=='show loaded mplpb':
        return reply('Loaded MPLPB collections: '+(', '.join(env['corpora']) or 'none')+'.',session['context'],suggestions=['show my MPLPB','load all MPLPB','just chat'])
    if session['mind'].get('guide',{}).get('active') and key in {'next','next step','continue guide','back','previous step','stop guide','finish guide','skip guide'}:
        return None
    # Explicit source management and note/help commands retain their existing paths.
    if re.match(r'^(?:search|find|import|remember|memory|forget|guide|define|dictionary|synonyms|thesaurus|language)\b',key) or key in {'show memory','what do you remember','forget notes'}:
        return None
    if env['mode']=='chat':
        if key in T.LIST:
            return reply('No MPLPB is loaded into this chat. Your saved collections are available in the load controls.',suggestions=['load all MPLPB','focus mode'])
        if key.startswith(('topic ','focus ')):
            load(app,session,[corpus]);env=session['environment']
        else:
            return explore_sources(app,data,session,message,corpus,profile) or general(message,session)
    # Social turns do not change loaded collections or the selected evidence page.
    conversational=EM.handle(message,session['mind']) or D.respond(message,session['mind'])
    if conversational is None and T.smalltalk_candidate(message,session['mind']):
        conversational=S.handle(message,None,session['mind']) or T.smalltalk(message,None,session['mind'],[],'loaded-chat')
    if conversational is None and session['mind'].get('idea_chat') and (key in {'tell me more','go on','why','how','how so','why not','any ideas'} or key.startswith(('what if ','imagine ','suppose '))):
        conversational=IC.handle(message,session['mind'])
    if conversational:
        conversational['context']=session['context']
        conversational.setdefault('response_structure',{}).update(factual_claims=False,mplpb_supported=False)
        return conversational
    entries,blocked=pages(app,env['corpora'],profile)
    choices=['focus '+k+' :: '+pin['title'] for k,pin in entries]
    if key in T.LIST or key=='explore loaded mplpb':
        return reply('Loaded pages (collection boundaries retained):\n'+('\n'.join(k+' :: '+p['title'] for k,p in entries) or 'No eligible pages.')+('\nSome collections are blocked; see evidence details.' if blocked else ''),session['context'],suggestions=choices[:40]+['just chat'],scope_pages=[{'corpus':k,**p} for k,p in entries],blocked_collections=blocked)
    focus=re.fullmatch(r'focus ([^ ]+) :: (.+)',message,re.I)
    topic=re.fullmatch(r'topic (.+)',message,re.I)
    if focus or topic:
        candidates=[(k,p) for k,p in entries if p['title'].casefold()==(focus[2] if focus else topic[1]).casefold() and (not focus or k==focus[1])]
        chosen,trace=RD.determine([{'id':k+' :: '+p['title'],'basis':'procedure','meaning':k+' :: '+p['path'],'page':(k,p)} for k,p in candidates],'focus')
        if chosen is None:
            return reply('Choose one eligible page and its collection; duplicate titles are kept separate.',None,suggestions=['focus '+k+' :: '+p['title'] for k,p in candidates][:40],blocked_collections=blocked,selection_determination=trace)
        k,p=chosen['page'];session['environment']['focus_corpus']=k
        result=C.turn(app,k,app.root(k),profile,'topic '+p['title'],None)
        result['selection_determination']=trace
        return result
    focused=env.get('focus_corpus');context=session['context']
    if focused and context:
        if focused not in env['corpora'] or (focused,context) not in entries:
            env['focus_corpus']=None
            return reply('The focused page changed or is unavailable. Choose an eligible page again.',None,suggestions=choices[:40],blocked_collections=blocked)
        root=app.root(focused)
        return M.handle(root,profile,message,context,session['mind']) or Q.handle(app,focused,root,profile,message,context) or C.turn(app,focused,root,profile,message,context)
    # Evaluate explicit named-subject attribute queries independently in each ledger.
    results=[]
    relation=bool(re.fullmatch(r'relate .+?\s*->\s*.+|is .+? (?:a|an|related to) .+[?.!]*',message,re.I))
    if relation:
        for k in dict.fromkeys(k for k,_ in entries):
            answer=C.turn(app,k,app.root(k),profile,message,None)
            results.append({'corpus':k,'response':answer})
    overview=re.fullmatch(r'(?:what is|tell me about|summarize|explain) (.+?)[?.!]*',message,re.I)
    for k,p in entries:
        if overview and overview[1].casefold()==p['title'].casefold():
            answer=C.turn(app,k,app.root(k),profile,'show source',p)
            results.append({'corpus':k,'response':answer})
        elif Q.question_intent(message,p['title']) and re.search(r'(?<!\w)'+re.escape(p['title'])+r'(?!\w)',message,re.I):
            answer=Q.handle(app,k,app.root(k),profile,message,p)
            results.append({'corpus':k,'response':answer})
    if results:
        values={Q.normalized(e['value']) for x in results for e in x['response'].get('evidence',[])}
        return M.reply('conflict' if len(values)>1 else 'federated_answers','Separate collection results; no cross-collection inference or preferred answer:\n\n'+'\n\n'.join(x['corpus']+' :: '+x['response']['message'] for x in results),None,'SCOPE-SEPARATE',
                       authority='separate_source_results',sources=[dict(s,corpus=x['corpus']) for x in results for s in x['response'].get('sources',[])],scope_results=results,blocked_collections=blocked,suggestions=choices[:40]+['just chat'])
    return reply('Serious mode keeps every loaded collection separate. Choose a page for follow-up questions, or ask a supported attribute question naming its topic.',None,suggestions=choices[:40]+['just chat'],blocked_collections=blocked)
