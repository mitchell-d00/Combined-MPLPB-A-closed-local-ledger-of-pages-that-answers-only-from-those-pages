"""Same-operator question-form development and sealed transfer; no runtime rules."""
from pathlib import Path
import json
import shutil
import zipfile
from tools.cryptid_trial import ROOT,save,sha,snapshot,digest
HOME=ROOT/'evaluation/cryptid/jackalope'
BASE='2f14a1495f7817f441ea2fd078c54048afaef86a'
TOOLS=['tools/cryptid_trial_v2.py','tools/cryptid_adapter_v2.py','tools/cryptid_worker.py','tools/cryptid_claim_score.py','tools/cryptid_jackalope_packets.py','tools/pole_worker.py','tools/study_sandbox.py']


def build(folder,held=False):
    rows=[];key={}
    specs=([('letter','Nadia Foss','wrote','write','written','the granite register'),('minutes','Irena Valdez','sent','send','sent','the harbor schedule'),('report','Galen Reyes','surveyed','survey','surveyed','the southern channel')] if held else [('letter','Talia Rowe','wrote','write','written','the tidal index'),('minutes','Selma Duarte','sent','send','sent','the berth schedule'),('report','Jonas Keene','surveyed','survey','surveyed','the western inlet')])
    for form,actor,past,base,part,obj in specs:
        def body(statement,quoted=False):
            prefix={'letter':'<pre>From: Owen Kestrel\nTo: Vera Moss\n</pre>','minutes':'<pre>Meeting minutes.\nRecorder: Owen Kestrel\n</pre>','report':'<pre>Report.\nWritten by Owen Kestrel\n</pre>'}[form]
            return prefix+('<blockquote>' if quoted else '<p>')+statement+('</blockquote>' if quoted else '</p>')
        def add(question,decision,statement=None,temporal='',quoted=False,source_flags=None,profile='internal'):
            ident='CRYPT-JACKALOPE-'+('T' if held else '')+f'{len(rows)+1:04d}'
            statement=statement or f'{actor} {past} {obj}.'
            packet=folder/'inputs'/ident
            source={'id':'DOCUMENT-1','body_html':body(statement,quoted)};source.update(source_flags or {})
            case={'id':ident,'adapter_mode':'documentary','question':question,'sources':[source],'profile':profile,'budget':{'passages':12,'characters':8000}}
            save(packet/'case.json',case)
            claim={'proposition':{'relation':'source_action_assertion','actor_text':actor,'action':base,'object_text':obj,'negative':False,'temporal_qualification_text':temporal,'unresolved_reference':False,'assertion_modality':'unconditional_source_assertion','event_identity':None},'qualification_fragments':['Source-attributed statement','historical truth are not independently verified'],'complete_witnesses':[statement]}
            key[ident]={'decision':decision,'claims':[] if decision=='withhold' else [claim],'missing_fragments':['voyage'] if decision=='partial' else [],'withholding_conditions':['wrong actor or expanded identity','unproved execution','conditions/negation/time scope not discarded','host policy/integrity/current eligibility']}
            rows.append({'id':ident,'family':'JACKALOPE','packet':'inputs/'+ident if held else str(packet.relative_to(ROOT)),'files':snapshot(packet),'semantic_input_hash':digest(case),'origin':{'test':'ordinary action-question forms across letter/minutes/report with contrasting obligations','prs':[2,57,74,102,104]},'source_form':form,'mechanism':'Question surface form fails to bind the same action/object goal while retaining full original constraints','protected_operation':'Question interpretation proposes shared action goal; native proof independently checks eligible complete witnesses under original question','baseline_commit':BASE,'budgets':{'records':8,'scan_characters':200000,'units':1000,'passages':12,'characters':8000,'cpu_seconds':30,'wall_seconds':45},'expectations':'key.json#'+ident,'candidate_version':'NOT_RUN at freeze; append runtime hashes and committed archive receipts','custody':'same-operator; frozen source bytes and scoring key outside workers; no independent preparation/blinding','raw_output_lookup':'runs/RUN/'+ident+'/result.json'})
        if not held:
            questions=[f'Who {past} {obj}?',f'Which person {past} {obj}?',f'By whom was {obj} {part}?',f'According to the record, identify who {past} {obj}.']
            for q in questions:
                add(q,'complete');add(q.rstrip('.?')+'? And did that person complete the assigned voyage?','partial')
            add(f'Which person did not {base} {obj}?','withhold')
            add(f'If the permit was granted, who {past} {obj}?','withhold')
            add(f'Before February 2, 1880, who {past} {obj}?','withhold')
            add(questions[0],'withhold',quoted=True)
            add(f'Did Richard Nixon {base} {obj}?','withhold',statement=f'RN {past} {obj}.')
            add(f'Did {actor} carry out that instruction?','withhold',statement=f'{actor} was instructed to {base} {obj}.')
            add(questions[0],'withhold',source_flags={'external':'no'},profile='external')
            add(questions[0],'withhold',source_flags={'withdraw':True})
            add(questions[0],'withhold',source_flags={'corrupt':{'old':actor,'new':'Changed Actor'}})
            add(questions[0].rstrip('?')+'? And did that person complete the assigned voyage?','withhold',source_flags={'not_for':'voyage'})
        else:
            for n,q in enumerate((f'Who was it that {past} {obj}?',f'Can you identify which person {past} {obj}?')):
                temporal='In 1893' if n else ''
                statement=(temporal+', ' if temporal else '')+f'{actor} {past} {obj}.'
                add(q,'complete',statement,temporal)
                add(q.rstrip('?')+'? And did that person complete the assigned voyage?','partial',statement,temporal)
                add(q,'withhold',statement,temporal,quoted=True)
                add('Unless the receipt is authenticated, '+q[0].lower()+q[1:],'withhold',statement,temporal)
    save(folder/'registry.json',{'schema':'cryptid-case-registry-v1','family':'JACKALOPE','exposure':'same-operator generator templates visible; exact transfer packet not reopened before candidate freeze' if held else 'development exposed; independently worded relative to retained old suites, not independently prepared','cases':rows})
    save(folder/'key.json',key)
    save(folder/'freeze.json',{'generator_seed':2026112503,'sampling':'deterministic template programme, no random or independent sampling claim','registry_sha256':sha(folder/'registry.json'),'key_sha256':sha(folder/'key.json'),'harness':{p:sha(ROOT/p) for p in TOOLS},'baseline_reader_commit':BASE,'independence':'NOT_RUN'})


def main():
    build(HOME/'development')
    stage=Path('/workspace/cryptid-custody/jackalope-sealed-build');build(stage,True)
    with zipfile.ZipFile(HOME/'transfer-sealed.zip','x',compression=zipfile.ZIP_DEFLATED) as z:
        for p in sorted(stage.rglob('*')):
            if p.is_file():z.write(p,str(p.relative_to(stage)))
    save(HOME/'transfer-seal.json',{'packet_sha256':sha(HOME/'transfer-sealed.zip'),'cases':24,'generator_seed':2026112503,'preparation':'same-operator deterministic templates; cleft/polite question structures, half temporal source clauses; no independence/blinding','packet_opened_after_preparation':False,'open_after':'committed candidate ZIP freeze'})
    shutil.rmtree(stage);print('Development54 and sealed transfer24 frozen before native changes.')

if __name__=='__main__':main()
