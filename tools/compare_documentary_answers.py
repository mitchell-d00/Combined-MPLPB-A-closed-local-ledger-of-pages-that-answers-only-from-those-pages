"""Compare frozen native answers and recheck documentary support certificates.

Counts typed, kernel-checked source assertions separately from full answers,
prose candidates, semantic accuracy and independently verified historical truth.
Never consumes expected answers during native execution or assigns human scores.
"""
import argparse
import json
from pathlib import Path
import tempfile
from tools.compare_documentary_scope import load_run
from tools.unprepared_challenge import code_pins,sha,save
from tools.unprepared_sources import import_corpus
from tools.source_roundtrip import original_passage
from mplpb_answers.body_text import body_text
from mplpb_answers.passages import PassageIndex
from mplpb_answers.evidence_contract import pin
from mplpb_answers import documentary_verify
from mplpb_combined.reader import PROFILES


def compare(corpus,before,after,output):
    corpus=Path(corpus);output=Path(output)
    b,bs,br,bi=load_run(corpus,before);a,as_,ar,ai=load_run(corpus,after)
    for key in ('freeze_sha256','harness_sha256','protocol_sha256','corpus_sha256','questions_sha256','import_receipt_sha256'):
        if b[key]!=a[key]:raise ValueError('Comparison inputs differ: '+key)
    if b['arm']!=a['arm'] or set(br)!=set(ar):raise ValueError('Execution modes/case coverage differ')
    if code_pins(Path(__file__).resolve().parents[1])!=a['implementation_sha256']:
        raise ValueError('Run the certificate audit from the exact updated implementation')
    output.mkdir(parents=True,exist_ok=False);rows=[];audit=[]
    with tempfile.TemporaryDirectory() as temp:
        ledger=Path(temp)/'ledger';receipt=import_corpus(corpus,ledger)
        for case in br:
            old=br[case].get('answer',{});new=ar[case].get('answer',{})
            claims=[c for c in new.get('claims',[]) if c.get('source_support_established')]
            if claims:
                question=ar[case]['question'];profile=PROFILES[new['documentary_support']['profile']]
                index=PassageIndex(ledger,question,profile);records={r.path:r for r in index.records};proposals=[]
                for claim in claims:
                    cites=claim['citations'];first=cites[0];record=records.get(first['path'])
                    if record is None:raise ValueError('Certificate source currently ineligible')
                    relation=claim['proposition']['relation']
                    same=[e for e in cites if e['path']==first['path']]
                    completion=bool(claim['proposition'].get('question_obligations_verified'))
                    start=first['body_start'] if completion else min(e['body_start'] for e in same)
                    end=first['body_end'] if completion else max(e['body_end'] for e in same)
                    text=body_text(record.body_html)
                    kind=('letter_instruction' if relation=='source_reports_instruction' else 'action_statement' if relation=='source_action_assertion'
                          else 'comparison_completion' if completion else 'wording_comparison' if relation=='exact_wording_comparison' else 'relationship_statement')
                    proposals.append({'kind':kind,'source_id':record.id,'path':record.path,'hash':record.hash_actual,
                                      'start':start,'end':end,'quote':text[start:end]})
                    if kind in {'wording_comparison','comparison_completion'}:
                        other=cites[1]
                        proposals[-1]['other']={'path':other['path'],'source_id':other['source_id'],'hash':other['hash'],
                                                'start':other['body_start'],'end':other['body_end'],'quote':other['quote']}
                checked=documentary_verify.check(index,proposals)
                if checked['status']!='checked':raise ValueError('Sources changed during certificate recheck')
                for claim in claims:
                    matches=[p for p in checked['proofs'] if pin(p)==claim['proof_sha256'] and p['proposition']==claim['proposition'] and p['citations']==claim['citations']]
                    if len(matches)!=1 or claim['historical_truth_independently_verified'] is not False:
                        raise ValueError('Certificate meaning/provenance differs from current kernel or overstates truth')
                    original=[original_passage(corpus,receipt,e) for e in claim['citations']]
                    audit.append({'case_id':case,'question':question,'claim':claim,'kernel_rechecked':True,
                                  'original_passages':original,'semantic_human_review':'NOT RUN'})
            rows.append({'case_id':case,'question':ar[case]['question'],'before_execution':br[case]['execution_status'],
                'after_execution':ar[case]['execution_status'],'before_kind':old.get('kind'),'after_kind':new.get('kind'),
                'before_supported_answer':old.get('answer_supported',False),'after_supported_answer':new.get('answer_supported',False),
                'before_checked_documentary_claims':sum(bool(c.get('source_support_established')) for c in old.get('claims',[])),
                'after_checked_documentary_claims':len(claims),'after_missing':new.get('missing',[]),
                'after_obligations':new.get('documentary_support',{}).get('obligations',[]),
                'semantic_correctness':None,'historical_truth_independently_verified':False})
    report={'schema':'checked-documentary-answer-comparison-v1','before_revision':b['implementation_commit'],
      'after_revision':a['implementation_commit'],'conditions_matched':True,'rows':rows,
      'before_summary':bs,'after_summary':as_,
      'before_supported_answers':sum(r['before_supported_answer'] for r in rows),
      'after_supported_answers':sum(r['after_supported_answer'] for r in rows),
      'before_checked_partial_answers':sum(r['before_kind']=='partial_answer' and r['before_checked_documentary_claims']>0 for r in rows),
      'after_checked_partial_answers':sum(r['after_kind']=='partial_answer' and r['after_checked_documentary_claims']>0 for r in rows),
      'kernel_rechecked_source_assertions':len(audit),'independent_human_review':'NOT RUN',
      'relationship_precision':None,'relationship_recall':None,'false_supported_answer_rate':None,
      'scope':'Checked documentary assertions under the finite kernel contract; source quotation, asserted historical events, and independently verified historical truth are distinct. Partial-claim counts are not semantic accuracy scores.'}
    save(output/'comparison.json',report);save(output/'certificate-audit.json',audit)
    template={'status':'NOT RUN','reviewer_id':None,'reviewer_is_human':None,'independence_attestation':None,
      'comparison_sha256':sha((output/'comparison.json').read_bytes()),'items':[
        {'case_id':r['case_id'],'assertion_meaning_correct':None,'question_part_answered':None,'false_source_support':None,
         'missing_or_misleading_qualification':None,'source_citations':[],'rationale':None,'review_seconds':None} for r in rows]}
    save(output/'reviewer-1.json',template);save(output/'reviewer-2.json',template)
    save(output/'adjudication.json',{'status':'NOT RUN','adjudicator_id':None,'review_pins':None,'decisions':None,'seconds':None})
    return report


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('corpus');p.add_argument('before');p.add_argument('after');p.add_argument('--output',required=True)
    args=p.parse_args();compare(args.corpus,args.before,args.after,args.output)


if __name__=='__main__':main()
