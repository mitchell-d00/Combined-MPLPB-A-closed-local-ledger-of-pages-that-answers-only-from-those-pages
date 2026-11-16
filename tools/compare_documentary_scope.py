"""Audit two frozen original-record runs without awarding semantic credit.

Uses the existing frozen harness unchanged. Review artifacts contain candidate
interpretations and exact raw-byte mappings, never an automatic correctness vote.
"""
import argparse
from pathlib import Path
from tools.unprepared_challenge import read, save, sha, summary
from tools.source_roundtrip import original_passage

SEMANTIC_METRICS = ('source_retrieval_recall_at_k', 'event_identity_precision',
    'event_identity_recall', 'relationship_precision', 'relationship_recall',
    'false_positive_relationship_rate', 'false_supported_answer_rate',
    'correction_identification_accuracy', 'temporal_relationship_accuracy',
    'appropriate_refusal_rate', 'incorrect_refusal_rate', 'human_review_seconds',
    'human_correction_seconds')


def load_run(corpus, directory):
    directory=Path(directory); receipt=read(directory/'run-receipt.json')
    # summary verifies the frozen seal, original bytes, receipt and per-case pins.
    totals=summary(corpus,directory)
    rows={}
    for entry in receipt['cases']:
        path=directory/(entry['id']+'.json')
        if sha(path.read_bytes())!=entry['sha256']:raise ValueError('Changed case output')
        rows[entry['id']]=read(path)
    return receipt,totals,rows,read(directory/'import-receipt.json')


def propositions(row):
    return row.get('investigation',{}).get('prose_candidates',{}).get('information_map',{}).get('proposed_reconstruction',{}).get('propositions',[])


def compare(corpus, before, after, output):
    corpus=Path(corpus); output=Path(output)
    b,bs,br,bi=load_run(corpus,before); a,as_,ar,ai=load_run(corpus,after)
    for field in ('freeze_sha256','harness_sha256','protocol_sha256','corpus_sha256','questions_sha256'):
        if b[field]!=a[field]:raise ValueError('Comparison inputs differ: '+field)
    if set(br)!=set(ar):raise ValueError('Case coverage differs')
    if b['arm']!=a['arm']:raise ValueError('Use identical execution modes for native comparisons')
    output.mkdir(parents=True,exist_ok=False)
    changes=[]; audits=[]
    for case_id in br:
        key=lambda f:(f['evidence'][0]['source_id'],f['evidence'][0]['hash'],f['predicate_start'],f['value']['action'])
        old={key(f):f for f in propositions(br[case_id])}
        new={key(f):f for f in propositions(ar[case_id])}
        for k in sorted(set(old)|set(new)):
            prior=old.get(k); current=new.get(k)
            # Additive unknown/default fields alone are not interpreted as gains.
            fields=('actor','modality','passive_agent_candidate','assertion_layer','governing_predicates','date_candidates')
            defaults={'assertion_layer':'direct_source_assertion_candidate','governing_predicates':[]}
            before_value={f:prior['value'].get(f,defaults.get(f)) for f in fields} if prior else None
            after_value={f:current['value'].get(f,defaults.get(f)) for f in fields} if current else None
            if before_value==after_value:continue
            changes.append({'case_id':case_id,'question':ar[case_id]['question'],
                'before':prior,'after':current,'before_interpretation':before_value,'after_interpretation':after_value,
                'semantic_correctness':None,'source_support_established':False})
        # Verify all new findings, not just selected favorable deltas.
        rich=ar[case_id].get('investigation',{}).get('prose_candidates',{}).get('information_map',{}).get('proposed_reconstruction',{})
        for group in ('propositions','connections','qualifications'):
            for finding in rich.get(group,[]):
                if finding['answer_supported'] or finding['content_truth_verified']:raise ValueError('Unexpected authority promotion')
                original=[original_passage(corpus,ai,e) for e in finding['evidence']]
                audits.append({'case_id':case_id,'mapping_id':finding['mapping_id'],'original_passages':original})
    def costs(rows):
        complete=[r['measurements'] for r in rows.values() if r.get('measurements')]
        return {'completed':len(complete),'failed_or_partial':len(rows)-len(complete),
            'cpu_seconds':sum(c['cpu_seconds'] for c in complete) if complete else None,
            'wall_seconds':sum(c['wall_seconds'] for c in complete) if complete else None,
            'peak_process_rss_bytes':max((c['peak_process_rss_bytes'] for c in complete),default=None),
            'source_bytes_read':sum(c['source_html_bytes_read'] for c in complete) if complete else None}
    report={'schema':'documentary-scope-comparison-v1','before_revision':b['implementation_commit'],
        'after_revision':a['implementation_commit'],'before_receipt_sha256':sha((Path(before)/'run-receipt.json').read_bytes()),
        'after_receipt_sha256':sha((Path(after)/'run-receipt.json').read_bytes()),
        'before_costs':costs(br),'after_costs':costs(ar),'before_summary':bs,'after_summary':as_,
        'changed_interpretations':changes,'new_findings_original_mapping_checked':len(audits),
        'metrics':{m:None for m in SEMANTIC_METRICS},'independent_review':'NOT RUN',
        'notice':'Changed interpretation counts and byte fidelity do not establish semantic improvement. Repeated appearances are not independent events.'}
    save(output/'comparison.json',report);save(output/'original-mapping-audit.json',audits)
    review={'status':'NOT RUN','reviewer_id':None,'reviewer_is_human':None,'independence_attestation':None,
        'comparison_sha256':sha((output/'comparison.json').read_bytes()),
        'instruction':'Inspect every source and both full run outputs, not just deltas. Mark regressions and omissions. Use existing unprepared_challenge score protocol for full semantic scoring; this delta sheet alone is insufficient.',
        'items':[{'case_id':c,'outcome':None,'correct_relationships':None,'false_relationships':None,'missing_relationships':None,
                  'unsupported_answer':None,'appropriate_refusal':None,'source_citations':[],'rationale':None,'review_seconds':None} for c in br]}
    for reviewer in (1,2):save(output/('reviewer-'+str(reviewer)+'.json'),review)
    save(output/'adjudication.json',{'status':'NOT RUN','adjudicator_id':None,'review_pins':None,'disagreements':None,'decisions':None,'seconds':None})
    return report


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('corpus');p.add_argument('before');p.add_argument('after');p.add_argument('--output',required=True)
    args=p.parse_args();compare(args.corpus,args.before,args.after,args.output)


if __name__=='__main__':main()
