"""Read-only selection for bounded chat skills and explicit retrieval plans.

Recognition never invokes an answer constructor. A selected skill runs once on
isolated state. Source absence advances only an explicitly declared retrieval
step; it does not authorize trying unrelated conversation interpretations.
"""
import copy
import re
from tools import casual_reasoning as D, emotional_rules as EM, idea_chat as IC
from tools import chat_tutor as T, social_chat as S, deterministic_mind as M
from tools import reference_resources as F, general_reference as GR

VERSION='skill-planner-v1'


def reference_request(message):
    return (message.strip().casefold().strip('?.!') in {'language resources','reference resources','grammar resources','grammar guide'} or
        bool(re.fullmatch(r'(?:define|dictionary|synonyms(?: for)?|thesaurus)\s+(.{1,80})|what does (.{1,80}) mean[?.!]*',message.strip(),re.I)))


def guide_request(message,mind):
    k=T.key(message);g=mind.get('guide',{})
    return (k in T.START or k in {'stop guide','finish guide','skip guide','no thanks'} or
        (g.get('active') and (k in {'next','next step','continue guide','back','previous step'} or
         (g.get('step')==1 and bool(re.fullmatch(r"[\w '\-]{1,80}",message.strip())) and 0<len(k.split())<=5 and
          k.split()[0] not in {'search','topic','import','find','remember','memory','summarize','explain','show','how','why','what','is','are','do','does','can','compare','relate','hello','hi','hey','thanks','thank','ok','okay'}))))


def conversation_request(message):
    return T.key(message) in {'keep it short','short answers please','be brief','give me more detail','more detail please',
        'lets talk about it',"let's talk about it",'can we talk about this','can we chat about it','talk to me about this','lets discuss it',"let's discuss it",
        'i am confused',"i'm confused",'i dont understand',"i don't understand",'that is confusing','help me understand','i am lost',"i'm lost",
        'that is interesting','thats interesting',"that's interesting",'interesting','sounds interesting','i like this topic','what should we discuss','what should i ask next','what next',
        'what do you think','what is your opinion','do you like this topic'}


def research_request(message,session):
    if session.get('environment',{}).get('mode')!='chat':return False
    k=message.casefold().replace('’',"'").strip(' .!?')
    if k in {'general topics','list general topics'}:return True
    if k in {'tell me more','more about that','go on'}:
        return any(r['topic']==session['mind'].get('general_reference_topic') for r in GR.records())
    subject=re.sub(r"^(?:(?:can|could|would) you )?(?:tell me about|chat about|talk about|explain|what is|what are|define) (?:the )?",'',k)
    subject=re.sub(r'^the ','',subject)
    return any(subject in [r['topic'],*r.get('aliases',[])] for r in GR.records())


def plan(message,session,scope='general',titles=()):
    """Collect every applicable local skill before selecting by explicit specificity."""
    mind=session.get('mind',{});context=session.get('context');k=T.casual_key(message)
    candidates=[]
    if scope in {'focus','legacy'} and (k in T.LIST or k=='explore loaded mplpb'):
        return {'version':VERSION,'phase':'before_execution','scope':scope,'request':message,'candidates':[],'selected':None}
    def add(name,priority,basis,authority):
        candidates.append(dict(skill=name,priority=priority,basis=basis,authority=authority))
    if reference_request(message):add('reference',120,'explicit language reference request','lexical_reference')
    if scope=='legacy' and guide_request(message,mind):add('guide',115,'guide command or pending guide topic','interface_instructions')
    if conversation_request(message):add('conversation',110,'explicit conversation preference or topic navigation','conversation_structure')
    if scope=='legacy' and re.fullmatch(r'(?:i want to learn about|i would like to learn about|help me learn about|teach me about|can we explore) (.{1,160})[?.!]*',message.strip(),re.I):
        add('learning',105,'explicit learning request','interface_instructions')
    emotion=EM.recognize(message,mind)
    if emotion and scope!='legacy':add('emotional',100 if emotion!='followup' else 65,'explicit feeling/preference or active listening','conversation_structure')
    discourse=D.recognize(message,mind)
    if discourse and scope!='legacy':add('discourse',95,'recognized speech act or its active follow-up','conversation_structure')
    if scope=='general' and research_request(message,session):add('research',90,'named research note or its continuation','research_note')
    subject=IC.PF.overview_subject(message) or IC.PF.definition_subject(message)
    if scope=='general' and subject and subject.casefold() not in {'it','this','that','you','yourself'}:
        _,senses,_=F.lookup_forms(re.sub(r'^(?:the|a|an)\s+','',subject.casefold()))
        if senses:add('lexical',85,'available dictionary senses for requested subject','lexical_reference')
    idea=bool(IC.topic_request(message)) or bool(mind.get('idea_chat') and (k in {'tell me more','go on','why','how','how so','why not','any ideas','yes','sure','explore an idea'} or k.startswith(('what if ','imagine ','suppose '))))
    if idea and scope!='legacy':add('idea',80,'explicit idea topic or active idea follow-up','conversation_structure')
    mentions=[t for t in titles if re.search(r'(?<!\w)'+re.escape(T.key(t))+r'(?!\w)',k)]
    if scope=='legacy' and ((mentions and (T.smalltalk_candidate(message,mind) or S.candidate(message,mind))) or (mind.get('topic_offer') and k in {'yes','yes please',"let's explore",'lets explore'})):
        add('smalltalk',125,'literal available title or pending topic acceptance','conversation_structure')
    if S.candidate(message,mind):add('social',60,'social act or active social conversation','conversation_structure')
    help_intent=M.help_intent(message,context)
    if help_intent:add('help',70 if help_intent not in {'HELP-GREETING','HELP-ACK'} else 50,'interface help request','interface_instructions')
    if T.smalltalk_candidate(message,mind):add('smalltalk',55 if scope=='legacy' else 40,'smalltalk act or pending topic offer','conversation_structure')
    if scope=='general' and mind.get('idea_chat') and not candidates:add('idea',10,'active topic with no more specific request','conversation_structure')
    # Open conversation continuation is deliberately lower than all explicit acts.
    if scope=='legacy' and not context and mind.get('casual_active') and not candidates and '?' not in message and not re.match(r'^(?:what|why|who|where|when|how|which|is|are|can|could|do|does|did|will|would|should|topic|search|find|import|define|dictionary|synonyms|thesaurus|grammar|language|reference|remember|memory|forget|clear|summarize|explain|compare|relate|show|guide|next|back|stop|finish|teach|tell)\b',k) and k not in {'more','continue','yes','yes please','no','no thanks'}:
        add('open_social',5,'open casual continuation','conversation_structure')
    candidates.sort(key=lambda c:(-c['priority'],c['skill']))
    return {'version':VERSION,'phase':'before_execution','scope':scope,'request':message,
            'candidates':candidates,'selected':candidates[0] if candidates else None,
            'policy':{'user_context_is_evidence':False,'synonyms_prove_facts':False}}


def execute(message,session,scope='general',app=None,corpus=None,profile=None,planned=None):
    from tools import chat_environment as E, chat_logic as C
    titles=[]
    if scope=='legacy' and app:
        try:titles=[p['title'] for p in app.inventory(corpus,profile)['pages'] if p['eligible']]
        except (ValueError,OSError):pass
    before=planned or plan(message,session,scope,titles)
    winner=before['selected']
    if not winner:return None
    shadow=copy.deepcopy(session);mind=shadow['mind'];context=shadow.get('context')
    def smalltalk():
        result=T.smalltalk(message,context,mind,titles,(corpus+'|'+profile) if corpus else 'loaded-chat')
        if result and 'select_topic' in result and app:
            return C.turn(app,corpus,app.root(corpus),profile,'topic '+result['select_topic'],context)
        return result
    def open_social():
        mind.setdefault('social',{}).update(active=True,stage='story',style='chat')
        return S.handle(message,context,mind)
    handlers={'reference':lambda:F.handle(message,context),'guide':lambda:T.guide(message,context,mind),
      'conversation':lambda:T.conversation(message,context,mind),'learning':lambda:T.learning_request(message,context),
      'emotional':lambda:EM.handle(message,mind),'discourse':lambda:D.respond(message,mind),
      'research':lambda:GR.handle(message,shadow),'lexical':lambda:E.lexical_topic(message,shadow),
      'idea':lambda:IC.handle(message,mind),'social':lambda:S.handle(message,context,mind),
      'help':lambda:M.help_reply(message,context),'smalltalk':smalltalk,'open_social':open_social}
    if winner['skill']!='discourse' and not D.recognize(message,mind):
        mind.pop('chat_discourse',None)
    result=handlers[winner['skill']]()
    if result is None:
        # No competing renderer is used to rescue an incorrectly recognized route.
        result=M.reply('clarify','Could you clarify that request?',context,'SKILL-DECLINED',authority='conversation_structure')
        result['execution_issue']='selected skill declined'
    else:
        session.clear();session.update(shadow)
    if scope=='legacy' and result.get('response_structure',{}).get('topic_mentions'):
        session['mind'].pop('social',None)
    result['skill_plan']=before
    result.setdefault('claim_units',[{'text':result['message'],'authority':result.get('authority',winner['authority']),
                                      'sources':copy.deepcopy(result.get('sources',[]))}])
    return result


def source_plan(message,context):
    """Select a single reader from syntax, leaving all evidence gates in the reader."""
    k=message.casefold().strip(' ?.!')
    from tools import grounded_chat as Q
    procedural=(M.help_intent(message,context) or k.startswith('remember ') or k in
        {'memory','what do you remember','show memory','forget notes','forget memory','forget topic','clear topic','why','why did you say that','explain your decision'} or
        re.fullmatch(r'(?:summarize|explain|tell me about) (.+)',message.strip(),re.I) or
        re.fullmatch(r'compare (.{1,160}?) vs (.{1,160})',message.strip().rstrip('?.!'),re.I))
    reader='mind' if procedural else 'grounded' if Q.recognizes(message,context) else 'ledger'
    return {'phase':'before_execution','reader':reader,'authority':'gated_source','request':message}


def read_source(app,corpus,root,profile,message,context,mind):
    from tools import grounded_chat as Q, chat_logic as C
    before=source_plan(message,context)
    if before['reader']=='mind':result=M.handle(root,profile,message,context,mind)
    elif before['reader']=='grounded':result=Q.handle(app,corpus,root,profile,message,context)
    else:result=C.turn(app,corpus,root,profile,message,context)
    if result is None:
        result=M.reply('clarify','I could not resolve that request against the selected page.',context,'SOURCE-DECLINED')
    result['source_plan']=before
    return result
