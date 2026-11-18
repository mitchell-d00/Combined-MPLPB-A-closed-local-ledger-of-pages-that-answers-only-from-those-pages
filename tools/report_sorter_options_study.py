"""Post-run accounting for frozen sorter options; never a runtime answer key."""
from collections import Counter
import argparse
import json
from pathlib import Path

from tools.unprepared_challenge import read,save,sha,covers,passages
from tools.sorter_options_study import ARMS,FAMILIES,ROOT
from tools.source_roundtrip import original_passage


def visible(row):
    return passages(row)+[e for c in row.get('answer',{}).get('claims',[]) for e in c.get('citations',[])]


def native(row):
    a=row.get('answer',{})
    return {'kind':a.get('kind'),'answer_supported':a.get('answer_supported',False),
        'claims':[{'text':c.get('text'),'qualifiers':c.get('qualifiers'),
                   'proposition':c.get('proposition'),'citations':c.get('citations')} for c in a.get('claims',[])],
        'missing':a.get('missing',[])}


def complete(row):
    return row['execution_status']=='completed' and row.get('answer',{}).get('kind')=='supported_answer' and row['answer']['answer_supported']


def metrics(rows):
    measured=[r['measurements'] for r in rows if r.get('measurements')]
    return {'questions':len(rows),'completed':sum(r['execution_status']=='completed' for r in rows),
        'complete_strict_answers':sum(complete(r) for r in rows),
        'native_kinds':dict(Counter(r.get('answer',{}).get('kind','no_answer') for r in rows)),
        'native_phase_cpu_seconds':sum(m['cpu_seconds'] for m in measured),
        'whole_child_cpu_seconds':sum(m['whole_worker_cpu_seconds'] for m in measured),
        'native_phase_wall_seconds':sum(m['wall_seconds'] for m in measured),
        'parent_worker_wall_seconds':sum(r['parent_wall_seconds'] for r in rows),
        'peak_worker_rss_bytes':max((m['peak_process_rss_bytes'] for m in measured),default=None),
        'logical_original_html_bytes_read':sum(m['source_html_bytes_read'] for m in measured),
        'source_read_calls':sum(m['source_read_calls'] for m in measured),
        'source_documents_examined_per_case':[m['source_documents_examined'] for m in measured],
        'api_usd':0,'compute_price_usd':None,'human_labeling_seconds':None,'human_review_seconds':None}


def report(output):
    output=Path(output).resolve();protocol=read(output/'options-protocol.json');all_rows={a:[] for a in ARMS};cases=[];changes=[];inventory={}
    for arm in ARMS:
        receipt=read(output/(arm+'-receipt.json'))
        if receipt['runtime_sha256']!=protocol['runtime_sha256']:raise ValueError('Reader pin differs')
        if receipt['protocol_sha256']!=sha((output/'options-protocol.json').read_bytes()):raise ValueError('Protocol differs')
    for family,(path,_) in FAMILIES.items():
        corpus=ROOT/path;refs={c['id']:c for c in read(corpus/'reference-draft.json')['cases']}
        imported=read(output/family/'import-receipt.json')
        for q in read(corpus/'questions.json')['cases']:
            row={'family':family,'case_id':q['id'],'question':q['question'],'arms':{}}
            actual={}
            for arm in ARMS:
                r=read(output/family/arm/(q['id']+'.json'));actual[arm]=r;all_rows[arm].append(r)
                found=[any(covers(p,ref) for p in visible(r)) for ref in refs[q['id']]['citations']]
                row['arms'][arm]={'execution_status':r['execution_status'],'native_kind':r.get('answer',{}).get('kind'),
                    'complete':complete(r),'draft_spans_found':found,'draft_span_total':len(found)}
                review_file=output/family/arm/(q['id']+'-review.json')
                if review_file.exists():
                    review=read(review_file)
                    for link in review['candidate_links']:
                        # Deduplicate unchanged source-linked suggestions across question variants.
                        key=sha(json.dumps([family,link['id']],sort_keys=True).encode())
                        if key not in inventory:inventory[key]={'review_key':key,'family':family,'link':link,'occurrences':[]}
                        inventory[key]['occurrences'].append({'case_id':q['id'],'arm':arm,'basis':link['basis'],'why':link['why']})
            for arm in ARMS[1:]:
                before=actual['sorter-alone'];after=actual[arm]
                gained=[];lost=[]
                for i,ref in enumerate(refs[q['id']]['citations']):
                    b=row['arms']['sorter-alone']['draft_spans_found'][i];a=row['arms'][arm]['draft_spans_found'][i]
                    if b==a:continue
                    record=next(x for x in imported['records'] if x['id']==ref['source_id'])
                    anchor=dict(source_id=ref['source_id'],path=record['path'],
                        hash=ref.get('source_hash',record['hash']),body_start=ref['start'],body_end=ref['end'],quote=ref['quote'])
                    (gained if a else lost).append({'reference':ref,'original':original_passage(corpus,imported,anchor)})
                changed=native(before)!=native(after)
                row['arms'][arm].update(new_draft_spans=len(gained),lost_draft_spans=len(lost),native_outcome_changed=changed)
                if changed or gained or lost:
                    changes.append({'case_id':q['id'],'family':family,'arm':arm,'native_outcome_changed':changed,
                        'before':native(before),'after':native(after),'new_draft_passages':gained,'lost_draft_passages':lost,
                        'before_original_claims':[original_passage(corpus,imported,e) for c in before.get('answer',{}).get('claims',[]) for e in c['citations']],
                        'after_original_claims':[original_passage(corpus,imported,e) for c in after.get('answer',{}).get('claims',[]) for e in c['citations']],
                        'sorter_trace':str((output/family/arm/(q['id']+'-trace.json')).relative_to(ROOT))})
            cases.append(row)
    totals={a:metrics(all_rows[a]) for a in ARMS}
    for arm in ARMS:
        totals[arm].update(draft_spans_found=sum(sum(c['arms'][arm]['draft_spans_found']) for c in cases),
            draft_spans_total=sum(c['arms'][arm]['draft_span_total'] for c in cases),
            preserved_baseline_successes=[c['case_id'] for c in cases if c['case_id'] in ['H02','H05'] and c['arms'][arm]['complete']])
    save(output/'link-review-inventory.json',{'schema':'developer-link-review-inventory-v1','assessment':'PENDING',
        'independent_human_evaluation':'NOT RUN','items':list(inventory.values()),
        'meaning':'Source-linked suggestions, not verified historical relations. Review useful/false/unresolved/irrelevant separately; exact-span replay is not semantic accuracy.'})
    save(output/'comparison.json',{'schema':'sorter-options-comparison-v1','reader_pin':protocol['strict_reader_revision'],
        'same_conditions':True,'totals':totals,'cases':cases,'changes':changes,
        'independent_human_evaluation':'NOT RUN','global_historical_recall':None,'global_false_link_rate':None})
    return totals


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('output',type=Path);a=p.parse_args()
    print(json.dumps(report(a.output),indent=2))
