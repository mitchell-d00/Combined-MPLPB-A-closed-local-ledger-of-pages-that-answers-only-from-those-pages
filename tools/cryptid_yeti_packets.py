"""Frozen same-operator polarity/modality inputs and separate sealed transfer."""
from pathlib import Path
import json,shutil,zipfile
from tools.cryptid_trial import ROOT,save,sha,snapshot,digest
HOME=ROOT/'evaluation/cryptid/yeti';BASE='814e793241f18e3bfe6d15ce742f4b3eac37623a'
TOOLS=['tools/cryptid_trial_v3.py','tools/cryptid_adapter_v3.py','tools/cryptid_worker_v3.py','tools/cryptid_claim_score_v3.py','tools/cryptid_yeti_packets.py','tools/pole_worker.py','tools/study_sandbox.py']
WRITER='Owen Kestrel';TEAM='the cargo team';OBJ='the canal';BOOK='the marine index'


def render(form,statement):
    if form=='letter':return '<p>Dear Vera Moss:</p><p>'+statement+'</p><p>Sincerely,<br>'+WRITER+'</p>'
    label,byline=('Meeting minutes.','Recorded by') if form=='minutes' else ('Report.','Written by')
    return '<p>'+label+'</p><p>'+byline+' '+WRITER+'.</p><p>'+statement+'</p>'


def atomic(actor,obj,negative,witness,relation='source_action_assertion'):
    return {'proposition':{'relation':relation,'actor_text':actor,'action':'write','object_text':obj,'negative':negative,'unresolved_reference':False},'qualification_fragments':['not independently verified'],'complete_witnesses':[witness]}


def modal(actor,kind,form,obj,witness,conditions=None,content_negative=False):
    return {'proposition':{'relation':'source_modality_assertion','actor':actor,'modality':kind,'source_form':form,'source_writer_or_unknown':WRITER,'task_actor':actor if kind in {'intention','conditional','completed_action'} else TEAM,'task_action':'complete' if kind=='completed_action' else 'inspect','task_object':obj,'outer_negative':False,'content_negative':content_negative,'conditions':conditions or [],'completion_asserted_by_source':kind=='completed_action','execution_independently_verified':False,'historical_truth_independently_verified':False},'qualification_fragments':['Source-attributed','not independently verified'],'complete_witnesses':[witness]}


def report(actor,author,obj,witness,mode):
    outer=mode=='denial_of_reporting';conditional=mode=='conditional_reporting';inner=mode=='reported_denial'
    return {'proposition':{'relation':'source_attributed_report_content','reporter':actor,'author':author,'inner_action':'write','object':obj,'inner_negative':None if outer or conditional else inner,'outer_negative':outer,'content_asserted_by_reporter':not outer and not conditional,'outer_polarity':'conditional_unestablished' if conditional else 'negative' if outer else 'affirmative','inner_polarity':'unasserted' if outer or conditional else 'negative' if inner else 'affirmative','conditions':['If the permit is granted'] if conditional else [],'actual_authorship_established':False,'completion_established':False},'qualification_fragments':['Source-scoped reporting statement','Independent authorship'],'complete_witnesses':[witness]}


def build(folder,held=False):
    rows=[];keys={}
    def add(question,sources,decision,claims=None,origin=None,form=None):
        ident='CRYPT-YETI-'+('T' if held else '')+f'{len(rows)+1:04d}';packet=folder/'inputs'/ident
        if origin:
            shutil.copytree(ROOT/'evaluation/current-failure-inventory'/origin['input_path'],packet);assert snapshot(packet)==origin['files']
        else:save(packet/'case.json',{'id':ident,'adapter_mode':'documentary','question':question,'sources':sources,'profile':'internal','budget':{'passages':12,'characters':8000}})
        keys[ident]={'decision':decision,'claims':claims or [],'missing_fragments':[],'withholding_conditions':['unproved execution or independent occurrence','different actor/layer','polarity/modality mismatch','withdrawal or ineligibility'],'historical_expected':origin.get('expected') if origin else None}
        rows.append({'id':ident,'family':'YETI','packet':'inputs/'+ident if held else str(packet.relative_to(ROOT)),'files':snapshot(packet),'semantic_input_hash':digest({'question':question,'files':snapshot(packet)}),'origin':origin or {'test':'local frozen source-claim polarity/modality contrast','related_prs':[17,28,56,101,102,103]},'source_form':form,'mechanism':'Source denial/modality lacks a source-scoped answer operation; reporting and content polarity must remain distinct','protected_operation':'Exact eligible complete witnesses -> shared source claim frame -> source-scoped status, never inferred execution','baseline_commit':BASE,'budgets':{'records':8,'scan_characters':200000,'units':1000,'passages':12,'characters':8000,'cpu_seconds':30,'wall_seconds':45},'expectations':'key.json#'+ident,'custody':'same-operator preparation/scoring; no independent blinding/adjudication','raw_output_lookup':'runs/RUN/'+ident+'/result.json'})
    if not held:
        selection=json.loads((ROOT/'evaluation/current-failure-inventory/selection.json').read_text())
        for c in selection['cases']:
            if c['family'] not in {'negated_statement','instruction_statement'}:continue
            packet=ROOT/'evaluation/current-failure-inventory'/c['input_path'];case=json.loads((packet/'case.json').read_text())
            if c['family']=='negated_statement':
                actor,obj=('Edda Marén','the orchard inventory') if c['id']=='DP00028' else ('Mira Vale','the harbor report')
                witness=f'{actor} did not write {obj}.';add(case['question'],[],'complete',[atomic(actor,obj,True,witness)],origin=c)
            else:add(case['question'],[],'diagnostic',origin=c)
    kinds=['affirmation','denial','reported_affirmation','reported_denial','denial_of_reporting','conditional_reporting','instruction','intention','recommendation','forecast','conditional','completed_action']
    if held:kinds=['denial','intention','recommendation','forecast','conditional','completed_action','instruction','reported_denial','denial_of_reporting','conditional_reporting']
    specs=[]
    for n,kind in enumerate(kinds):
        actor=('Leona Silva' if held else 'Mara Flint');author='Ivo Keene';form=('letter','minutes','report')[(n+2 if held else n)%3]
        obj='the inlet inspection' if kind=='completed_action' else BOOK if kind in {'affirmation','denial','reported_affirmation','reported_denial','denial_of_reporting','conditional_reporting'} else OBJ
        if kind=='affirmation':
            statement=f'{actor} wrote {obj}.';q=f'Who wrote {obj}?';claim=atomic(actor,obj,False,statement)
        elif kind=='denial':
            statement=(f'{obj.capitalize()} was not written by {actor}.' if held else f'{actor} did not write {obj}.');q=f'What does the record deny about {actor} and {obj}?';claim=atomic(actor,obj,True,statement,'source_passive_action_assertion' if held else 'source_action_assertion')
        elif kind.startswith('reported_') or kind in {'denial_of_reporting','conditional_reporting'}:
            statement=(f'{actor} reported that {author} '+('did not write' if kind=='reported_denial' else 'wrote')+f' {obj}.')
            if held and kind=='reported_denial':statement=f'The statement that {author} did not write {obj} was reported by {actor}.'
            if kind=='denial_of_reporting':statement=f'{actor} did not report that {author} wrote {obj}.'
            if kind=='conditional_reporting':statement=(f'If the permit is granted, the statement that {author} wrote {obj} would be reported by {actor}.' if held else f'If the permit is granted, {actor} would report that {author} wrote {obj}.')
            q=f'What conditional authorship statement does {actor} report about {obj}?' if kind=='conditional_reporting' else f'What does {actor} report about whether {author} wrote {obj}?'
            claim=report(actor,author,obj,statement,kind)
        elif kind=='instruction':
            statement=f'The instruction given by {actor} to {TEAM} was to inspect {obj}.' if held else f'{actor} instructed {TEAM} to inspect {obj}.'
            if not held:
                q=f'According to the {form}, what did {actor} instruct {TEAM} to do?'
                claim={'proposition':{'relation':'source_attributed_instruction','actor':actor,'writer':WRITER,'recipient':TEAM,'task':f'inspect {obj}','source_form':form,'modality':'instruction_only','polarity':'affirmative','completion_established':False},'qualification_fragments':['Source-attributed instruction only','execution remain unverified'],'complete_witnesses':[statement]}
            else:q=f'What instruction does the record attribute to {actor} concerning {obj}?';claim=modal(actor,kind,form,obj,statement)
        else:
            word={'intention':'intention','recommendation':'recommendation','forecast':'forecast','conditional':'conditional statement','completed_action':'completed action'}[kind]
            q=f'What {word} does the record attribute to {actor} concerning {obj}?'
            statement={'intention':f"{actor}'s stated intention was to inspect {obj}." if held else f'{actor} intended to inspect {obj}.','recommendation':f"{actor}'s recommendation to {TEAM} was to inspect {obj}." if held else f'{actor} recommended that {TEAM} inspect {obj}.','forecast':f'{actor} predicted that {TEAM} would inspect {obj}.' if held else f'{actor} forecast that {TEAM} would inspect {obj}.','conditional':f'{actor} would inspect {obj} only if the marker is present.' if held else f'If the marker is present, {actor} would inspect {obj}.','completed_action':f'{actor} had completed {obj}.' if held else f'{actor} completed {obj}.'}[kind]
            conditions=['only if the marker is present' if held else 'If the marker is present'] if kind=='conditional' else []
            claim=modal(actor,kind,form,obj,statement,conditions)
        source={'id':'DOCUMENT-1','body_html':render(form,statement)}
        add(q,[source],'complete',[claim],form=form)
        wrong=q.replace(actor,WRITER) if kind!='affirmation' else f'Did {WRITER} write {obj}?'
        add(wrong,[source],'withhold',form=form)
        if held:add(q,[dict(source,withdraw=True)],'withhold',form=form)
        else:
            execution=(f'Who wrote {obj}?' if kind in {'reported_affirmation','reported_denial','denial_of_reporting','conditional_reporting'} else f'According to the {form}, did {TEAM} complete the task instructed by {actor}?' if kind=='instruction' else f'Did {actor} conclude an agreement about {obj}?')
            add(execution,[source],'withhold',form=form)
        specs.append((kind,actor,form,obj,q,statement,claim,source))
    if not held:
        by_kind={r[0]:r for r in specs}
        for kind in ('denial','instruction','intention','conditional'):
            _,actor,form,obj,q,statement,claim,source=by_kind[kind];add(q,[dict(source,withdraw=True)],'withhold',form=form)
        for kind in ('instruction','intention'):
            _,actor,form,obj,q,statement,claim,source=by_kind[kind]
            q=f'What {kind} does the record attribute to {actor} concerning {obj}?';full='If the marker is present. '+statement
            c=modal(actor,kind,form,obj,statement,['If the marker is present']);c['complete_witnesses']=['If the marker is present.',statement]
            add(q,[{'id':'DOCUMENT-1','body_html':render(form,full)}],'complete',[c],form=form)
        for kind in ('instruction','forecast'):
            _,actor,form,obj,q,statement,claim,source=by_kind[kind];q=f'What {kind} does the record attribute to {actor} concerning {obj}?'
            negative=f'{actor} instructed {TEAM} not to inspect {obj}.' if kind=='instruction' else f'{actor} forecast that {TEAM} would not inspect {obj}.'
            add(q,[{'id':'DOCUMENT-1','body_html':render(form,negative)}],'complete',[modal(actor,kind,form,obj,negative,content_negative=True)],form=form)
            outer=f'{actor} did not instruct {TEAM} to inspect {obj}.' if kind=='instruction' else f'{actor} did not forecast that {TEAM} would inspect {obj}.'
            add(q,[{'id':'DOCUMENT-1','body_html':render(form,outer)}],'withhold',form=form)
        _,actor,form,obj,q,statement,claim,source=by_kind['denial'];opposed=f'{actor} wrote {obj}.'
        add(q,[source,{'id':'DOCUMENT-2','body_html':render(form,opposed)}],'conflict',[claim,atomic(actor,obj,False,opposed)],form=form)
        _,actor,form,obj,q,statement,claim,source=by_kind['intention'];opposed=f'{actor} did not intend to inspect {obj}.';negative=modal(actor,'intention',form,obj,opposed);negative['proposition']['outer_negative']=True
        add(q,[source,{'id':'DOCUMENT-2','body_html':render(form,opposed)}],'conflict',[claim,negative],form=form)
    save(folder/'registry.json',{'schema':'cryptid-case-registry-v1','family':'YETI','exposure':'same-operator; templates visible; sealed transfer exact bytes not reopened until candidate freeze' if held else 'development exposed; old source hashes unchanged; two first-person arrangement leads diagnostic only','cases':rows})
    save(folder/'key.json',keys)
    save(folder/'freeze.json',{'generator_seed':2026112504,'sampling':'deterministic templates, no random or independent sampling claim','registry_sha256':sha(folder/'registry.json'),'key_sha256':sha(folder/'key.json'),'harness':{p:sha(ROOT/p) for p in TOOLS},'baseline_reader_commit':BASE,'independence':'NOT_RUN'})


def main():
    HOME.mkdir(exist_ok=False);build(HOME/'development');stage=Path('/workspace/cryptid-custody/yeti-sealed-build');build(stage,True)
    with zipfile.ZipFile(HOME/'transfer-sealed.zip','x',compression=zipfile.ZIP_DEFLATED) as z:
        for p in sorted(stage.rglob('*')):
            if p.is_file():z.write(p,str(p.relative_to(stage)))
    save(HOME/'transfer-seal.json',{'packet_sha256':sha(HOME/'transfer-sealed.zip'),'cases':30,'generator_seed':2026112504,'preparation':'same-operator templates visible; passive/nominal/postposed/past-perfect and passive-conditional reporting forms; no independence/blinding','packet_opened_after_preparation':False,'open_after':'committed candidate ZIP freeze'})
    shutil.rmtree(stage);print('Frozen Yeti development and separate sealed30transfer.')

if __name__=='__main__':main()
