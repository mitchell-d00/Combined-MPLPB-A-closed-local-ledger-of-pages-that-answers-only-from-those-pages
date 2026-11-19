"""Offline first-use archive: fictional UI examples, never an accuracy benchmark."""
import argparse
import hashlib
import html
import json
from pathlib import Path
from mplpb_combined.ledger import write
from mplpb_answers.pipeline import answer_query

DOCUMENTS = (
    'Ada Rose surveyed West Reach.',
    'Tomas Venn wrote the berth ledger.',
    'Elin Ward wrote the berth ledger.',
    'Citation: Telegram from Captain Vale announcing withdrawal from South Cove; July 23, 1884; Archive collection.\n'
    'On July 18, the coastal artillery opened fire on the harbour.\n'
    'At 4:15 p.m., July 19, Captain Vale surrendered South Cove, evacuating the garrison on the following day.\n'
    'This page was last reviewed on March 2, 2021.')
QUESTIONS = ('Who surveyed West Reach?', 'Who wrote the berth ledger?',
             'Did surveying West Reach cause the bombardment of South Cove?',
             'Distinguish the bombardment, surrender, evacuation and telegram dates in the South Cove record, without treating the webpage review date as an event date.')


def build(output):
    output=Path(output);output.mkdir(parents=True,exist_ok=False)
    raw=output/'originals';raw.mkdir();ledger=output/'ledger';sources=[]
    for number,text in enumerate(DOCUMENTS,1):
        p=raw/('document-'+str(number)+'.txt');p.write_bytes(text.encode())
        r=write(ledger,doc_id='ARCHIVE-'+str(number),title='Tutorial archive',scope='archive',
                body_html='<pre>'+html.escape(text)+'</pre>',when='2026-01-01T00:00Z')
        sources.append({'path':str(p.relative_to(output)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
                        'source_id':r.id,'ledger_hash':r.hash})
    before={p.relative_to(ledger).as_posix():p.read_bytes() for p in ledger.rglob('*') if p.is_file()}
    answers=[answer_query(ledger,q).contract for q in QUESTIONS]
    unchanged=before=={p.relative_to(ledger).as_posix():p.read_bytes() for p in ledger.rglob('*') if p.is_file()}
    result={'schema':'archival-tutorial-v1','scope':'Fictional prepared first-use examples, not historical evaluation.',
            'sources':sources,'answers':answers,'read_only_queries':unchanged,
            'notice':'One eligible owner returns its page; competing owners stop; none refuses. Strict source support additionally needs finite body evidence. Source assertions do not prove historical truth.'}
    (output/'walkthrough.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
    for answer in answers:
        print(answer['question']+'\n'+answer['kind']+' — '+answer['diagnostic']['code'])
        print(answer['text'] or answer['diagnostic']['message'])
        print()
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True,type=Path)
    result=build(p.parse_args().output)
    return 0 if result['read_only_queries'] else 1


if __name__=='__main__':raise SystemExit(main())
