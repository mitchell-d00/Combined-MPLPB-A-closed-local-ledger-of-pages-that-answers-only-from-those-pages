"""Fixed full conversations; not generated from recognizer forms or human ratings."""
import json
import tempfile
from pathlib import Path
from tools.ledger_ui import App

def run():
    fixture=json.loads((Path(__file__).resolve().parents[1]/'evaluation/conversation/architecture-smoke.json').read_text())
    checks=[]
    for mode in ['chat mode','load all MPLPB']:
        for scenario in fixture['scenarios']:
            with tempfile.TemporaryDirectory() as tmp:
                base=Path(tmp)/'topics';app=App(topic_base=base)
                sid=app.chat({'corpus':'logic','message':mode})['session']
                for question,want in scenario['turns']:
                    r=app.chat({'corpus':'logic','session':sid,'message':question})['response']
                    checks.append({'mode':mode,'scenario':scenario['name'],'request':question,'reply':r['message'],
                        'expected_fragment':want,'relevance_check':want.casefold() in r['message'].casefold(),
                        'unexpected_sources':bool(r['sources']),
                        'planned_before_execution':r['reply_plan'].get('phase')=='before_execution',
                        'selected':r['reply_plan']['selected']['handler']})
                    app=App(topic_base=base)
    return {'provenance':fixture['provenance'],'independent_validation':False,'turns':len(checks),
        'relevance_passes':sum(c['relevance_check'] for c in checks),
        'unexpected_source_failures':sum(c['unexpected_sources'] for c in checks),'checks':checks}

if __name__=='__main__':
    report=run()
    target=Path('evaluation/conversation/architecture-results.json')
    target.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='checks'}))
    for c in report['checks']:
        if not c['relevance_check'] or c['unexpected_sources']:print(c)
    raise SystemExit(0 if report['relevance_passes']==report['turns'] and not report['unexpected_source_failures'] else 1)
