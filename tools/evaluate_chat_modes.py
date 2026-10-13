"""Synthetic mode comparison only. Does not record a user's free-chat session."""
import json
import tempfile
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from mplpb_combined.ledger import write
from tools.ledger_ui import App


def evaluate():
    with tempfile.TemporaryDirectory() as temp:
        root=Path(temp)/'corpus';root.mkdir()
        write(root,doc_id='MODE-0001',title='Aster',scope='Aster service port',body='The Other service port is 8123.')
        app=App(custom=root,topic_base=Path(temp)/'topics')
        rows=[]
        for question in ['What is the Aster service port?','step 2 of procedure missing','hello','tell me a story']:
            strict=app.query({'corpus':'custom','question':question})['reader']
            free=app.chat({'corpus':'custom','message':question,'off_record':True})['response']
            rows.append({'question':question,'constrained':{'kind':strict['kind'],'text':strict['text']},
                         'free_chat':{'kind':free['kind'],'text':free['message'],'source_backed':False}})
        return {'purpose':'Synthetic behavior comparison, not an accuracy benchmark',
                'free_chat_means':'deterministic conversation without source answering; no saved transcript or network',
                'context_is_evidence':False,'cases':rows}

if __name__=='__main__':print(json.dumps(evaluate(),indent=2))
