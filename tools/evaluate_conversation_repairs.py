"""Per-behavior development records; fixed fixtures, not independent evaluation."""
import json
import tempfile
from collections import Counter
from pathlib import Path
from unittest.mock import patch
from mplpb_combined import ledger as L
from tools.ledger_ui import App

TOPICS=['Moon','Sphere','Beacon','Capsule','Lantern','Tower','Marble','Spindle','Vessel','Column']


def scenarios():
    return [
        ('social','Hi how are you to ight',[], 'social'),
        ('social','Hello! How are you doing tonihgt?',[], 'social'),
        ('social','Hey, how have you been this evning?',[], 'social'),
        ('social',"How's it going to night?",[], 'social'),
        ('social','how r u today',[], 'social'),
        ('social',"how's your day going this afternoon",[], 'social'),
        ('temporal_repair','Sorry I meant tonight',['how are you today'], 'repair'),
        ('temporal_repair','Actually, I mean this evening',['Hi how are you today','thanks'], 'repair'),
        ('temporal_repair','no I meant this morning',['how are you tonight','RELOAD'], 'repair'),
        ('clarify','Sorry I meant tonight',[], 'clarify'),
        ('clarify','I meant today',['how are you tonight','what is 2 plus 2'], 'clarify'),
        ('clarify','I meant tonight',['how are you today','thanks','thanks','thanks'], 'clarify'),
        ('attribute_repair','Sorry I meant age',['TOPIC','how big is it?'], 'age'),
        ('attribute_repair','Actually I meant its age',['TOPIC','how big is it?','hello'], 'age'),
        ('attribute_followup','and age?',['TOPIC','how big is it?','RELOAD'], 'age'),
        ('attribute_followup','how about the age?',['TOPIC','how big is it?'], 'age'),
        ('missing_evidence','and mass?',['TOPIC','how big is it?'], 'unsupported'),
        ('clarify','and age?',[], 'clarify'),
        ('stale_source','I meant age',['TOPIC','how big is it?','clear topic'], 'clarify'),
        ('damaged_source','and age?',['TOPIC','how big is it?','TAMPER'], 'unsupported'),
        ('no_reinterpretation','say how are you tonight',[], 'unchanged'),
        ('no_reinterpretation','how are you tonight according to this document',[], 'unchanged'),
        ('compound_preserved','how are you tonight and what is its mass',[], 'compound'),
        ('no_reinterpretation','do not tell me how are you tonight',[], 'unchanged'),
    ]


def run():
    records=[]
    with tempfile.TemporaryDirectory() as temp, patch('socket.create_connection', side_effect=AssertionError('no network')):
        for title in TOPICS:
            for index,(category,q,setup,expected) in enumerate(scenarios()):
                base=Path(temp)/title/str(index);root=base/'corpus';root.mkdir(parents=True)
                quote='The '+title+' is 4.5 billion years old.'
                page=L.write(root,title=title,scope=title,body='The '+title+' is 12 km in diameter. '+quote,
                             origin='machine',owner='fixture',source_authorship='unknown',external='no')
                app=App(root,topic_base=base/'topics')
                sid=app.chat({'corpus':'custom','message':'chat mode'})['session']
                history=[]
                def ask(message):
                    r=app.chat({'corpus':'custom','session':sid,'message':message,'auto_wiki':False})['response']
                    history.append({'question':message,'answer':r['message'],'kind':r['kind']})
                    return r
                for item in setup:
                    if item=='TOPIC':ask('topic '+title)
                    elif item=='RELOAD':app=App(root,topic_base=base/'topics')
                    elif item=='TAMPER':
                        p=root/page.path;p.write_text(p.read_text().replace('4.5','9.9'))
                    else:ask(item)
                r=ask(q);trace=r['interpretation'].get('conversational_repair',{})
                passed=False
                if expected in {'social','repair'}:
                    passed=not r['sources'] and r['authority']=='conversation_structure' and trace.get('intent')=='wellbeing'
                    if expected=='repair':passed=passed and trace.get('repaired') and 'you meant' in r['message']
                elif expected=='clarify':passed=not r['sources'] and trace.get('needs_clarification') and 'resend' in r['message']
                elif expected=='age':passed=r['kind']=='grounded_answer' and quote in r['message'] and r['sources'][0]['hash']==page.hash
                elif expected=='unsupported':passed=not r['sources'] and r['kind']!='grounded_answer'
                elif expected=='unchanged':passed=not trace and not r['sources'] and 'functional, thanks' not in r['message']
                elif expected=='compound':passed=not trace and not r['sources'] and 'functional, thanks' in r['message'] and 'can’t supply a factual answer' in r['message']
                records.append({'class':category,'topic':title,'question':q,'expected':expected,'passed':bool(passed),
                                'trace':trace,'sources':r['sources'],'history':history,
                                'chain_intact':app.resume_chat({'session':sid})['chain_intact']})
            print(title, len(records), 'cases',flush=True)
    summary={c:{'total':sum(r['class']==c for r in records),
                'passed':sum(r['class']==c and r['passed'] and r['chain_intact'] for r in records)} for c in sorted({r['class'] for r in records})}
    return {'synthetic':True,'independent_evaluation':False,'summary':summary,'total':len(records),
            'passed':sum(r['passed'] and r['chain_intact'] for r in records),'records':records}

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);args=p.parse_args()
    r=run();Path(args.output).write_text(json.dumps(r,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({k:v for k,v in r.items() if k!='records'},indent=2))
    if r['passed']!=r['total']:raise SystemExit(1)
