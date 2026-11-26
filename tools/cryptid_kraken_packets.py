"""Frozen checked-prefix targets: every bridge and requested obligation separate."""
from tools.cryptid_packet_support_v2 import programme,key

def build(held=False):
 actor,sender,receiver=('Vera Moss','Jonas Calder','Lina Reyes') if held else ('Mara Flint','Len Kay','Bea Park');obj='the tide ledger' if held else 'the water chart';dest='the south quay' if held else 'the west landing';ids=['REQUEST','DISPATCH','RECEIPT']
 texts=[f'{actor} requested that {sender} send {obj} to {dest}.',f'In response to request source REQUEST, {sender} sent {obj} to {dest}.',f'Referring to dispatch source DISPATCH, {receiver} reported receiving {obj} at {dest} from {sender}.']
 q='What is established and missing in the request, dispatch and reported receipt chain in sources REQUEST, DISPATCH and RECEIPT?'
 if held:q='For sources REQUEST, DISPATCH and RECEIPT, trace the checked request, dispatch and reported receipt and identify unresolved links.'
 def claim(n):return {'proposition':{'relation':'documentary_chain_prefix','verified_roles':['request','dispatch','reported_receipt'][:n],'sender':sender,'object':obj,'destination':dest,'completion_established':False,'receipt_independently_verified':False},'qualification_fragments':['cited source statements only','Reading, acknowledgment and task completion remain unproved'],'complete_witnesses':texts[:n]}
 rows=[]
 variants=['complete','no-receipt','no-dispatch','wrong-bridge','wrong-sender','wrong-object','wrong-destination','restricted-middle','quoted-middle','conditional-middle','negated-request','missing-request','extra-obligations','budget-two','competing-dispatch','withdrawn-receipt']
 for variant in variants:
  sources=[{'id':i,'body_html':'<p>'+t+'</p>'} for i,t in zip(ids,texts)];n=3;question=q;profile='internal';budget={'passages':12,'characters':8000}
  if variant=='no-receipt':sources=sources[:2];n=2
  if variant=='no-dispatch':sources=[sources[0],sources[2]];n=1
  if variant in {'wrong-bridge','wrong-sender','wrong-object','wrong-destination'}:
   old,new={'wrong-bridge':('source REQUEST','source OTHER'),'wrong-sender':(sender,'Ivo Stone'),'wrong-object':(obj,'the unrelated index'),'wrong-destination':(dest,'the east depot')}[variant];sources[1]['body_html']=sources[1]['body_html'].replace(old,new);n=1
  if variant=='restricted-middle':sources[1].update(external='no');profile='external';n=1
  if variant=='quoted-middle':sources[1]['body_html']='<blockquote>'+texts[1]+'</blockquote>';n=1
  if variant=='conditional-middle':sources[1]['body_html']='<p>If approved. '+texts[1]+'</p>';n=1
  if variant=='negated-request':sources[0]['body_html']='<p>'+texts[0].replace('requested','did not request')+'</p>';n=0
  if variant=='missing-request':sources=sources[1:];n=0
  if variant=='extra-obligations':question+=' Was the material read and the task completed?'
  if variant=='budget-two':budget['passages']=2;n=2
  if variant=='competing-dispatch':sources.append({'id':'COMPETING','body_html':'<p>'+texts[1].replace(dest,'the east depot')+'</p>'});n=1
  if variant=='withdrawn-receipt':sources[2].update(withdraw=True);n=2
  decision='withhold' if n==0 else 'complete' if n==3 and variant!='extra-obligations' else 'partial'
  k=key(decision);k['claims']=[] if not n else [claim(n)];k['missing_fragments']=['read','complet'] if variant=='extra-obligations' else ['receipt'] if n==2 else ['dispatch'] if n==1 else []
  if decision=='complete':k['allowed_partial_claims']=[claim(1),claim(2)]
  rows.append({'question':question,'sources':sources,'profile':profile,'budget':budget,'key':k,'mechanism':'A complete named chain is rejected when a bridge is missing; checked prefixes should survive without inferred receipt or completion','protected_operation':'Verify each eligible explicit bridge independently and retain unresolved obligations'})
 return rows
if __name__=='__main__':programme('KRAKEN',build(),build(True),'tools/cryptid_kraken_packets.py',2026112507)
