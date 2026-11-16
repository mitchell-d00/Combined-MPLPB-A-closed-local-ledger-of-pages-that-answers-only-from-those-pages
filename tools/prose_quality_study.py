"""Source-linked developer assessment support; never independent human scoring.

Frozen runtime evaluation stays in unprepared_challenge. This post-run tool
inventories proposed semantic associations and retains every manual label.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
from tools.unprepared_challenge import read,save,summary,digest


def inventory(studies,output):
    unique={};runs=[]
    for corpus,run in studies:
        corpus=Path(corpus);run=Path(run);summary(corpus,run)
        receipt=read(run/'run-receipt.json');originals={x['id']:x for x in read(run/'import-receipt.json')['records']}
        runs.append({'corpus':str(corpus),'run':str(run),'receipt_sha256':hashlib.sha256((run/'run-receipt.json').read_bytes()).hexdigest()})
        for entry in receipt['cases']:
            out=read(run/(entry['id']+'.json'))
            pack=out.get('investigation',{}).get('prose_candidates',{}).get('information_map',{}).get('proposed_reconstruction',{})
            for kind,name in [('proposition','propositions'),('connection','connections')]:
                for item in pack.get(name,[]):
                    ev=item['evidence'][0];original=originals[ev['source_id']]
                    identity=[original['original_sha256'],item.get('predicate_start'),item['kind'],item['value'],
                              [(e['source_id'],e['body_start'],e['body_end']) for e in item['evidence']]]
                    key=hashlib.sha256(json.dumps(identity,sort_keys=True).encode()).hexdigest()
                    if key not in unique:
                        unique[key]={'review_key':key,'short_id':('P' if kind=='proposition' else 'C')+str(len(unique)+1).zfill(3),
                            'kind':kind,'corpus':corpus.name,'original_id':original['original_id'],'original_url':original['original_url'],
                            'original_sha256':original['original_sha256'],'value':item['value'],'candidate_kind':item['kind'],
                            'evidence':item['evidence'],'occurrences':[]}
                    unique[key]['occurrences'].append({'case_id':entry['id'],'mapping_id':item['mapping_id']})
    value={'schema':'developer-proposition-review-inventory-v1','assessment_status':'PENDING',
        'assessment_type':'Codex developer semantic inspection, NOT independent human review','runs':runs,'items':list(unique.values())}
    save(output,value);return value


def score(inventory_path,assessment_path):
    inv=read(inventory_path);assessment=read(assessment_path)
    if assessment['inventory_sha256']!=hashlib.sha256(Path(inventory_path).read_bytes()).hexdigest():raise ValueError('Assessment inventory differs')
    if assessment.get('independent_review')!='NOT RUN':raise ValueError('Developer judgments cannot be independent human evaluation')
    expected={i['review_key']:i for i in inv['items']};labels=assessment['items']
    if len(labels)!=len(expected) or {x['review_key'] for x in labels}!=set(expected):raise ValueError('Every unique interpretation needs one retained assessment')
    allowed={'correct','incorrect','unresolved','irrelevant'}
    for row in labels:
        if row['label'] not in allowed or not row.get('rationale'):raise ValueError('Missing semantic judgment/rationale')
        if row['evidence']!=expected[row['review_key']]['evidence']:raise ValueError('Assessment evidence differs')
    counts=Counter(x['label'] for x in labels);tp=counts['correct'];fp=counts['incorrect'];n=len(labels)
    return {'schema':'developer-proposition-score-v1','scope':assessment['scope'],'assessor':assessment['assessor'],
        'unique_interpretations':n,'occurrence_count':sum(len(i['occurrences']) for i in inv['items']),
        'unique_labels':dict(counts),'source_consistency_precision_among_decided':tp/(tp+fp) if tp+fp else None,
        'correct_fraction_of_all_proposals':tp/n if n else None,
        'incorrect_candidate_count':fp,'irrelevant_connection_count':counts['irrelevant'],
        'historical_relationship_false_positive_rate':None,'historical_relationship_recall':None,
        'metric_limit':'No exhaustive historical negative opportunities or complete reference graph. Precision describes developer-assessed source consistency only; unresolved/irrelevant counts stay visible.',
        'independent_human_evaluation':'NOT RUN','human_labeling_seconds':None,
        'inventory_sha256':hashlib.sha256(Path(inventory_path).read_bytes()).hexdigest(),
        'assessment_sha256':hashlib.sha256(Path(assessment_path).read_bytes()).hexdigest()}


def main():
    p=argparse.ArgumentParser(description=__doc__);s=p.add_subparsers(dest='command',required=True)
    a=s.add_parser('inventory');a.add_argument('--study',action='append',nargs=2,metavar=('CORPUS','RUN'),required=True);a.add_argument('--output',required=True)
    b=s.add_parser('score');b.add_argument('inventory');b.add_argument('assessment');b.add_argument('--output',required=True)
    args=p.parse_args()
    if args.command=='inventory':inventory(args.study,args.output)
    else:save(args.output,score(args.inventory,args.assessment))


if __name__=='__main__':main()
