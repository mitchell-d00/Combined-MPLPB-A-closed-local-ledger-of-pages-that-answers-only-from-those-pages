"""Structural transfer prepared after limited substitution packet; native frozen."""
from pathlib import Path
import subprocess,zipfile,shutil,json
from tools.cryptid_packet_support import packet,key
from tools.cryptid_trial import ROOT,save,sha
from tools.cryptid_chupacabra_packets import expected,QUAL,Q

def main():
 home=ROOT/'evaluation/cryptid/chupacabra/fresh';home.mkdir();stage=Path('/workspace/cryptid-custody/chupacabra-fresh-build')
 date='September 13, 1892';old='eighteen';new='twenty';dest='the south landing';first=f'This letter was written on {date}. The consignment contains {old} crates for {dest}.';canonical=f'In my letter of {date}, the count should read {new} crates. The destination remains {dest}.'
 texts=[(first,f'In my letter dated {date}, the count should read {new} crates. The destination remains {dest}.'),(f'On {date}, this letter was written. The consignment contains {old} crates for {dest}.',canonical),(first,f'The count in my letter of {date} is corrected from {old} to {new} crates. The destination remains {dest}.'),(first,f'In my letter of {date}, replace the count of {old} crates with {new} crates. The destination remains {dest}.')]
 specs=[]
 for n,(a,b) in enumerate(texts+[(first,'That correction is only a quotation: '+canonical),(first,canonical.replace(date,'January 3, 1894')),(first,canonical),(first,canonical)]):
  decision='complete' if n<4 else 'withhold';sources=[{'id':'ORIGINAL','body_html':'<p>'+a+'</p>'},{'id':'CORRECTION','body_html':'<p>'+b+'</p>'}]
  if n==6:sources[0].update(withdraw=True)
  if n==7:sources[1].update(external='no')
  specs.append({'question':Q,'sources':sources,'profile':'external' if n==7 else 'internal','key':key(decision,expected(old,new,date,dest) if n<4 else None,[],QUAL),'mechanism':'New directive/date sentence structures versus explicit source scope','protected_operation':'Same date/old count/replacement/destination obligations; no execution inference'})
 base=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();packet(stage,'CHUPACABRA',specs,base,'tools/cryptid_chupacabra_fresh.py',True)
 # Distinct stable IDs from consumed first transfer. All prepared before sealing.
 registry=json.loads((stage/'registry.json').read_text());keys=json.loads((stage/'key.json').read_text());renamed={}
 for n,c in enumerate(registry['cases'],101):
  oldid=c['id'];ident=f'CRYPT-CHUPACABRA-T{n:04d}';p=stage/'inputs'/oldid;p.rename(stage/'inputs'/ident);case=json.loads((stage/'inputs'/ident/'case.json').read_text());case['id']=ident;(stage/'inputs'/ident/'case.json').write_text(json.dumps(case,indent=2)+'\n');c.update(id=ident,packet='inputs/'+ident);c['files']['case.json']=sha(stage/'inputs'/ident/'case.json');renamed[ident]=keys[oldid]
 for path,value in [('registry.json',registry),('key.json',renamed)]: (stage/path).write_text(json.dumps(value,indent=2)+'\n')
 freeze=json.loads((stage/'freeze.json').read_text());freeze.update(registry_sha256=sha(stage/'registry.json'),key_sha256=sha(stage/'key.json'));(stage/'freeze.json').write_text(json.dumps(freeze,indent=2)+'\n')
 with zipfile.ZipFile(home/'transfer-sealed.zip','x',compression=zipfile.ZIP_DEFLATED) as z:
  for p in sorted(stage.rglob('*')):
   if p.is_file():z.write(p,str(p.relative_to(stage)))
 save(home/'transfer-seal.json',{'packet_sha256':sha(home/'transfer-sealed.zip'),'cases':8,'generator_seed':20261125061,'generator_sha256':sha(Path(__file__)),'custody':'Same operator templates visible; fresh case bytes not reopened until new committed ZIP freeze; structure differs, no native repair informed by first transfer','native_matches_candidate':'a3c020ad79b3872a622aa23ec8a187089c608b91'})
 shutil.rmtree(stage)
if __name__=='__main__':main()
