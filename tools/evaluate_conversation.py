"""Replay synthetic user conversations; outputs are observations, not human ratings."""
import argparse,json,tempfile
from pathlib import Path
from tools.ledger_ui import App

def run():
    records=[]
    scenarios=json.loads(Path('evaluation/conversation/scenarios.json').read_text())
    with tempfile.TemporaryDirectory() as tmp:
        app=App(topic_base=Path(tmp)/'topics')
        for mode in ['chat mode','load MPLPB']:
            for case in scenarios:
                sid=app.chat({'corpus':'logic','message':mode,'default_chat':True})['session']
                for message in case['turns']:
                    r=app.chat({'corpus':'logic','session':sid,'message':message,'default_chat':True})['response']
                    records.append({'scenario':case['id'],'mode':mode,'question':message,'answer':r['message'],'kind':r['kind'],'authority':r.get('authority'),'source_count':len(r.get('sources',[]))})
    return records
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);args=p.parse_args()
    Path(args.output).write_text(json.dumps(run(),indent=2,ensure_ascii=False)+'\n')
