"""Replay frozen suggestions and freshly verify every native claim/source quote.

Run with --implementation pointing at the exact experimental runtime. Fidelity
and finite-rule verification are separate from semantic relationship accuracy.
"""
import argparse
import json
from pathlib import Path
import sys
import tempfile
import time


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('study',type=Path)
    p.add_argument('--implementation',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();implementation=a.implementation.resolve();study=a.study.resolve()
    sys.path.insert(0,str(implementation))
    from tools.unprepared_challenge import read,save,code_pins,sha
    from tools.unprepared_sources import import_corpus
    from tools.source_roundtrip import original_passage
    from mplpb_work.sorter_suggestions import verify_suggestions
    from mplpb_answers.passages import PassageIndex
    from mplpb_answers.body_text import body_text
    from mplpb_answers.evidence_contract import pin
    from mplpb_answers import documentary_verify as kernel
    protocol=read(study/'options-protocol.json')
    if code_pins(implementation)!=protocol['runtime_sha256']:raise ValueError('Use exact frozen runtime')
    if not Path(kernel.__file__).resolve().is_relative_to(implementation):raise ValueError('Wrong verifier imported')
    start=time.perf_counter();cpu=time.process_time();rows=[];replays=[]
    for family,path in [('original','evaluation/unprepared-originals/2026-11-16'),('government','evaluation/unprepared-originals/2026-11-16-followup/unfamiliar')]:
        corpus=implementation/path
        with tempfile.TemporaryDirectory() as tmp:
            ledger=Path(tmp)/'ledger';imported=import_corpus(corpus,ledger)
            if imported!=read(study/family/'import-receipt.json'):raise ValueError('Import changed')
            for arm in ['sorter-alone','synonyms','synonyms-relater']:
                for case in read(corpus/'questions.json')['cases']:
                    result=read(study/family/arm/(case['id']+'.json'))
                    if result.get('implementation_sha256')!=protocol['runtime_sha256']:raise ValueError('Worker reader differs')
                    review_file=study/family/arm/(case['id']+'-review.json')
                    if review_file.exists():
                        stored=read(review_file)
                        payload={k:v for k,v in stored.items() if k not in {'base_graph_sha256','preprocessing_wall_seconds','preprocessing_cpu_seconds'}}
                        payload['sorter_graph']=read(study/family/'compare.json')
                        verify_suggestions(payload,study/family/'sorter-inputs')
                        replays.append({'case_id':case['id'],'arm':arm,'file_sha256':sha(review_file.read_bytes()),
                            'ranked_hits':len(payload['ranked_hits']),'links':len(payload['candidate_links']),
                            'all_source_spans_scores_links_replayed':True,'semantic_accuracy_established':False})
                    claims=result.get('answer',{}).get('claims',[])
                    if not claims:continue
                    index=PassageIndex(ledger,case['question'])
                    for claim in claims:
                        cs=claim['citations'];first=cs[0];relation=claim.get('proposition',{}).get('relation')
                        kind='action_statement';end=first['body_end']
                        if relation=='source_reports_instruction':kind='letter_instruction';end=cs[1]['body_end']
                        if relation=='exact_wording_comparison':kind='comparison_completion' if claim['proposition'].get('question_obligations_verified') else 'wording_comparison'
                        record=next(r for r in index.records if r.path==first['path']);body=body_text(record.body_html)
                        proposal={'kind':kind,'source_id':first['source_id'],'path':first['path'],'hash':first['hash'],
                            'start':first['body_start'],'end':end,'quote':body[first['body_start']:end]}
                        if relation=='exact_wording_comparison':
                            other=cs[1];proposal['other']={'source_id':other['source_id'],'path':other['path'],'hash':other['hash'],
                                'start':other['body_start'],'end':other['body_end'],'quote':other['quote']}
                        checked=kernel.check(index,[proposal]);matches=[x for x in checked['proofs'] if pin(x)==claim['proof_sha256']]
                        if len(matches)!=1:raise ValueError('Fresh proof mismatch: '+case['id'])
                        raw=[original_passage(corpus,imported,e) for e in cs]
                        rows.append({'case_id':case['id'],'arm':arm,'fresh_kernel_match':True,
                            'proof_sha256':claim['proof_sha256'],'original_passages':raw,'historical_truth_verified':False})
    save(a.output,{'schema':'sorter-study-source-audit-v1','implementation':str(implementation),
        'runtime_sha256':protocol['runtime_sha256'],'claims_checked':len(rows),
        'citations_checked':sum(len(r['original_passages']) for r in rows),'suggestion_files_replayed':len(replays),
        'rows':rows,'replays':replays,'wall_seconds':time.perf_counter()-start,'cpu_seconds':time.process_time()-cpu,
        'scope':'Exact source/score/link replay and native independent kernel certificate plus original-byte roundtrip; not historical semantic review.',
        'independent_human_evaluation':'NOT RUN'})
    print('Verified claims/citations/review files:',len(rows),sum(len(r['original_passages']) for r in rows),len(replays))


if __name__=='__main__':main()
