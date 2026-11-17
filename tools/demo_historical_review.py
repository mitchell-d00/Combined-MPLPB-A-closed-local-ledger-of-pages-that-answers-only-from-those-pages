"""Run a labelled synthetic historical-truth test through actual work rules.

No historical benchmark inputs, people or real independent reviewers are used.
The oracle is separate from source prose and is used only after review entries.
"""
import argparse
import json
from pathlib import Path
from mplpb_combined.ledger import write
from mplpb_work import WorkStore
from mplpb_work.model import OPERATIONS
from mplpb_work.store import digest
from mplpb_work.historical_review import enter_review,inspect_reviews


def run(output):
    output=Path(output);output.mkdir(parents=True,exist_ok=False)
    proposition='The expedition was delayed because of rain.'
    rec=write(output/'sources',doc_id='SYNTHETIC-1',title='Fictional expedition log',scope='synthetic fixture',
              body=proposition,when='1900-01-02T00:00Z')
    store,host=WorkStore.create(output/'work',{'fixture':output/'sources'},clock=lambda:1000)
    seats=['fixture-author','fixture-reviewer-a','fixture-reviewer-b'];tokens={}
    for seat in seats:
        tokens[seat]=store.assign(host,seat=seat,instance=seat+'-1',
            model={'name':seat,'provider':'synthetic-software-fixture','version':'1','context_policy_hash':'unknown'},
            contract={'operations':sorted(OPERATIONS),'tools':[],'scopes':['T1'],'share_with':seats,'profile':'internal','expires_at':2000},
            expected_head=store.head(host)['hash'])['credential']
    author=tokens[seats[0]]
    def put(identifier,kind,payload,deps=None):
        return store.put(author,id=identifier,kind=kind,payload=payload,dependencies=deps or {},visibility=seats,
                         expected_revision=0,expected_head=store.snapshot(author)['head'])
    put('T1','task',{'goal':'Test synthetic truth entry rules','criteria':['traceable fixture assessment'],'review_budget':4,'state':'open','acceptance':{}})
    put('E1','evidence',{'task':'T1','corpus':'fixture','source_id':rec.id,'source_hash':rec.hash_actual,'quote':proposition,'query':'expedition'})
    put('C1','claim',{'task':'T1','proposition':proposition,'basis':'observation','assessment':'proposed','assumptions':[],
                      'alternatives':[],'revisit_when':'Any source/review changes'},{'E1':1})
    for n,seat in enumerate(seats[1:],1):
        enter_review(store,tokens[seat],{'id':'R'+str(n),'claim_id':'C1','claim_revision':1,'reviewer_id':seat,
            'reviewer_kind':'synthetic_fixture','decision':'support','rationale':'Synthetic software test; no human review.',
            'independence_attestation':'Two fixture seats, not real independent reviewers.','evidence_ids':['E1'],
            'scope':'synthetic-expedition-v1 only','uncertainties':['No real historical truth evaluated']})
    oracle={'universe':'synthetic-expedition-v1','proposition':proposition,'truth_value':True}
    result=inspect_reviews(store,author,'C1',synthetic_oracle=oracle,oracle_sha256=digest(oracle))
    (output/'synthetic-oracle.json').write_text(json.dumps(oracle,indent=2)+'\n')
    (output/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    # No bearer/host credentials are written into the evidence packet.
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True);a=p.parse_args();r=run(a.output)
    print(json.dumps({'review_status':r['review_status'],'synthetic_fixture_truth_matches':r['synthetic_fixture_truth_matches'],
                      'historical_truth_independently_verified':False,'real_independent_review':'NOT RUN'},indent=2))


if __name__=='__main__':main()
