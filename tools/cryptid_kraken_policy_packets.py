"""Source-origin admission is host fixture metadata, never a tag's permission."""
from pathlib import Path
import subprocess,shutil,json,zipfile
from tools.cryptid_packet_support_v3 import packet,key
from tools.cryptid_trial import ROOT,read,save,sha

def specs(held=False):
 actor,sender,receiver=('Vera Moss','Jonas Calder','Lina Reyes') if held else ('Mara Flint','Len Kay','Bea Park');obj='the tide register' if held else 'the water chart';dest='the southern quay' if held else 'the west landing'
 q='For sources REQUEST, DISPATCH and RECEIPT, trace the checked request, dispatch and reported receipt and identify unresolved links.' if held else 'What is established and missing in the request, dispatch and reported receipt chain in sources REQUEST, DISPATCH and RECEIPT?'
 texts=[f'{actor} requested that {sender} send {obj} to {dest}.',f'In response to request source REQUEST, {sender} sent {obj} to {dest}.',f'Referring to dispatch source DISPATCH, {receiver} reported receiving {obj} at {dest} from {sender}.'];rows=[]
 variants=['internal-full','external-scoped','external-private','internal-prefix']* (3 if held else 1)
 for n,variant in enumerate(variants):
  sources=[{'id':i,'body_html':'<pre>'+t.replace(' that ',' that\n').replace(', ',',\n')+'</pre>' if held else '<p>'+t+'</p>','origin':'human','scope':q} for i,t in zip(['REQUEST','DISPATCH','RECEIPT'],texts)]
  if variant=='external-private':sources[1]['external']='no'
  count=2 if variant=='internal-prefix' else 3
  if count==2:sources=sources[:2]
  decision='withhold' if variant.startswith('external') else 'partial' if count==2 else 'complete'
  c={'proposition':{'relation':'documentary_chain_prefix','verified_roles':['request','dispatch','reported_receipt'][:count],'sender':sender,'object':obj,'destination':dest,'completion_established':False,'receipt_independently_verified':False},'qualification_fragments':['cited source statements only','Reading, acknowledgment and task completion remain unproved'],'complete_witnesses':texts[:count]}
  k=key(decision);k['claims']=[] if decision=='withhold' else [c];k['missing_fragments']=['receipt'] if count==2 else []
  if decision=='complete':k['allowed_partial_claims']=[dict(c,proposition=dict(c['proposition'],verified_roles=['request','dispatch']),complete_witnesses=texts[:2])]
  # Repeat variants use independently sealed source wording/layout, not independent evidence.
  if held and n>=4:
   for s in sources:s['body_html']=s['body_html'].replace(' to ', ' to\n') if n<8 else s['body_html'].replace(' the ', '\nthe ')
  rows.append({'question':q,'sources':sources,'profile':'external' if variant.startswith('external') else 'internal','key':k,'mechanism':'Matching declared scopes must not bypass no-prose delivery policy','protected_operation':'Host origin/profile/scope gating before checked-prefix synthesis'})
 return rows

def rename(folder,start,transfer):
 registry=read(folder/'registry.json');keys=read(folder/'key.json');out={}
 for n,c in enumerate(registry['cases'],start):
  old=c['id'];ident='CRYPT-KRAKEN-'+('T' if transfer else '')+f'{n:04d}';p=folder/'inputs'/old;p.rename(folder/'inputs'/ident);case=read(folder/'inputs'/ident/'case.json');case['id']=ident;(folder/'inputs'/ident/'case.json').write_text(json.dumps(case,indent=2)+'\n');c.update(id=ident,packet='inputs/'+ident if transfer else str((folder/'inputs'/ident).relative_to(ROOT)));c['files']['case.json']=sha(folder/'inputs'/ident/'case.json');out[ident]=keys[old]
 for path,value in [('registry.json',registry),('key.json',out)]: (folder/path).write_text(json.dumps(value,indent=2)+'\n')
 freeze=read(folder/'freeze.json');freeze.update(registry_sha256=sha(folder/'registry.json'),key_sha256=sha(folder/'key.json'));(folder/'freeze.json').write_text(json.dumps(freeze,indent=2)+'\n')
def main():
 base=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();home=ROOT/'evaluation/cryptid/kraken';packet(home/'wrap','KRAKEN',specs(),base,'tools/cryptid_kraken_policy_packets.py');rename(home/'wrap',90,False)
 fresh=home/'fresh';fresh.mkdir();stage=Path('/workspace/cryptid-custody/kraken-policy-build');packet(stage,'KRAKEN',specs(True),base,'tools/cryptid_kraken_policy_packets.py',True);rename(stage,101,True)
 with zipfile.ZipFile(fresh/'transfer-sealed.zip','x',compression=zipfile.ZIP_DEFLATED) as z:
  for p in sorted(stage.rglob('*')):
   if p.is_file():z.write(p,str(p.relative_to(stage)))
 save(fresh/'transfer-seal.json',{'packet_sha256':sha(fresh/'transfer-sealed.zip'),'cases':12,'generator_seed':20261125072,'generator_sha256':sha(Path(__file__)),'custody':'same-operator visible templates; multiline clauses and new actors/task; narrow policy/layout transfer, not general syntax transfer','open_after':'new committed candidate ZIP freeze'})
 shutil.rmtree(stage)
if __name__=='__main__':main()
