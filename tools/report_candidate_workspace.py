"""Post-run native-regression and exploration accounting; no semantic gold labels."""
import argparse
from pathlib import Path
from tools.unprepared_challenge import read,save,sha
from tools.report_sorter_options_study import native,metrics
from tools.sorter_options_study import FAMILIES,ROOT
from tools.source_roundtrip import original_passage


def report(directory):
    directory=Path(directory).resolve();baseline=ROOT/'evaluation/sorter-first-originals/2026-11-18-witness-admission-final'
    rows=[];cases=[]
    for family,(corpus,_) in FAMILIES.items():
        imported=read(directory/'native-replay'/family/'import-receipt.json')
        for q in read(ROOT/corpus/'questions.json')['cases']:
            old=read(baseline/family/'direct'/(q['id']+'.json'))
            new=read(directory/'native-replay'/family/'direct'/(q['id']+'.json'))
            rows.append(new)
            cases.append({'id':q['id'],'question':q['question'],'unchanged_native_result':native(old)==native(new),
                'before':native(old),'after':native(new),'execution_status':new['execution_status'],
                'original_citations':[original_passage(ROOT/corpus,imported,e) for c in new.get('answer',{}).get('claims',[]) for e in c['citations']]})
    summary=metrics(rows)
    demonstrations=read(directory/'public-originals/run.json');checks=[]
    for row in demonstrations['cases']:
        w=read(directory/'public-originals'/(row['id']+'.json'));spans={}
        for d in w['processed_passages']:
            assert d['status']=='candidate for review' and d['answer_supported'] is False
            s=d['span'];spans[('processed',s['path'],s['source_sha256'],s['byte_start'],s['byte_end'])]=s['text']
        for c in w['candidates']:
            assert c['answer_supported'] is False and c['approval_transferred'] is False
            assert c['processed']['answer_supported'] is False and c['original']['answer_supported'] is False
            o=c['original'];spans[('original',o['path'],o['hash'],o['body_start'],o['body_end'])]=o['quote']
        b=w['exploration_budget']
        assert len(spans)==b['unique_spans']<=b['max_passages']
        assert sum(map(len,spans.values()))==b['characters']<=b['max_characters']
        assert b['strict_slots_consumed']==0
        checks.append({'id':row['id'],'exact_span_charging_pass':True,'candidate_authority_flags_false':True,
                       'strict_slots_consumed':0,'workspace_sha256':sha((directory/'public-originals'/(row['id']+'.json')).read_bytes())})
    save(directory/'native-comparison.json',{'schema':'candidate-workspace-native-regression-v1',
        'runtime_revision':read(directory/'native-replay/protocol.json')['reader_revision'],
        'baseline_complete_answers':2,'summary':summary,'all_native_results_unchanged':all(c['unchanged_native_result'] for c in cases),
        'cases':cases,'exploration_invariants':checks,'independent_human_evaluation':'NOT RUN',
        'correct_outcomes':None,'semantic_relationship_precision':None,'semantic_relationship_recall':None,
        'scope':'Native results compare claims/propositions/exact citations/missing information, excluding software pin metadata. Workspace ownership policy is reported separately from multi-source proof completion.'})
    return summary


if __name__=='__main__':
    import json
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('directory',type=Path);a=p.parse_args()
    print(json.dumps(report(a.directory),indent=2))
