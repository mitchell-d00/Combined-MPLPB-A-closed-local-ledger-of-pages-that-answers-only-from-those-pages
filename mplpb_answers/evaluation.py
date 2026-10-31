"""Pinned human scoring, selective-risk curves and explicit release evidence gates.

Document identity, matching quotations, model confidence and fixture success are
never silently converted into semantic answer correctness.
"""
import copy
import math
from .evidence_contract import pin, ReaderError, shape

RETURNED = {'supported_answer', 'model_assisted_answer', 'partial_answer'}
DEFAULT_POLICY = {'min_reviewed_returns': 200, 'min_domains': 3,
                  'min_complete_answerable_coverage': 0.6, 'max_error_upper95': 0.02}


def seal_report(report):
    result = copy.deepcopy(report)
    result.pop('run_sha256', None)
    result['run_sha256'] = pin(result)
    return result


def verify_report(report):
    if seal_report(report)['run_sha256'] != report.get('run_sha256'):
        raise ValueError('Evaluation report differs from its run pin')
    ids = [r['id'] for r in report['rows']]
    if len(ids) != len(set(ids)):
        raise ValueError('Evaluation IDs must be unique')


def review_template(report):
    verify_report(report)
    return {'run_sha256': report['run_sha256'], 'reviewers': [],
            'judgments': [{'id': r['id'], 'correct': None, 'citation_complete': None,
                           'complete': None, 'reason': ''} for r in report['rows'] if r['answer']['kind'] in RETURNED]}


def _upper95(errors, n):
    if n == 0:
        return None
    # Two-sided 95% Wilson upper limit, not a guarantee under dependence or shift.
    z = 1.959963984540054
    p = errors/n
    return (p+z*z/(2*n)+z*math.sqrt(p*(1-p)/n+z*z/(4*n*n)))/(1+z*z/n)


def _metrics(rows, judgments):
    returned = [r for r in rows if r['answer']['kind'] in RETURNED]
    reviewed = [r for r in returned if r['id'] in judgments]
    assisted = [r for r in reviewed if r['answer']['kind'] in {'model_assisted_answer', 'partial_answer'}]
    assisted_wrong = sum(not (judgments[r['id']]['correct'] and judgments[r['id']]['citation_complete']) for r in assisted)
    wrong = sum(not (judgments[r['id']]['correct'] and judgments[r['id']]['citation_complete']) for r in reviewed)
    answerable = [r for r in rows if r['answerability'] == 'answerable']
    full = sum(r['answer']['kind'] != 'partial_answer' and judgments[r['id']]['correct']
               and judgments[r['id']]['citation_complete'] and judgments[r['id']]['complete']
               for r in reviewed if r['answerability'] == 'answerable')
    recalls = [r['retrieval_recall'] for r in answerable if r.get('retrieval_recall') is not None]
    return {'questions': len(rows), 'returns': len(returned), 'reviewed_returns': len(reviewed),
            'unreviewed_returns': len(returned)-len(reviewed), 'wrong_reviewed_returns': wrong,
            'reviewed_assisted_returns': len(assisted), 'wrong_reviewed_assisted_returns': assisted_wrong,
            'assisted_error_upper95_wilson': _upper95(assisted_wrong, len(assisted)),
            'reviewed_return_precision': 1-wrong/len(reviewed) if reviewed else None,
            'reviewed_error_upper95_wilson': _upper95(wrong, len(reviewed)),
            'answerable_questions': len(answerable), 'correct_complete_answers': full,
            'complete_answerable_coverage': full/len(answerable) if answerable else None,
            'partial_answers': sum(r['answer']['kind'] == 'partial_answer' for r in rows),
            'clarifications': sum(r['answer']['kind'] == 'clarify' for r in rows),
            'conflicts': sum(r['answer']['kind'] == 'conflict' for r in rows),
            'abstentions': sum(r['answer']['kind'] == 'abstain' for r in rows),
            'mean_gold_passage_retrieval_recall': sum(recalls)/len(recalls) if recalls else None,
            'strict_supported_returns': sum(r['answer']['answer_supported'] for r in rows)}


def score(report, review, policy=None):
    verify_report(report)
    policy = dict(report.get('release_policy', DEFAULT_POLICY) if policy is None else policy)
    if report.get('release_policy_sha256') != pin(policy):
        raise ValueError('Scoring must use the release policy frozen before this run')
    if set(policy) != set(DEFAULT_POLICY) or any(type(v) not in (int, float) or not math.isfinite(v) for v in policy.values()):
        raise ValueError('Release policy must contain finite, explicit thresholds')
    if (type(policy['min_reviewed_returns']) is not int or policy['min_reviewed_returns'] < 1
            or type(policy['min_domains']) is not int or policy['min_domains'] < 1
            or not 0 <= policy['min_complete_answerable_coverage'] <= 1 or not 0 < policy['max_error_upper95'] < 1):
        raise ValueError('Invalid release policy thresholds')
    if review.get('run_sha256') != report['run_sha256'] or not isinstance(review.get('judgments'), list):
        raise ValueError('Human judgments must identify the exact evaluated run')
    rows = {r['id']: r for r in report['rows']}
    judgments, seen = {}, set()
    for row in review['judgments']:
        shape(row, 'id correct citation_complete complete reason')
        if row['id'] not in rows or row['id'] in seen or rows[row['id']]['answer']['kind'] not in RETURNED:
            raise ValueError('Judgment IDs must identify unique returned answers')
        seen.add(row['id'])
        if any(row[k] is None for k in ('correct', 'citation_complete', 'complete')):
            continue
        if any(type(row[k]) is not bool for k in ('correct', 'citation_complete', 'complete')) or not isinstance(row['reason'], str) or not row['reason'].strip():
            raise ValueError('Completed judgments require booleans and a review reason')
        judgments[row['id']] = row
    metrics = _metrics(report['rows'], judgments)
    domains = {name: _metrics([r for r in report['rows'] if r['domain'] == name], judgments)
               for name in sorted({r['domain'] for r in report['rows']})}
    curve = []
    for threshold in [n/10 for n in range(11)]:
        selected = [r for r in report['rows'] if r['answer']['kind'] not in RETURNED
                    or r['answer']['kind'] == 'supported_answer'
                    or (type(r['answer'].get('confidence')) in (int, float) and r['answer']['confidence'] >= threshold)]
        point = _metrics(selected, judgments)
        point['threshold'] = threshold
        point['overall_return_coverage'] = point['returns']/len(report['rows']) if report['rows'] else None
        # The denominator remains the whole original answerable test set.
        point['complete_answerable_coverage'] = point['correct_complete_answers']/metrics['answerable_questions'] if metrics['answerable_questions'] else None
        curve.append(point)
    blocks = []
    if report.get('role') != 'test':
        blocks.append('A fresh frozen test set is required; development/calibration data cannot certify release.')
    if report.get('mode') != 'assisted' or not report.get('reader', {}).get('live_inference'):
        blocks.append('No live local-reader evaluation is recorded; scripted fixtures do not establish model accuracy.')
    if not isinstance(report.get('calibration_run_sha256'), str) or not report['calibration_run_sha256'].startswith('sha256:'):
        blocks.append('A frozen prior calibration-run reference is required; confidence is not calibrated by its numeric value.')
    if not review.get('reviewers'):
        blocks.append('Human evidence review has not been attributed.')
    if metrics['unreviewed_returns']:
        blocks.append('Some returned answers lack complete human judgments.')
    if metrics['reviewed_assisted_returns'] < policy['min_reviewed_returns']:
        blocks.append('Too few reviewed model-assisted returns for the declared policy.')
    if len(domains) < policy['min_domains']:
        blocks.append('Too few evaluated domains for the declared policy.')
    for domain, data in domains.items():
        coverage = data['complete_answerable_coverage']
        upper = data['assisted_error_upper95_wilson']
        if coverage is None or coverage < policy['min_complete_answerable_coverage']:
            blocks.append('Insufficient complete answerable coverage in '+domain+'.')
        if upper is None or upper > policy['max_error_upper95']:
            blocks.append('Insufficient evidence for the declared error bound in '+domain+'.')
    return {'run_sha256': report['run_sha256'], 'judgments_sha256': pin(review), 'metrics': metrics,
            'domains': domains, 'risk_coverage_curve': curve, 'policy': policy,
            'release_assessment': 'blocked' if blocks else 'eligible_for_human_release_review',
            'blockers': blocks, 'independence_verified': False,
            'notice': 'Human labels are supplied declarations. Wilson intervals assume a suitable sample; dependence, labeling errors and domain shift invalidate general guarantees. Curves are diagnostic; choose thresholds using calibration data, never this final test set.'}
