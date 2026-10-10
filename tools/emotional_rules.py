"""Respond to explicit feelings; no diagnosis or inferred emotional profile."""
import re
from tools import social_chat as S, deterministic_mind as M, reduction as R

VERSION='emotional-rules-v1'
WORDS={'sad':'difficult','down':'difficult','upset':'difficult','lonely':'difficult',
       'angry':'frustrated','frustrated':'frustrated','annoyed':'frustrated',
       'worried':'uncertain','anxious':'uncertain','nervous':'uncertain','scared':'uncertain',
       'overwhelmed':'tired','tired':'tired','exhausted':'tired',
       'happy':'positive','excited':'positive','proud':'positive','relieved':'positive'}


def feeling(message):
    key=S.key(message)
    # Entire first-person declarations only. No third-party/quoted/hypothetical inference.
    match=re.fullmatch(r'i (?:am|feel|have been feeling) (.+?)(?: (?:today|right now))?(?: because ([^?]+))?',key)
    if not match:return None
    expression=match[1]
    negative=re.fullmatch(r'(?:not|no longer) (?:really |very |so )?('+ '|'.join(WORDS)+r')',expression)
    if negative:return {'negated':True,'words':[negative[1]]}
    words=re.split(r' (?:and|but|but also|and also) ',expression)
    words=[re.sub(r'^(?:really|very|so|a bit|quite|also) ','',w) for w in words]
    if not 1<=len(words)<=2 or any(w not in WORDS for w in words):return None
    return {'negated':False,'words':words}


def recognize(message,memory):
    key=S.key(message);state=memory.get('emotional',{})
    if key in {'no jokes','please be gentle','be gentle','be serious with me','jokes are okay','you can joke','jokes are ok'}:return 'preference'
    if state.get('no_jokes') and key in {'tell me a joke','a silly question','tell me something funny','make me laugh'}:return 'preference'
    if re.match(r'^(?:say|repeat)\b|^(?:can|could|would) you say\b|^tell me (?:a joke|a story)\b',key):return None
    if feeling(message):return 'feeling'
    if key in {'just listen','listen','i just want to vent','no advice','do not give advice',"don't give advice"}:return 'listen'
    if state.get('active'):
        if key in {'ideas','some ideas','help me think','help me think it through','what should i do','give me advice'}:return 'ideas'
        if key in S.NO|S.STOP|{'change the subject','something lighter'}:return 'stop'
        if key in {'you got that wrong','that is not how i feel',"that's not how i feel",'stop assuming'}:return 'correction'
        if key in S.YES:return 'clarify_preference'
        if not re.match(S.COMMAND,key) and not re.search(S.QUESTION,key) and '?' not in message:return 'followup'
    return None


def handle(message,memory):
    if not recognize(message,memory):return None
    key=S.key(message);cue=feeling(message)
    state=memory.setdefault('emotional',{'active':False,'style':'ask','turn':0,'no_jokes':False})
    intent=None;words=[]
    if key in {'no jokes','please be gentle','be gentle','be serious with me'}:
        state.update(no_jokes=True);intent='preference'
        options=['Okay. I’ll keep things gentle and leave the jokes out.']
    elif key in {'jokes are okay','you can joke','jokes are ok'}:
        state.update(no_jokes=False);intent='preference'
        options=['Okay; light humor is welcome again.']
    elif state.get('no_jokes') and key in {'tell me a joke','a silly question','tell me something funny','make me laugh'}:
        intent='preference';options=['You asked me to leave jokes out. Say “jokes are okay” if you want to change that.']
    elif re.match(r'^(?:say|repeat)\b|^(?:can|could|would) you say\b|^tell me (?:a joke|a story)\b',key):
        return None  # Explicit requests outrank listening acknowledgments.
    elif cue:
        words=cue['words'];state['active']=True
        if cue['negated']:
            intent='correction';options=['Thanks for clarifying. I won’t assume that feeling.']
        elif len(words)>1:
            intent='mixed';options=['You described feeling '+words[0]+' and '+words[1]+'. We can make room for both.']
        else:
            intent='acknowledge';word=words[0]
            # Explicit attribution avoids claiming an independently assessed feeling.
            options=['You said you’re feeling '+word+'. Thanks for telling me.',
                     'Feeling '+word+' is what you described; I’m listening.']
        if state.get('style')=='listen':options=[o+' Take your time.' for o in options]
        else:options=[o+' Would you like me to listen, or help you think through some ideas?' for o in options]
    elif key in {'just listen','listen','i just want to vent','no advice','do not give advice',"don't give advice"}:
        state.update(active=True,style='listen');intent='listen'
        options=['I’ll listen. Say as much or as little as you want; no advice or questions.']
    elif state.get('active') and key in {'ideas','some ideas','help me think','help me think it through','what should i do','give me advice'}:
        state.update(style='ideas');intent='ideas'
        options=['Let’s start with what you want to be different. Would it help to name one small thing you can influence?',
                 'We can think through options together. What happened, and what outcome would you prefer?']
    elif state.get('active') and key in S.NO|S.STOP|{'change the subject','something lighter'}:
        state.update(active=False,style='ask');intent='stop'
        options=['Okay. We can leave that there and talk about something else.']
    elif state.get('active') and key in {'you got that wrong','that is not how i feel',"that's not how i feel",'stop assuming'}:
        state.update(style='ask');intent='correction'
        options=['Thanks for correcting me. I shouldn’t assume how you feel. How would you describe it?']
    elif state.get('active') and key in S.YES:
        intent='clarify_preference'
        options=['Would you prefer listening or ideas? Either is okay.'] if state.get('style')!='listen' else ['Go ahead. Take your time.']
    elif state.get('active') and not re.match(S.COMMAND,key) and not re.search(S.QUESTION,key) and '?' not in message:
        if state.get('style')=='listen':
            intent='listen';options=['I’m following. Take your time.','I’m listening. There’s no rush.']
        elif state.get('style')=='ideas':
            intent='ideas';options=['What part would you most like to change? We can start there.', 'Which option feels workable to you? We can take it one step at a time.']
        else:
            intent='followup';options=['I’m following. Would you like me to listen, or work through ideas with you?']
    else:
        if key not in {'thanks','thank you'}:state['active']=False
        return None
    state['turn']+=1
    body,trace=R.wording(options,'emotional_'+intent,state['turn'])
    memory.pop('chat_discourse',None)
    return M.reply('conversation',body,None,'EMOTION-'+intent.upper(),authority='conversation_structure',
                   suggestions=['just listen','ideas','change the subject'] if state['active'] else ['can we talk','tell me a story'],
                   response_structure={'intent':'casual_emotional_'+intent,'engine':VERSION,'factual_claims':False,
                                       'expressed_words':words,'assessment':False,'wording_determination':trace,
                                       'style':state['style'],'mplpb_supported':False})
