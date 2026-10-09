"""Small, attributed research notes for general chat; never MPLPB evidence."""
import json
import re
from pathlib import Path
from tools import deterministic_mind as M
VERSION='general-reference-v1'
PATH=Path(__file__).resolve().parents[1]/'resources/general_chat.json'

def records():
    return json.loads(PATH.read_text(encoding='utf-8'))['topics']

def handle(message,session):
    if session.get('environment',{}).get('mode')!='chat':return None
    key=message.casefold().replace('’',"'").strip(' .!?')
    rows=records()
    if key in {'general topics','list general topics'}:
        return M.reply('conversation','We can explore '+', '.join(r['topic'] for r in rows)+'. These are short research notes; saved pages and Wikipedia can cover more.',session.get('context'),'GENERAL-TOPICS',authority='system_description',suggestions=['Tell me about '+r['topic'] for r in rows[:8]])
    more=key in {'tell me more','more about that','go on'}
    if more:
        row=next((r for r in rows if r['topic']==session['mind'].get('general_reference_topic')),None)
    else:
        subject=re.sub(r"^(?:(?:can|could|would) you )?(?:tell me about|chat about|talk about|explain|what is|what are|define) (?:the )?",'',key)
        subject=re.sub(r'^the ','',subject)
        row=next((r for r in rows if subject in [r['topic'],*r.get('aliases',[])]),None)
    if not row:return None
    session['mind']['general_reference_topic']=row['topic']
    facts=row['facts'][1:] if more else row['facts'][:1]
    if not facts:facts=row['facts'][:1]
    body=' '.join(facts)+'\n\n'+('What part interests you?' if not more else 'Would you like to look for more detail?')
    return M.reply('conversation',body,session.get('context'),'GENERAL-REFERENCE',authority='research_note',
        sources=[{'title':row['source_title'],'url':row['url'],'reviewed':'2026-10-09','basis':'authored paraphrase'}],
        suggestions=['Tell me more','Search '+row['topic'],'general topics'],
        response_structure={'intent':'research_note','factual_claims':True,'mplpb_supported':False,'version':VERSION})
