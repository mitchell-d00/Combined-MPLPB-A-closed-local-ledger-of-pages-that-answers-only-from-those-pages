"""Custodian-only descriptive cohorts from the sealed D% roll trace.

This never runs inside MPLPB, changes expectations, or awards source support.
"""
import argparse
from collections import Counter, defaultdict
from pathlib import Path
from tools import dpercent as study

STRUCTURAL={'layout','line_ending','extension','wrapping','question_structure','distractor_count','scope_structure'}


class RecordedDice(study.Dice):
    def __init__(self,seed):
        super().__init__(seed);self.choices=[]

    def choose(self,label,values):
        value=super().choose(label,values)
        self.choices.append((label,value))
        return value


def analyze(packets,custodian,score_path,out):
    packets=Path(packets);custodian=Path(custodian)
    seal=study.verify(packets,custodian)
    if study.sha(Path(study.__file__).read_bytes())!=seal['generator_sha256']:
        raise ValueError('Replay requires the exact frozen generator')
    key=study.read(custodian/'key.json')['cases'];rolls=study.read(custodian/'dice.json')
    scored=study.read(score_path);rows={r['id']:r for r in scored['cases']}
    if len(rows)!=len(key) or set(rows)!={k['id'] for k in key}:raise ValueError('Score coverage differs')
    dice=RecordedDice(int(rolls['seed']))
    schedule=dice.shuffle('family_schedule',[list(study.FAMILIES)[i%len(study.FAMILIES)] for i in range(len(key))])
    observations=[];cohorts=defaultdict(list)
    for number,family in enumerate(schedule,1):
        dice.choices=[];case,documents,expected=study.case_material(number,family,dice)
        if expected!=key[number-1]:raise ValueError('Replayed key differs')
        folder=packets/'packets'/case['id']
        if study.read(folder/'case.json')!=case or any((folder/s['path']).read_bytes()!=raw for s,raw in documents):
            raise ValueError('Replayed packet differs')
        row=rows[case['id']]
        if row['family']!=family or row['expected']!=expected['expected']:raise ValueError('Score labels differ')
        features={'family':family,'effective_profile':case['profile']}
        for label,value in dice.choices:
            if label in STRUCTURAL:
                features['rolled.'+label]={'\n':'LF','\r\n':'CRLF'}.get(value,value) if isinstance(value,str) else value
            elif label=='actor':features['actor_has_non_ascii']=not value.isascii()
        observations.append({'id':case['id'],'features':features,'outcome':row['outcome']})
        for name,value in features.items():cohorts[(name,str(value))].append(row)
    if dice.rolls!=rolls['rolls']:raise ValueError('Dice trace differs')
    groups={}
    for (name,value),cases in sorted(cohorts.items()):
        positives=[r for r in cases if r['expected']=='answer'];negatives=[r for r in cases if r['expected']=='refuse']
        incomplete=sum(r['execution']!='completed' for r in cases)
        counts=Counter(r['outcome'] for r in cases)
        groups.setdefault(name,{})[value]={'cases':len(cases),'answer_cases':len(positives),'refuse_cases':len(negatives),
            'outcomes':dict(counts),'incomplete_executions':incomplete,
            'missed_complete_answer_rate':1-counts['detected_answer']/len(positives) if positives and not incomplete else None,
            'false_alarm_rate':counts['false_alarm']/len(negatives) if negatives and not incomplete else None}
    result={'schema':'dpercent-feature-cohorts-v1','score_sha256':study.sha(Path(score_path).read_bytes()),
            'seal_sha256':study.sha((packets/'seal.json').read_bytes()),'roll_replay_verified':True,
            'cases':observations,'by_feature':groups,'scope':'Descriptive correlated cohorts,not causal attribution or independent evaluation. Rolled layout may be overridden to retain required documentary context. Actor names and answers are excluded from feature labels.'}
    study.save(out,result);return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for field in ('packets','custodian','score','out'):p.add_argument('--'+field,type=Path,required=True)
    a=p.parse_args();r=analyze(a.packets,a.custodian,a.score,a.out)
    print('Verified roll replay and grouped',len(r['cases']),'cases')


if __name__=='__main__':main()
