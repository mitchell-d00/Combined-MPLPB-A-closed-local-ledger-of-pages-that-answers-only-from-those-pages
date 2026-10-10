"""Shared discourse interpretation before routing; never grants evidence authority."""
import copy
import re
from tools import conversation_engine as CE, conversation_branches as B, chat_language_graph as LG
from tools.chat_phrasing import conversational_request
VERSION='conversation-continuity-v2'

def prepare(message,session):
    text=CE.normalize(message);k=B.key(text)
    state=session.setdefault('mind',{}).setdefault('continuity',{})
    frame={'version':VERSION,'original':message,'resolved':text,'acts':[CE.act(c) for c in CE.clauses(text)],
           'subject':state.get('subject'),'correction':False,'reference':None}
    text, lead_in = conversational_request(text)
    if lead_in:
        k = B.key(text)
        frame['normalization'] = 'social_lead_in'
        frame['social_lead_in'] = lead_in
    # Closed typo vocabulary for conversational controls, never names or source terms.
    typo={'helo':'hello','helllo':'hello','thnaks':'thanks','tell me moer':'tell me more'}
    if k in typo:text=typo[k];k=text;frame['normalization']='control_typo'
    choices=state.get('choices',[])
    selected=None
    if k in {'the other one','other one','the other','the second one','second one','the first one','first one'} and choices:
        if 'other' in k:
            remaining=[c for c in choices if c['id']!=state.get('selected')]
            if len(remaining)==1:selected=remaining[0]
            else:
                session['mind'].setdefault('conversation_branches',{})['pending']=copy.deepcopy(choices)
                text='what is that';frame['reference']=k
        else:selected=choices[min(1 if 'second' in k else 0,len(choices)-1)]
        if selected:
            session['mind'].setdefault('conversation_branches',{})['pending']=copy.deepcopy(choices)
            text=selected['label'];frame['reference']=k
    correction=re.fullmatch(r"(?:no[, ]+i meant|no[, ]+i mean|i meant|i mean) (.{1,120})",text,re.I)
    if correction and state.get('subject'):
        target=correction[1].strip(' .?!')
        selected=next((c for c in choices if B.key(c['label'])==B.key(target)),None)
        text=selected['label'] if selected else 'Tell me about '+target
        if selected:session['mind'].setdefault('conversation_branches',{})['pending']=copy.deepcopy(choices)
        frame['correction']=True;frame['subject']=target
    if k in {'that','what is that',"what's that",'explain that','tell me more'}:
        frame['reference']=k
        if k=='that':text='what is that'
        if choices and not state.get('selected'):
            session['mind'].setdefault('conversation_branches',{})['pending']=copy.deepcopy(choices)
        elif state.get('branch'):
            session['mind'].setdefault('conversation_branches',{})['active']=copy.deepcopy(state['branch'])
    graph=LG.interpret(text)
    branch_state=session['mind'].get('conversation_branches',{})
    if graph and not (graph['subject']=='identity' and (branch_state.get('active') or branch_state.get('pending'))):
        frame['language_graph']=graph
        text=graph['command']
    frame['resolved']=text
    frame['original_acts']=frame['acts']
    frame['acts']=[CE.act(c) for c in CE.clauses(text)]
    return frame

def finish(frame,result,session):
    state=session['mind'].setdefault('continuity',{})
    choices=result.get('response_structure',{}).get('branch_candidates')
    branch=result.get('conversation_branch',{}).get('selected')
    if choices:state['choices']=copy.deepcopy(choices);state.pop('selected',None)
    if branch:
        state.update(subject=branch['label'],selected=branch['id'],branch=copy.deepcopy(branch))
    elif frame['correction']:
        state['subject']=frame['subject'];state.pop('branch',None);state.pop('selected',None);state.pop('choices',None)
    elif result.get('context'):
        state['subject']=result['context']['title']
    # Preserve pending questions over social interruptions; bound all history.
    if choices:
        state['unanswered_question']=result['message']
    elif branch:state.pop('unanswered_question',None)
    substantive=any(a['type'] not in {'greet','wellbeing'} for a in frame['acts'])
    if substantive and not choices and not branch and not frame['reference'] and not frame['correction'] and B.key(frame['original']) not in {'thanks','thank you','thnaks','chat mode','serious mode','just chat'}:
        state.pop('choices',None);state.pop('branch',None);state.pop('selected',None);state.pop('unanswered_question',None)
        branches=session['mind'].get('conversation_branches',{})
        branches.pop('pending',None);branches.pop('active',None)
    state['recent']=(state.get('recent',[])+[{'request':frame['original'],'subject':state.get('subject'),'authority':result.get('authority'),'kind':result['kind']}])[-16:]
    result['interpretation']=frame
    # Keep the pre-execution decision immutable; realized output is separate.
    result['reply_plan']=copy.deepcopy(frame.get('reply_plan',{}))
    result['reply_plan']['subplans']={name:copy.deepcopy(result[name]) for name in ('skill_plan','source_plan','retrieval_plan') if name in result}
    result['reply_plan']['sources']=copy.deepcopy(result.get('sources',[]))
    result['realization']={'message':result['message'],'authority':result.get('authority'),
        'sources':copy.deepcopy(result.get('sources',[])),
        'claim_units':copy.deepcopy(result.get('claim_units',[])),
        'scope_results':copy.deepcopy(result.get('scope_results',[])),
        'chat_is_evidence':False}
    return result
