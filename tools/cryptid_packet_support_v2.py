"""Host-only deterministic packet writer; never shipped into reader workers."""
from pathlib import Path
import shutil,zipfile,subprocess
from tools.cryptid_trial import ROOT,save,sha,snapshot,digest
TOOLS=['tools/cryptid_trial_v3.py','tools/cryptid_adapter_v3.py','tools/cryptid_worker_v3.py','tools/cryptid_claim_score_v3.py','tools/pole_worker.py','tools/study_sandbox.py','tools/cryptid_packet_support_v2.py','tools/cryptid_claim_score_v5.py']
BUDGET={'records':8,'scan_characters':200000,'units':1000,'passages':12,'characters':8000,'cpu_seconds':30,'wall_seconds':45}
def packet(folder,family,specs,base,generator,held=False):
    folder.mkdir(parents=True,exist_ok=False);rows=[];keys={}
    for n,s in enumerate(specs,1):
        ident=f'CRYPT-{family}-'+('T' if held else '')+f'{n:04d}';p=folder/'inputs'/ident
        case={'id':ident,'adapter_mode':'documentary','question':s['question'],'sources':s['sources'],'profile':s.get('profile','internal'),'budget':s.get('budget',{'passages':12,'characters':8000})}
        save(p/'case.json',case);keys[ident]=s['key']
        rows.append({'id':ident,'family':family,'packet':'inputs/'+ident if held else str(p.relative_to(ROOT)),'files':snapshot(p),'semantic_input_hash':digest(case),'origin':s.get('origin',{'test':s['mechanism'],'prs':[104]}),'mechanism':s['mechanism'],'protected_operation':s['protected_operation'],'baseline_commit':base,'budgets':BUDGET,'expectations':'key.json#'+ident,'candidate_version':'Append immutable run/ZIP receipts','custody':'same operator, deterministic visible templates; no independent preparation/blinding/scoring','raw_output_lookup':'runs/RUN/'+ident+'/result.json'})
    save(folder/'registry.json',{'schema':'cryptid-case-registry-v1','family':family,'exposure':'sealed instance bytes not reopened until committed candidate; generator templates visible' if held else 'development exposed','cases':rows});save(folder/'key.json',keys)
    save(folder/'freeze.json',{'registry_sha256':sha(folder/'registry.json'),'key_sha256':sha(folder/'key.json'),'harness':{p:sha(ROOT/p) for p in TOOLS+[generator]},'baseline_reader_commit':base,'independence':'NOT_RUN'})
def programme(family,specs,transfer,generator,seed):
    home=ROOT/'evaluation/cryptid'/family.lower();home.mkdir(exist_ok=False)
    base=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();packet(home/'development',family,specs,base,generator)
    stage=Path('/workspace/cryptid-custody')/(family.lower()+'-sealed-build');packet(stage,family,transfer,base,generator,True)
    with zipfile.ZipFile(home/'transfer-sealed.zip','x',compression=zipfile.ZIP_DEFLATED) as z:
        for p in sorted(stage.rglob('*')):
            if p.is_file():z.write(p,str(p.relative_to(stage)))
    save(home/'transfer-seal.json',{'packet_sha256':sha(home/'transfer-sealed.zip'),'cases':len(transfer),'generator_seed':seed,'generator_sha256':sha(ROOT/generator),'preparation':'same-operator deterministic structure-varying templates; not independently blind','packet_opened_after_preparation':False,'open_after':'committed candidate ZIP freeze'})
    shutil.rmtree(stage)
def key(decision,proposition=None,witnesses=(),qualifiers=('Historical identity and independent corroboration remain unverified',)):
    return {'decision':decision,'claims':[] if proposition is None else [{'proposition':proposition,'qualification_fragments':list(qualifiers),'complete_witnesses':list(witnesses)}],'missing_fragments':[],'withholding_conditions':['no outside identity','unique eligible complete witness required','no inferred execution','original question/host policy/current hash authoritative']}
