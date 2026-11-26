"""Freeze raw versus automatic source-linked structure on identical source bytes."""
from tools.cryptid_packet_support_v4 import programme,key
from tools.cryptid_trial import ROOT,read,sha
from pathlib import Path
import json,zipfile,shutil
QUAL=['Source-attributed statement','historical truth are not independently verified']
def build(held=False):
 actor='Nora Ibarra' if held else 'Mara Flint';obj='the coastal register' if held else 'the tidal index';statement=f'{actor} wrote {obj}.';header='From: Owen Kestrel\nTo: Vera Moss\n';q=f'Who wrote {obj}?';rows=[]
 def add(body,decision='complete',mutation='none',tag=True,report=None,extra=None):
  prop={'relation':'source_action_assertion','actor_text':actor,'action':'write','object_text':obj,'negative':False,'unresolved_reference':False}
  if report:
   who='Lina Mercer';q1=f'What does {who} report about whether {actor} wrote {obj}?';prop={'relation':'source_attributed_report_content','reporter':who,'author':actor,'object':obj,'inner_negative':False,'outer_negative':False,'actual_authorship_established':False,'completion_established':False};quals=['Source-scoped reporting statement','Independent authorship'];witness=f'{who} reported that {actor} wrote {obj}.'
  else:q1=q;quals=QUAL;witness=statement
  k=key(decision,prop if decision!='withhold' else None,[witness] if decision!='withhold' else [],quals)
  sources=[{'id':'DOCUMENT-1','body_html':body}];profile='internal'
  if extra:
   sources[0].update(extra)
   if extra.get('external')=='no':profile='external'
  rows.append({'question':q1,'sources':sources,'profile':profile,'key':k,'structure_mutation':mutation,'structure_expected':tag,'mechanism':'Flattened header/byline boundaries block complete source clauses; tags cannot supply facts or permissions','protected_operation':'Independently verify original HTML boundary and exact canonical witnesses under the original question'})
 base='<pre>'+header+'</pre><p>'+statement+'</p>'
 if held:
  for markup in [base,'<article>'+base+'</article>','<section>'+base+'</section>','<pre>'+header.replace('Owen Kestrel','Owen &lt;owen@example.org&gt;')+'</pre><p>'+statement+'</p>']:
   add(markup)
  add('<pre>'+header+'Subject: Conditional instructions\n</pre><p>'+statement+'</p>','withhold')
  add('<blockquote>'+base+'</blockquote>','withhold')
  add(base,extra={'external':'no'},decision='withhold',tag=False)
  add(base,extra={'withdraw':True},decision='withhold',tag=False)
  add(base,mutation='altered_original',tag=False);add(base,mutation='swapped_roles',tag=False)
  report=f'Lina Mercer reported that {actor} wrote {obj}.'
  add('<p>Report.</p><p>Written by Owen Kestrel.</p><p>'+report+'</p>',report=True)
  add('<p>Meeting minutes.</p><p>Recorded by Owen Kestrel.</p><p>'+report+'</p>',report=True)
 else:
  add(base);add('<pre>'+header+'Date written: March 9, 1882\n</pre><p>'+statement+'</p>');add('<article>'+base+'</article>');add('<pre>'+header.rstrip('\n')+'</pre><p>'+statement+'</p>')
  add('<pre>'+header+'Subject: Routine\n If approved\n</pre><p>'+statement+'</p>','withhold')
  add('<pre>'+header+'Subject: Conditional instruction\n</pre><p>'+statement+'</p>','withhold')
  add('<blockquote>'+base+'</blockquote>','withhold')
  add('<pre>'+header+'From: Ivo Calder\n</pre><p>'+statement+'</p>','withhold')
  report=f'Lina Mercer reported that {actor} wrote {obj}.'
  add('<p>Report.</p><p>Written by Owen Kestrel.</p><p>'+report+'</p>',report=True)
  add('<p>Meeting minutes.</p><p>Recorded by Owen Kestrel.</p><p>'+report+'</p>',report=True)
  add('<pre>'+header+'Date written: March 9\n</pre><p>'+statement+'</p>')
  add(base,'withhold',tag=False,extra={'corrupt':{'old':actor,'new':'Altered Actor'}})
  add(base,'withhold',tag=False,extra={'external':'no'})
  for mode in ['private','famous','swapped_roles','altered_span','altered_original','stale_hash','wrong_kind','forged_relation']:add(base,mutation=mode,tag=False)
 return rows

def extras(home,specs,held=False):
 registry=read(home/'registry.json');keys=read(home/'key.json')
 for c,s in zip(registry['cases'],specs):
  p=home/'inputs'/c['id']/'case.json';v=read(p);v['structure_mutation']=s['structure_mutation'];p.write_text(json.dumps(v,indent=2)+'\n');c['files']['case.json']=sha(p);keys[c['id']]['structure_expected']=s['structure_expected']
 for p,v in [('registry.json',registry),('key.json',keys)]: (home/p).write_text(json.dumps(v,indent=2)+'\n')
 freeze=read(home/'freeze.json');freeze.update(registry_sha256=sha(home/'registry.json'),key_sha256=sha(home/'key.json'));(home/'freeze.json').write_text(json.dumps(freeze,indent=2)+'\n')
def main():
 # Add public mutation operations and separate tag expectations during preparation,
 # before final seals and before any native changes. Keys never enter workers.
 programme('NESSIE',build(),build(True),'tools/cryptid_nessie_packets.py',2026112508)
 home=ROOT/'evaluation/cryptid/nessie';extras(home/'development',build())
 # Preserve initial preparatory seal as an unused packet, not a run or a pass.
 (home/'transfer-sealed.zip').rename(home/'preparatory-transfer-unused.zip');(home/'transfer-seal.json').rename(home/'preparatory-transfer-unused-seal.json')
 stage=Path('/workspace/cryptid-custody/nessie-final-seal');stage.mkdir()
 with zipfile.ZipFile(home/'preparatory-transfer-unused.zip') as z:z.extractall(stage)
 extras(stage,build(True),True)
 with zipfile.ZipFile(home/'transfer-sealed.zip','x',compression=zipfile.ZIP_DEFLATED) as z:
  for p in sorted(stage.rglob('*')):
   if p.is_file():z.write(p,str(p.relative_to(stage)))
 seal=read(home/'preparatory-transfer-unused-seal.json');seal['packet_sha256']=sha(home/'transfer-sealed.zip');seal['preparation_note']='Final public mutation modes and outside-worker tag expectations frozen before native code; initial unused preparatory packet retained.';(home/'transfer-seal.json').write_text(json.dumps(seal,indent=2)+'\n');shutil.rmtree(stage)
if __name__=='__main__':main()
