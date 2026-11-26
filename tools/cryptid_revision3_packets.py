"""Freeze new reporting-negation and prospective partial-policy controls.

The two consumed final packets and their keys are referenced unchanged.
"""
from pathlib import Path
import copy,json
from tools.cryptid_packet_support_v4 import packet,key
from tools.cryptid_trial import ROOT,read,sha

BASE='1251cc471a24ba4be91949ffc0c4752d0c3bf202'
HOME=ROOT/'evaluation/cryptid/revision3'

def save(path,value):
    with path.open('x') as stream:json.dump(value,stream,indent=2,ensure_ascii=False)

def freeze(folder,family,specs,start):
    packet(folder,family,specs,BASE,'tools/cryptid_revision3_packets.py')
    registry=read(folder/'registry.json');keys=read(folder/'key.json');changed={}
    for number,row in enumerate(registry['cases'],start):
        old=row['id'];ident=f'CRYPT-{family}-{number:04d}';source=folder/'inputs'/old;source.rename(folder/'inputs'/ident)
        case=read(folder/'inputs'/ident/'case.json');case['id']=ident;(folder/'inputs'/ident/'case.json').write_text(json.dumps(case,indent=2)+'\n')
        row.update(id=ident,packet=str((folder/'inputs'/ident).relative_to(ROOT)));row['files']['case.json']=sha(folder/'inputs'/ident/'case.json');changed[ident]=keys[old]
    for name,value in [('registry.json',registry),('key.json',changed)]: (folder/name).write_text(json.dumps(value,indent=2)+'\n')
    seal=read(folder/'freeze.json');seal.update(registry_sha256=sha(folder/'registry.json'),key_sha256=sha(folder/'key.json'));(folder/'freeze.json').write_text(json.dumps(seal,indent=2)+'\n')

def report_specs():
    rows=[];reporter='Leda Voss';author='Marin Holt';obj='the ridge register';writer='Quentin Moss'
    q=f'What does {reporter} report about whether {author} wrote {obj}?'
    def source(statement,form=0):
        if form==0:return '<article><p>Report.</p><p>Written by '+writer+'</p><p>'+statement+'</p></article>'
        if form==1:return '<section><p>Meeting minutes.</p><p>Recorded by '+writer+'.</p><p>'+statement+'</p></section>'
        return '<p>'+statement+'</p>'
    def claim(outer,inner):
        return {'relation':'source_attributed_report_content','reporter':reporter,'author':author,'object':obj,'outer_negative':outer,'inner_negative':None if outer else inner,'inner_polarity':'unasserted' if outer else 'negative' if inner else 'affirmative','content_asserted_by_reporter':not outer,'conditions':[],'actual_authorship_established':False,'completion_established':False}
    def add(statement,body=None,question=q,decision='complete',outer=False,inner=False,flags=None,extra=None):
        expected=key(decision,claim(outer,inner) if decision=='complete' else None,[statement] if decision=='complete' else [],['Source-scoped reporting statement','Independent authorship'])
        sources=[dict(id='RPT-1',body_html=body if body is not None else source(statement),**(flags or {}))]
        if extra:sources+=extra
        rows.append({'question':question,'sources':sources,'key':expected,'mechanism':'Reporting-shell polarity is independent of the embedded action; source denies reporting vs reporter denies content','protected_operation':'Complete reporting witness, unasserted embedded payload under outer denial, original actor/writer roles and full source scope'})
    for form in range(3):
        for outer in [False,True]:
            for inner in [False,True]:
                payload=f'{author} '+('did not write' if inner else 'wrote')+' '+obj
                if form==0:statement=reporter+(' did not say' if outer else ' said')+', “'+payload+'.”'
                elif form==1:statement='“'+payload+',” '+reporter+(' did not state.' if outer else ' stated.')
                else:statement=reporter+(' did not report' if outer else ' reported')+' that '+payload+'.'
                add(statement,source(statement,form),outer=outer,inner=inner)
    positive=f'{reporter} reported that {author} wrote {obj}.'
    negative=f'{reporter} did not say, “{author} did not write {obj}.”'
    add(negative,question=q.replace(reporter,writer),decision='withhold')
    add(negative,question=q.replace(author,'Bela Neri'),decision='withhold')
    add(negative,question=f'Do these records independently establish that {author} actually wrote {obj}?',decision='withhold')
    add(negative,question=f'Did {author} complete the ridge inspection?',decision='withhold')
    add(negative,'<p>unless the seal is approved.</p>'+source(negative),decision='withhold')
    add(negative,'<blockquote>'+source(negative)+'</blockquote>',decision='withhold')
    add(negative,decision='withhold',flags={'withdraw':True})
    add(negative,decision='withhold',flags={'external':'no'});rows[-1]['profile']='external'
    add(negative,'<p>From: '+writer+'</p><p>To: '+reporter+'</p>'+source(negative),decision='withhold')
    # Opposed reporting appearances, not independently established authorship.
    add(positive,extra=[{'id':'RPT-2','body_html':source(negative)}],decision='conflict')
    rows[-1]['key']['claims']=[{'proposition':claim(False,False),'qualification_fragments':['Source-scoped reporting statement'],'complete_witnesses':[positive]},{'proposition':claim(True,True),'qualification_fragments':['Source-scoped reporting statement'],'complete_witnesses':[negative]}]
    broken=f'{reporter} did not say, “{author} wrote {obj}.'
    add(broken,decision='withhold')
    add(positive,extra=[{'id':'RPT-2','body_html':source(broken)}],decision='withhold')
    assert len(rows)==24
    return rows

def partial_specs():
    rows=[]
    def add(q,actor,action,obj,statement,decision='partial',missing=(),**flags):
        prop={'relation':'source_action_assertion','actor_text':actor,'action':action,'object_text':obj,'negative':False,'unresolved_reference':False}
        k=key(decision,prop if decision in {'complete','partial'} else None,[statement] if decision in {'complete','partial'} else [],['Source-attributed statement','not independently verified']);k['missing_fragments']=list(missing)
        rows.append({'question':q,'sources':[dict(id='FACT-1',body_html='<section><p>'+statement+'</p></section>',**flags)],'key':k,'mechanism':'Checked partial support with an unresolved temporal or additional obligation must not become a complete answer','protected_operation':'Full original question, exact eligible atomic claim and qualifications; explicit missing time/execution; no actor substitution'})
    add('Who surveyed the northern dunes before October 8?','Leda Voss','survey','the northern dunes','Leda Voss surveyed the northern dunes.',missing=['before October 8'])
    add('By whom was the shale register written before June 6?','Quentin Moss','write','the shale register','Quentin Moss wrote the shale register.',missing=['before June 6'])
    add('Who was it that sent the jade parcel before March 9?','Bela Neri','send','the jade parcel','Bela Neri sent the jade parcel.',missing=['before March 9'])
    add('Which individual received the copper notice before May 5?','Asha Dell','receive','the copper notice','Asha Dell received the copper notice.',missing=['before May 5'])
    add('Who wrote the silver register? And was it read?','Jana Pell','write','the silver register','Jana Pell wrote the silver register.',missing=['read'])
    add('Who revised the inland report? And was the revision dispatched?','Miko Zane','revise','the inland report','Miko Zane revised the inland report.',missing=['dispatched'])
    add('Who wrote the amber index?','Jana Pell','write','the amber index','Jana Pell wrote the amber index.','complete')
    add('Which person surveyed the eastern quay?','Miko Zane','survey','the eastern quay','Miko Zane surveyed the eastern quay.','complete')
    add('Did Leda Voss survey the northern dunes before October 8?','Quentin Moss','survey','the northern dunes','Quentin Moss surveyed the northern dunes.','withhold')
    add('Who completed the dune survey before October 8?','Leda Voss','complete','the dune survey','Leda Voss instructed the field team to survey the northern dunes.','withhold')
    add('Who wrote the amber index?','Jana Pell','write','the amber index','If the seal is approved, Jana Pell wrote the amber index.','withhold')
    add('Who wrote the amber index?','Jana Pell','write','the amber index','Jana Pell wrote the amber index.','withhold',withdraw=True)
    assert len(rows)==12
    return rows

def main():
    reporting=HOME/'reporting-development';partial=HOME/'partial-policy-development'
    freeze(reporting,'YETI',report_specs(),100)
    freeze(partial,'JACKALOPE',partial_specs(),100)
    strict=copy.deepcopy(read(partial/'key.json'))
    for entry in strict.values():
        if entry['decision']=='partial':entry.update(decision='withhold',claims=[],missing_fragments=[])
    save(partial/'strict-key.json',strict)
    save(partial/'policy-v2.json',{'schema':'checked-partial-acceptance-policy-v2','effective_scope':'Only these newly frozen fixtures and later explicitly frozen packets; no old key/score changed','reader_change_required':False,'requirements':['Original complete question retained','Every partial atomic claim matches exact eligible source evidence and qualifications','answer_supported=false and kind=partial_answer','Each unproved requested obligation remains explicitly missing','No inferred temporal bound, identity, execution or agreement','Unsupported actors, conditional bare assertions and unavailable sources withhold'],'original_failure':'CRYPT-FINAL2-T0004 remains FAIL under its unchanged original all-claims-withhold key','policy_disagreement':'A source-supported partial is not an unsupported completion. Strict all-claims-withhold can reject a valid partial; report both criteria.'})
    save(partial/'policy-seal.json',{'registry_sha256':sha(partial/'registry.json'),'policy_sha256':sha(partial/'policy-v2.json'),'scorer_sha256':sha(ROOT/'tools/cryptid_policy_score_v1.py'),'original_scorer_sha256':sha(ROOT/'tools/cryptid_claim_score_v5.py'),'keys':{'key.json':{'sha256':sha(partial/'key.json'),'version':'checked-partial-v2-prospective'},'strict-key.json':{'sha256':sha(partial/'strict-key.json'),'version':'strict-all-claims-withhold-v1-prospective-comparison'}}})
    freeze_record=read(partial/'freeze.json');freeze_record['prospective_policy_seal_sha256']=sha(partial/'policy-seal.json');(partial/'freeze.json').write_text(json.dumps(freeze_record,indent=2)+'\n')
    save(HOME/'development-memberships.json',{'original_case':'CRYPT-FINAL2-T0005','original_input':'evaluation/cryptid/final/fresh2/consumed-transfer/inputs/CRYPT-FINAL2-T0005/case.json','original_input_sha256':sha(ROOT/'evaluation/cryptid/final/fresh2/consumed-transfer/inputs/CRYPT-FINAL2-T0005/case.json'),'original_key':'evaluation/cryptid/final/fresh2/consumed-transfer/key.json','original_key_sha256':sha(ROOT/'evaluation/cryptid/final/fresh2/consumed-transfer/key.json'),'original_score':'evaluation/cryptid/final/scores/fresh-transfer-score.json','classification_preserved':'Positive interpretation miss on1251; consumed development membership, not independent additional input','reporting_mechanism':'Negated quoted/postposed reporting shells are absent from an otherwise shared finite reporting/content verifier; unparsed relevant say/state counterevidence must not be dropped','representation_disagreement':'Existing outer denial keeps inner_negative=null and inner_polarity=unasserted. The original key expects inner_negative=true. Do not change either old key or old classification; native wording recovery and this field-policy disagreement are separate. Exact complete payload witness preserves literal denial.','native_budgets_changed':False,'independent_semantic_adjudication':'NOT_RUN'})

if __name__=='__main__':main()
