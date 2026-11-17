"""Compare identical frozen runs, source support and measured costs, not truth."""
import argparse
from collections import Counter
import json
from pathlib import Path


def compare(root):
    root=Path(root);families={};changes=[];new_external=[]
    for family in ('original','government'):
        receipts={arm:json.loads((root/family/arm/'run-receipt.json').read_text()) for arm in ('before','after')}
        for field in ('corpus_sha256','questions_sha256','protocol_sha256','freeze_sha256',
                      'harness_sha256','import_receipt_sha256','case_count','execution_isolation'):
            if receipts['before'][field]!=receipts['after'][field]:raise ValueError('Comparison conditions differ: '+field)
        metrics={};cases={}
        for arm in ('before','after'):
            ds=[json.loads((root/family/arm/(case['id']+'.json')).read_text()) for case in receipts[arm]['cases']]
            if any(d['execution_status']!='completed' for d in ds):raise ValueError('Failed cases require explicit partial accounting')
            cases[arm]={d['case_id']:d for d in ds}
            metrics[arm]={'native_kinds':dict(Counter(d['answer']['kind'] for d in ds)),
                         'cpu_seconds':sum(d['measurements']['cpu_seconds'] for d in ds),
                         'wall_seconds':sum(d['measurements']['wall_seconds'] for d in ds),
                         'peak_worker_rss_bytes':max(d['measurements']['peak_process_rss_bytes'] for d in ds),
                         'source_html_bytes_read':sum(d['measurements']['source_html_bytes_read'] for d in ds),
                         'source_read_calls':sum(d['measurements']['source_read_calls'] for d in ds)}
        for ident,before in cases['before'].items():
            after=cases['after'][ident]
            if before['question']!=after['question']:raise ValueError('Question changed')
            a,b=before['answer'],after['answer']
            if (a['kind'],a['answer_supported'])!=(b['kind'],b['answer_supported']):
                changes.append({'case_id':ident,'before':a['kind'],'after':b['kind']})
            else:
                # Ignore proof-version pins, preserve meanings/excerpts and qualifications.
                stripped=lambda c:[{k:v for k,v in x.items() if k not in {'verification','proof_sha256'}} for x in c['claims']]
                if stripped(a)!=stripped(b):raise ValueError('Unchanged case claim meaning differs: '+ident)
            for claim in b['claims']:
                p=claim.get('proposition',{})
                for flag in ('dispatch_verified','receipt_verified','execution_verified','delivery_verified',
                             'instruction_event_truth_verified','actual_arrangement_independently_verified'):
                    if p.get(flag) is True:new_external.append({'case_id':ident,'flag':flag})
        families[family]=metrics
    return {'schema':'solo-frozen-comparison-v1','conditions_identical':True,'families':families,
            'native_support_changes':changes,'new_external_execution_or_delivery_claims':new_external,
            'human_semantic_accuracy':None,'human_review':'NOT RUN',
            'scope':'Native finite-kernel outcomes and measured isolated-worker resources; AI opinions scored separately.'}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('runs',type=Path);parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args();result=compare(args.runs)
    with args.output.open('x') as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps(result,indent=2))
