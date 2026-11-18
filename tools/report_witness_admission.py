"""Post-run source-linked admission accounting; never imported by workers."""
import argparse
from pathlib import Path
from tools.report_sorter_options_study import report,metrics,visible,native,complete
from tools.sorter_options_study import ARMS,FAMILIES,ROOT
from tools.unprepared_challenge import read,save,covers,sha
from tools.source_roundtrip import original_passage


def build(study):
    study=Path(study).resolve();report(study)
    arms=['direct']+ARMS;rows={a:[] for a in arms};cases=[];audits=[]
    for family,(corpus_path,_) in FAMILIES.items():
        corpus=ROOT/corpus_path;imported=read(study/family/'import-receipt.json')
        refs={c['id']:c for c in read(corpus/'reference-draft.json')['cases']}
        for q in read(corpus/'questions.json')['cases']:
            case={'case_id':q['id'],'family':family,'question':q['question'],'arms':{},
                  'correct_outcome_assessment':'UNASSESSED: source-grounded semantic review required',
                  'reviewer_1':None,'reviewer_2':None,'adjudication':None}
            for arm in arms:
                path=study/family/arm/(q['id']+'.json');r=read(path);rows[arm].append(r)
                answer=r.get('answer',{});budget=answer.get('documentary_support',{}).get('admission')
                raw=[original_passage(corpus,imported,e) for c in answer.get('claims',[]) for e in c['citations']]
                trace_path=study/family/arm/(q['id']+'-trace.json')
                offers=[]
                if trace_path.exists():
                    offers=[h for call in read(trace_path)['calls'] for h in call.get('offered_hints_for_reader_review',[])]
                found=[any(covers(p,ref) for p in visible(r)) for ref in refs[q['id']]['citations']]
                suggested=[any(covers(p,ref) for p in offers) for ref in refs[q['id']]['citations']]
                if budget:
                    spans=budget['admitted'];keys=[(e['source_id'],e['path'],e['hash'],e['body_start'],e['body_end']) for e in spans]
                    assert len(set(keys))==len(keys)==budget['passages_admitted']<=budget['max_passages']
                    assert sum(len(e['quote']) for e in spans)==budget['characters_admitted']<=budget['max_characters']
                    audits.append({'case_id':q['id'],'arm':arm,'admission':budget,'budget_invariants_pass':True})
                case['arms'][arm]={'execution_status':r['execution_status'],'complete':complete(r),
                    'answer':native(r),'original_citations':raw,'native_draft_spans_found':found,
                    'review_only_draft_spans_located':suggested,
                    'review_only_new_vs_native_draft_spans':sum(s and not f for s,f in zip(suggested,found)),
                    'result_file':str(path.relative_to(ROOT)),'admission':budget}
            previous={}
            for label,folder,oldarm in [('historical_direct','2026-11-18','direct'),
                ('historical_unreserved','2026-11-18','sorter-first'),('v2_conservative','2026-11-18-conservative','sorter-alone')]:
                old=read(ROOT/'evaluation/sorter-first-originals'/folder/family/oldarm/(q['id']+'.json'))
                previous[label]={'complete':complete(old),'answer':native(old),
                    'original_citations':[original_passage(corpus,imported,e) for c in old.get('answer',{}).get('claims',[]) for e in c['citations']]}
            case['previous']=previous
            case['changed_from_v2']={a:native(read(study/family/a/(q['id']+'.json')))!=previous['v2_conservative']['answer'] for a in arms}
            cases.append(case)
    totals={a:metrics(rows[a]) for a in arms}
    for a in arms:
        totals[a].update(native_draft_spans_found=sum(sum(c['arms'][a]['native_draft_spans_found']) for c in cases),
            review_only_draft_spans_located=sum(sum(c['arms'][a]['review_only_draft_spans_located']) for c in cases),
            review_only_new_vs_native_draft_spans=sum(c['arms'][a]['review_only_new_vs_native_draft_spans'] for c in cases),
            draft_spans_total=32,correct_outcomes=None,semantic_review='NOT RUN',
            complete_ids=[c['case_id'] for c in cases if c['arms'][a]['complete']])
    save(study/'witness-comparison.json',{'schema':'reader-witness-comparison-v1',
        'runtime_revision':read(study/'options-protocol.json')['strict_reader_revision'],
        'goal_correct_outcomes':22,'historical_complete_baseline':2,'totals':totals,'cases':cases,
        'correct_outcomes':None,'independent_human_evaluation':'NOT RUN',
        'interpretation':'Draft-span coverage is source discovery, not semantic relationship accuracy. Refusal is not credited merely for being conservative. Concurrent local executions are not controlled efficiency comparisons.'})
    save(study/'admission-audit.json',{'rows':audits,'all_pass':True,
        'meaning':'Exact span charging and limit invariants; independent source/meaning verification remains separate.'})
    save(study/'independent-review-packet.json',{'status':'NOT RUN','reviewers_required':2,
        'questions_are_development_data':True,'unseen_evaluation':'NOT RUN',
        'instructions':['Assess actual event identity, chronology, correction/relationship accuracy, missing evidence, source fidelity and completeness against originals.',
          'Complete cited answer when established; source-backed conflict/abstention when genuine conflict or gap. Do not credit implementation/budget/grammar failure as correct.',
          'Keep the two reviewer files separate, preserve disagreements, and require explicit source-linked adjudication. Record real review/correction/adjudication seconds or null.'],
        'machine_results':'witness-comparison.json','candidate_links':'link-review-inventory.json',
        'assessment_template':[{'case_id':c['case_id'],'reviewer':None,'arm':None,'correct_outcome':None,
            'event_accuracy':None,'chronology_accuracy':None,'correction_accuracy':None,'relationship_accuracy':None,
            'false_causal_links':None,'missed_relationships':None,'unsupported_conclusions':None,
            'citation_fidelity':None,'appropriate_refusal':None,'completeness':None,'source_linked_rationale':None,
            'operator_seconds':None} for c in cases]})
    return totals

if __name__=='__main__':
    import json
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('study',type=Path);a=p.parse_args()
    print(json.dumps(build(a.study),indent=2))
