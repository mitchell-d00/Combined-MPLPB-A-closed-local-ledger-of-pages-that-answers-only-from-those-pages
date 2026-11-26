"""Fixed-cap resource and counterevidence cases, not a cap-increase experiment."""
from tools.cryptid_packet_support_v3 import programme,key
from tools.cryptid_trial import ROOT,read,sha
from pathlib import Path
import json

def build(held=False):
 actor='Vera Calder' if held else 'Mara Flint';obj='the southern channel' if held else 'the canal';statement=f'{actor} intended to inspect {obj}.';negative=f'{actor} did not intend to inspect {obj}.';q=f'What intention does the record attribute to {actor} concerning {obj}?'
 def report(text):return '<p>Report.</p><p>Written by Owen Kestrel.</p><p>'+text+'</p>'
 def claim(neg=False):return {'proposition':{'relation':'source_modality_assertion','actor':actor,'modality':'intention','source_form':'report','source_writer_or_unknown':'Owen Kestrel','task_actor':actor,'task_action':'inspect','task_object':obj,'outer_negative':neg,'conditions':[],'completion_asserted_by_source':False,'execution_independently_verified':False,'historical_truth_independently_verified':False},'qualification_fragments':['Source-attributed','not independently verified'],'complete_witnesses':[negative if neg else statement]}
 specs=[('small',1,0,0,False,'complete',None),('records-eight',8,0,0,False,'complete',None),('records-nine',9,0,0,False,'withhold','record_limit'),('units-1000',1,997,0,False,'complete',None),('units-1001',1,998,0,False,'withhold','unit_limit'),('near-scan',1,0,185000,False,'complete',None),('over-scan',1,0,201000,False,'withhold','scan_limit'),('counter-at-eight',8,0,0,True,'conflict',None),('counter-at-nine',9,0,0,True,'withhold','record_limit'),('long-counter',1,0,3500,True,'partial','phrase_limit'),('long-irrelevant',1,0,10000,False,'complete',None),('repeated-equivalent',2,0,0,False,'withhold','ambiguous_multiple_assertions')]
 if held:specs=[specs[i] for i in [1,2,3,4,7,8,9,10]]
 rows=[]
 for name,records,notes,filler,counter,decision,limiter in specs:
  fill=('Context '*((filler//8)+1))[:filler]
  if name=='long-counter':
   body=report(statement)[:-4]+'</p><p>'+fill+' '+negative+'</p>'
  else:body=report(('Note. '*notes)+(fill+'. ' if fill else '')+statement)
  sources=[{'id':'REPORT-1','body_html':body}]
  for n in range(2,records+1):sources.append({'id':f'REPORT-{n}','body_html':report(negative) if counter and n==records else '<p>The storeroom is cool.</p>'})
  if name=='repeated-equivalent':sources[1]['body_html']=report(statement)
  k=key(decision);k['claims']=[] if decision=='withhold' else [claim()]+([claim(True)] if decision=='conflict' else []);k['missing_fragments']=['qualification'] if decision=='partial' else []
  k.update(source_answerable_without_caps=not counter and name!='repeated-equivalent',expected_limiter=limiter,counterevidence_present=counter,require_visible_phrase_stop=name=='long-counter')
  rows.append({'question':q,'sources':sources,'key':k,'mechanism':'Fixed budgets must disclose incomplete proof and retain competing evidence as corpus size or unit length grows','protected_operation':'No definitive answer from a partial scan or an incomplete counterevidence graph; measure resource and source-read costs separately'})
 return rows

def main():
 programme('THUNDERBIRD',build(),build(True),'tools/cryptid_thunderbird_packets.py',2026112509)
 home=ROOT/'evaluation/cryptid/thunderbird';registry=read(home/'development/registry.json');keys=read(home/'development/key.json');plan=[]
 for c in registry['cases']:
  case=read(ROOT/c['packet']/'case.json');plan.append({'id':c['id'],'records':len(case['sources']),'body_html_characters':sum(len(s['body_html']) for s in case['sources']),'expected_limiter':keys[c['id']]['expected_limiter'],'source_answerable_without_caps':keys[c['id']]['source_answerable_without_caps']})
 (home/'resource-plan.json').write_text(json.dumps({'caps_changed':False,'proof_limits':{'records':8,'source_html_characters':200000,'units':1000,'statement_characters':2200,'passages':12,'answer_characters':8000},'cases':plan,'scope':'Source-modality operation limits; other existing reader operations can have distinct limits. This does not raise any cap.'},indent=2)+'\n')
if __name__=='__main__':main()
