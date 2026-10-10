"""Offline five-minute-demo conversation with disposable local state."""
import tempfile
from pathlib import Path
from tools.ledger_ui import App


def main():
    with tempfile.TemporaryDirectory() as tmp:
        app=App(topic_base=Path(tmp)/'topics');sid=None
        for message in ["Hi I'm Zuri, who are you?",'My pet is Juniper; what is my pet?',
                        'Actually my pet is Miso; what is my pet?','What is my pet?',
                        'please be gentle','repeat exactly purple rabbit']:
            result=app.chat({'corpus':'logic','message':message,'session':sid,'default_chat':True})
            sid=result['session'];r=result['response']
            print('\nUSER:',message,'\nMPLPB:',r['message'])
            print('Mode:',r.get('environment',{}).get('mode'),'Sources:',len(r.get('sources',[])),
                  'Pre-execution plan:',bool(r.get('reply_plan')))

if __name__=='__main__':main()
