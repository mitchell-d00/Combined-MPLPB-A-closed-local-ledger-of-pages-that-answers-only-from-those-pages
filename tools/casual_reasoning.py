"""Bounded conversational intent rules and discourse; not ledger evidence."""
import re
from tools import deterministic_mind as M
from tools import reduction as R

VERSION='casual-reasoning-v2'
NOTICE='Deterministic chat; not MPLPB-supported.'


def normalize(message):
    key=message.casefold().replace('’',"'")
    for pattern,replacement in ((r"\b(?:aren't|arent|arnt|arrnt)\b",'are not'),
                                (r"\b(?:you're|youre)\b",'you are'),
                                (r"\b(?:don't|dont)\b",'do not'),
                                (r"\b(?:what's|whats)\b",'what is')):
        key=re.sub(pattern,replacement,key)
    key=re.sub(r'\s+',' ',key).strip(' ?!.,')
    return re.sub(r'^(?:(?:so|okay|ok|well|hey)[, ]+)+','',key)


def respond(message,memory):
    key=normalize(message)
    state=memory.setdefault('chat_discourse',{'turn':0})
    state['turn']+=1
    state.pop('followup_of',None)
    echo=re.fullmatch(r"(?:please\s+)?(?:(?:can|could|would) you\s+)?(?:say( exactly| only)?\s+|repeat after me[: ]+|repeat\s+)(.+)",message.strip(),re.I|re.S)
    if state.get('topic')=='echo' and key in {'again','say it again','repeat it'}:
        echo=None
    if echo:
        target=echo[2].strip()
        if re.match(r'^(?:please\s+)?(?:can|could|would) you\b',message.strip(),re.I):
            target=target.rstrip('?').rstrip()
        exact=bool(echo[1]) or 'repeat after me' in message.casefold()
        if len(target)>300:
            return M.reply('conversation','Give me a word or a short phrase up to 300 characters to repeat.',None,'CASUAL-ECHO-LIMIT',authority='conversation_structure')
        state.update(topic='echo',echo=target,echo_exact=exact)
        body=target
        if not exact:
            if target.casefold().strip(' .!')=='potato':
                body+='\n\n'+('Why potato? Have I just been promoted to a spudsperson?','Potato delivered. What’s the occasion; a tiny vegetable roll call?')[(state['turn']-1)%2]
            else:
                body+='\n\n'+('What made you pick that?','There you go. Is there a story behind that one?')[(state['turn']-1)%2]
        return M.reply('conversation',body,None,'CASUAL-ECHO',authority='conversation_structure',
                       suggestions=['again','just because','say banana'],
                       response_structure={'intent':'casual_echo','factual_claims':False,'mplpb_supported':False,'engine':VERSION,'quoted_user_text':target,'execute_text':False})
    if state.get('topic')=='echo' and key in {'again','say it again','repeat it','why','why not','just because','because i asked','because i said so','for fun'}:
        body=state['echo'] if key in {'again','say it again','repeat it'} else ('Fair enough. Sometimes a word can just be a word. Want to pick another?' if key not in {'why','why not'} else 'You asked me to say it; I was just playing along. No hidden agenda.')
        return M.reply('conversation',body,None,'CASUAL-ECHO-FOLLOWUP',authority='conversation_structure',
                       suggestions=['say potato','say banana','can we talk'],
                       response_structure={'intent':'casual_echo_followup','factual_claims':False,'mplpb_supported':False,'engine':VERSION})
    state.pop('echo',None);state.pop('echo_exact',None)
    topic=None
    if re.fullmatch(r'(?:hi|hello|hey)(?: there| again)?',key):topic='greeting'
    elif re.fullmatch(r'(?:you are (?:not )?(?:an? )?(?:ai|llm|language model)|are you (?:not )?(?:an? )?(?:ai|llm|language model)|you are (?:not )?(?:an? )?(?:ai|llm|language model) (?:then|right)|why (?:are|are not) you (?:an? )?(?:ai|llm))',key):topic='identity'
    elif key in {'what are you','who are you','what kind of ai are you','are you artificial intelligence'}:topic='identity'
    elif re.fullmatch(r'(?:what (?:are|is)|explain|tell me|tell me about|show me) (?:the |your )?(?:rules|rule|construct rules|construction rules|response rules)(?: you (?:use|follow))?',key):topic='rules'
    elif key in {'how do you think','how do you work','how does your mind work','how do you reply','how do you make replies','can you think'}:topic='construction'
    elif key in {'do you have feelings','are you alive','are you conscious','are you a person'}:topic='experience'
    elif key in {'can we talk','can you chat','can you talk to me','what can we talk about','what should we talk about','what do you want to talk about'}:topic='conversation'
    elif key in {"i'm bored",'i am bored','im bored','any ideas','what can i do for fun','help me think of something to do'}:topic='ideas'
    elif key in {'and you','what about you','how about you'}:topic='experience'
    elif key in {'tell me a story','make up a story','tell me something imaginary'}:topic='story'
    elif key in {'is that true','is this verified','where is your evidence','is that from a mplpb','is this from a mplpb','are these facts'}:topic='support'
    elif key in {'why','how','how so','why is that','why not','tell me more','go on','what does that mean','explain that','what do you mean','what do you mean by that'}:
        previous=state.get('topic')
        topic={'identity':'construction','construction':'rules','rules':'rules','experience':'experience','support':'support','conversation':'conversation','greeting':'conversation','ideas':'ideas','story':'story'}.get(previous)
        if topic:state['followup_of']=previous
    else:
        # Do not attach a later "why?" to an old subject after an unrelated turn.
        state.pop('topic',None);state.pop('followup_of',None)
        return None
    if topic is None:
        return None
    opening={
        'ideas':['We could invent a tiny story, try a silly question, or talk about something you enjoy.'],
        'story':['Here’s a little made-up story:'],
        'identity':['I’m your rule-based little monster; I don’t run an LLM.', 'Right; my replies come from programmed rules, not a language model.'],
        'rules':['Here are the rules behind my chat:', 'My chat follows these construction rules:'],
        'construction':['I use explicit rules to match your wording to a conversational intent, keep track of the current thread, and build a reply from allowed phrases.', 'I use explicit rules to connect your message with our current conversation and choose how to respond.'],
        'experience':['I don’t have feelings or private experiences, but I can respond to what you share.'],
        'conversation':['Of course. We can talk about your day, explore an idea, or keep it light.'],
        'support':['This is a deterministic chat reply; it isn’t evidence from an MPLPB.'],
        'greeting':['Hi! What’s on your mind?', 'Hey! How’s your day going?', 'Hello again. Want to talk about something or just hang out?'],
    }[topic]
    # Do not answer an affirmative question with an ambiguous "Right".
    if topic=='identity' and 'not' not in key:opening=opening[:1]
    body,determination=R.wording(opening,topic,state['turn'])
    detail={
        'ideas':'Which sounds best: a story, a question, or talking about your day?',
        'story':'',
        'identity':'I can still chat, keep track of our conversation and help with wording. Focus mode is where I use loaded MPLPB pages for supported answers.',
        'rules':'1. Identify your request, context and mode.\n2. Reduce the candidate replies using those constraints.\n3. Choose equivalent conversational wording by a fixed order; clarify materially different meanings.\n4. If nothing qualifies, explain what is missing.\n5. MPLPB mode stays serious and requires source support; reducing alternatives never creates evidence.',
        'construction':'Some replies use written explanations; social replies can combine phrases and WordNet-checked adjectives. The same message and saved state produce the same reply.',
        'experience':'Want me to listen, ask questions, or help you organize your thoughts?',
        'conversation':'Would you prefer a question, a joke, or a listening ear?',
        'support':'Dictionary answers carry their own reference. For page-supported claims, load an MPLPB and use focus mode.',
        'greeting':'',
    }[topic]
    if topic=='story':
        turn=state['turn']
        hero=('a little purple monster','a curious paper dragon','a very small librarian')[turn%3]
        place=('a moonlit library','a quiet garden','an attic full of maps')[(turn//3)%3]
        object_=('a book with a blank final page','a key tied to a question mark','a tiny door behind a dictionary')[(turn//2)%3]
        detail='In '+place+', '+hero+' found '+object_+'. Instead of guessing what it meant, the creature invited a friend to investigate. What should they try first?'
    if detail:body+='\n\n'+detail
    state['topic']=topic
    suggestions={'ideas':['tell me a story','a silly question','I had a bad day'], 'story':['tell me more','can we talk'], 'greeting':['I had a bad day','tell me a joke'], 'identity':['how do you think?','what are the rules?'], 'construction':['what are the rules?','can we talk'], 'rules':['how do you think?','load all MPLPB']}.get(topic,['can we talk','just listen','load all MPLPB'])
    return M.reply('conversation',body,None,'CASUAL-'+topic.upper(),authority='conversation_structure',suggestions=suggestions,
                   response_structure={'intent':'casual_'+topic,'factual_claims':False,'mplpb_supported':False,
                                       'engine':VERSION,'wording_determination':determination,'discourse_topic':topic,'followup_of':state.get('followup_of')})
