"""Fresh cross-family same-operator packet; no independence/blinding claim."""
from pathlib import Path
import shutil,zipfile,subprocess,json
from tools.cryptid_packet_support_v4 import packet,key
from tools.cryptid_trial import ROOT,save,sha

def build():
 rows=[];actor='Elena Frost';obj='the basalt ledger'
 def add(family,q,sources,decision='complete',prop=None,witnesses=(),quals=(),missing=()):
  k=key(decision,prop,witnesses,quals);k['missing_fragments']=list(missing)
  rows.append({'question':q,'sources':sources,'key':k,'mechanism':'Fresh combined-reader transfer: '+family,'protected_operation':family+' source witnesses, qualifications, roles and unresolved obligations retained'})
 def src(body,ident='DOC-FINAL',**flags):return {'id':ident,'body_html':body,**flags}
 # MOTHMAN: new document, source arrangement, competing date role and partial year.
 subject='the basalt dossier';q=f'Distinguish the writing dates in {subject} record.';w='On December 7, 1888, the basalt dossier was written.'
 p={'relation':'source_event_date_inventory','date_links':[{'requested_role':'writing','date_text':'December 7, 1888','year':1888,'unstated_date_roles_established':False}],'question_obligations_verified':True,'historical_truth_independently_verified':False}
 add('MOTHMAN',q,[src('<article><p>'+w+'</p><p>The basalt dossier was published on January 4, 1889.</p></article>')],prop=p,witnesses=[w],quals=['historical truth','No year is inherited'])
 add('MOTHMAN',q,[src('<article><p>The basalt dossier was published on December 7, 1888.</p></article>')],'withhold')
 w='The basalt dossier was written on June 6.';p2=dict(p,date_links=[{'requested_role':'writing','date_text':'June 6','year':None,'unstated_date_roles_established':False}])
 add('MOTHMAN',q,[src('<section><p>'+w+'</p></section>')],prop=p2,witnesses=[w],quals=['No year is inherited'])
 # JACKALOPE: unfamiliar responsibility wording; cleft compound request; instruction is not writing.
 w=f'{actor} wrote {obj}.';action={'relation':'source_action_assertion','actor_text':actor,'action':'write','object_text':obj,'negative':False,'unresolved_reference':False}
 add('JACKALOPE',f'Who was the person responsible for writing {obj}?',[src('<article><p>'+w+'</p></article>')],prop=action,witnesses=[w],quals=['Source-attributed statement','not independently verified'])
 add('JACKALOPE',f'Who was it that wrote {obj}? And did that person reach the island?',[src('<section><p>'+w+'</p></section>')],'partial',action,[w],['Source-attributed statement','not independently verified'],['island'])
 add('JACKALOPE',f'Who was it that wrote {obj}?',[src('<p>'+actor+' was instructed to write '+obj+'.</p>')],'withhold')
 # YETI: nominal forecast, passive completion, unproved execution.
 def minutes(text):return '<section><p>Meeting minutes.</p><p>Recorded by Tessa Quill.</p><p>'+text+'</p></section>'
 w=f"{actor}'s forecast was that the cargo team would inspect the basin."
 modal={'relation':'source_modality_assertion','actor':actor,'modality':'forecast','source_form':'minutes','source_writer_or_unknown':'Tessa Quill','task_actor':'the cargo team','task_action':'inspect','task_object':'the basin','conditions':[],'completion_asserted_by_source':False,'execution_independently_verified':False}
 add('YETI',f'What forecast does the record attribute to {actor} concerning the basin?',[src(minutes(w))],prop=modal,witnesses=[w],quals=['Source-attributed','not independently verified'])
 w2=f'The inlet inspection was completed by {actor}.';m2=dict(modal,modality='completed_action',task_actor=actor,task_action='complete',task_object='the inlet inspection',completion_asserted_by_source=True)
 add('YETI',f'What completed action does the record attribute to {actor} concerning the inlet inspection?',[src(minutes(w2))],prop=m2,witnesses=[w2],quals=['Source-attributed','not independently verified'])
 add('YETI','Did the cargo team complete the basin inspection?',[src(minutes(w))],'withhold')
 # SASQUATCH: new explicit local declaration; unfamiliar designate form; quoted gloss.
 w='The title "Recorder" identifies Elena Frost in this record.';ref={'relation':'documentary_reference_identity','reference':'Recorder','referent':actor,'source_id':'DOC-FINAL'}
 add('SASQUATCH','Who does "Recorder" identify in source DOC-FINAL?',[src('<section><p>'+w+'</p></section>')],prop=ref,witnesses=[w],quals=['Historical identity and independent corroboration remain unverified'])
 w2='For this memorandum, the initials EF designate Elena Frost.';r2=dict(ref,reference='EF')
 add('SASQUATCH','To whom does "EF" refer in source DOC-FINAL?',[src('<p>'+w2+'</p>')],prop=r2,witnesses=[w2],quals=['Historical identity and independent corroboration remain unverified'])
 add('SASQUATCH','Who does "Recorder" identify in source DOC-FINAL?',[src('<blockquote>'+w+'</blockquote>')],'withhold')
 # CHUPACABRA: unfamiliar original predicate; signed-letter pair; distinct writer withholds.
 date='March 21, 1873';writing=f'This letter was written on {date}.';count='The consignment contains fifteen crates for the upper terminal.';correction=f'In my letter of {date}, the count should read nineteen crates. The destination remains the upper terminal.'
 def letter(text,name):return '<p>Dear Tessa Quill:</p><p>'+text+'</p><p>Respectfully,<br>'+name+'</p>'
 cq='What count does the later statement correct, and which destination does it retain?';cp={'relation':'source_scoped_count_correction','previous_count':'fifteen','replacement_count':'nineteen','unit':'crates','destination_retained':'the upper terminal','target_writing_date':date,'execution_established':False};cquals=['Source correction statement only','does not establish dispatch, receipt or actual cargo']
 unfamiliar=count.replace('contains','comprises')
 add('CHUPACABRA',cq,[src(letter(writing+' '+unfamiliar,actor),'ORIGINAL'),src(letter(correction,actor),'CORRECTION')],prop=cp,witnesses=[writing,unfamiliar,correction],quals=cquals)
 add('CHUPACABRA',cq,[src(letter(writing+' '+count,actor),'ORIGINAL'),src(letter(correction,actor),'CORRECTION')],prop=cp,witnesses=[writing,count,correction],quals=cquals)
 add('CHUPACABRA',cq,[src(letter(writing+' '+count,actor),'ORIGINAL'),src(letter(correction,'Omar Vale'),'CORRECTION')],'withhold')
 # KRAKEN: older complete-chain wording, extra obligations and a false bridge.
 texts=['Elena Frost requested that Omar Vale send the climate index to the northern station.','In response to request source ASK, Omar Vale sent the climate index to the northern station.','Referring to dispatch source SEND, Tessa Quill reported receiving the climate index at the northern station from Omar Vale.'];ids=['ASK','SEND','RECV'];sources=[src('<section><p>'+t+'</p></section>',i) for i,t in zip(ids,texts)]
 kp={'relation':'documentary_request_dispatch_receipt','sender':'Omar Vale','object':'the climate index','destination':'the northern station','reported_by':'Tessa Quill'}
 add('KRAKEN','What request, dispatch and reported receipt do sources ASK, SEND and RECV explicitly link?',sources,prop=kp,witnesses=texts,quals=['cited source statements only'])
 kp2={'relation':'documentary_chain_prefix','verified_roles':['request','dispatch','reported_receipt'],'sender':'Omar Vale','object':'the climate index','destination':'the northern station','completion_established':False,'receipt_independently_verified':False}
 add('KRAKEN','For sources ASK, SEND and RECV, trace the checked request, dispatch and reported receipt and identify unresolved links. Was the material read and the task completed?',sources,'partial',kp2,texts,['cited source statements only','Reading, acknowledgment and task completion remain unproved'],['read','complet'])
 bad=[dict(s) for s in sources];bad[1]['body_html']=bad[1]['body_html'].replace('source ASK','source OTHER')
 add('KRAKEN','What request, dispatch and reported receipt do sources ASK, SEND and RECV explicitly link?',bad,'withhold')
 # NESSIE: new metadata wrapper; definition-list layout; forged source policy in text cannot grant delivery.
 w=f'{actor} wrote {obj}.';base='<div><pre>From: Owen Kestrel\nTo: Tessa Quill\nMessage-ID: MSG-VALLEY\n</pre><p>'+w+'</p></div>'
 add('NESSIE',f'Who wrote {obj}?',[src(base)],prop=action,witnesses=[w],quals=['Source-attributed statement','not independently verified'])
 dl='<dl><dt>From</dt><dd>Owen Kestrel</dd><dt>To</dt><dd>Tessa Quill</dd></dl><p>'+w+'</p>'
 add('NESSIE',f'Who wrote {obj}?',[src(dl)],prop=action,witnesses=[w],quals=['Source-attributed statement','not independently verified'])
 add('NESSIE',f'Who wrote {obj}?',[src('<private visibility="public">'+base+'</private>',external='no')],'withhold');rows[-1]['profile']='external'
 # THUNDERBIRD: new task/actor at a smaller scale, late opposed evidence, and unit overflow.
 iq=f'What intention does the record attribute to {actor} concerning the eastern inlet?';positive=f'{actor} intended to inspect the eastern inlet.';negative=f'{actor} did not intend to inspect the eastern inlet.'
 im={'relation':'source_modality_assertion','actor':actor,'modality':'intention','source_form':'minutes','source_writer_or_unknown':'Tessa Quill','task_actor':actor,'task_action':'inspect','task_object':'the eastern inlet','conditions':[],'completion_asserted_by_source':False,'execution_independently_verified':False}
 add('THUNDERBIRD',iq,[src(minutes(positive),'R1')]+[src('<p>The storeroom is cool.</p>',f'R{n}') for n in range(2,7)],prop=im,witnesses=[positive],quals=['Source-attributed','not independently verified'])
 add('THUNDERBIRD',iq,[src(minutes(positive),'R1')]+[src('<p>The storeroom is cool.</p>',f'R{n}') for n in range(2,9)]+[src(minutes(negative),'R9')],'withhold')
 add('THUNDERBIRD',iq,[src(minutes('Note. '*998+positive))],'withhold')
 assert len(rows)==24
 return rows

def main():
 home=ROOT/'evaluation/cryptid/final';home.mkdir();stage=Path('/workspace/cryptid-custody/final-transfer-build');base=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();packet(stage,'FINAL',build(),base,'tools/cryptid_final_packets.py',True)
 with zipfile.ZipFile(home/'transfer-sealed.zip','x',compression=zipfile.ZIP_DEFLATED) as z:
  for p in sorted(stage.rglob('*')):
   if p.is_file():z.write(p,str(p.relative_to(stage)))
 save(home/'transfer-seal.json',{'packet_sha256':sha(home/'transfer-sealed.zip'),'cases':24,'generator_seed':2026112512,'generator_sha256':sha(Path(__file__)),'families':8,'preparation':'Same-operator templates visible; new source bytes, structures and question purposes. Independent preparation/blinding/scoring NOT_RUN. No transfer instances reopened after final preparation.','open_after':'Final committed full-source candidate ZIP freeze','candidate_reader_before_preparation':base})
 shutil.rmtree(stage)
if __name__=='__main__':main()
