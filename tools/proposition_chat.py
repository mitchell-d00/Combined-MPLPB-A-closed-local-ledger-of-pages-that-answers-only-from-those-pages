"""Finite subject/predicate discourse and compositional conversational realization.

User opinions are never promoted to source facts. Lexical senses aid wording;
source excerpts concern the subject and do not prove the user's predicate.
"""
import copy
import re
from tools import question_frames as F, deterministic_mind as M
from tools import reference_resources as R

VERSION='proposition-chat-v1'
# Opinion vocabulary identifies a conversational act, not a factual property.
OPINIONS={'cute','adorable','beautiful','pretty','lovely','cool','interesting','boring',
          'fun','funny','amazing','awesome','wonderful','ugly','scary','fascinating',
          'delightful','appealing','dull','gorgeous','charming','annoying'}
PRONOUNS={'it','they','these','those','that','this','them'}


def parse(message,memory):
    text=F.normalize(message).strip(' .!?').casefold()
    text=re.sub(r"\b(isn't|isnt)\b",'is not',text)
    text=re.sub(r"\b(aren't|arent)\b",'are not',text)
    text=re.sub(r"\b(don't|dont)\b",'do not',text)
    text=re.sub(r'^(?:i think|i feel like|in my opinion)\s+','',text)
    if re.match(r'^(?:say|repeat|search|find|import|remember|forget|show|load|clear|tell|explain|define|imagine|suppose|what if|never|topic|focus|guide|compare|relate|synonyms|dictionary|thesaurus|language|teach)\b',text):return None
    explicit=False; question=bool(re.match(r'^(?:do you think|is|are)\b',text))
    text=re.sub(r'^do you think\s+','',text)
    opinion_request=re.fullmatch(r'(?:what do you think (?:of|about)|how do you feel about|do you (?:like|love|enjoy)) (.{1,100})',text)
    if re.match(r'^(?:what|who|where|when|why|how|which|can|could|will|would|should|does|do)\b',text) and not opinion_request and not question:return None
    preferred=re.fullmatch(r'i (do not )?(like|love|enjoy|dislike|hate) (.{1,100})',text)
    copula=re.fullmatch(r'(.{1,100}?) (?:is|are|seems?|looks?) (not )?(?:(?:really|very|so|quite) )?([a-z][a-z0-9 -]{0,79})',text)
    inverted=re.fullmatch(r'(?:is|are) (.{1,100}?) (not )?(?:(?:really|very|so|quite) )?([a-z-]+)',text)
    if opinion_request:
        subject=opinion_request[1];predicate='interesting';negative=False;question=True
    elif preferred:
        subject=preferred[3];predicate=preferred[2];negative=bool(preferred[1]);explicit=True
    elif copula or inverted:
        match=copula or inverted;subject,predicate=match[1],match[3];negative=bool(match[2])
        # Avoid asserting objective properties or hijacking relation questions.
        if predicate not in OPINIONS:
            # Objective questions retain the existing factual and relation reader.
            if question:return None
            # A novel description can still be discussed as a user declaration.
            # No lexical entry is required and no truth is inferred.
            pass
    else:return None
    subject=re.sub(r'^(?:a|an|the) ', '',subject)
    if not re.fullmatch(r'[a-z][a-z0-9 -]{0,99}',subject):return None
    if re.search(r'\b(?:and|or|if|because|that|who|which|not)\b',subject) and subject not in PRONOUNS:return None
    if subject in {'i','you','we','he','she','my day','my life','my work','my job','myself','yourself'}:return None
    resolved=False
    if subject in PRONOUNS:
        prior=memory.get('idea_chat',{}).get('subject') or memory.get('proposition',{}).get('subject')
        if not prior:return None
        subject=prior;resolved=True
    return {'subject':subject,'predicate':predicate,'negated':negative,'question':question,
            'act':'opinion_request' if opinion_request else 'preference' if explicit else 'opinion_question' if question else 'opinion' if predicate in OPINIONS else 'description',
            'reference_resolved':resolved,'user_claim_verified':False}


def realize(frame,turn,listening=False):
    subject=frame['subject'];predicate=frame['predicate'];negative=frame['negated']
    if frame['act']=='opinion_request':
        opening='I can explore '+subject+' with you; I don’t have personal tastes.'
        follow='What interests you about '+subject+'?'
    elif frame['act']=='preference':
        favorable=(predicate in {'like','love','enjoy'}) != negative
        opening=('You’re drawn to ' if favorable else 'You’re not keen on ')+subject+'.'
        follow=('What do you enjoy about ' if favorable else 'What puts you off ')+subject+'?'
    elif frame['act']=='description':
        opening='Let’s check that description of '+subject+'.'
        follow='Are you asking about whether '+subject+' fits that description, or exploring an idea?'
    else:
        if frame['question']:
            opening='That’s a matter of taste.'
        elif negative:opening='That description doesn’t fit your view of '+subject+'.'
        else:opening=('Sounds like '+subject+' made an impression.' if turn%2 else 'You have a clear take on '+subject+'.')
        follow=('What makes '+subject+' seem '+('less ' if negative else '')+predicate+' to you?')
    return opening+('' if listening else '\n\n'+follow)


def handle(app,data,session,message,corpus,profile):
    if not session.get('environment') and not data.get('default_chat',False):return None
    memory=session.setdefault('mind',{})
    from tools import emotional_rules as EM
    if EM.handle(message,copy.deepcopy(memory)) is not None:return None
    requested=F.definition_subject(message)
    declarations=memory.get('user_descriptions',[])
    matching=[d for d in declarations if requested and d['subject']==requested.casefold()]
    if matching:
        from tools import chat_environment as E
        shadow=copy.deepcopy(session)
        source=E.explore_sources(app,data,shadow,'tell me about '+requested,corpus,profile)
        if source and source.get('sources'):return None
        descriptions=list(dict.fromkeys(('not ' if d['negated'] else '')+d['predicate'] for d in matching))
        body='For '+requested+', you’ve supplied '+('this description' if len(descriptions)==1 else 'these descriptions')+': '+ '; '.join(descriptions)+'.'
        if len(descriptions)>1:body+=' Which description should we use for this conversation?'
        return M.reply('conversation',body,session.get('context'),'USER-TOPIC-CONTEXT',authority='user_declaration',
            user_context=matching,suggestions=['Explore an idea about '+requested,'Search '+requested],
            response_structure={'intent':'user_topic_context','subject':requested,'factual_claims':False,'mplpb_supported':False})
    frame=parse(message,memory)
    if not frame:return None
    # Exact requests, social disclosures and explicit source commands have other routes.
    from tools import chat_environment as E
    turn=memory.get('proposition',{}).get('turn',0)+1
    memory['proposition']={**frame,'turn':turn}
    if frame['act']=='description':
        declaration={k:frame[k] for k in ('subject','predicate','negated')}
        if declaration not in declarations:declarations.append(declaration)
        memory['user_descriptions']=declarations[-8:]
    shadow=copy.deepcopy(session)
    lookup='tell me about '+frame['subject']
    sourced=E.explore_sources(app,data,shadow,lookup,corpus,profile)
    if not sourced and session.get('environment',{}).get('mode')=='focus':
        sourced=E.discover_saved(app,shadow,lookup,profile)
    # Remember the subject, never the opinion as established page evidence.
    memory['idea_chat']=shadow['mind'].get('idea_chat',{'subject':frame['subject'],'turn':0})
    lexical=[];subject_senses=[];subject_head=frame['subject']
    for word in (frame['subject'],frame['predicate']):
        head,senses,_=R.lookup_forms(word)
        if word==frame['subject']:subject_senses=senses;subject_head=head
        lexical.append({'query':word,'headword':head,'sense_ids':[s['id'] for s in senses[:3]],
                        'synonyms_are_not_evidence':True})
    listening=memory.get('emotional',{}).get('style')=='listen'
    body=realize(frame,turn,listening)
    suggestions=['Tell me about '+frame['subject'],'Explore an idea about '+frame['subject'],
                 'define '+frame['predicate']] if frame['act']!='preference' else ['Tell me about '+frame['subject'],'Explore an idea about '+frame['subject']]
    if sourced and sourced.get('sources'):
        # Keep source prose intact; no claim that it entails an aesthetic judgment.
        excerpts=[];shown=sourced.get('scope_results',[])[:3]
        for i,item in enumerate(shown,1):
            text=E.factual_body(item['response'])
            sentence=re.split(r'(?<=[.!?])\s+(?=[A-Z])',text)[0]
            if sentence:excerpts.append(sentence+' ['+str(i)+']')
        if excerpts:
            chunks=body.split('\n\n')
            body=chunks[0]+'\n\n'+'\n\n'.join(excerpts)+('' if listening else '\n\n'+chunks[-1])
            result=M.reply('federated_answers',body,session.get('context'),'PROPOSITION-CONTEXT',
                authority='separate_source_results',scope_results=shown,
                sources=[dict(s,corpus=item['corpus']) for item in shown for s in item['response'].get('sources',[])],
                source_scope=sourced.get('source_scope'),suggestions=suggestions)
        else:sourced=None
    if (not sourced or not sourced.get('sources')) and subject_senses:
        result=R.handle('define '+subject_head,session.get('context'))
        definitions=['; '.join(sense.get('definitions',[])) for sense in subject_senses[:3] if sense.get('definitions')]
        chunks=body.split('\n\n')
        result['message']=chunks[0]+'\n\nDictionary senses of '+subject_head+' include: '+ '; '.join(definitions)+'.'+('' if listening else '\n\n'+chunks[-1])
        result['suggestions']=suggestions
        result['source_scope']='dictionary_reference'
    elif not sourced or not sourced.get('sources'):
        result=M.reply('conversation',body,session.get('context'),'PROPOSITION-CONVERSATION',
                       authority='conversation_structure',suggestions=suggestions)
    result['response_structure']={'intent':'topic_opinion' if result.get('sources') else 'casual_topic_opinion',
                                 'subject':frame['subject'],'factual_claims':bool(result.get('sources')),
                                 'mplpb_supported':bool(result.get('sources')) and result.get('authority')!='lexical_reference',
                                 'construction':{'rules':['subject + predicate + polarity + speech_act','opinion_is_not_source_fact','preserve_source_spans'],
                                                 'frame':frame,'lexical_lookup':lexical,'version':VERSION}}
    result['support_notice']='Conversation; cited passages describe the topic, not proof of the opinion.'
    return result
