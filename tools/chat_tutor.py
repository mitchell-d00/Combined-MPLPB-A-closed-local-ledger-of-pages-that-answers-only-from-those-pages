"""Saved, deterministic interface tutor; no semantic search or generated facts."""
import re
from tools import deterministic_mind as M

START={'guide me','yes guide me','yes please guide me','start guide','start the guide','walk me through it','teach me how to use mplpb'}
LIST={'show my mplpb','show my pages','what pages do i have','what is in my mplpb','present my mplpb','show this collection','what can i ask about'}
LESSONS=[
 ('Meet your MPLPB','I can help you explore sealed local pages. Would you like to look at the pages already loaded, or build a collection about a topic? Nothing is searched or deleted until you explicitly request an action.',['show my MPLPB','how do I search?','next step']),
 ('Choose your material','Use “show my MPLPB” for available page titles. To build new material, choose Simple English Wikipedia beside Send and type “search dinosaurs”. Wikipedia mode needs no API key. General Web needs the separate crawler setup. What topic would you like to explore?',['show my MPLPB','I want to learn about fossils','next step']),
 ('Ask and check the source','Select a title with “topic Exact title”. Then ask what it is, request a summary, or inspect its source. Summaries quote source text; they do not prove the source is true. A question can be refused or ambiguous. What would you like to check?',['show my MPLPB','how do I ask a question?','why did you refuse?','next step']),
 ('Keep or clear your work','Successful operations save in this browser. Export transcript makes a chat copy, not a full source backup. You can keep notes, restart a chat, or clear selected collections through confirmed controls. Which would you like help with?',['how do I save?','how do I clear all?','how do I use memory?','finish guide']),
]

def key(message):return re.sub(r'\s+',' ',re.sub(r'[?!.,]','',message.casefold().replace('’',"'"))).strip()

def guide(message,context,memory):
    command=key(message);saved=memory.get('guide',{})
    if command in START: saved={'active':True,'step':0};memory['guide']=saved
    elif command in {'stop guide','finish guide','skip guide','no thanks'}:
        memory['guide']={'active':False,'step':saved.get('step',0)}
        return M.reply('help','Guide stopped. Your sources, notes and chat are unchanged. You can use “guide me” whenever you want.',context,'GUIDE-STOP',authority='interface_instructions',suggestions=['show my MPLPB','how do I search?'])
    elif saved.get('active') and command in {'next','next step','continue guide','back','previous step'}:
        saved['step']=max(0,min(len(LESSONS)-1,saved['step']+(-1 if command in {'back','previous step'} else 1)))
    elif saved.get('active') and saved.get('step')==1 and re.fullmatch(r"[\w '\-]{1,80}",message.strip()) and len(command.split())<=5 and command.split()[0] not in {'search','topic','import','find','remember','memory','summarize','explain','show','how','why','what','is','are','do','does','can','compare','relate','hello','hi','hey','thanks','thank','ok','okay'}:
        saved['topic']=message.strip()
        return M.reply('guide','Let’s explore “'+saved['topic']+'”. Choose a Wikipedia mode beside Send, then use the search suggestion to build it, or select a page already loaded. Suggestions do not run until you send them.',context,'GUIDE-TOPIC',authority='interface_instructions',guide={'step':2,'total':len(LESSONS)},suggestions=['search '+saved['topic'],'topic '+saved['topic'],'show my MPLPB','next step'])
    else:return None
    step=saved['step'];title,body,suggestions=LESSONS[step]
    if context and step==2:suggestions=['what is it?','summarize it','show source','next step']
    if step:suggestions=suggestions+['previous step']
    return M.reply('guide',f'Step {step+1} of {len(LESSONS)}: {title}\n\n{body}',context,'GUIDE-'+str(step+1),authority='interface_instructions',guide={'step':step+1,'total':len(LESSONS)},suggestions=suggestions)

def learning_request(message,context):
    match=re.fullmatch(r'(?:i want to learn about|i would like to learn about|help me learn about|teach me about|can we explore) (.{1,160})[?.!]*',message.strip(),re.I)
    if not match:return None
    topic=match[1].rstrip('?.!').strip()
    return M.reply('help','We can explore “'+topic+'”. If that exact page is already in your collection, select it. Otherwise choose a Wikipedia mode and send a search to build a new MPLPB. Which would you like to do?',context,'LEARN-REQUEST',authority='interface_instructions',suggestions=['topic '+topic,'search '+topic,'show my MPLPB'])

def local_phrase(message):
    aliases={'what is this about':'what is it?','what is this page about':'what is it?','explain this':'summarize it','explain it to me':'summarize it','can you summarize this':'summarize it','give me a summary':'summarize it','tell me more about it':'show source','where did that come from':'show source','what does the page say':'show source'}
    return aliases.get(key(message),message)

SMALL_TALK={
 'hello':('Hello. We can just chat, or explore a topic when you feel like it.','How is your day going?'),
 'hi':('Hi. There’s no need to start a research session.','What’s on your mind?'),
 'hey':('Hey. We can keep this casual.','How is your day going?'),
 'how are you':('I’m ready to chat. I don’t have feelings or a day of my own.','How is your day going?'),
 'what are you':('I’m MPLPB, a deterministic chat interface around a local collection of pages. I use defined response rules.','Would you like to chat casually or see your pages?'),
 'why are you':('My purpose is to help you explore information while showing its sources and knowing when to stop.','We can also keep the conversation casual.'),
 'why do you exist':('I’m here to help you work with your local pages, their sources and their limits.','Would you like to chat or explore something?'),
 'what is your purpose':('I help you explore local pages with explicit rules and provenance checks.','You can also talk to me without choosing a topic.'),
 'just chatting':('That’s fine. We can leave the research aside for now.','What’s on your mind?'),
 'small talk':('We can keep this light.','How has your day been?'),
 'i am bored':('We could chat, try a joke, or choose a topic to explore.','Would you like to tell me about your day?'),
 'nothing much':('Nothing much is a perfectly good place to start.','Has anything caught your attention today?'),
 'good':('Glad to hear your day is going well.','What have you been up to?'),
 'not great':('Sorry it’s been a rough day.','Would you like to talk about it or change the subject?'),
 'tell me a joke':('Why did the notebook bring a ladder? To reach its higher notes.','Want to keep chatting?'),
}
CASUAL_PREFIXES=('i like ','i enjoy ','i was thinking about ','just chatting about ','i had a ','my day was ','today i ','i feel ')
SMALL_ALIASES={'hi there':'hi','hello there':'hello','good morning':'hello','good afternoon':'hello','good evening':'hello','how are you doing':'how are you','how is it going':'how are you','how are things':'how are you',"i'm bored":'i am bored','just chat':'just chatting',"let's chat":'just chatting','lets chat':'just chatting','can we just chat':'just chatting','why are you here':'why do you exist','why were you made':'why do you exist','are you ai':'what are you','fine':'good','pretty good':'good','not much':'nothing much'}

def casual_key(message):
    command=key(message)
    for greeting in ('hello ','hi ','hey '):
        if command.startswith(greeting) and command[len(greeting):] in SMALL_TALK:
            command=command[len(greeting):]
            break
    return SMALL_ALIASES.get(command,command)

def smalltalk_candidate(message,memory):
    command=casual_key(message)
    return (command in SMALL_TALK or command in {'keep chatting','stay casual'}
            or (command in {'yes','yes please','lets explore',"let's explore",'no','no thanks'} and bool(memory.get('topic_offer')))
            or command.startswith(CASUAL_PREFIXES))

def smalltalk(message,context,memory,titles,scope):
    """Literal topic mentions invite a transition; no source facts or auto-fetch."""
    command=casual_key(message);offer=memory.get('topic_offer')
    if offer and offer.get('scope')!=scope:
        memory.pop('topic_offer',None);offer=None
    if command in {'yes','yes please','lets explore',"let's explore"} and offer:
        if len(offer['titles'])==1 and offer['titles'][0] in titles:
            memory.pop('topic_offer',None)
            return {'select_topic':offer['titles'][0]}
        return M.reply('clarify','Choose an exact available title to begin. The earlier offer does not override source checks.',context,'SMALL-ACCEPT-CHECK',suggestions=['topic '+t for t in offer['titles'] if t in titles]+['show my MPLPB'])
    if command in {'no','no thanks','keep chatting','stay casual'}:
        memory.pop('topic_offer',None)
        return M.reply('smalltalk','Sure. We’ll keep it casual. What’s on your mind?',context,'SMALL-STAY',authority='conversation_structure',suggestions=['nothing much','tell me a joke','what are you?'])
    body,question=SMALL_TALK.get(command,('I’m listening. We can keep this light.','Would you like to say more, or change the subject?'))
    mentions=[t for t in titles if re.search(r'(?<!\w)'+re.escape(key(t))+r'(?!\w)',command)]
    # Preserve specificity when one title is entirely contained in another.
    mentions=[t for t in mentions if not any(t!=u and key(t) in key(u) for u in mentions)]
    choices=['keep chatting','tell me a joke','show my MPLPB']
    if mentions:
        memory['topic_offer']={'titles':mentions,'scope':scope}
        body='You mentioned '+', '.join('“'+t+'”' for t in mentions)+'. Those titles are in the current MPLPB.'
        question='Would you like to move into a source-backed conversation about '+('this topic?' if len(mentions)==1 else 'one of these topics?')
        choices=(['yes please'] if len(mentions)==1 else ['topic '+t for t in mentions[:8]])+['keep chatting']
    return M.reply('smalltalk',body+'\n\n'+question,context,'SMALL-OFFER' if mentions else 'SMALL-CHAT',authority='conversation_structure',suggestions=choices,response_structure={'intent':'topic_offer' if mentions else 'smalltalk','factual_claims':False,'topic_mentions':mentions,'automatic_topic_switch':False})

def conversation(message,context,memory):
    """Conversation about handling a topic, never evidence about its contents."""
    command=key(message)
    topic=context.get('title') if context else None
    focus='“'+topic+'”' if topic else 'a topic'
    choices=['summarize it','show source','show my MPLPB'] if topic else ['show my MPLPB','guide me','how do I search?']
    style=memory.setdefault('conversation',{}).get('style','brief')
    if command in {'keep it short','short answers please','be brief','give me more detail','more detail please'}:
        style='detailed' if 'detail' in command else 'brief'
        memory['conversation']['style']=style
        purpose='I’ll include the available next steps and explain how to check their sources.' if style=='detailed' else 'I’ll keep conversational replies short and offer a next step.'
        rule='CHAT-STYLE'
    elif command in {'lets talk about it',"let's talk about it",'can we talk about this','can we chat about it','talk to me about this','lets discuss it',"let's discuss it"}:
        purpose='We can explore '+focus+'. Would you like an overview, the original source, or a different page?'
        rule='CHAT-DISCUSS'
    elif command in {'i am confused',"i'm confused",'i dont understand',"i don't understand",'that is confusing','help me understand','i am lost',"i'm lost"}:
        purpose='Let’s take one step at a time. '+('We have '+focus+' selected. Start with its summary, then check the source.' if topic else 'First choose a page from your MPLPB, or use Guide me to build a collection.')
        rule='CHAT-CLARIFY'
    elif command in {'that is interesting','thats interesting',"that's interesting",'interesting','sounds interesting','i like this topic','what should we discuss','what should i ask next','what next'}:
        purpose='For '+focus+', we can look at an overview or inspect where the information came from. Which would you prefer?'
        rule='CHAT-NEXT'
    elif command in {'what do you think','what is your opinion','do you like this topic'}:
        purpose='I don’t form personal opinions. I can help you examine '+focus+' by checking what a page says and where it came from.'
        rule='CHAT-OPINION'
    else:return None
    detail='These are choices for exploring the collection. A summary or source request will still check the selected page and its provenance. I have not searched the web or added any topic facts in this reply.'
    return M.reply('conversation',purpose+('\n\n'+detail if style=='detailed' else ''),context,rule,authority='conversation_structure',suggestions=choices,response_structure={'intent':rule,'topic':topic,'style':style,'next_step':'choose a suggested question','factual_claims':False})

def followups(result,memory):
    if result.get('suggestions'):return
    if result['kind'] in {'return','summary','topic','built'}:
        result['suggestions']=['what is it?','summarize it','show source','show my MPLPB']
    elif result['kind'] in {'clarify','not_in_corpus','ambiguous','unknown_relation','crawl_failed'}:
        result['suggestions']=['show my MPLPB','why did you refuse?','guide me']
    else:result['suggestions']=['guide me','show my MPLPB','how do I search?']
    if memory.get('guide',{}).get('active'):result['suggestions'].append('next step')
