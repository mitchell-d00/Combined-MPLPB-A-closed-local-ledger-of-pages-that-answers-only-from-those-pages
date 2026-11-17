"""Target accounting after the existing two-reviewer/adjudication validator.

No runtime execution or gold access. Human identity/independence are participant
attestations, not authenticated by software. Missing evaluation stays NOT RUN.
"""
import argparse
import json
import math
from pathlib import Path
from tools.unprepared_challenge import score_reviews,read,digest,save

TARGETS={'answerable_question_accuracy':.80,'relationship_precision':.95,
         'relationship_recall':.75,'unsupported_question_refusal_accuracy':.95,
         'currently_eligible_exact_citation_rate':1.0,'minimum_questions':200,'minimum_domains':3}


def proportion(successes,total):
    if type(successes) is not int or type(total) is not int or not 0<=successes<=total:raise ValueError('Invalid observed counts')
    if not total:return {'numerator':successes,'denominator':total,'estimate':None,'wilson_95':None}
    z=1.959963984540054;p=successes/total;den=1+z*z/total
    middle=(p+z*z/(2*total))/den
    margin=z*math.sqrt(p*(1-p)/total+z*z/(4*total*total))/den
    return {'numerator':successes,'denominator':total,'estimate':p,'wilson_95':[max(0,middle-margin),min(1,middle+margin)]}


def protocol():
    return {'schema':'historical-target-protocol-v1','status':'NOT RUN','targets':TARGETS,
        'independent_questions':None,'independent_human_review':'NOT RUN','adjudication':'NOT RUN',
        'requirements':['Freeze implementation, budgets, source hashes and salt-sealed private expected annotations before runtime.',
            'Use independently authored unseen questions across at least three domains; existing development questions are ineligible.',
            'Use existing fail-closed study sandbox and unchanged source importer; expected answers never enter runtime.',
            'Run baseline, updated, BM25 and keyword under identical source access and budgets; retain every failure and timeout.',
            'Prepare complete packets using tools.unprepared_challenge; two real reviewers and bound adjudication assess all cases.',
            'After output freeze, unseal answerability/domain annotations and pass the existing review validator before target accounting.'],
        'metrics':{k:None for k in TARGETS if not k.startswith('minimum')},
        'critical_false_support_count':None,'critical_false_support_upper_95':None,
        'notice':'Targets are proposed, not achieved. Synthetic truth fixtures do not satisfy independent historical evaluation.'}


def assess(packets,reviews,annotations,custody,adjudication=None):
    scored=score_reviews(packets,reviews,adjudication)
    if scored['status']=='adjudication_required':return scored
    labels=read(annotations);seal=read(custody)
    if digest(labels)!=seal.get('sealed_expected_sha256'):raise ValueError('Expected annotations differ from the pre-run custody seal')
    if not seal.get('question_author') or not seal.get('custodian') or not seal.get('unseen_attestation'):raise ValueError('External authorship/custody attestation required')
    rows=labels.get('cases',[]);ids={r['case_id'] for r in rows}
    template=read(Path(packets)/'review-template.json');expected={i['case_id'] for i in template['items']}
    if len(ids)!=len(rows) or ids!=expected or any(type(r.get('answerable')) is not bool or not r.get('domain') for r in rows):raise ValueError('Complete unique answerability/domain annotations required')
    labels={r['case_id']:r for r in rows};documents=[read(p) for p in reviews];by_review=[{(i['arm'],i['case_id']):i for i in d['items']} for d in documents]
    chosen=by_review[0].copy()
    if adjudication:
        adj=read(adjudication)
        for key in chosen:
            selected=adj.get('accepted_review_sha256',{}).get(':'.join(key))
            if selected in scored['review_sha256']:chosen[key]=by_review[scored['review_sha256'].index(selected)][key]
    arms={}
    for arm,summary in scored['arms'].items():
        values=[v for (a,_),v in chosen.items() if a==arm];answerable=[v for v in values if labels[v['case_id']]['answerable']];unsupported=[v for v in values if not labels[v['case_id']]['answerable']]
        rel=summary['relationship'];metrics={
            'answerable_question_accuracy':proportion(sum(v['outcome']=='successful' for v in answerable),len(answerable)),
            'unsupported_question_refusal_accuracy':proportion(sum(v['appropriate_refusal'] is True and v['unsupported_answer'] is False for v in unsupported),len(unsupported)),
            'relationship_precision':None if rel['tp'] is None else proportion(rel['tp'],rel['tp']+rel['fp']),
            'relationship_recall':None if rel['recall'] is None else proportion(rel['tp'],rel['tp']+rel['fn']),
            'currently_eligible_exact_citation_rate':None}
        # Review citation validation is not a final serving-state recheck. Do
        # not silently convert it into the current-eligibility target metric.
        false=sum(v['unsupported_answer'] is True for v in values)
        arms[arm]={'metrics':metrics,'reviewed_cases':len(values),'unassessed':sum(v['outcome']=='unassessed' for v in values),
                   'unsupported_answer_cases':false,'unsupported_case_wilson_95':proportion(false,len(values)),
                   'zero_observed_unsupported_one_sided_95_upper':1-.05**(1/len(values)) if values and false==0 else None,
                   'outcomes':summary['outcomes'],'critical_false_support_count':None}
    return {'schema':'historical-target-accounting-v1','status':'participant_attested_review_accounting',
        'targets':TARGETS,'arms':arms,'question_count':len(labels),'domains':sorted({r['domain'] for r in labels.values()}),
        'minimum_sample_satisfied':len(labels)>=200 and len({r['domain'] for r in labels.values()})>=3,
        'annotations_sha256':digest(read(annotations)),'custody_sha256':digest(seal),'review_validation':scored,
        'reviewer_identity_authenticated':False,'independence_verified':False,'historical_truth_independently_verified':False,
        'notice':'Intervals are descriptive binomial intervals; clustered relationships and domains need further statistical review. Zero observed errors is not universal zero risk. Software does not authenticate independent humans.'}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--packets');p.add_argument('--reviews',nargs='+');p.add_argument('--annotations');p.add_argument('--custody');p.add_argument('--adjudication');p.add_argument('--output',required=True);a=p.parse_args()
    result=assess(a.packets,a.reviews,a.annotations,a.custody,a.adjudication) if a.packets else protocol()
    save(a.output,result)


if __name__=='__main__':main()
