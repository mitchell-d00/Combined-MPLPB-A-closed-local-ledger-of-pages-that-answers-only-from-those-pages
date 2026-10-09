"""Explicit empty/chat and federated/focus scopes; never merge ledger evidence."""
import re
import copy
from tools import casual_reasoning as D
from tools import reduction as RD
from tools import emotional_rules as EM
from tools import idea_chat as IC
from tools import chat_logic as C, chat_tutor as T, deterministic_mind as M
from tools import social_chat as S, grounded_chat as Q, reference_resources as F

VERSION = 'chat-environment-v8'


def reply(body, context=None, **extra):
    return M.reply('conversation', body, context, 'ENVIRONMENT-1',
                   authority='conversation_structure', **extra)


def load(app, session, keys):
    roots = app.roots()
    if keys == 'all': keys = sorted(roots)
    if not isinstance(keys, list) or len(keys) > 64 or any(not isinstance(k,str) or k not in roots for k in keys) or len(set(keys)) != len(keys):
        raise ValueError('Choose distinct available MPLPB collections (up to 64), or none.')
    previous=session.get('environment',{})
    if previous.get('mode')=='focus' and previous.get('corpora'):
        session['saved_focus_corpora']=list(previous['corpora'])
    session['environment'] = {'mode': 'focus' if keys else 'chat', 'corpora': list(keys), 'focus_corpus': None}
    session['context'] = None
    mind = session['mind']
    mind.pop('idea_chat', None); mind.pop('proposition',None); mind.pop('topic_offer', None); mind.pop('guide', None); mind.pop('chat_discourse',None); mind.pop('emotional',None)
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
    lexical=lexical_topic(message,session)
    if lexical:return lexical
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
        return reply('I can’t supply a factual answer from the available local material yet. Could you name the topic or rephrase the question? We can also look for a source.',suggestions=['can we talk','load all MPLPB','language resources'])
    mind.setdefault('social',{}).update(active=True,stage='story',style='chat')
    return S.handle(message,None,mind) or reply('Tell me a little more about what you have in mind.',suggestions=['can we talk','load all MPLPB'])


def subject_key(subject):
    return re.sub(r'^(?:the|a|an)\s+', '', subject.casefold().strip(' ?.!, '))


def factual_body(answer):
    """Drop attribution-only lines, not factual prose; retain exact excerpt wording."""
    title=(answer.get('context') or {}).get('title','')
    lines=[]
    for line in answer.get('message','').splitlines():
        text=line.strip()
        check=text
        if title:
            check=re.sub(r'^(?:'+re.escape(title)+r'\s*)+', '',check,flags=re.I)
        if not check or re.match(r'^(?:Source(?: capture| authorship)?:|License:)',check,re.I):continue
        # Captured HTML can flatten a heading into the first sentence. Remove
        # only a duplicated title prefix, retaining the sentence's own subject.
        if title:text=re.sub(r'^'+re.escape(title)+r'\s+(?='+re.escape(title)+r'\b)', '',text,flags=re.I)
        lines.append(text)
    return '\n'.join(lines)


def topic_suggestions(subject, body=''):
    subject=subject_key(subject or '').strip()[:160]
    if not subject:return []
    choices=['Tell me more about '+subject,'Search '+subject]
    # Offer attribute questions only when their vocabulary appears in the answer.
    if re.search(r'\b(diameter|radius|height|length|width)\b',body,re.I):choices.insert(1,'How big is '+subject+'?')
    elif re.search(r'\b(age|years old)\b',body,re.I):choices.insert(1,'How old is '+subject+'?')
    return choices[:3]


def explore_sources(app,data,session,message,corpus,profile):
    """Use normal page gates for factual conversation in either mode."""
    request=IC.topic_request(message)
    defined=IC.PF.definition_subject(message)
    if not request and defined:request=(None,defined)
    state=session['mind'].get('idea_chat',{})
    followup=T.casual_key(message) in {'tell me more','more','go on','continue','show source','show page'} and state.get('sourced')
    if not request and not followup and (D.respond(message,copy.deepcopy(session['mind'])) or T.smalltalk_candidate(message,session['mind'])):return None
    subject=request[1].strip() if request else state.get('subject')
    continuation=bool(followup or (request and re.match(r'^tell me more about ',IC.PF.normalize(message),re.I) and subject_key(subject)==subject_key(state.get('subject',''))))
    if request:
        if subject_key(subject) in {'it','this','that'}:
            subject=state.get('subject') or (session.get('context') or {}).get('title') or subject
        if not continuation:IC.handle('tell me about '+subject,session['mind'])
        session['mind']['idea_chat']['subject']=subject
    if not request and not followup and not re.match(r'^(?:what|who|when|where|how|is|are|does|do|can|will|tell me about|summarize|explain)\b',message,re.I):return None
    env=session.get('environment',{})
    serious=env.get('mode')=='focus'
    keys=env.get('corpora',[]) if serious else sorted(app.roots())
    entries,blocked=pages(app,keys,profile)
    names={subject_key(subject)} if subject else set()
    if subject and re.fullmatch(r'[a-z]{1,39}s',subject_key(subject)) and not subject_key(subject).endswith('ss'):
        headword,senses,_=F.lookup_forms(subject_key(subject))
        if senses:names.add(headword)
    candidates=[(k,p) for k,p in entries if subject_key(p['title']) in names]
    # Broader local navigation may return several related pages; never choose a truth winner.
    if (request or followup) and subject:
        words=set(re.findall(r'[a-z0-9]+',subject_key(subject)))
        exact={(k,p['path']) for k,p in candidates}
        candidates=[(k,p) for k,p in entries if (k,p['path']) in exact or (words and words <= set(re.findall(r'[a-z0-9]+',subject_key(p['title']))))]
    if not request and state.get('source_pages'):
        selected={(x['corpus'],x['path']) for x in state['source_pages']}
        current={(k,p['path']) for k,p in candidates}
        candidates=[(k,p) for k,p in entries if (k,p['path']) in selected | current]
    results=[]
    if request or followup:
        for k,p in candidates:
            answer=C.turn(app,k,app.root(k),profile,'show source',p)
            if answer.get('kind')=='return' and answer.get('sources') and factual_body(answer):results.append({'corpus':k,'response':answer})
    elif candidates and Q.question_intent(message,subject):
        for k,p in candidates:
            answer=Q.handle(app,k,app.root(k),profile,message,p)
            if answer and answer.get('sources'):results.append({'corpus':k,'response':answer})
    else:
        # Named factual queries retain the existing independent-collection reader.
        shadow=copy.deepcopy(session)
        shadow['environment']={'mode':'focus','corpora':keys,'focus_corpus':None}
        shadow['context']=None
        shadow['mind'].pop('idea_chat',None)
        result=handle(app,data,shadow,message,corpus,profile)
        if result and result.get('sources'):results=result.get('scope_results',[])
    if not results and request:
        # Ask each eligible collection's established ownership reader independently.
        for k in dict.fromkeys(k for k,_ in entries):
            answer=C.turn(app,k,app.root(k),profile,subject,None)
            if answer.get('kind')=='return' and answer.get('sources') and factual_body(answer):
                results.append({'corpus':k,'response':answer})
    if not results:return None
    if request:
        session['mind']['idea_chat'].update(subject=subject,sourced=True,source_pages=[{'corpus':x['corpus'],'path':x['response']['context']['path']} for x in results if x['response'].get('context')])
    excerpts=[]
    offsets=session['mind'].get('idea_chat',{}).get('excerpt_offsets',{}) if continuation else {}
    seen=set(session['mind'].get('idea_chat',{}).get('seen_sentences',[])) if continuation else set()
    has_more=False
    for i,item in enumerate(results,1):
        body=factual_body(item['response'])
        sentences=re.split(r'(?<=[.!?])\s+(?=[A-Z])',body)
        pin=item['response'].get('context') or item['response'].get('sources',[{}])[0]
        key=item['corpus']+'|'+pin.get('path','')+'|'+pin.get('hash','')
        cursor=offsets.get(key,0);part=[]
        while cursor<len(sentences) and len(part)<2:
            sentence=sentences[cursor];cursor+=1
            fingerprint=' '.join(sentence.casefold().split())
            if fingerprint not in seen:part.append(sentence);seen.add(fingerprint)
        offsets[key]=cursor
        if any(' '.join(t.casefold().split()) not in seen for t in sentences[cursor:]):has_more=True
        if part:excerpts.append(' '.join(part)+' ['+str(i)+']')
    if session['mind'].get('idea_chat'):
        session['mind']['idea_chat'].update(excerpt_offsets=offsets,seen_sentences=sorted(seen))
    exhausted=not excerpts
    if exhausted:
        body='We’ve reached the end of the available text about '+str(subject)+'. We can find more sources or explore an idea about it.'
    else:
        opener=('Here’s more about '+subject+'.') if continuation else ('Let’s talk about '+subject+'.') if subject else 'Here’s what I found.'
        body=opener+'\n\n'+'\n\n'.join(excerpts)+'\n\nWhat part interests you most?'
    result=M.reply('federated_answers',body,session.get('context') if serious else None,'CHAT-SOURCES',authority='separate_source_results',scope_results=results,sources=[dict(s,corpus=x['corpus']) for x in results for s in x['response'].get('sources',[])],blocked_collections=blocked)
    result['source_scope']='loaded_scope' if serious else 'saved_reference'
    result['source_exhausted']=exhausted
    result['has_more_source_text']=has_more
    result['support_notice']='Factual conversation; cited passages come from MPLPB pages. Conversational framing is not additional evidence.'
    result['suggestions']=topic_suggestions(subject,' '.join(excerpts))
    if not has_more:
        result['suggestions']=[q for q in result['suggestions'] if not q.casefold().startswith('tell me more')]+['Explore an idea about '+str(subject)]
    result['response_structure']={'intent':'source_exploration','mode':env.get('mode','chat'),'factual_claims':True,'mplpb_supported':True,'subject':subject}
    return result



def lexical_topic(message,session):
    """Construct a topical reply from exact dictionary senses, preserving ambiguity."""
    subject=IC.PF.overview_subject(message) or IC.PF.definition_subject(message)
    if not subject or subject_key(subject) in {'it','this','that','you','yourself'}:return None
    word=subject_key(subject)
    headword,senses,_=F.lookup_forms(word)
    if not senses:return None
    result=F.handle('define '+headword,session.get('context'))
    parts=[]
    for sense in senses[:3]:
        definitions=sense.get('definitions',[])
        if not definitions:continue
        synonyms=[w for w in sense.get('synonyms',[]) if w.casefold()!=headword.casefold()]
        part='; '.join(definitions)
        if len(senses)>1:part='One meaning: '+part
        if synonyms:part+=' Related wording in this sense: '+', '.join(synonyms[:4])+'.'
        parts.append(part)
    if not parts:return None
    result['message']='Let’s start with '+headword+'.\n\n'+'\n\n'.join(parts)
    if session.get('mind',{}).get('emotional',{}).get('style')!='listen':
        result['message']+='\n\n'+('Which meaning did you have in mind?' if len(senses)>1 else 'What would you like to explore about '+headword+'?')
    result['suggestions']=['synonyms '+headword,'Search '+headword,'Explore an idea about '+headword]
    result['response_structure']={'intent':'lexical_topic','subject':headword,'factual_claims':True,'mplpb_supported':False}
    result['source_scope']='dictionary_reference'
    return result


def discover_saved(app,session,message,profile):
    """Retrieve saved references separately from loaded serious evidence."""
    active=set(session.get('environment',{}).get('corpora',[]))
    outside=sorted(set(app.roots())-active)
    if not outside:return None
    shadow=copy.deepcopy(session)
    shadow['environment']={'mode':'focus','corpora':outside,'focus_corpus':None}
    shadow['context']=None
    # explore_sources never invokes this helper recursively.
    result=explore_sources(app,{},shadow,message,outside[0],profile)
    if not result or not result.get('sources'):return None
    if shadow['mind'].get('idea_chat'):session['mind']['idea_chat']=shadow['mind']['idea_chat']
    result['context']=session.get('context')
    result['source_scope']='saved_reference_outside_loaded_scope'
    result['support_notice']='Saved reference; outside the loaded serious scope.'
    return result


def handle(app, data, session, message, corpus, profile):
    message=IC.PF.normalize(message)
    key=T.casual_key(message)
    if re.match(r'^explore an idea about ',message,re.I):
        if not session.get('environment'):load(app,session,[])
        result=IC.handle(message,session['mind'])
        result['context']=session.get('context')
        return result
    composed=re.fullmatch(r'(?:say (?:hi|hello)|give a greeting) to (.{1,100}?) and (?:tell (?:them|everyone)|talk) about (.{1,160}?)[?.!]*',message,re.I)
    if composed and ' and ' not in composed[1].casefold():
        result=handle(app,data,session,'tell me about '+composed[2],corpus,profile)
        if result:
            result['message']='Hello to '+composed[1]+'!\n\n'+result['message']
            result['composition']={'acts':['greeting','topic_overview'],'audience':composed[1],'sent_externally':False}
            return result
    if key in {'just chatting','chat mode','switch to chat','switch to chat mode','casual mode','stay casual','keep chatting'}:return load(app,session,[])
    if not data.get('default_chat') and not session.get('environment') and re.match(r'^(?:summari[sz]e |i (?:want|would like) to learn about )',message,re.I):return None
    # Topic requests keep the mode and consult available evidence before idea prompts.
    if (IC.topic_request(message) or IC.PF.definition_subject(message)) and key not in {"let's talk about it",'lets talk about it','talk about it','talk about this'}:
        if session.get('environment',{}).get('mode') == 'focus':
            result=explore_sources(app,data,session,message,corpus,profile) or discover_saved(app,session,message,profile) or lexical_topic(message,session) or IC.handle(message,session['mind'])
            result['context']=session['context']
            return result
        if not session.get('environment'):load(app,session,[])
        return explore_sources(app,data,session,message,corpus,profile) or general(message,session)
    if key in {'load all mplpb','load saved mplpb'}:return load(app,session,'all')
    if key in {'focus mode','serious mode','switch to serious','switch to serious mode','switch to focus mode'}:
        keys=[k for k in session.get('saved_focus_corpora',[]) if k in app.roots()]
        return load(app,session,keys or [corpus])
    if key=='load mplpb':return load(app,session,data.get('loaded_corpora',[corpus]))
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
    if session['mind'].get('idea_chat',{}).get('sourced') and (key in {'tell me more','more','go on','continue','show source','show page'} or (not session.get('context') and Q.question_intent(message,session['mind']['idea_chat']['subject']))):
        sourced=explore_sources(app,data,session,message,corpus,profile) or discover_saved(app,session,message,profile)
        if sourced:return sourced
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
    overview=re.fullmatch(r'(?:what is|what are|who is|tell me about|summarize|explain) (.+?)[?.!]*',message,re.I)
    for k,p in entries:
        if overview and subject_key(overview[1])==subject_key(p['title']):
            answer=C.turn(app,k,app.root(k),profile,'show source',p)
            results.append({'corpus':k,'response':answer})
        elif Q.question_intent(message,p['title']) and re.search(r'(?<!\w)'+re.escape(p['title'])+r'(?!\w)',message,re.I):
            answer=Q.handle(app,k,app.root(k),profile,message,p)
            results.append({'corpus':k,'response':answer})
    if results:
        values={Q.normalized(e['value']) for x in results for e in x['response'].get('evidence',[])}
        return M.reply('conflict' if len(values)>1 else 'federated_answers','Separate collection results; no cross-collection inference or preferred answer:\n\n'+'\n\n'.join(x['corpus']+' :: '+x['response']['message'] for x in results),None,'SCOPE-SEPARATE',
                       authority='separate_source_results',sources=[dict(s,corpus=x['corpus']) for x in results for s in x['response'].get('sources',[])],scope_results=results,blocked_collections=blocked,suggestions=topic_suggestions(overview[1] if overview else session['mind'].get('idea_chat',{}).get('subject')))
    return reply('What would you like to know about that? You can tell me a topic or ask a specific question; I’ll check the loaded pages.',session['context'],suggestions=topic_suggestions(session['mind'].get('idea_chat',{}).get('subject')),blocked_collections=blocked)
