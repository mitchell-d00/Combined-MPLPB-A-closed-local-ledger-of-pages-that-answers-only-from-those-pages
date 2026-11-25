"""Freeze current date-linked correction leads and contrasting source claims."""
from pathlib import Path
import json,shutil,re
from tools.cryptid_packet_support import programme,key
from tools.cryptid_trial import ROOT,read,save,sha,snapshot,digest
Q='What count does the later statement correct, and which destination does it retain?'
QUAL=('Source correction statement only','does not establish dispatch, receipt or actual cargo')
def expected(old,new,date,dest,unit='crates',partial=False):return {'relation':'source_scoped_count_correction','previous_count':old,'replacement_count':new,'unit':unit,'destination_retained':None if partial else dest,'target_writing_date':date,'execution_established':False}
def build(held=False):
 rows=[];date='October 9, 1881' if held else 'April 7, 1876';old='eleven' if held else 'four';new='thirteen' if held else 'seven';dest='the north quay' if held else 'the west depot'
 first=f'This letter was written on {date}. The cargo contains {old} crates for {dest}.'
 core=f'In my letter of {date}, the count should read {new} crates.'
 last=core+f' The destination remains {dest}.'
 for variant in ['valid','missing-retention','wrong-date','wrong-destination','quoted','conditional','negated','missing-original','restricted-original','ambiguous-original','missing-year','identical-count']:
  a=first;b=last;extra=[];profile='internal';flags={};decision='complete';partial=False
  if variant=='missing-retention':b=core;decision='partial';partial=True
  if variant=='wrong-date':b=b.replace(date,'February 2, 1899');decision='withhold'
  if variant=='wrong-destination':b=b.replace(dest,'the east quay');decision='withhold'
  if variant=='quoted':b='<blockquote>'+b+'</blockquote>';decision='withhold'
  if variant=='conditional':b='If the permit is approved. '+b;decision='withhold'
  if variant=='negated':b+=' That correction was denied.';decision='withhold'
  if variant=='missing-original':a='The original is unavailable.';decision='withhold'
  if variant=='restricted-original':flags={'external':'no'};profile='external';decision='withhold'
  if variant=='ambiguous-original':extra=[{'id':'ORIGINAL-2','body_html':'<p>'+first.replace(old,'ninety')+'</p>'}];decision='withhold'
  if variant=='missing-year':b=b.replace(', 1881' if held else ', 1876','');decision='withhold'
  if variant=='identical-count':b=b.replace(new,old);decision='complete';new_expected=old
  else:new_expected=new
  witnesses=[f'This letter was written on {date}.',f'The cargo contains {old} crates for {dest}.',b]
  k=key(decision,expected(old,new_expected,date,dest,partial=partial) if decision!='withhold' else None,witnesses if decision!='withhold' else [],QUAL)
  if partial:k['missing_fragments']=['destination']
  rows.append({'question':Q if not held else 'According to the record, '+Q[0].lower()+Q[1:],'sources':[{'id':'ORIGINAL','body_html':'<p>'+a+'</p>',**flags},{'id':'CORRECTION','body_html':'<p>'+b+'</p>'}]+extra,'profile':profile,'key':k,'mechanism':'Date-linked count correction lacks a verified target and independent retained-destination obligation','protected_operation':'Preserve original count, explicit replacement, literal target date and unchanged destination separately; no inferred shipment'})
 return rows

def main():
 programme('CHUPACABRA',build(),build(True),'tools/cryptid_chupacabra_packets.py',2026112506)
 home=ROOT/'evaluation/cryptid/chupacabra/development';registry=read(home/'registry.json');keys=read(home/'key.json')
 expected_values={'DP00002':('six','nine','June 18, 1848'),'DP00024':('twelve','fourteen','November 25, 1847'),'POLE-e96eaa9dffad704a-00003':('six','nine','January 06, 1846'),'POLE-e96eaa9dffad704a-00012':('twenty','seventeen','June 16, 1843')}
 for c in read(ROOT/'evaluation/current-failure-inventory/selection.json')['cases']:
  if c['id'] not in expected_values:continue
  ident=f'CRYPT-CHUPACABRA-{len(registry["cases"])+1:04d}';source=ROOT/'evaluation/current-failure-inventory'/c['input_path'];p=home/'inputs'/ident;shutil.copytree(source,p);assert snapshot(p)==c['files']
  old,new,date=expected_values[c['id']];case=read(p/'case.json');texts=[(p/s['path']).read_text() for s in case['sources'][:2]]
  witnesses=[]
  for text,pattern in [(texts[0],r'This letter was written on [\s\S]+?\.'),(texts[0],r'The\s+consignment[\s\S]+?\.'),(texts[1],r'In my letter[\s\S]+?The destination remains[\s\S]+?\.')]:witnesses.append(re.search(pattern,text)[0])
  keys[ident]=key('complete',expected(old,new,date,'the east depot'),witnesses,QUAL)
  registry['cases'].append({'id':ident,'family':'CHUPACABRA','packet':str(p.relative_to(ROOT)),'files':snapshot(p),'semantic_input_hash':digest({'question':case['question'],'files':snapshot(p)}),'origin':c,'mechanism':'Unchanged historical date-linked partial-correction lead','protected_operation':'Verify original/replacement/unchanged destination from exact eligible witnesses','baseline_commit':registry['cases'][0]['baseline_commit'],'budgets':registry['cases'][0]['budgets'],'custody':'same-operator scoring; original bytes unchanged'})
 (home/'registry.json').write_text(json.dumps(registry,indent=2,ensure_ascii=False)+'\n');(home/'key.json').write_text(json.dumps(keys,indent=2,ensure_ascii=False)+'\n');freeze=read(home/'freeze.json');freeze.update(registry_sha256=sha(home/'registry.json'),key_sha256=sha(home/'key.json'));(home/'freeze.json').write_text(json.dumps(freeze,indent=2)+'\n')
if __name__=='__main__':main()
