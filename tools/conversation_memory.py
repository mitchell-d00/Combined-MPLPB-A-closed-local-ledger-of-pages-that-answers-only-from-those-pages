"""Recall user-declared names and earlier turns; conversation is not page evidence."""
import re
from tools import deterministic_mind as M
from tools.chat_phrasing import memory_question

VERSION='conversation-memory-v4'
FORGET={'forget my name','do not remember my name',"don't remember my name",'stop using my name'}
NAME_QUESTIONS={'what is my name',"what's my name",'do you remember my name','who am i','what do you call me'}
STATES={'sad','happy','tired','bored','angry','worried','anxious','upset','lonely','hungry','sorry','fine','okay','ok','good','great','excited','scared','stressed','depressed','sick','confused','here','back','ready','done','listening','not','a','an'}


def key(text):return re.sub(r'\s+',' ',text.replace('’',"'")).strip(' .!?').casefold()


def introduction(text):
    text=re.sub(r'\s+',' ',text.replace('’',"'")).strip(' .!?')
    text=re.split(r'[.!?;]+\s*|,?\s+and\s+(?=(?:how|who|what)\b)',text, maxsplit=1,flags=re.I)[0]
    text=re.sub(r'^(?:hi|hello|hey)[,! ]+', '',text,flags=re.I)
    text=re.sub(r'^(?:actually|no)[, ]+', '',text,flags=re.I)
    match=re.fullmatch(r"(?:my name is|call me|please call me|remember my name is|i(?: am|'m)) ([^,;!?]{1,64}?)(?:[,;]? (?:and )?(?:who are you|what are you|what(?: is|'s) your name))?",text,re.I)
    if not match:return None
    name=match[1].strip()
    words=name.split()
    if len(words)>4 or not all(re.fullmatch(r"[^\W\d_]+(?:[-'][^\W\d_]+)*",w,re.UNICODE) for w in words):return None
    explicit=bool(re.match(r'^(?:my name is|call me|please call me|remember my name is) ',text,re.I))
    initial=len(name)==1 and name.isalpha() and name.isupper()
    if not explicit and not initial and any(w.casefold() in STATES|{'and','but','because','from','feeling','doing','the'} for w in words):return None
    # Bare 'I am ...' can be a state or occupation. Explicit name markers are
    # stronger; greeting + I am is a common introduction, never verified identity.
    bare=bool(re.match(r"^i(?: am|'m) ",text,re.I))
    if bare and not initial and re.fullmatch(r"[a-z][a-z '-]{0,79}",words[0].casefold()):
        from tools import reference_resources as R
        _,senses,_=R.lookup_forms(words[0].casefold())
        if any(s['part_of_speech'] in {'a','s','v','r'} for s in senses):return None
    return ' '.join(w[:1].upper()+w[1:] if w.islower() else w for w in words)


def user_turns(session):
    for number,turn in enumerate(session.get('log',[]),1):
        question=turn.get('payload',{}).get('question')
        if isinstance(question,str):yield number,question


def name_from_chat(session):
    name=None;at=None
    for number,text in user_turns(session):
        if key(text) in FORGET:name=None;at=number
        else:
            found=introduction(text)
            if found:name=found;at=number
    return name,at


def reply(body,session,refs=None,**extra):
    return M.reply('conversation',body,session.get('context'),'CHAT-MEMORY',authority='user_declaration',
                   response_structure={'intent':'chat_memory','factual_claims':False,'mplpb_supported':False,
                                       'chat_references':refs or [],'identity_verified':False,'version':VERSION},**extra)


def handle(message,session):
    command=memory_question(message)
    # Only scan the current conversation; assistant prose cannot name the user.
    name,at=name_from_chat(session)
    found=introduction(message)
    if command in FORGET:
        return reply('Okay; I won’t use your name. Your existing transcript is unchanged.',session)
    if found:
        return reply('Hi, '+found+'! I’m MPLPB, your little monster 😈. What’s on your mind?',session,
                     [{'turn':len(session.get('log',[]))+1,'basis':'user introduction'}],
                     suggestions=['What can you do?','What is my name?','Talk about my day'])
    if command in NAME_QUESTIONS:
        return reply(('You asked me to call you '+name+'.' if name else 'What would you like me to call you?'),session,
                     [{'turn':at,'basis':'user introduction'}] if name else [])
    identity=re.fullmatch(r"(?:(?:that's me|that is me|yes that's me|yes that is me)[,; ]+)?(?:who are you|what is your name)",command)
    # Keep existing unqualified self-identification routes when no name is known.
    if identity and (name or command.startswith(('that','yes that'))):
        return reply(('Hi, '+name+'! ' if name else 'Hi! ')+'I’m MPLPB, the little monster 😈. I use rules, our conversation and available references to construct replies.',session,
                     [{'turn':at,'basis':'user introduction'}] if name else [],suggestions=['What can you do?','How do your modes work?'])
    if name and command in {'hi','hello','hey','hi again','hello again'}:
        return reply('Hi, '+name+'! What’s on your mind?',session,[{'turn':at,'basis':'user introduction'}])
    query=re.fullmatch(r'(?:what did (?:i|we) (?:say|tell you|mention|discuss)|what have (?:i|we) (?:said|mentioned|discussed)|do you remember what i said) about (.{1,120})',command)
    if not query:return None
    subject=query[1]
    def tokens(text):
        return {w[:-1] if len(w)>3 and w.endswith('s') and not w.endswith('ss') else w for w in re.findall(r'[^\W_]+',text.casefold()) if w not in {'the','a','an','my','our'}}
    wanted=tokens(subject)
    hits=[]
    for number,text in user_turns(session):
        # Recall actual statements, not earlier recall requests or executable commands.
        if re.match(r'^(?:what|do you remember|search|find|import|say|repeat)\b',key(text)):continue
        if wanted and wanted <= tokens(text):hits.append({'turn':number,'quote':text})
    if not hits:return reply('I don’t see an earlier message from you about '+subject+' in this conversation. What would you like me to know about it?',session)
    hits=hits[-3:]
    body='About '+subject+', you told me:\n\n'+'\n'.join('“'+h['quote']+'” (turn '+str(h['turn'])+')' for h in hits)
    return reply(body,session,hits,suggestions=['Tell me about '+subject,'Explore an idea about '+subject])
