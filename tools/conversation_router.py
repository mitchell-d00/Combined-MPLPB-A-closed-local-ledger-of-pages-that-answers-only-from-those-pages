"""Pure route proposals and pre-execution plans; no candidate grants evidence.

Specific speech acts outrank general topic retrieval. Executors remain bounded
legacy skills; only the selected executor can commit conversation state.
"""
import copy
import re
from tools import conversation_engine as CE, conversation_memory as CM
from tools import conversation_branches as CB, context_index as CX
from tools import self_knowledge as SK, proposition_chat as PC
from tools import dialogue_rules as DR, chat_environment as E, emotional_rules as EM
from tools import deterministic_mind as M
from tools.chat_phrasing import memory_question

VERSION = 'conversation-router-v2'

def relationships(session, acts):
    """Replay typed user declarations only. Assistant answers are never premises."""
    state=CE.replay(session)
    turn=len(session.get('log',[]))+1
    for act in acts:CE.apply(state,act,turn)
    nodes=[{'id':'user','type':'person','label':state['name'] or 'user'}]
    edges=[]
    for ident,person in sorted(state['people'].items()):
        nodes.append({'id':'person:'+ident,'type':'person','label':person['name']})
        for predicate,item in sorted(person['attributes'].items()):
            edges.append({'subject':'person:'+ident,'predicate':predicate,'object':item['value'],
                          'turn':item['turn'],'authority':'user_declaration'})
    # Relationship labels come from explicit user introductions, not inference
    # from names, pronouns, or assistant text.
    roles={}
    for number,entry in enumerate(session.get('log',[]),1):
        for item in map(CE.act,CE.clauses(entry.get('payload',{}).get('question',''))):
            if item['type']=='person':roles[item['person'].casefold()]=(item['relation'],number)
    for item in acts:
        if item['type']=='person':roles[item['person'].casefold()]=(item['relation'],turn)
    for ident,(relation,number) in sorted(roles.items()):
        edges.append({'subject':'user','predicate':relation,'object':'person:'+ident,
                      'turn':number,'authority':'user_declaration'})
    # Explicit possessive declarations and corrections share the same replay rules
    # as personal recall. Prepare a copy: interpretation has no session effects.
    index=CX.prepare(copy.deepcopy(session))
    slots=copy.deepcopy(index['slots'])
    for act in acts:
        for item in CX.declarations(act.get('text','')):
            slots[item['slot']]=dict(item,turn=turn,basis='user_declaration')
    for slot,item in sorted(slots.items()):
        edges.append({'subject':'user','predicate':slot,'object':item['value'],
                      'turn':item['turn'],'authority':'user_declaration',
                      'negated':item.get('negated',False),'supersedes':item.get('supersedes')})
    if state['topic']:
        nodes.append({'id':'topic','type':'topic','label':state['topic']})
        edges.append({'subject':'user','predicate':'discusses','object':state['topic'],
                      'authority':'conversation_context'})
    return {'nodes':nodes,'edges':edges,'identity_verified':False,'source_evidence':False}

def propose(frame, session, data):
    """Collect competing intents without calling reply constructors or readers."""
    text=frame['resolved'];k=CM.key(text);mind=session.get('mind',{})
    candidates=[]
    def add(handler,intent,priority,basis,authorities):
        candidates.append({'handler':handler,'intent':intent,'priority':priority,
                           'basis':basis,'allowed_authorities':authorities})
    # High specificity commands cannot be swallowed by a topic/opinion handler.
    controls={'show loaded mplpb','list topics','show topics','what topics do you have',
              'load all mplpb','load saved mplpb','load mplpb','just chat','just chatting','chat mode',
              'switch to chat','switch to chat mode','casual mode','stay casual','keep chatting',
              'focus mode','serious mode','switch to serious','switch to serious mode','switch to focus mode'}
    if k in controls or 'load_corpora' in data:
        add('environment','control',120,'explicit session command',['session_state'])
    if EM.feeling(text) or k in {'no jokes','please be gentle','be gentle','be serious with me',
        'jokes are okay','you can joke','jokes are ok','just listen','listen','i just want to vent',
        'no advice','do not give advice',"don't give advice"}:
        add('environment','emotional_preference',98,'explicit feeling or conversation preference',['conversation_structure'])
    if SK.recognize(text):
        add('self','system_description',90,'authored capability or observed state',['system_description'])
    branch=mind.get('conversation_branches',{})
    choices=branch.get('pending',[]) or CB.candidates(session)
    choice_words={CM.key(c['label']) for c in choices}
    aliases={CM.key(v) for values in CB.ALIASES.values() for v in values}
    if ((k in CB.FOLLOWUPS and (len(choices)>1 or branch.get('active')) and
         (k not in {'tell me more','more about it'} or branch.get('pending') or branch.get('active'))) or
        (branch.get('pending') and k in choice_words|aliases|{'first','second','1','2','yes','no','that one','it','that'}) or
        (branch.get('active') and k in aliases) or
        (re.match(r'^(?:no[,; ]+|i mean |not that[,; ]+)',k) and any(re.fullmatch(re.escape(v)+r'(?: what is it| what is that)?',re.sub(r'^(?:no[,; ]+|i mean |not that[,; ]+)','',k)) for v in aliases))):
        add('branch','resolve_reference',110,'pending choice or typed referent',['conversation_structure','system_description','gated_source'])
    dialogue=CE.recognize(text,session,acts=frame['acts'])
    frame['dialogue_interpretation']=dialogue
    if dialogue:
        acts=dialogue['acts'];specific=any(a['type'] in {'person','person_update','person_query','recall_name','recall_topic','introduce'} for a in acts)
        add('dialogue','multiple_intentions' if len(acts)>1 else acts[0]['type'],105 if len(acts)>1 or specific else 85,
            'recognized dialogue acts',['user_declaration','system_description','conversation_structure','gated_source'])
    cmd=memory_question(k)
    if (CM.introduction(text) or cmd in CM.FORGET|CM.NAME_QUESTIONS or
        re.match(r'^(?:what did (?:i|we) (?:say|tell you|mention|discuss)|what have (?:i|we) (?:said|mentioned|discussed)|do you remember what i said) about ',cmd) or
        (CM.name_from_chat(session)[0] and cmd in {'hi','hello','hey','hi again','hello again','who are you','what is your name'}) or
        re.match(r"^(?:that's me|that is me|yes that's me|yes that is me)",cmd)):
        add('memory','personal_memory',100,'explicit personal request',['user_declaration','system_description'])
    index=CX.prepare(copy.deepcopy(session))
    meaning=re.fullmatch(r'what does (.{1,50}?) mean',cmd)
    if ((CX.declarations(text) and CX.declarations(text)[0]['slot']!='name') or
        re.match(r"^(?:(?:what (?:is|are)|what's|do you remember|remind me (?:of|about)) my (?!name\b)|forget my (?!name\b)|when i say |forget the meaning of |what did we (?:discuss|talk about)|what have we discussed|go back to |return to )",cmd) or
        (meaning and meaning[1] in index['vocabulary']) or
        (re.match(r"^(?:what is|what's) (?:its|their) ",cmd) and index['slots'])):
        add('context','user_context',100,'explicit declaration or indexed recall',['user_declaration'])
    # These recognizers do not evaluate arithmetic, generate prose, or mutate state.
    arithmetic=re.sub(r"^(?:what is|what's|calculate|work out)\s+",'',k)
    arithmetic=re.sub(r'\b(?:multiplied by|divided by|times|plus|minus)\b','+',arithmetic)
    bounded_math=bool(re.fullmatch(r'[\d\s.+*/()\-]+',arithmetic) and re.search(r'\d',arithmetic) and re.search(r'[+*/\-]',arithmetic))
    d=mind.get('dialogue',{})
    literal=bool(re.match(r'^(?:say|repeat|echo|when i say)\b',k))
    if not literal and (bounded_math or k.startswith('if all ') or
        re.match(r"^(?:i want to|i would like to|i'm trying to|i am trying to|help me) (?:build|make|design|create|plan|organize|write) ",k) or
        (d.get('goal') and (re.match(r'^(?:it (?:must|should|needs to)|i need it to|keep it) ',k) or k in {'what is the plan','what are we making','summarize our plan','what did we decide'})) or
        (d.get('explanation') and k in {'why','why is that','explain your reasoning','how did you get that'}) or
        (d.get('selected_idea') and k in {'make it simpler','simplify it','what did we just decide','what did i choose','what did we decide'}) or
        re.fullmatch(r'(?:the |option |number )?(?:first|second|third|1|2|3)(?: one| option)?',k) or
        k in {'how is it going',"how's it going",'hello there','thanks, that helps','thanks that helps','thank you that helps','thanks a lot','thank you so much','bye for now','see you later','talk later'} or
        DR.SC.cue(text,session) is not None or
        any(DR.SC.wellbeing(part) for part in CE.clauses(text)) or
        (EM.feeling(text) is None and re.search(r"(?:^| and | but | because )i (?:feel|am|'m) (?:disappointed|frustrated|overwhelmed|excited|sad|worried|lonely|happy)\b",k)) or
        (d.get('feeling') and k in {'help me think through options','can you help me think through options','help me think it through'})):
        add('rules','bounded_reasoning' if bounded_math or k.startswith('if all ') else 'dialogue_skill',95,
            'bounded skill syntax or active goal',['calculation','user_premise','conversation_structure','user_declaration'])
    proposition=PC.parse(text,mind)
    definition=PC.F.definition_subject(text)
    if (session.get('environment') or data.get('default_chat')) and (proposition or any(x['subject']==(definition or '').casefold() for x in mind.get('user_descriptions',[]))):
        add('proposition','subject_description',50,'subject/predicate/polarity',['user_declaration','conversation_structure','lexical_reference','gated_source'])
    add('environment','scoped_environment',0,'explicit scope, local skill plan, or gated retrieval plan',['gated_source','lexical_reference','research_note','conversation_structure'])
    return sorted(candidates,key=lambda c:(-c['priority'],c['handler'],c['intent']))

def plan(frame, session, data, compound=True):
    frame['entities']=relationships(session,frame['acts'])
    frame['unresolved_choices']=copy.deepcopy(session.get('mind',{}).get('conversation_branches',{}).get('pending',[]))
    candidates=propose(frame,session,data)
    frame['candidates']=candidates
    winner=candidates[0]
    tied=[c for c in candidates if c['priority']==winner['priority'] and c['handler']!=winner['handler']]
    # Equal-specificity interpretations are not decided by registration order.
    planned={'version':VERSION,'phase':'before_execution','request':frame['original'],
            'resolved_request':frame['resolved'],'subject':frame['subject'],
            'intentions':copy.deepcopy(frame['acts']), 'selected':winner,
            'ambiguities':tied,'steps':[{'action':'answer_request','intent':winner['intent'],
            'allowed_authorities':winner['allowed_authorities']},
            {'action':'attach_source_details','requires':'existing reader result; never chat memory'}],
            'policy':{'chat_is_evidence':False,'hash_proves_truth':False, 'lexical_match_proves_answer':False}}
    planned['claims']=[{'act':a['type'], 'basis':('user_declaration' if a['type'] in
        {'introduce','recall_name','person','person_update','person_query','recall_topic'} else
        'system_description' if a['type'] in {'identity','abilities'} else 'route_specific'),
        'may_promote_chat_to_evidence':False} for a in frame['acts']]
    parts=CE.clauses(frame['resolved'])
    # Compose only fully recognized local skills. Never execute a partial command
    # or invent an interpretation for an unknown clause.
    identity_ack=bool(re.fullmatch(r"(?:that's me|that is me|yes that's me|yes that is me)[,; ]+(?:who are you|what is your name)[?!.]*",CM.key(frame['resolved'])))
    if compound and len(parts)>1 and winner['handler']!='dialogue' and not identity_ack:
        children=[]
        for part in parts:
            child=dict(frame,original=part,resolved=part,acts=[CE.act(part)])
            child_plan=plan(child,session,data,compound=False)
            if child_plan['ambiguities'] or child_plan['selected']['handler'] not in {'self','memory','context','rules','dialogue'}:
                planned['selected']={'handler':'clarify','intent':'unresolved_clause','priority':130,
                    'basis':'not every clause has an executable plan','allowed_authorities':['conversation_structure']}
                planned['unresolved_clause']=part
                break
            children.append(child)
        else:
            planned['children']=children
            planned['selected']={'handler':'compose','intent':'multiple_intentions',
                'priority':130,'basis':'every clause has a recognized local skill',
                'allowed_authorities':['user_declaration','system_description','conversation_structure','calculation','user_premise']}
            planned['ambiguities']=[]
            planned['steps']=[{'action':'answer_clause','request':c['resolved'],
                'allowed_authorities':c['candidates'][0]['allowed_authorities']} for c in children]
    return planned

def execute(app,data,session,frame,corpus,profile):
    before=plan(frame,session,data)
    frame['reply_plan']=copy.deepcopy(before)
    if before['selected']['handler']=='clarify':
        return M.reply('conversation','I’m not sure how to handle every part of that request. Could you separate the questions?',session.get('context'),
            'COMPOSE-CLARIFY',authority='conversation_structure',suggestions=[])
    if before['selected']['handler']=='compose':
        shadow=copy.deepcopy(session);units=[];last=None
        for child in before['children']:
            last=execute(app,data,shadow,child,corpus,profile)
            if last is None or child.get('execution_issue'):
                return M.reply('conversation','I could not resolve every part of that request. Could you separate the questions?',session.get('context'),
                    'COMPOSE-UNRESOLVED',authority='conversation_structure',suggestions=[])
            units.append({'text':last['message'],'authority':last.get('authority','conversation_structure'),
                          'sources':copy.deepcopy(last.get('sources',[])),'request':child['original']})
            # Make preceding user clauses available to the same role-aware replay
            # used across turns. These temporary turns are not persisted.
            shadow['log'].append({'payload':{'question':child['original'],'response':last}})
        shadow['log']=copy.deepcopy(session['log'])
        session.clear();session.update(shadow)
        result=M.reply('conversation','\n\n'.join(u['text'] for u in units),session.get('context'),
            'COMPOSE-PLAN',authority='separate_conversation_claims',suggestions=last.get('suggestions',[]))
        result['claim_units']=units
        return result
    if before['ambiguities']:
        names=[before['selected']['intent']]+[x['intent'] for x in before['ambiguities']]
        return M.reply('conversation','Do you mean '+ ' or '.join(x.replace('_',' ') for x in names)+'?',session.get('context'),
                       'ROUTE-CLARIFY',authority='conversation_structure',suggestions=[])
    text=frame['resolved']
    # A rejected candidate must not leave partially applied memory behind.
    shadow=copy.deepcopy(session)
    reader=lambda q:E.handle(app,data,shadow,q,corpus,profile)
    handlers={'self':lambda:SK.handle(text,shadow,app.roots()),
              'branch':lambda:CB.handle(text,shadow,reader),
              'dialogue':lambda:CE.handle(text,shadow,reader,interpretation=frame.get('dialogue_interpretation')),
              'memory':lambda:CM.handle(text,shadow),
              'context':lambda:CX.handle(text,shadow),
              'rules':lambda:DR.handle(text,shadow),
              'proposition':lambda:PC.handle(app,data,shadow,text,corpus,profile),
              'environment':lambda:E.handle(app,data,shadow,text,corpus,profile)}
    handler=before['selected']['handler']
    result=handlers[handler]()
    if result is not None:
        result.setdefault('claim_units',[{'text':result['message'],'authority':result.get('authority','legacy_skill_result'),
            'sources':copy.deepcopy(result.get('sources',[])),'granularity':'skill result; source scopes remain separate'}])
        session.clear();session.update(shadow)
    elif handler=='proposition' and PC.F.definition_subject(text):
        frame['handoff']={'from':'proposition','to':'environment','reason':'definition needs source resolution'}
        result=E.handle(app,data,session,text,corpus,profile)
    elif handler!='environment':
        # Do not try the other competing interpretations. A recognized but
        # unsupported skill asks for clarification instead of guessing a topic.
        result=M.reply('conversation','I could identify the request, but not resolve it confidently. Could you clarify what you mean?',session.get('context'),
                       'ROUTE-UNRESOLVED',authority='conversation_structure',suggestions=[])
        frame['execution_issue']='selected skill declined'
    return result
