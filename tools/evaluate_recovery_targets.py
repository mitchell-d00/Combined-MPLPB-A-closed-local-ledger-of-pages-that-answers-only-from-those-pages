"""Post-run targeted recovery checks using unchanged quoted originals.

These are narrowly scoped parser recovery checks, not historical truth scoring.
No reference target or expected field enters any runtime worker.
"""
import argparse
from pathlib import Path
from tools.unprepared_challenge import read,save,summary,projections,covers


def check(corpus,prior,current,target):
    corpus=Path(corpus);prior=Path(prior);current=Path(current)
    for run in [prior,current]:summary(corpus,run)
    receipt=read(current/'import-receipt.json');texts=projections(corpus,receipt)
    needle={'distribution':'The order was distributed to the 175,000-member expeditionary force on the eve of the invasion.',
        'cancellation':'In exchange for Executive Order 8802, Randolph called off the march, though he would be a driving force of the 1963 March on Washington.'}[target]
    matches=[(sid,b.index(needle)) for sid,(r,b) in texts.items() if needle in b]
    if len(matches)!=1:raise ValueError('Target source ambiguous or missing')
    sid,start=matches[0];ref={'source_id':sid,'start':start,'end':start+len(needle)};arms={}
    for label,run in [('prior',prior),('recovery',current)]:
        rows=[];rr=read(run/'run-receipt.json')
        for c in rr['cases']:
            out=read(run/(c['id']+'.json'));pc=out['investigation']['prose_candidates'];present=any(covers(p,ref) for p in pc['candidates'])
            frames=pc['information_map'].get('proposed_reconstruction',{}).get('propositions',[])
            found=[]
            for m in frames:
                if not any(e['source_id']==sid and e['quote']==needle for e in m['evidence']):continue
                v=m['value']
                ok=(v['action']=='distribute' and any(d['candidate_role']=='distribution' and 'eve' in d['raw_text'] for d in v['date_candidates'])) if target=='distribution' else v['action']=='cancel' and v['actor']=='Randolph' and 'the march' in v['object_text'] and v['modality']=='source_reports_action'
                if ok:found.append(m['mapping_id'])
            rows.append({'case_id':c['id'],'full_target_quote_retrieved':present,'targeted_candidate_recovered':bool(found),'mapping_ids':found})
        eligible=[r for r in rows if r['full_target_quote_retrieved']]
        arms[label]={'rows':rows,'opportunities_with_full_evidence':len(eligible),'recovered_given_full_evidence':sum(x['targeted_candidate_recovered'] for x in eligible),
            'all_cases_recovered':sum(x['targeted_candidate_recovered'] for x in rows),'all_cases':len(rows)}
    return {'schema':'targeted-source-recovery-v1','target':target,'supporting_quote':needle,'reference':ref,'arms':arms,
        'scope':'Consistency across existing frozen question/context variants when the complete target evidence is retrieved. Not independent unseen evaluation, general historical recall, or verified fact. Distribution agent remains unresolved; cancellation/date context remains available for review.',
        'answer_supported':False,'content_truth_verified':False,'independent_human_review':'NOT RUN'}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('corpus');p.add_argument('prior');p.add_argument('current');p.add_argument('--target',choices=['distribution','cancellation'],required=True);p.add_argument('--output',required=True);a=p.parse_args();save(a.output,check(a.corpus,a.prior,a.current,a.target))


if __name__=='__main__':main()
