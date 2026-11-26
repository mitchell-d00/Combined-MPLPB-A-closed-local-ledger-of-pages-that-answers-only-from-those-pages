"""Frozen qualification-preservation Wrap around newly readable byline boundaries."""
from tools.cryptid_packet_support_v4 import packet,key
from tools.cryptid_trial import ROOT,read,sha
from pathlib import Path
import subprocess,json

def main():
 home=ROOT/'evaluation/cryptid/nessie/wrap';specs=[];statement='Lina Mercer reported that Mara Flint wrote the tidal index.';q='What does Lina Mercer report about whether Mara Flint wrote the tidal index?'
 for governor,quoted in [('If the permit is granted.',False),('if the permit is granted.',False),('Unless the permit is withheld.',False),('unless the permit is withheld.',False),('if the permit is granted.',True),('If the permit is granted.',True)]:
  body='<p>Report.</p><p>Written by Owen Kestrel.</p>'+('<blockquote>'+governor+'</blockquote>' if quoted else '<p>'+governor+'</p>')+'<p>'+statement+'</p>'
  prop={'relation':'source_attributed_report_content','reporter':'Lina Mercer','author':'Mara Flint','object':'the tidal index','conditions':[],'inner_negative':False,'outer_negative':False,'actual_authorship_established':False,'completion_established':False}
  k=key('complete' if quoted else 'withhold',prop if quoted else None,[statement] if quoted else [],['Source-scoped reporting statement','Independent authorship']);k['structure_expected']=True
  specs.append({'question':q,'sources':[{'id':'DOCUMENT-1','body_html':body}],'key':k,'mechanism':'Byline-boundary repair must not erase an external conditional governor or attach an unrelated quotation','protected_operation':'Case-insensitive governor recognition with independent native quotation scope'})
 base=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();packet(home,'NESSIE',specs,base,'tools/cryptid_nessie_governors.py');registry=read(home/'registry.json');keys=read(home/'key.json');out={}
 for n,c in enumerate(registry['cases'],30):
  old=c['id'];ident=f'CRYPT-NESSIE-{n:04d}';p=home/'inputs'/old;p.rename(home/'inputs'/ident);case=read(home/'inputs'/ident/'case.json');case['id']=ident;case['structure_mutation']='none';(home/'inputs'/ident/'case.json').write_text(json.dumps(case,indent=2)+'\n');c.update(id=ident,packet=str((home/'inputs'/ident).relative_to(ROOT)));c['files']['case.json']=sha(home/'inputs'/ident/'case.json');out[ident]=keys[old]
 for p,v in [('registry.json',registry),('key.json',out)]: (home/p).write_text(json.dumps(v,indent=2)+'\n')
 freeze=read(home/'freeze.json');freeze.update(registry_sha256=sha(home/'registry.json'),key_sha256=sha(home/'key.json'));(home/'freeze.json').write_text(json.dumps(freeze,indent=2)+'\n')
if __name__=='__main__':main()
