"""Bounded dialogue acts and explicit-premise reasoning; never corpus evidence.

No model, sampling, eval, or source mutation. Unrecognized turns fall through to
existing source readers. Conversation state is session-local and serializable.
"""
import ast
import operator
import re
from fractions import Fraction
from tools import deterministic_mind as M, conversation_memory as CM, emotional_rules as EM

VERSION='dialogue-rules-v1'

def reply(session,body,intent,**details):
    suggestions=details.pop('suggestions',[])
    return M.reply('conversation',body,session.get('context'),'DIALOGUE-'+intent.upper(),
        authority='user_declaration' if intent=='premise_reasoning' else 'conversation_structure',
        suggestions=suggestions,response_structure={'intent':'casual_'+intent,'factual_claims':False,
        'mplpb_supported':False,'version':VERSION,**details})

def arithmetic(text):
    expression=re.sub(r'^(?:what is|what\'s|calculate|work out)\s+','',text,flags=re.I).strip(' ?')
    for word,symbol in [('multiplied by','*'),('divided by','/'),('times','*'),('plus','+'),('minus','-')]:
        expression=re.sub(r'\b'+word+r'\b',symbol,expression,flags=re.I)
    if len(expression)>160 or not re.fullmatch(r'[\d\s.+*/()\-]+',expression) or not re.search(r'\d',expression):return None
    if not re.search(r'[+*/\-]',expression):return None
    try:
        tree=ast.parse(expression,mode='eval')
        if len(list(ast.walk(tree)))>48:raise ValueError('expression too large')
        def value(node):
            if isinstance(node,ast.Constant) and type(node.value) in (int,float):
                result=Fraction(str(node.value))
            elif isinstance(node,ast.UnaryOp) and isinstance(node.op,(ast.UAdd,ast.USub)):
                result=value(node.operand)*(-1 if isinstance(node.op,ast.USub) else 1)
            elif isinstance(node,ast.BinOp) and type(node.op) in {ast.Add,ast.Sub,ast.Mult,ast.Div}:
                result={ast.Add:operator.add,ast.Sub:operator.sub,ast.Mult:operator.mul,ast.Div:operator.truediv}[type(node.op)](value(node.left),value(node.right))
            else:raise ValueError('unsupported operator')
            if abs(result.numerator)>10**18 or result.denominator>10**18:raise ValueError('number too large')
            return result
        result=value(tree.body)
        return expression+' = '+str(result)+'.',{'expression':expression,'result':str(result),'rule':'rational arithmetic; + - * / and parentheses'}
    except ZeroDivisionError:return 'Division by zero is undefined. Want to change the divisor?',{'expression':expression,'error':'division by zero'}
    except (ValueError,SyntaxError,OverflowError):return 'I can calculate bounded numbers with +, −, ×, ÷ and parentheses. That expression is outside those rules.',{'expression':expression,'error':'outside bounded grammar'}

def premise(text):
    # Controlled, explicit syllogism. Symbols have no outside-world meaning.
    atom=r'[a-z][a-z -]{0,45}?'
    match=re.fullmatch(r'if all ('+atom+r') are ('+atom+r') and ('+atom+r') is (?:a |an )?('+atom+r'),? (?:then )?is \3 (?:a |an )?('+atom+r')\??',text,re.I)
    if not match:return None
    group,property_,entity,membership,asked=[x.strip() for x in match.groups()]
    g,p,m,q=[s.casefold() for s in (group,property_,membership,asked)]
    premises=['All '+group+' are '+property_,entity+' is '+membership]
    if g in {m,m+'s'} and q==p:
        body='Yes, under your premises, '+entity+' is '+property_+'. Every '+membership+' has that property, and you placed '+entity+' in that group.'
        conclusion=True;rule='universal instantiation'
    else:
        body='That does not follow from those premises. Being '+membership+' does not by itself establish the requested conclusion about '+entity+'. We would need another premise.'
        conclusion=None;rule='no converse or missing premise'
    return body,{'premises':premises,'conclusion':conclusion,'rule':rule,'premises_verified':False}

def handle(message,session):
    text=re.sub(r'\s+',' ',message.replace('’',"'")).strip()
    key=text.casefold().strip(' .!?')
    memory=session.setdefault('mind',{})
    state=memory.setdefault('dialogue',{})
    # Only complete bounded numeric/premise grammar can preempt source readers.
    calculated=arithmetic(text)
    if calculated:
        body,trace=calculated;state['explanation']=body+' I evaluated the arithmetic expression using exact fractions.'
        return reply(session,body,'calculation',calculation=trace)
    reasoned=premise(text)
    if reasoned:
        body,trace=reasoned;state['explanation']=body+' These are your hypothetical premises, not facts checked against MPLPB.'
        return reply(session,body,'premise_reasoning',proof=trace,suggestions=['Why?'])
    if key in {'why','why is that','explain your reasoning','how did you get that'} and state.get('explanation'):
        return reply(session,state.pop('explanation'),'premise_explanation')
    state.pop('explanation',None)
    # Multi-act social turns: independently recognize every clause, then compose.
    clauses=re.split(r'[.!?;]+\s*|,?\s+and\s+(?=(?:how|who|what)\b)',text)
    clauses=[c.strip(' ,') for c in clauses if c.strip(' ,')]
    acts=[];name=None
    for clause in clauses:
        normalized=CM.key(clause)
        found=CM.introduction(clause)
        if found:name=found;acts.append('introduce')
        elif normalized in {'how are you','how are you doing','how is it going',"how's it going"}:acts.append('wellbeing')
        elif normalized in {'hi','hey','hello','so hi','hi there','hello there'}:acts.append('greet')
        else:break
    else:
        if acts and (len(acts)>1 or 'wellbeing' in acts or key in {'so hi','hi there','hello there'}):
            known=name or CM.name_from_chat(session)[0]
            body=('Hi, '+known+'!' if known else 'Hi!')
            if 'introduce' in acts:body+=' I’m MPLPB, your little monster 😈.'
            if 'wellbeing' in acts:body+=' Ready to chat and explore ideas with you.'
            body+=' What’s on your mind?'
            return reply(session,body,'greeting',acts=acts,suggestions=['What can you do?','Help me brainstorm'])
    if key in {'thanks, that helps','thanks that helps','thank you that helps','thanks a lot','thank you so much'}:
        return reply(session,'You’re welcome! We can keep going whenever you like.','acknowledgment')
    if key in {'bye for now','see you later','talk later'}:
        return reply(session,'See you later'+(', '+CM.name_from_chat(session)[0] if CM.name_from_chat(session)[0] else '')+'!','farewell')
    # Goal and constraint slots apply to arbitrary user-supplied projects.
    goal=re.fullmatch(r"(?:i want to|i would like to|i'm trying to|i am trying to|help me) (build|make|design|create|plan|organize|write) (.{1,160})",key)
    if goal:
        action,subject=goal.groups()
        state['goal']={'action':action,'subject':subject,'constraints':[]}
        return reply(session,'Let’s work on '+subject+'. Who is it for, and what should it do? We can start small and build from there.','goal',subject=subject,suggestions=['Keep it simple','Help me brainstorm '+subject])
    constraint=re.fullmatch(r"(?:it (?:must|should|needs to)|i need it to|keep it) (.{1,120})",key)
    if constraint and state.get('goal'):
        goal=state['goal'];goal['constraints']=(goal['constraints']+[constraint[1]])[-8:]
        body='For '+goal['subject']+', I’ll keep this requirement in view: '+constraint[1]+'. What is the one feature you most want to include?'
        return reply(session,body,'goal',subject=goal['subject'],constraints=list(goal['constraints']))
    if state.get('goal') and key in {'what is the plan','what are we making','summarize our plan','what did we decide'}:
        goal=state['goal']
        body='Your goal is to '+goal['action']+' '+goal['subject']+'.'
        if goal['constraints']:body+=' Your requirements: '+'; '.join(goal['constraints'])+'.'
        body+=' Next, choose one feature and make a small example to try.'
        return reply(session,body,'goal',subject=goal['subject'],constraints=list(goal['constraints']))
    # Recover the pending choice from the actual last assistant response.
    prior=(session.get('log') or [{}])[-1].get('payload',{}).get('response',{})
    choices=re.findall(r'^\d+\. (.+)$',prior.get('message',''),re.M)
    selected=re.fullmatch(r'(?:the |option |number )?(first|second|third|1|2|3)(?: one| option)?',key)
    if selected and choices:
        number={'first':0,'second':1,'third':2,'1':0,'2':1,'3':2}[selected[1]]
        if number<len(choices):
            choice=choices[number];state['selected_idea']=choice
            subject=memory.get('idea_chat',{}).get('subject','your idea')
            body='Let’s develop that direction for '+subject+': '+choice+'\n\nStart with one sketch or short example. What would you keep, and what would you change?'
            return reply(session,body,'idea_choice',subject=subject,selection=number+1,suggestions=['Make it simpler','What did we just decide?'])
    if state.get('selected_idea') and key in {'make it simpler','simplify it','what did we just decide','what did i choose','what did we decide'}:
        choice=state['selected_idea']
        body=('You chose this direction: '+choice+' We haven’t settled the details yet.' if 'decide' in key or 'choose' in key else 'Keep just one part of this idea: '+choice+' Make a small example first; leave the extra features for later.')
        return reply(session,body,'idea_choice',selection_basis='earlier user choice')
    # Emotion-bearing clauses, without interpreting quoted or third-party feelings.
    emotional=re.search(r"(?:^| and | but | because )i (?:feel|am|'m) (disappointed|frustrated|overwhelmed|excited|sad|worried|lonely|happy)(?:\b)(.*)$",key)
    if emotional and EM.feeling(message) is None and not key.startswith(('say ','repeat ','if ','suppose ','what if ')):
        emotion=emotional[1];memory.setdefault('emotional',{'active':False,'style':'ask','turn':0,'no_jokes':False}).update(active=True)
        event=re.split(r' and i | but i ',text,flags=re.I)[0] if not key.startswith('i ') else ''
        state['feeling']=emotion;state['event']=event
        positive=emotion in {'excited','happy'}
        body=('That sounds like something you’re enjoying.' if positive else 'That sounds hard'+('; you said “'+event+'”' if event else '')+'.')
        if memory['emotional'].get('style')=='listen':body+=' I’m listening; take your time.'
        else:body+=' Would you like to talk it through, or work on a next step?'
        return reply(session,body,'emotional_context',expressed_feeling=emotion,assessment=False,suggestions=['Just listen','Help me think through options'])
    if state.get('feeling') and key in {'help me think through options','can you help me think through options','help me think it through'}:
        memory.setdefault('emotional',{})['style']='ideas'
        return reply(session,'We can break it down together: what happened, what you can change, and what you want next. Which part feels most useful to start with?','emotional_options',suggestions=['What happened','What I can change','What I want next'])
    return None
