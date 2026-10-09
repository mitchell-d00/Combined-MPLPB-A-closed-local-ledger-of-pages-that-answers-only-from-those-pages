"""Synthetic context paraphrase matrix; executable assertions, not human ratings."""
import argparse
import json
import tempfile
from pathlib import Path
from tools.ledger_ui import App

TOPICS = ['dog', 'cat', 'rabbit', 'orchid', 'bicycle', 'spaceship', 'garden', 'robot',
          'novel', 'painting', 'game', 'recipe', 'telescope', 'workshop', 'boat',
          'dragon', 'flarn', 'project', 'computer', 'song']
QUERIES = ['What is my {slot}?', 'What’s my {slot}?', 'Do you remember my {slot}?',
           'Remind me about my {slot}', 'Can you tell me my {slot}?',
           'Please remind me of my {slot}', 'Could you remember my {slot}?',
           'Tell me what my {slot} is']

def run():
    records=[]
    with tempfile.TemporaryDirectory() as tmp:
        for mode in ['chat mode','load MPLPB']:
            for topic in TOPICS:
                app=App(topic_base=Path(tmp)/mode.replace(' ','_')/topic/'topics')
                sid=app.chat({'corpus':'logic','message':mode,'default_chat':True})['session']
                def send(q):
                    return app.chat({'corpus':'logic','session':sid,'message':q,'default_chat':True})['response']
                slot=topic+"'s name"
                send('My '+slot+' is Amber')
                send('Actually, my '+slot+' is Indigo')
                for template in QUERIES:
                    q=template.format(slot=slot);r=send(q)
                    ok=('Indigo' in r['message'] and 'Amber' not in r['message'] and not r.get('sources')
                        and r.get('authority')=='user_declaration')
                    records.append(dict(mode=mode,topic=topic,question=q,answer=r['message'],passed=ok))
                send('forget my '+slot)
                r=send('What is my '+slot+'?')
                records.append(dict(mode=mode,topic=topic,question='recall after forgetting',answer=r['message'],
                                    passed='Indigo' not in r['message'] and not r.get('sources')))
                if not app.resume_chat({'session':sid})['chain_intact']:
                    raise AssertionError('Broken transcript chain')
    return {'synthetic':True,'independent_evaluation':False,'records':records,
            'total':len(records),'passed':sum(r['passed'] for r in records)}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);a=p.parse_args()
    result=run();Path(a.output).write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
    print(str(result['passed'])+'/'+str(result['total'])+' synthetic checks passed')
    if result['passed'] != result['total']:raise SystemExit(1)
