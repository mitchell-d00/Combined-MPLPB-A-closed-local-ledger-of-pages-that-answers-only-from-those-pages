"""Post-run exact kernel and original-byte audit; no semantic answer-key input."""
import json,tempfile,sys
from pathlib import Path
sys.path.insert(0,str(Path.cwd()))
from tools.unprepared_sources import import_corpus
from tools.source_roundtrip import original_passage
from mplpb_answers.passages import PassageIndex
from mplpb_answers.evidence_contract import pin
from mplpb_answers import documentary_verify as kernel

import argparse
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument("--runs", required=True, type=Path)
parser.add_argument("--output", required=True, type=Path)
args=parser.parse_args()
rows=[]
for family,corpus in [('original','evaluation/unprepared-originals/2026-11-16'),('government','evaluation/unprepared-originals/2026-11-16-followup/unfamiliar')]:
    corpus=Path(corpus)
    run=args.runs/family/'after'
    with tempfile.TemporaryDirectory() as tmp:
        ledger=Path(tmp)/'ledger';receipt=import_corpus(corpus,ledger)
        assert receipt==json.loads((run/'import-receipt.json').read_text())
        for file in sorted(run.glob('*.json')):
            result=json.loads(file.read_text())
            if 'case_id' not in result:continue
            from tools.unprepared_challenge import code_pins
            assert result['implementation_sha256']==code_pins(Path.cwd()), 'Run the audit under the pinned implementation'
            answer=result['answer']
            if not answer['claims']:continue
            index=PassageIndex(ledger,result['question'])
            for claim in answer['claims']:
                cs=claim['citations'];first=cs[0];relation=claim.get('proposition',{}).get('relation')
                kind='action_statement'
                if relation=='source_reports_instruction':
                    kind='letter_instruction';end=cs[1]['body_end']
                else:end=first['body_end']
                if relation=='exact_wording_comparison':kind='comparison_completion' if claim['proposition'].get('question_obligations_verified') else 'wording_comparison'
                proposal={'kind':kind,'source_id':first['source_id'],'path':first['path'],'hash':first['hash'],
                          'start':first['body_start'],'end':end,'quote':None}
                from mplpb_answers.body_text import body_text
                body=body_text(next(r for r in index.records if r.path==first['path']).body_html)
                proposal['quote']=body[proposal['start']:end]
                if relation=='exact_wording_comparison':
                    other=cs[1];proposal['other']={'source_id':other['source_id'],'path':other['path'],'hash':other['hash'],
                           'start':other['body_start'],'end':other['body_end'],'quote':other['quote']}
                checked=kernel.check(index,[proposal]);matches=[p for p in checked['proofs'] if pin(p)==claim['proof_sha256']]
                assert len(matches)==1,(result['case_id'],checked['rejected'])
                raw=[original_passage(corpus,receipt,cite) for cite in cs]
                assert all(r['round_trip_quote_fidelity'] for r in raw)
                rows.append({'case_id':result['case_id'],'proof_sha256':claim['proof_sha256'],
                             'fresh_kernel_match':True,'source_support_scope':claim['support_scope'],
                             'historical_truth_verified':False,'original_passages':raw})
args.output.open('x').write(json.dumps({'schema':'solo-certificate-fidelity-v1','independent_human_validation':'NOT RUN','source_claims_checked':len(rows),'source_citations_checked':sum(len(r['original_passages']) for r in rows),'rows':rows},indent=2)+'\n')
print('Checked source claims/citations:',len(rows),sum(len(r['original_passages']) for r in rows))
