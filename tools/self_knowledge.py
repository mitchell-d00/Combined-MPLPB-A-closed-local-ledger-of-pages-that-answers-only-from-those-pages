"""Authored software capability model plus observed session state; not world evidence."""
import re
from tools import deterministic_mind as M
from tools import question_frames as F

VERSION='self-knowledge-v6'
CAPABILITIES={
 'definition': ('What is a MPLPB?', 'A MPLPB is a bounded local collection of knowledge pages. Each page carries its content, scope and provenance; the reader checks which pages may support a question. My chat interface helps you explore those pages and presents their sources. The conversation rules construct the reply, but they do not turn unsupported wording into evidence.'),
 'identity': ('What are you?', 'I’m MPLPB’s rule-based little monster. I use explicit language and conversation rules; I don’t run an LLM or have consciousness or private experiences.'),
 'abilities': ('What can you do?', 'We can talk about your day, explore an idea, work through a small calculation, or discuss a topic using available content. I can index this conversation, replay explicit personal-detail corrections, recall earlier exchanges, remember user-defined word meanings, chat, follow a topic, explain my rules, look up words, explore saved pages, show sources and construct bounded replies. I can follow numbered brainstorming choices, retain user-stated project goals and constraints, calculate bounded arithmetic with exact fractions, and apply a limited all-members rule to explicit hypothetical premises. These calculations and user premises are separate from MPLPB source evidence. In Chat and Serious modes, “browse library” opens the library index. “library ask in SHELF: QUESTION” checks one declared book scope; ambiguous routes ask you to narrow. I can capture public sources through the configured search tools. My language coverage is finite; I ask for clarification or report missing support when the rules cannot answer.'),
 'modes': ('How do your modes work?', 'I can chat in Chat, Serious, and off-the-record free chat. Free chat keeps only an ephemeral session in the running app, uses local conversation rules, bundled dictionary references and attributed seed notes, and never saves a transcript or fetches sources. Leaving free chat discards that session. Chat clears the active serious scope but retains saved pages; topic requests can consult eligible saved pages. Serious mode checks loaded collections first. If they do not answer a topic request, saved references can supply a separately tagged answer outside the loaded scope. Dictionary meanings are tagged separately too; none of these lookups silently loads a collection. Their sources and boundaries remain separate.'),
 'language': ('How do you construct sentences?', 'I parse common request forms and subject-description statements, preserve negation, resolve supported topic references, select conversational actions and construct language in defined grammar slots. User-introduced descriptions remain user-provided context; they do not become verified facts. The dictionary and thesaurus help with word senses and wording. Conversational framing uses pinned verb senses; “Other words for that meaning” offers alternatives within a selected dictionary sense without inventing tone or register. I can respond to interest, confusion and discussion requests using freshly checked content. Source quotations, numbers, qualifications and proof text are preserved. Recent social and attribute-question frames support bounded corrections and follow-ups. Explicit guards select behavior classes; fixed ranks resolve supported temporal spelling variants, and ties request clarification. Identical input and complete session state give identical results. Source follow-ups still pass existing evidence checks. Some procedural explanations remain authored text.'),
 'operation': ('How do you work?', 'I use explicit rules: I read your message and the current conversation, identify a supported kind of request, then choose the appropriate local rule. For ordinary chat I construct a response from conversation context and grammar. For a topic I can consult bundled reference notes, dictionary senses or eligible saved pages. Page-based claims keep their source checks and citations. Finally I validate the response and, outside free chat, save the conversation. The same rules, inputs and complete state produce the same result; no language model samples the next word.'),
 'sources': ('Where do your answers come from?', 'Page-based factual replies use eligible MPLPB pages and show their references. Bundled seed notes retain their separate research-note attribution in every mode. Definitions use the bundled WordNet resource. Conversation and imagined ideas are labeled separately; they are not page evidence. A matching page or a valid hash does not prove that a claim is true.'),
 'search': ('How do you search?', 'I check eligible local pages first for supported topic requests. With automatic Wikipedia lookup enabled, missing or exhausted material can trigger a bounded capture and retry. Explicit search and import also contact the selected service. You can type “search dogs”, select a Wikipedia source, and send it. General web crawling needs a configured, deployed crawler and its access settings. Wikipedia mode needs neither that crawler nor its token; I do not browse the whole web or scan local folders independently.'),
 'memory': ('How does your memory work?', 'In Chat and Serious modes, I retain conversation state, notes, topic context and captured pages in the configured local save store, with no fixed retention timer or guaranteed storage lifetime. In off-the-record free chat, only the running app’s ephemeral session retains conversation context; leaving it or restarting the app discards that session, and MPLPB does not save its transcript. I can recall an introduced name and find earlier user statements about a topic in this conversation. Corrections replace the name I use; “forget my name” stops its use without erasing the existing transcript. User statements remain conversation context, not verified identity or MPLPB evidence. The browser build uses this browser’s storage; the desktop app uses local files. Saving is not model training. Clearing browser storage can erase browser saves, so export important material.'),
 'limits': ('What are your limitations?', 'My reader uses lexical matching, not general semantic understanding. My grammar covers finite patterns. Missing, ambiguous or conflicting evidence must stay visible; selecting fewer candidates never creates proof. Developer tests are not independent human validation, and production reliability in critical settings has not been established.'),
 'resources': ('What data do you have?', 'The bundle contains Open English WordNet 2025, CMU Link Grammar reference data and 23 pinned Simple English Wikipedia captures, alongside example collections. The Link Grammar parser is not running. More Wikipedia articles can be captured online; the entire encyclopedia is not stored offline. Saved user collections depend on this installation.'),
}
ALIASES={
 'identity': {'what are you','who are you','what is your name'},
 'definition': {'what is mplpb','what is your mplpb','what is your molpb',"what's your mplpb","what's your molpb",'what is a mplpb','what is an mplpb','what does mplpb mean','explain mplpb','describe mplpb','tell me about mplpb'},
 'abilities': {'what can you do','what are your capabilities','what can you help me with','help me understand you'},
 'modes': {'how do your modes work','what is serious mode','what is chat mode','explain your modes'},
 'language': {'how do you construct sentences','how do you generate language','how does your language planner work','are your replies canned','what are your rules','explain your rules'},
 'sources': {'where do your answers come from','how do you know things','can i trust your answers','are all your answers facts'},
 'search': {'how do you search','how do i search','search help','how do you crawl','can you access the internet','do you search automatically'},
 'memory': {'how does your memory work','do you learn from me','do you train on our chats','where do you save our conversation'},
 'limits': {'what are your limitations','what can you not do','what are your limits','can you be wrong'},
 'resources': {'what data do you have','what references do you have','do you have all of wikipedia'},
}


def snapshot(session):
    env=session.get('environment') or {}
    return {'mode':env.get('mode','legacy'), 'loaded_collections':list(env.get('corpora',[])),
            'focused_topic':(session.get('context') or {}).get('title'),
            'conversation_topic':session.get('mind',{}).get('idea_chat',{}).get('subject')}


def recognize(message, session=None):
    key=re.sub(r'\s+',' ',F.normalize(message).casefold().replace('’',"'")).strip(' ?!.')
    # Whole request slots: never recognize a self-question merely embedded in
    # a quote, negation, third-party question or arbitrary instruction.
    if re.match(r"^(?:say|repeat|echo|when i say|do not|don't|never|imagine)\b",key):return None
    key=re.sub(r'^(?:explain|describe) (?:exactly|briefly|simply|in detail) ', 'explain ',key)
    key=re.sub(r'^(?:explain|describe) (?:to me )?(?=how you )','',key)
    key=re.sub(r'^how you (work|chat|talk|respond|think)$',r'how do you \1',key)
    parts=re.split(r'\s+and\s+(?=(?:how|what|who|explain|describe)\b)|[;?!]\s*',key)
    parts=[part for part in parts if part]
    if 1<len(parts)<=4:
        matches=[recognize(part) for part in parts]
        if all(m and m.get('topic') for m in matches):
            topics=list(dict.fromkeys(t for m in matches for t in m.get('topics',[m['topic']])))
            return {'current':False,'topic':topics[-1],'topics':topics}
        return None
    compound=re.fullmatch(r'(what are you|who are you)[,; ]+(?:and )?(?:explain|describe|tell me) (?:exactly |briefly |simply )?(?:how you work|how you chat|how you construct sentences)',key)
    if compound:
        return {'current':False,'topic':'operation','topics':['identity','operation','language']}
    previous=(session or {}).get('log',[])
    last=previous[-1].get('payload',{}).get('response',{}) if previous else {}
    if last.get('self_knowledge') and key in {'tell me more','explain that','how does that work','explain how that works','can you explain that','put that simply'}:
        prior=last['self_knowledge']['topic']
        topic='operation' if prior in {'identity','current_state','definition'} else 'language' if prior=='operation' else prior
        return {'current':topic=='current_state','topic':None if topic=='current_state' else topic,'followup':True}
    if re.fullmatch(r'(?:how (?:do|can) you|how does (?:mplpb|your (?:chat|system)))(?: actually)? (?:work|chat|talk|respond|think)(?: normally| naturally)?',key):
        return {'current':False,'topic':'language' if re.search(r'\b(?:chat|talk|respond)\b',key) else 'operation'}
    if re.fullmatch(r'(?:what (?:is|are)|which|show|list|describe|tell me about) (?:the |your |my )?(?:loaded|active|selected) (?:mplpb|mplpbs|collections?|pages?|content)(?: collections?| loaded)?',key) or key in {'what is loaded','what have i loaded','what have you loaded','what is in your mplpb','what is in my mplpb'}:
        return {'current':True,'topic':None}
    if re.fullmatch(r'(?:how do|do|can) you use (?:the |your )?(?:dictionary|thesaurus|grammar|language rules|seed information|seed content|mplpb information)(?: (?:to|for) (?:chat|talk|respond|construct language))?',key):
        return {'current':False,'topic':'language'}
    if key in {'how do you use the dictionary','how do you use the thesaurus','how do you use seed information','how do you use mplpb information'}:
        return {'current':False,'topic':'language'}
    if key in {'chat normally','talk normally','chat naturally','talk naturally','can you chat normally','can you talk normally','can you have a conversation','what can we talk about','what can we discuss','what can you talk about','what can you chat about'}:
        return {'current':False,'topic':'abilities'}
    duration=re.fullmatch(r'(?:how long (?:will|do|can) you (?:remember|keep)|for how long (?:will|do|can) you (?:remember|keep)) (?:my name|that|this|me|our (?:chat|conversation)|my details)',key)
    if duration:return {'current':False,'topic':'memory'}
    current=key in {'what mode are you in','what do you have loaded','what are we talking about','describe your current state'}
    topic=next((name for name,forms in ALIASES.items() if key in forms),None)
    if not topic:
        subject=F.overview_subject(key)
        definition=re.fullmatch(r'(?:what is|what are) (.+)',key)
        subject=subject or (definition[1] if definition else '')
        subject=re.sub(r'^(?:a|an|the) ', '',subject)
        # Concept aliases are bound slots; surrounding arbitrary prose is not a match.
        concepts={'mplpb':'definition','combined mplpb':'definition','mplpb system':'definition',
                  'your capabilities':'abilities','your modes':'modes','your memory':'memory',
                  'your limitations':'limits','your data':'resources','your sources':'sources',
                  'your language generation':'language'}
        topic=concepts.get(subject)
    return {"current":current,"topic":topic} if current or topic else None


def handle(message,session,collections=None):
    match=recognize(message,session)
    if not match:return None
    current,topic=match["current"],match["topic"]
    state=snapshot(session)
    if current:
        mode={'focus':'Serious','chat':'Chat','legacy':'No explicit mode selected','free':'Off-the-record free chat'}[state['mode']]
        names=[(collections or {}).get(k,(k,None))[0] for k in state['loaded_collections']]
        body='Current mode: '+mode+'. Loaded collections: '+(', '.join(names) or 'none')+'.'
        if state['focused_topic']:body+=' Focused page: '+state['focused_topic']+'.'
        if state['conversation_topic']:body+=' Conversation topic: '+state['conversation_topic']+'.'
    else:body='\n\n'.join(CAPABILITIES[t][1] for t in match.get('topics',[topic]))
    if topic=='memory':
        body=('In off-the-record free chat, I keep your name and context only in this running app’s ephemeral session. Leaving free chat or restarting the app clears that session; it is not saved as a transcript. There is no fixed retention timer. Device or browser logging is outside this promise.' if state['mode']=='free' else 'In Chat and Serious modes, I recall your name from this conversation’s saved transcript while that saved conversation remains available. There is no fixed retention timer or guaranteed storage lifetime. '+body)
    return M.reply('help',body,session.get('context'),'SELF-KNOWLEDGE',authority='system_description',
        suggestions=[CAPABILITIES[k][0] for k in ('abilities','modes','limits') if k!=topic],
        self_knowledge={'version':VERSION,'topic':topic or 'current_state','basis':'authored capability model and observed session state','snapshot':state,'topics':match.get('topics',[topic or 'current_state']),'not_independent_validation':True},
        response_structure={'intent':'system_description','factual_claims':False,'mplpb_supported':False})


def documentation():
    text='# Current system and self-knowledge\n\nThis document is generated from `tools/self_knowledge.py`. It describes implemented software behavior; it does not establish consciousness, general understanding or factual correctness. Self-description is labeled separately from MPLPB source evidence.\n'
    for title,body in CAPABILITIES.values():text+='\n## '+title+'\n\n'+body+'\n'
    text+='\n## Current-state questions\n\nAsk “What mode are you in?”, “What do you have loaded?” or “What are we talking about?”. These answers read the current session, preserve its mode and scope, and do not fetch remote sources. Current loaded collections are distinct from collections merely saved locally.\n'
    return text
