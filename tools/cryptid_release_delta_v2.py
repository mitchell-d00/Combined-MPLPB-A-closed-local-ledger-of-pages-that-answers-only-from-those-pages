"""Preserve an accepted release comparison and admit only fully scored new gains."""
import argparse,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from tools.cryptid_trial import read,save,sha,digest
from tools.bubble_wrap_trial import normal

def main(a):
    old=read(a.before/'run.json');new=read(a.after/'run.json');registry=read(ROOT/'evaluation/bubble-wrap/2026-11-25/continuation/development.json');targets={};diagnostics={};checks=[]
    for spec in a.transition:
        registry_path,run_path,score_path=map(Path,spec.split(','));rr=read(run_path/'run.json');sc=read(score_path);assert rr['reader_files']==new['runtime_sha256'] and sc['run_sha256']==sha(run_path/'run.json');scores={x['id']:x for x in sc['cases']}
        for c in read(registry_path)['cases']:
            if scores[c['id']].get('budget_stop'):
                diagnostics[digest(c['files'])]=read(run_path/c['id']/'result.json')['answer']
            if scores[c['id']]['passed'] and not scores[c['id']].get('false_support'):
                answer=read(run_path/c['id']/'result.json')['answer']
                if answer['answer_supported']:targets[digest(c['files'])]=answer
        checks.append({'registry':str(registry_path),'run_sha256':sha(run_path/'run.json'),'score_sha256':sha(score_path)})
    entries={e['id']:e for e in new['rows']};rows=[]
    for c in registry['cases']:
        ident=c['id'];entry=entries[ident];errors=[];same=False;recovered=False;diagnostic_only=False
        if entry['execution_status']!='completed':errors.append('execution_failed')
        else:
            before=read(a.before/ident/'result.json')['answer'];after=read(a.after/ident/'result.json')['answer'];same=normal(before)==normal(after)
            if not same:
                target=targets.get(digest(c['files']))
                if before['claims'] or before['answer_supported']:errors.append('prior_support_contract_changed')
                elif target is None or normal(target)!=normal(after):
                    expected=diagnostics.get(digest(c['files']))
                    left=normal(before);right=normal(after);left.pop('diagnostic',None);right.pop('diagnostic',None)
                    diagnostic_only=(not after['claims'] and not after['answer_supported'] and expected is not None and normal(expected)==normal(after) and left==right and after['diagnostic']['code']=='reference_scan_budget')
                    if not diagnostic_only:errors.append('changed_contract_not_fully_key_checked')
                else:recovered=True
        rows.append({'id':ident,'passed':not errors,'unchanged':same,'recovered_complete':recovered,'budget_diagnostic_only':diagnostic_only,'errors':errors,'raw_sha256':entry.get('result_sha256')})
    counts={'planned':280,'passed':sum(r['passed'] for r in rows),'unchanged':sum(r['unchanged'] for r in rows),'recovered_complete':sum(r['recovered_complete'] for r in rows),'budget_diagnostic_only':sum(r['budget_diagnostic_only'] for r in rows),'failed':sum(not r['passed'] for r in rows)}
    save(a.output,{'schema':'cryptid-release-delta-v2','scorer_sha256':sha(Path(__file__)),'before_run_sha256':sha(a.before/'run.json'),'after_run_sha256':sha(a.after/'run.json'),'transition_checks':checks,'counts':counts,'rows':rows});print(counts)
    if counts['failed']:raise SystemExit(2)
if __name__=='__main__':
    p=argparse.ArgumentParser()
    for n in ['before','after','output']:p.add_argument('--'+n,type=Path,required=True)
    p.add_argument('--transition',action='append',default=[]);main(p.parse_args())
