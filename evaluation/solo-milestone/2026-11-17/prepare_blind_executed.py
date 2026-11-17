import hashlib,json,random
from pathlib import Path
out=Path('/tmp/mplpb-solo-blind-review');rng=random.Random(184731)
questions=json.loads((out/'questions.json').read_text());items=[];key={}
for case in questions:
 group=case['source_group'];ident=case['id'];responses=[]
 for phase in ('before','final'):
  root=Path('/tmp/mplpb-solo-'+group+'-'+phase)
  raw=(root/(ident+'.json')).read_bytes();full=json.loads(raw);c=full['answer']
  assert full['execution_status']=='completed'
  imported=json.loads((root/'import-receipt.json').read_text())
  origins={r['id']:r['original_id'] for r in imported['records']}
  quotes=[]
  for claim in c['claims']:
   for cite in claim.get('citations',[]):
    quotes.append({'source_id':origins[cite['source_id']], 'quote':cite['quote'],
                   'quote_basis':'canonical documentary excerpt; consult unchanged original for raw layout'})
  response_id=hashlib.sha256((ident+phase+'solo-blind').encode()).hexdigest()[:12]
  responses.append({'response_id':response_id,'answer_text':c['text'] or c['diagnostic']['message'],
                    'unresolved':c['missing'],'provided_excerpts':quotes})
  key[response_id]={'case_id':ident,'phase':phase,'response_sha256':hashlib.sha256(raw).hexdigest()}
 rng.shuffle(responses)
 items.append({'id':ident,'question':case['question'],'source_group':group,'responses':responses})
(out/'responses.json').write_text(json.dumps(items,indent=2)+'\n')
Path('/tmp/mplpb-solo-score-key.json').write_text(json.dumps(key,indent=2)+'\n')
print('Prepared 44 responses in blinded order, with no implementation labels or developer scores.')
