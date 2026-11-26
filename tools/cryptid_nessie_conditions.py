"""Case-independent external conditions on distinct source modalities."""
from tools.cryptid_packet_support_v4 import packet,key
from tools.cryptid_trial import ROOT,read,sha
from pathlib import Path
import subprocess,json

def main():
 home=ROOT/'evaluation/cryptid/nessie/condition-wrap';specs=[]
 for actor,kind,governor,statement,taskactor in [('Mara Flint','intention','if the marker is present.','Mara Flint intended to inspect the canal.','Mara Flint'),('Nora Ibarra','forecast','unless the marker is absent.','Nora Ibarra forecast that the cargo team would inspect the canal.','the cargo team')]:
  prop={'relation':'source_modality_assertion','actor':actor,'modality':kind,'source_form':'report','source_writer_or_unknown':'Owen Kestrel','task_actor':taskactor,'task_action':'inspect','task_object':'the canal','conditions':[governor[:-1]],'completion_asserted_by_source':False,'execution_independently_verified':False,'historical_truth_independently_verified':False}
  k=key('complete',prop,[governor,statement],['Source-attributed','not independently verified']);k['structure_expected']=True
  specs.append({'question':f'What {kind} does the record attribute to {actor} concerning the canal?','sources':[{'id':'DOCUMENT-1','body_html':'<p>Report.</p><p>Written by Owen Kestrel.</p><p>'+governor+'</p><p>'+statement+'</p>'}],'key':k,'mechanism':'External lowercase governor is left unresolved despite complete explicit source evidence','protected_operation':'Shared qualification scope preserves literal conditions on intentions and forecasts without asserting execution'})
 base=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();packet(home,'NESSIE',specs,base,'tools/cryptid_nessie_conditions.py');registry=read(home/'registry.json');keys=read(home/'key.json');out={}
 for n,c in enumerate(registry['cases'],40):
  old=c['id'];ident=f'CRYPT-NESSIE-{n:04d}';p=home/'inputs'/old;p.rename(home/'inputs'/ident);case=read(home/'inputs'/ident/'case.json');case['id']=ident;case['structure_mutation']='none';(home/'inputs'/ident/'case.json').write_text(json.dumps(case,indent=2)+'\n');c.update(id=ident,packet=str((home/'inputs'/ident).relative_to(ROOT)));c['files']['case.json']=sha(home/'inputs'/ident/'case.json');out[ident]=keys[old]
 for p,v in [('registry.json',registry),('key.json',out)]: (home/p).write_text(json.dumps(v,indent=2)+'\n')
 freeze=read(home/'freeze.json');freeze.update(registry_sha256=sha(home/'registry.json'),key_sha256=sha(home/'key.json'));(home/'freeze.json').write_text(json.dumps(freeze,indent=2)+'\n')
if __name__=='__main__':main()
