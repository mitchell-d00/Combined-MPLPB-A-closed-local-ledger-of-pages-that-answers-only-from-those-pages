"""Summarize actual returned pilot judgments; never supply missing people."""
import argparse
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
HOME=ROOT/'evaluation/onboarding/2026-11-25'

def summarize(rows, assignment, expected_wheel=None):
    expected={p:group for group,people in assignment['groups'].items() for p in people}
    seen=set();groups={g:{'observed':0,'answer_and_citation':0,'classify_four_of_five':0}
                       for g in assignment['groups']}
    deviations=[]
    for row in rows:
        ident=row['participant_id']
        if ident not in expected or ident in seen:raise ValueError('Unknown or duplicate participant ID')
        seen.add(ident);group=expected[ident]
        if row['group']!=group:raise ValueError('Assignment differs from frozen plan')
        if type(row['answer_and_citation']) is not bool:raise ValueError('Explicit answer/citation judgment required')
        scores=row['classification_correct']
        if type(scores) is not list or len(scores)!=5 or any(type(v) is not bool for v in scores):
            raise ValueError('Five explicit classification judgments required; unfinished tasks count as failed')
        if not row.get('evidence_records') or not row.get('judgment_reasons'):
            raise ValueError('Retained observations and judgment reasons required')
        elapsed=row['elapsed_seconds']
        valid=(row['first_time_user'] is True and row['coached'] is False
               and type(elapsed) in {int,float} and 0<=elapsed<=600
               and (expected_wheel is None or row.get('engine_wheel_sha256')==expected_wheel))
        if not valid:deviations.append(ident)
        groups[group]['observed']+=1
        groups[group]['answer_and_citation']+=int(valid and row['answer_and_citation'])
        groups[group]['classify_four_of_five']+=int(valid and sum(scores)>=4)
    complete=len(seen)==12 and all(g['observed']==6 for g in groups.values())
    new,old=groups['new_path'],groups['existing']
    passed=(not deviations and new['answer_and_citation']>=5
            and new['answer_and_citation']-old['answer_and_citation']>=2
            and new['classify_four_of_five']>=5)
    return {'execution_status':'COMPLETED' if complete else 'PARTIAL' if seen else 'NOT_RUN',
            'participants_planned':12,'participants_observed':len(seen) if seen else None,
            'groups':groups,'protocol_deviations':deviations,
            'acceptance_passed':passed if complete else None,
            'independent_historical_accuracy':'NOT_RUN','independent_semantic_adjudication':'NOT_RUN',
            'native_oocc':'NOT_RUN','population_inference':'Not supported by this small pilot'}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--observations',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    data=json.loads(a.observations.read_text())
    if data.get('source')!='actual_human_observations':raise SystemExit('Actual returned human observations required')
    frozen=json.loads((HOME/'freeze.json').read_text())
    result=summarize(data['participants'],json.loads((HOME/'administrator-assignment.json').read_text()),frozen['engine_wheel_sha256'])
    with a.output.open('x') as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps(result,indent=2))
