"""Carry correction-link writer consistency from metadata to signed letters."""
from tools.cryptid_packet_support_v4 import packet,key
from tools.cryptid_trial import ROOT,read,sha
from pathlib import Path
import subprocess,json

def main():
 home=ROOT/'evaluation/cryptid/nessie/signer-wrap';specs=[];q='What count does the later statement correct, and which destination does it retain?';date='July 18, 1879'
 for left,right,decision in [('Mara Flint','Nora Ibarra','withhold'),('Richard Nixon','RN','withhold'),('Mara Flint','Mara Flint','complete'),('Richard Nixon','Richard Nixon','complete')]:
  writing=f'This letter was written on {date}.';count='The cargo contains four crates for the west depot.';correction=f'In my letter of {date}, the count should read seven crates. The destination remains the west depot.'
  def letter(text,signer):return '<p>Dear Vera Moss:</p><p>'+text+'</p><p>Sincerely,<br>'+signer+'</p>'
  sources=[{'id':'ORIGINAL','body_html':letter(writing+' '+count,left)},{'id':'CORRECTION','body_html':letter(correction,right)}]
  prop={'relation':'source_scoped_count_correction','previous_count':'four','replacement_count':'seven','unit':'crates','destination_retained':'the west depot','target_writing_date':date,'execution_established':False}
  k=key(decision,prop if decision=='complete' else None,[writing,count,correction] if decision=='complete' else [],['Source correction statement only','does not establish dispatch, receipt or actual cargo']);k['structure_expected']=True
  specs.append({'question':q,'sources':sources,'key':k,'mechanism':'First-person date links cannot ignore distinct full signatures or expand an initials-only signature','protected_operation':'One scoped consistency rule for printed headers and signed-letter markers; no authenticated identity inference'})
 base=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();packet(home,'NESSIE',specs,base,'tools/cryptid_nessie_signers.py');registry=read(home/'registry.json');keys=read(home/'key.json');out={}
 for n,c in enumerate(registry['cases'],46):
  old=c['id'];ident=f'CRYPT-NESSIE-{n:04d}';p=home/'inputs'/old;p.rename(home/'inputs'/ident);case=read(home/'inputs'/ident/'case.json');case['id']=ident;case['structure_mutation']='none';(home/'inputs'/ident/'case.json').write_text(json.dumps(case,indent=2)+'\n');c.update(id=ident,packet=str((home/'inputs'/ident).relative_to(ROOT)));c['files']['case.json']=sha(home/'inputs'/ident/'case.json');out[ident]=keys[old]
 for p,v in [('registry.json',registry),('key.json',out)]: (home/p).write_text(json.dumps(v,indent=2)+'\n')
 freeze=read(home/'freeze.json');freeze.update(registry_sha256=sha(home/'registry.json'),key_sha256=sha(home/'key.json'));(home/'freeze.json').write_text(json.dumps(freeze,indent=2)+'\n')
if __name__=='__main__':main()
