"""Compact retained-evidence dashboard. No new scoring or independent judgments."""
import argparse
import hashlib
import json
from pathlib import Path

METRICS=('supported_answer_precision','complete_answer_recall','correct_refusal_rate','citation_fidelity')


def row(label,revision,path,kind):
    path=Path(path);raw=path.read_bytes();data=json.loads(raw)
    result={'label':label,'revision':revision,'dataset':kind,'evidence_path':str(path),
            'evidence_sha256':hashlib.sha256(raw).hexdigest(),
            'metrics':dict.fromkeys(METRICS),'independent_semantic_review':'NOT RUN'}
    if kind=='synthetic_development':
        if data.get('schema')!='dpercent-v1-score':raise ValueError('Expected a retained D% score')
        cases=data['cases'];m=data['metrics'];complete=not m['execution_failures']
        positives=[r for r in cases if r['expected']=='answer'];negatives=[r for r in cases if r['expected']=='refuse']
        accepted=[r for r in cases if r.get('answer_supported') is True]
        correct=sum(r['outcome']=='detected_answer' for r in cases)
        refusals=sum(r['outcome']=='appropriate_refusal' for r in negatives)
        if (len(positives)!=m['answer_cases'] or len(negatives)!=m['refuse_cases'] or
                correct!=m['correct_complete_answers'] or refusals!=m['appropriate_refusals']):
            raise ValueError('Score rows and denominators disagree')
        result['counts']={'cases':len(cases),'answerable':len(positives),'unsupported':len(negatives),
                          'complete_correct':correct,'accepted':len(accepted),'execution_failures':m['execution_failures'],
                          'unscored_supported':m['unscored_supported']}
        if complete:
            result['metrics']={'supported_answer_precision':correct/len(accepted) if accepted and not m['unscored_supported'] else None,
                'complete_answer_recall':correct/len(positives) if positives else None,
                'correct_refusal_rate':refusals/len(negatives) if negatives else None,
                'citation_fidelity':sum(r.get('quotation_fidelity') is True for r in accepted)/len(accepted) if accepted else None}
        result['scope']='Developer-key results on frozen fiction. Citation metric is per accepted output at run time, not live serving eligibility or historical semantics.'
    elif kind=='authentic_development':
        if data.get('schema')!='article-preservation-study-v1':raise ValueError('Expected an original-record preservation report')
        result['counts']={'cases':data['cases'],'native_outcomes':data['native_outcomes'],'independently_answerable':None}
        result['scope']='Native outcome counts only; neither complete-answer recall nor refusal correctness is independently known.'
    else:raise ValueError('Unknown dataset type')
    return result


def render(document):
    lines=['# Archival inspection benchmark dashboard','','Last reviewed: 2026-11-19.','',
           'Synthetic development, authentic development and unseen independent evaluation are separate. Percentages below are developer-key measurements; they are not historical accuracy. Citation fidelity concerns exact source anchoring at run time, not historical truth or permanent eligibility.','',
           '| Version / revision | Dataset | Cases | Supported precision | Complete recall | Correct refusal | Citation fidelity |',
           '|---|---|---:|---:|---:|---:|---:|']
    for r in document['rows']:
        show=lambda v:'unmeasured' if v is None else str(round(100*v,2))+'%'
        lines.append('| '+r['label']+' / `'+r['revision'][:12]+'` | '+r['dataset']+' | '+str(r['counts']['cases'])+' | '+
                     ' | '.join(show(r['metrics'][k]) for k in METRICS)+' |')
    lines+=['| Unseen independent | NOT RUN | 0 | unmeasured | unmeasured | unmeasured | unmeasured |','',
            'For counts, denominators, source report hashes and limitations, inspect the adjacent JSON. Unknown is null, never zero. Incomplete executions do not get full-run rates. Unscored supported semantics prevents a precision claim. No independent human score has been supplied.']
    return '\n'.join(lines)+'\n'


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--synthetic',nargs=3,action='append',default=[],metavar=('LABEL','REVISION','SCORE'))
    p.add_argument('--historical',nargs=3,action='append',default=[],metavar=('LABEL','REVISION','REPORT'))
    p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    rows=[row(*r,'synthetic_development') for r in a.synthetic]+[row(*r,'authentic_development') for r in a.historical]
    if not rows:raise ValueError('Supply at least one retained report')
    document={'schema':'archival-dashboard-v1','rows':rows,'unseen_independent':{
        'status':'NOT RUN','questions':0,'metrics':dict.fromkeys(METRICS),'reviewer_identity_authenticated':False}}
    a.output.mkdir(parents=True,exist_ok=False)
    (a.output/'dashboard.json').write_text(json.dumps(document,indent=2)+'\n')
    (a.output/'dashboard.md').write_text(render(document))


if __name__=='__main__':main()
