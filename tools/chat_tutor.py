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

def key(message):return re.sub(r'\s+',' ',re.sub(r'[?!.,]','',message.casefold())).strip()

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

def followups(result,memory):
    if result.get('suggestions'):return
    if result['kind'] in {'return','summary','topic','built'}:
        result['suggestions']=['what is it?','summarize it','show source','show my MPLPB']
    elif result['kind'] in {'clarify','not_in_corpus','ambiguous','unknown_relation','crawl_failed'}:
        result['suggestions']=['show my MPLPB','why did you refuse?','guide me']
    else:result['suggestions']=['guide me','show my MPLPB','how do I search?']
    if memory.get('guide',{}).get('active'):result['suggestions'].append('next step')
