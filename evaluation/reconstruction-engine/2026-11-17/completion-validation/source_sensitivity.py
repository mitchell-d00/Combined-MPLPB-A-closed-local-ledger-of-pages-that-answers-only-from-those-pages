"""Development sensitivity experiment on temporary imported copies, not gold labels."""
import argparse,json,tempfile,time
from pathlib import Path
from tools.unprepared_sources import import_corpus,verify
from mplpb_combined.ledger import revise
from mplpb_answers.pipeline import answer_query

def run(corpus):
    corpus=Path(corpus);verify(corpus)
    question=next(c['question'] for c in json.loads((corpus/'questions.json').read_text())['cases'] if c['id']=='H05')
    observations=[];start=time.monotonic()
    for kind in ['unaltered','alter_source_author','alter_referenced_work']:
        with tempfile.TemporaryDirectory() as temp:
            ledger=Path(temp)/'ledger';receipt=import_corpus(corpus,ledger)
            if kind!='unaltered':
                from mplpb_combined.ledger import Ledger
                records=Ledger(ledger).records
                if kind=='alter_source_author':
                    r=next(r for r in records if 'reconstruction of Thomas Jefferson' in r.body_html)
                    body=r.body_html.replace('reconstruction of Thomas Jefferson','reconstruction of Thomas Hale')
                else:
                    r=next(r for r in records if 'parchment Declaration of Independence' in r.body_html)
                    body=r.body_html.replace('parchment Declaration of Independence','parchment Harbor Charter')
                revise(ledger,r.id,body_html=body,origin='machine',note='Explicit temporary source-sensitivity fixture; not a historical correction')
            answer=answer_query(ledger,question).contract
            assert answer['answer_supported'] is (kind=='unaltered')
            observations.append({'mutation':kind,'answer':answer,'scope':'Temporary copied ledger only; original frozen bytes unchanged. Not an independently judged historical result.'})
    verify(corpus)
    return {'schema':'source-comparison-sensitivity-v1','question':question,'observations':observations,'all_controls_passed':True,
            'original_bytes_unchanged':True,'wall_seconds':time.monotonic()-start,'independent_human_review':'NOT RUN','historical_truth_independently_verified':False}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--corpus',required=True);p.add_argument('--output',required=True);a=p.parse_args()
    with Path(a.output).open('x') as f:json.dump(run(a.corpus),f,indent=2)
