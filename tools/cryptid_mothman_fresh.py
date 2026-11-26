"""Fresh same-operator date-role packet sealed before consumed-transfer repair."""
from pathlib import Path
import shutil
import zipfile
from tools.cryptid_trial import ROOT,save,sha,snapshot,digest


def main():
    home=ROOT/'evaluation/cryptid/mothman/fresh';home.mkdir(exist_ok=False)
    stage=Path('/workspace/cryptid-custody/mothman-fresh-build');stage.mkdir(exist_ok=False)
    rows=[];key={};roles={'writing':'written','sending':'sent','receipt':'received','publication':'published'}
    for n,noun in enumerate(('the quartz schedule','the valley dossier')):
        for role,verb in roles.items():
            date=f'October {17+n}, 1891'
            positive=(f'On {date}, {noun} was {verb}.' if not n else f'{noun.capitalize()} was {verb} on {date}.')
            other=next(v for r,v in roles.items() if r!=role)
            variants=[(positive,True),(positive.replace('was '+verb,'was '+other),False),('If permission is granted. '+positive,False)]
            for statement,supported in variants:
                ident=f'CRYPT-MOTHMAN-T{len(rows)+17:04d}';packet=stage/'inputs'/ident
                save(packet/'case.json',{'id':ident,'adapter_mode':'documentary','question':f'Distinguish the {role} dates in {noun} record.','sources':[{'id':'DOC-1','body_html':'<p>'+statement+'</p>'}],'profile':'internal','budget':{'passages':12,'characters':8000},'discovery':True})
                key[ident]={'decision':'answer' if supported else 'withhold','expected_date_links':[[role,date,1891]] if supported else [],'required_qualifications':['source attributed','no unrecorded identity or execution','original date wording'],'withholding_conditions':['wrong explicitly stated role','unmet condition']}
                rows.append({'id':ident,'family':'MOTHMAN','packet':'inputs/'+ident,'files':snapshot(packet),'semantic_input_hash':digest({'statement':statement,'requested_role':role}),'origin':{'test':'fresh same-operator date-role composition','prs':[104]},'mechanism':'Explicit document passive date roles including date-first ordering','protected_operation':'Requested role equals witnessed passive role; outside conditions survive','baseline_commit':'a439ddc2c9e438863383b90c41d995d274785847','budgets':{'records':8,'scan_characters':200000,'units':1000,'passages':12,'characters':8000,'cpu_seconds':30,'wall_seconds':45},'custody':'same-operator, templates visible; exact packet not reopened after preparation'})
    save(stage/'registry.json',{'schema':'cryptid-case-registry-v1','family':'MOTHMAN','exposure':'same-operator; date-first structural transfer subset plus date-last substitutions; not independent preparation or blinding','cases':rows})
    save(stage/'key.json',key)
    tools=['tools/cryptid_trial.py','tools/cryptid_score.py','tools/cryptid_mothman_fresh.py','tools/bubble_wrap_adapter.py','tools/bubble_wrap_worker.py','tools/pole_worker.py','tools/study_sandbox.py']
    save(stage/'freeze.json',{'generator_seed':202611250203,'registry_sha256':sha(stage/'registry.json'),'key_sha256':sha(stage/'key.json'),'harness':{p:sha(ROOT/p) for p in tools},'baseline_reader_commit':'a439ddc2c9e438863383b90c41d995d274785847','independence':'NOT_RUN'})
    with zipfile.ZipFile(home/'transfer-sealed.zip','x',compression=zipfile.ZIP_DEFLATED) as z:
        for p in sorted(stage.rglob('*')):
            if p.is_file():z.write(p,str(p.relative_to(stage)))
    save(home/'transfer-seal.json',{'packet_sha256':sha(home/'transfer-sealed.zip'),'cases':24,'expected_positive':8,'expected_withhold':16,'generator_seed':202611250203,'preparation':'same-operator; wording templates visible; four date-first positives structurally differ from consumed transfer, four date-last positives are limited substitution transfer','packet_opened_after_preparation':False,'open_after':'committed candidate4ZIP freeze'})
    shutil.rmtree(stage)

if __name__=='__main__':main()
