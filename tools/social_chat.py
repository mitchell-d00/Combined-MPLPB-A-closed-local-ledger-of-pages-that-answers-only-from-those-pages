"""Local conversational turn-taking. No model, inferred world facts or network."""
import re
from tools import deterministic_mind as M

VERSION='social-turns-v1'
YES={'yes','yes please','sure','sure thing','yeah','yep','ok','okay','please','go on',"let's talk",'lets talk','i do'}
NO={'no','no thanks','not now','not really',"i'd rather not",'id rather not','maybe later'}
STOP={'stop chatting','stop asking','leave it','never mind','nevermind','goodbye','bye','a little quiet','quiet please'}
COMMAND=r'^(?:topic|search|find|import|define|dictionary|synonyms|thesaurus|grammar|language|reference|remember|memory|forget|clear|summarize|explain|compare|relate|show|guide|next|back|finish|teach)\b'
QUESTION=r'\b(?:what|why|who|where|when|how|which)\b|^(?:is|are|can|could|do|does|did|will|would|should)\b'


def key(message):
    text=message.casefold().replace('’',"'")
    text=re.sub(r"\b(?:i've|ive|iv)\b",'i have',text)
    text=re.sub(r"\b(?:i'm|im)\b",'i am',text)
    return re.sub(r'\s+',' ',text).strip(' ?!.,')


def opening(command):
    # Full constructions avoid treating "not a bad day" or hypothetical stories
    # as disclosures of a bad day. No emotional classification is persisted as fact.
    prefix=r'(?:(?:i have |i |it has |it\'s |its )?(?:had|been) (?:a |such a |a really )?|(?:my|the) (?:day|morning|afternoon|evening) (?:was|is) (?:really )?|(?:a |such a )?)'
    if re.fullmatch(prefix+r'(?:bad|rough|awful|terrible|crummy|stressful|hard|difficult)(?: day| morning| afternoon| evening)?(?: today| at work)?',command):return 'rough'
    if re.fullmatch(r'(?:today|my day) (?:sucked|was awful|was terrible|was rough)',command):return 'rough'
    if re.fullmatch(prefix+r'(?:good|great|lovely|wonderful|amazing)(?: day| morning| afternoon| evening)?(?: today)?',command):return 'good'
    if re.fullmatch(r'i (?:am|feel|have been feeling) (?:really |so |a bit )?(?:sad|down|upset|frustrated|stressed|overwhelmed|lonely)',command):return 'rough'
    if re.fullmatch(r'i (?:am|feel) (?:really |so )?(?:tired|exhausted|worn out)',command):return 'tired'
    return None


def candidate(message,memory):
    command=key(message)
    if opening(command):return True
    if command in {'just listen','i just want to vent','can i vent','can we talk',"let's just talk",'lets just talk','change the subject','something lighter','distract me'}:return True
    state=memory.get('social',{})
    if not state.get('active'):return False
    if command in YES|NO|STOP|{'thanks','thank you','that helped','what do you mean','what do you mean by that'}:return True
    if re.match(COMMAND,command) or re.search(QUESTION,command) or '?' in message:return False
    if command.startswith(('tell me ','how ','who ','what ','why ')):return False
    if command in {'more','continue','keep it short','give me more detail','keep chatting','stay casual','hello','hi','hey','nothing','a silly question','small talk','just chatting'}:return False
    return state.get('stage') in {'invitation','story','followup','listen'}


def tone(command):
    # Negation suppresses interpretation of cue words rather than guessing polarity.
    if re.search(r"\b(?:not|never|no|nothing|wasn't|wasnt|isn't|isnt|didn't|didnt)\b",command):return 'neutral'
    if re.search(r'\b(?:yelled|shouted|argued|argument|frustrating|annoying|ignored|interrupted|unfair)\b',command):return 'frustrated'
    if re.search(r'\b(?:exhausted|tired|drained|nonstop|overloaded|overtime)\b',command):return 'tired'
    if re.search(r'\b(?:sad|upset|disappointed|let down|missed out)\b',command):return 'sad'
    if re.search(r'\b(?:happy|excited|great|wonderful|fun|promoted|celebrate)\b',command):return 'good'
    return 'neutral'


def handle(message,context,memory):
    if not candidate(message,memory):return None
    command=key(message);state=memory.setdefault('social',{'active':False,'stage':'idle','turns':0,'style':'chat'})
    state['turns']=state.get('turns',0)+1
    intent='followup';suggestions=['just listen','change the subject']
    opener=opening(command)
    if command in STOP:
        state.update(active=False,stage='idle');body='No problem. We can leave it there. You can pick this up whenever you like.';intent='stop'
        suggestions=['just chatting','show my MPLPB']
    elif command in NO:
        state.update(active=False,stage='idle');body='That’s okay. No need to explain. We can talk about something else or leave it for now.';intent='decline'
        suggestions=['a silly question','a little quiet']
    elif command in {'change the subject','something lighter','distract me'}:
        state.update(active=True,stage='story',style='light')
        body='Sure, a change of subject. If you could have an entirely ordinary superpower—like always finding your keys—what would you choose?';intent='light'
    elif command in {'just listen','i just want to vent','can i vent'}:
        state.update(active=True,stage='listen',style='listen')
        body='Of course. Go ahead—I’ll keep my replies short and leave room for you to talk.';intent='listen'
        suggestions=['change the subject','stop chatting']
    elif command in {'can we talk',"let's just talk",'lets just talk'}:
        state.update(active=True,stage='story',style='chat');body='Sure. Tell me what’s on your mind.';intent='start'
    elif opener:
        state.update(active=True,stage='invitation',style='chat')
        body={'rough':'I’m sorry it’s been rough. Want to talk about it?',
              'good':'That sounds like a good day. Want to tell me about it?',
              'tired':'Sounds like you’re worn out. Want to talk about your day, or keep things light?'}[opener]
        intent='invitation';suggestions=['sure','not now','something lighter']
    elif command in YES:
        state.update(active=True,stage='story')
        body='Okay, tell me about it. What happened?' if state.get('style')!='listen' else 'Go ahead. Take your time.'
        intent='accept';suggestions=['just listen','change the subject']
    elif command in {'what do you mean','what do you mean by that'}:
        body='I meant you can tell me more if you want to. You don’t need to explain anything you’d rather keep to yourself.';intent='clarify'
    elif command in {'thanks','thank you','that helped'}:
        state.update(active=False,stage='idle');body='You’re welcome. We can keep talking or leave it there—your choice.';intent='acknowledge'
        suggestions=['can we talk','something lighter']
    else:
        previous=state.get('last_reply','')
        state.update(active=True,stage='listen' if state.get('style')=='listen' else 'followup')
        if state.get('style')=='listen':
            options=('I’m following. Take your time.','Go on, if you want to.','I’m listening. There’s no rush.','You don’t have to tidy it up—say it however it comes.')
        else:
            reactions={
                'frustrated':('That sounds frustrating.','Oof, that sounds unpleasant.'),
                'tired':('That sounds exhausting.','Sounds like you’ve had a lot going on.'),
                'sad':('That sounds disappointing.','I’m sorry—that sounds upsetting.'),
                'good':('That sounds like a bright spot.','Sounds like that meant a lot to you.'),
                'neutral':('I’m following.','Okay, tell me more.','Thanks for telling me.')}
            category=tone(command);reactions=reactions[category]
            questions=('What happened next?','What part is sticking with you?','Want to say a little more about that?')
            options=tuple(a+' '+q for a in reactions for q in questions)
        available=[s for s in options if s!=previous]
        body=available[(state['turns']-1)%len(available)]
    state['last_reply']=body
    memory['casual_active']=True
    return M.reply('smalltalk',body,context,'SOCIAL-'+intent.upper(),authority='conversation_structure',
                   suggestions=suggestions,response_structure={'intent':'social_'+intent,'stage':state['stage'],
                   'factual_claims':False,'automatic_topic_switch':False,'engine':VERSION})
