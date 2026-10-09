"""Developer-authored synthetic runs; not independent human evaluation."""
import json
import tempfile
from pathlib import Path
from tools.ledger_ui import App

def run():
    checks=[]
    for mode in ['chat mode','load all MPLPB']:
        for name in ['Zuri','A','José','Anika','Jean-Luc']:
            with tempfile.TemporaryDirectory() as tmp:
                base=Path(tmp)/'topics';app=App(topic_base=base)
                sid=app.chat({'corpus':'logic','message':mode})['session']
                turns=[('helo','Hi'),('Hi I’m '+name+' what are you',name),("What's that",'Do you mean'),
                       ('thanks',None),('the second one','chat interface'),('the other one','bounded local collection'),
                       ('No I meant little monster','chat interface'),('tell me moer','grammar'),
                       ("What's my name",name),('My friend Rowan likes weaving','Rowan'),
                       ('What does she like','weaving'),('chat mode','0 MPLPB'),
                       ("What's my name",name),('say marshmallow','marshmallow')]
                fallback=0
                for q,want in turns:
                    r=app.chat({'corpus':'logic','session':sid,'message':q})['response']
                    bad='Could you name the topic' in r['message'] or 'Tell me a little more about what you have in mind' in r['message']
                    fallback=fallback+1 if bad else 0
                    checks.append({'mode':mode,'name':name,'question':q,'reply':r['message'],
                       'relevant':want is None or want.casefold() in r['message'].casefold(),
                       'memory_check':q=="What's my name",'boundary_failure':bool(r['sources']),
                       'repeated_fallback':fallback>=2})
                    app=App(topic_base=base)
    report={'method':'developer-authored synthetic conversation smoke tests; expectations are narrow checks, not human ratings',
      'turns':len(checks),'relevance_passes':sum(c['relevant'] for c in checks),
      'memory_passes':sum(c['relevant'] for c in checks if c['memory_check']),
      'memory_checks':sum(c['memory_check'] for c in checks),
      'boundary_failures':sum(c['boundary_failure'] for c in checks),
      'repeated_fallbacks':sum(c['repeated_fallback'] for c in checks),'checks':checks}
    return report

if __name__=='__main__':
    report=run()
    Path('evaluation/conversation-continuity-smoke.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='checks'},indent=2))
    raise SystemExit(0 if report['relevance_passes']==report['turns'] and not report['boundary_failures'] else 1)
