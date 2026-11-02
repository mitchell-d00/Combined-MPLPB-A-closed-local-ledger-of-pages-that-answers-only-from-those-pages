"""Frozen synthetic end-to-end procedure journeys; no human validation claim."""
import hashlib
import json
from pathlib import Path
import tempfile
from mplpb_combined.ledger import write
from mplpb_answers.procedures import MARKER
from mplpb_answers.support import code_pins
from tools.ledger_ui import App


def run():
    path=Path(__file__).resolve().parents[1]/'evaluation/procedure-recovery/fresh.json'
    raw=path.read_bytes();fixture=json.loads(raw);rows=[]
    for journey in fixture['journeys']:
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp);root=base/'corpus';root.mkdir()
            doc={'id':journey['id'],'steps':[
                dict(order=1,action=journey['action'],prerequisites=[],conditions=['Use only dry material.'],warnings=[journey['warning']]),
                dict(order=2,action='Close the cover.',prerequisites=[1],conditions=['Only after alignment.'],warnings=['Stop if the cover binds.'])]}
            write(root,doc_id='FRESH-001',title='Local process',scope='notes',body=MARKER+json.dumps(doc))
            app=App(custom=root,topic_base=base/'topics');sid=None
            for n,turn in enumerate(fixture['turns']):
                # Recreate the application before answering the pending step.
                if n==2:app=App(custom=root,topic_base=base/'topics')
                message=turn['message'].format(words=journey['id'].replace('-',' '))
                result=app.chat(dict(corpus='custom',message=message,session=sid,auto_wiki=False))
                sid=result['session'];response=result['response']
                passed=response['kind']==turn['kind'] and not response.get('procedure',{}).get('execution_verified',False)
                if turn['kind']=='return':
                    passed=passed and all(s in response['message'] for s in (journey['warning'], 'Use only dry material.')) if n!=4 else passed and 'Stop if the cover binds.' in response['message']
                rows.append(dict(domain=journey['domain'],message=message,passed=passed,response=response))
    return dict(role=fixture['role'],fixture_sha256=hashlib.sha256(raw).hexdigest(),code_sha256=code_pins(),
                passed=sum(r['passed'] for r in rows),total=len(rows),rows=rows)


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);args=p.parse_args()
    result=run();Path(args.output).write_text(json.dumps(result,indent=2)+'\n')
    print(result['passed'],'/',result['total'])
