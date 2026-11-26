"""Prospective source-checked retention policy; original CI/key/score stay intact.

Same-operator software assessment, not independent semantic adjudication. This
host-only tool never enters reader workers and never supplies runtime answers.
"""
import argparse,copy,hashlib,html,json,re,tempfile
from pathlib import Path
from tools import verify_bounded_repair as prior
from tools import verify_bounded_reported_content as reported
from tools.bubble_wrap_trial import normal
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'evaluation/cryptid/revision3/final3/bounded1000-host-pin-replay'
def read(p):return json.loads(Path(p).read_text())
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def norm(s):return ' '.join(s.split()).casefold()
def require(value,message):
    if not value:raise ValueError(message)
def source_assessment():
    findings=read(BASE/'prior-v1-acceptance.json')['findings'];keys={k['id']:k for k in read(reported.HOME/'positive-witness-key.json')};rows=[]
    with tempfile.TemporaryDirectory(prefix='bunyip-frozen-inputs-') as temporary:
        packets=prior.unpack_inputs(prior.PACKETS,Path(temporary));prior.D.verify(packets)
        for item in findings:
            ident=item['case'];family=item['family'];raw=read(BASE/'run'/ident/'result.json');a=raw['answer'];case=read(packets/'packets'/ident/'case.json');sources={r['source_id']:r for r in raw['source_receipts']}
            require(a['kind']=='supported_answer' and a['answer_supported'] and a['question']==case['question'],'answer/question scope')
            require(a['verification']['truth_verified'] is False and len(a['claims'])==1,'independent truth/claim cardinality')
            require(prior.citations_valid(a,raw['source_receipts']),'canonical citation validation')
            c=a['claims'][0];p=c['proposition'];require(c.get('source_support_established') is True and c.get('qualifiers'),'source support and qualifications')
            for r in raw['source_receipts']:
                original=packets/'packets'/ident/r['source_file'];require(sha(original)==r['raw_sha256'],'original source hash changed')
            for citation in c['citations']:
                r=sources[citation['source_id']];number=next(i for i,s in enumerate(case['sources'],1) if s['path']==r['source_file']);original=(packets/'packets'/ident/r['source_file']).read_text();admitted=('<h1>Synthetic source '+str(number)+'</h1>\n<pre>'+html.escape(original)+'</pre>').replace('\r\n','\n').strip().encode();w=citation['original_witness'];lo,hi=w['start_byte'],w['end_byte']
                require(w['coordinate_space']=='admitted_record_body_html_utf8' and w['body_html_sha256']==hashlib.sha256(admitted).hexdigest() and 0<=lo<hi<=len(admitted) and html.unescape(admitted[lo:hi].decode())==citation['quote'],'original-byte witness')
            quotes=' '.join(norm(x['quote']) for x in c['citations']);question=norm(a['question'])
            if family=='reported_statement':
                clean=copy.deepcopy(raw);value=clean['answer']['claims'][0]['proposition'];require(value['embedded_content_negative'] is False and value['inner_negative'] is False,'literal reporting payload');value.pop('embedded_content_negative')
                require(reported.reported_match(packets/'packets'/ident,clean,keys[ident]),'unchanged full source-scoped reported claim')
                require(p['actual_authorship_established'] is False and p['completion_established'] is False,'reporting truth/execution guard')
            elif family=='negated_statement':
                require(p['relation']=='source_action_assertion' and p['negative'] is True and p['action']=='write' and p.get('unresolved_reference') is False,'denial semantics')
                expected=p['actor_text']+' did not write '+p['object_text']+'.';require(norm(expected) in [norm(x['quote']) for x in c['citations']],'complete denial witness')
                require(norm('deny about '+p['actor_text']+' and '+p['object_text']) in question,'requested denial actor/object')
                require(c['text']=='Source assertion: '+expected,'full denial rendering')
                require(any('not independently verified' in q for q in c['qualifiers']),'denial qualification')
            elif family=='date_roles':
                require(p['relation']=='source_event_date_inventory' and p['unresolved_roles']==[] and p['question_obligations_verified'] and p['verified_question']==a['question'],'date completion')
                require(len(p['date_links'])==2 and {x['requested_role'] for x in p['date_links']}=={'sending','writing'},'separate requested date roles')
                require('reported sending date and the writing date' in question,'requested date-role distinction')
                for link in p['date_links']:
                    text=norm(link['statement_text']);date=norm(link['date_text']);require(any(text==norm(x['quote']) for x in c['citations']),'complete date witness')
                    if link['requested_role']=='sending':require(re.fullmatch(r'on '+re.escape(date)+r', .+ sent '+re.escape('the '+p['subject_text'].removeprefix('the '))+r'\.',text),'sending role')
                    else:
                        require(re.fullmatch(r'this record was written on '+re.escape(date)+r'\.',text),'writing role')
                        require(all(link[k] is False for k in ['sending_established','receipt_established','event_occurrence_established']),'writing does not prove transmission/event')
                    require(str(link['year']) in link['date_text'] and link['event_identity'] is None and link['normalized_event_time'] is None,'no inherited year or event identity')
                require(p['causation_established'] is False and p['event_coreference_established'] is False and p['historical_truth_independently_verified'] is False,'date scope')
                require(any('source-attributed' in q.casefold() for q in c['qualifiers']),'date qualification')
            elif family=='partial_correction':
                require(p['relation']=='source_scoped_count_correction' and p['execution_established'] is False and p['historical_truth_independently_verified'] is False,'correction scope')
                date=norm(p['target_writing_date']);old=norm(sources[p['original_source_id']]['canonical_body']);new=norm(sources[p['correction_source_id']]['canonical_body']);before=norm(p['previous_count']);after=norm(p['replacement_count']);dest=norm(p['destination_retained']);unit=norm(p['unit'])
                require('this letter was written on '+date+'.' in old and 'the consignment contains '+before+' '+unit+' for '+dest+'.' in old,'original complete fields')
                require('in my letter of '+date+', the count should read '+after+' '+unit+'.' in new and 'the destination remains '+dest+'.' in new,'specific correction and retained destination')
                require(sum('this letter was written on '+date+'.' in norm(r['canonical_body']) for r in raw['source_receipts'])==1,'unique explicit date reference')
                require(c['text']==f"The correction changes the stated count from {p['previous_count']} to {p['replacement_count']} {p['unit']}. It explicitly retains the destination {p['destination_retained']}.",'full correction rendering')
                require(any('writer identity is unresolved' in q for q in c['qualifiers']) and any('does not establish dispatch' in q for q in c['qualifiers']),'correction qualifications')
            else:raise ValueError('Unassessed gain family '+family)
            rows.append({'id':ident,'family':family,'raw_sha256':sha(BASE/'run'/ident/'result.json'),'complete_question':a['question'],'complete_claim_text':c['text'],'qualifications':c['qualifiers'],'source_witnesses':[x['quote'] for x in c['citations']],'source_checked':True})
    require(len(rows)==65,'expected frozen assessment membership');return rows

def main(args):
    assessment=source_assessment();result={'policy':'bunyip-source-checked-retention-v2','original_gate_unchanged':True,'source_checked_prior_additional_outputs':44,'source_checked_reported_metadata_cases':21,'source_assessment':assessment,'independent_historical_semantic_adjudication':'NOT_RUN'}
    if args.run:
        before=read(BASE/'run/run.json');after=read(args.run/'run.json');old={x['case_id']:x for x in before['cases']};rows=[]
        for entry in after['cases']:
            ident=entry['case_id'];require(entry['execution']=='completed','worker execution failed; semantic result NOT_RUN');p=args.run/ident/'result.json';require(sha(p)==entry['sha256'],'raw output changed');a=read(p);b=read(BASE/'run'/ident/'result.json');require(a['question']==b['question'],'question changed');same=normal(a['answer'])==normal(b['answer']);rows.append({'id':ident,'same_semantic_contract':same,'raw_sha256':sha(p)})
        require(len(rows)==1000 and set(old)=={x['id'] for x in rows},'omitted or duplicate executions');result.update(cases=rows,contract_preserved=sum(r['same_semantic_contract'] for r in rows),acceptance_passed=all(r['same_semantic_contract'] for r in rows))
    with args.output.open('x') as f:json.dump(result,f,indent=2)
    print({k:v for k,v in result.items() if k not in ['cases','source_assessment']});return 0 if result.get('acceptance_passed',True) else 1
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--run',type=Path);p.add_argument('--output',type=Path,required=True);raise SystemExit(main(p.parse_args()))
