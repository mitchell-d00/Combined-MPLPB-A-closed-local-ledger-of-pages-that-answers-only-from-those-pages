"""Compare unchanged claims while checking one additive reporting-polarity field.

Original exact-comparison failures remain separate evidence. This audit permits
only source-checked embedded polarity and an explicitly reported unit-count
increase; every legacy claim, qualification, witness and outcome must match.
An optional predeclared claim-free recovery criterion is scored separately.
"""
import argparse,copy,hashlib,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from tools.bubble_wrap_trial import normal

def read(path):return json.loads(Path(path).read_text())
def sha(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def norm(value):return ' '.join(value.split()).casefold()

def validate(raw):
    errors=[];removed=0;answer=normal(copy.deepcopy(raw['answer']))
    records={r.get('id',r.get('source_id')):r for r in raw.get('records',raw.get('source_receipts',[]))}
    for claim in answer['claims']:
        for citation in claim.get('citations',[]):
            record=records.get(citation.get('source_id'));body=(record or {}).get('body',(record or {}).get('canonical_body',''));lo=citation.get('body_start',citation.get('start'));hi=citation.get('body_end',citation.get('end'))
            if not record or type(lo) is not int or type(hi) is not int or not 0<=lo<hi<=len(body) or body[lo:hi]!=citation.get('quote') or record['hash']!=citation.get('hash'):errors.append('invalid_exact_citation')
        prop=claim.get('proposition',{})
        if prop.get('relation')!='source_attributed_report_content' or 'embedded_content_negative' not in prop:continue
        value=prop['embedded_content_negative'];author=re.escape(norm(prop['author']));obj=re.escape(norm(prop['object']));signs=set()
        active=re.compile(r'(?<!\w)'+author+r' (did not write|wrote) '+obj+r'(?!\w)')
        passive=re.compile(r'(?<!\w)'+obj+r' was (not )?written by '+author+r'(?!\w)')
        for citation in claim.get('citations',[]):
            text=norm(citation['quote'])
            signs.update(m[1]=='did not write' for m in active.finditer(text))
            signs.update(bool(m[1]) for m in passive.finditer(text))
        if type(value) is not bool or signs!={value}:errors.append('additive_embedded_polarity_not_uniquely_source_witnessed')
        prop.pop('embedded_content_negative');removed+=1
    return answer,errors,removed

def recovery_ok(before,after,criterion):
    if before['claims'] or before['answer_supported'] or not criterion:return False
    if after['question']!=criterion['question'] or after['kind']!='supported_answer' or not after['answer_supported'] or len(after['claims'])!=1:return False
    claim=after['claims'][0];prop=claim['proposition']
    if claim.get('source_support_established') is not True:return False
    if after.get('verification',{}).get('truth_verified') is not False and prop.get('historical_truth_independently_verified') is not False and claim.get('historical_truth_independently_verified') is not False:return False
    if not all(prop.get(k)==v for k,v in criterion['required_legacy_proposition'].items()):return False
    if not any(c['quote']==criterion['complete_witness'] for c in claim['citations']):return False
    return all(any(fragment.casefold() in qualifier.casefold() for qualifier in claim.get('qualifiers',[])) for fragment in criterion['qualification_fragments'])

def main(args):
    prior=read(args.before/'run.json');current=read(args.after/'run.json');old_rows={r['id']:r for r in prior.get('cases',prior.get('rows',[]))};rows=[]
    criteria=read(args.recoveries)['recoveries'] if args.recoveries else {}
    for entry in current.get('cases',current.get('rows',[])):
        ident=entry['id'];old=old_rows[ident];errors=[];exact=measurement=recovered=False;added=0
        if entry['execution_status']!='completed' or old['execution_status']!='completed':errors.append('execution_failed')
        else:
            old_path=args.before/ident/'result.json';new_path=args.after/ident/'result.json';before_raw=read(old_path);after_raw=read(new_path)
            assert sha(old_path)==old.get('raw_sha256',old.get('result_sha256')) and sha(new_path)==entry.get('raw_sha256',entry.get('result_sha256'))
            before,old_errors,_=validate(before_raw);after,new_errors,added=validate(after_raw);errors+=old_errors+new_errors
            exact=normal(before_raw['answer'])==normal(after_raw['answer'])
            if before!=after:
                left=copy.deepcopy(before);right=copy.deepcopy(after);l=left.get('documentary_support',{});r=right.get('documentary_support',{});x=l.pop('examined_units',None);y=r.pop('examined_units',None)
                measurement=(left==right and type(x) is int and type(y) is int and y==x+1 and y==after['documentary_support'].get('paragraph_units') and y<=after['documentary_support'].get('limits',{}).get('max_units',-1))
                recovered=recovery_ok(before,after,criteria.get(ident))
                if not measurement and not recovered:errors.append('legacy_claim_qualification_citation_or_outcome_changed')
        rows.append({'id':ident,'passed':not errors,'exact_contract':exact,'source_checked_additive_fields':added,'unit_measurement_only':measurement,'predeclared_checked_recovery':recovered,'errors':errors})
    assert set(old_rows)=={r['id'] for r in rows}
    counts={'planned':len(rows),'passed':sum(r['passed'] for r in rows),'failed':sum(not r['passed'] for r in rows),'exact_contracts':sum(r['exact_contract'] for r in rows),'source_checked_additive_fields':sum(r['source_checked_additive_fields'] for r in rows),'unit_measurement_only':sum(r['unit_measurement_only'] for r in rows),'checked_recoveries':sum(r['predeclared_checked_recovery'] for r in rows)}
    result={'schema':'cryptid-semantic-preservation-v1','auditor_sha256':sha(Path(__file__)),'before_run_sha256':sha(args.before/'run.json'),'after_run_sha256':sha(args.after/'run.json'),'recovery_criterion_sha256':sha(args.recoveries) if args.recoveries else None,'counts':counts,'rows':rows,'scope':'Legacy assertions/qualifications/citations/outcomes unchanged after separately validating an additive literal-payload field. Exact failures remain separate. No source labels or old scores changed; same-operator review, independent adjudicationNOT_RUN.'}
    with args.output.open('x') as stream:json.dump(result,stream,indent=2)
    print(counts);return 2 if counts['failed'] else 0

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    for name in ['before','after','output']:parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--recoveries',type=Path);raise SystemExit(main(parser.parse_args()))
