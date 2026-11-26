"""Fresh cross-family packet after reporting repair; visible same-operator templates."""
import random,shutil,subprocess,zipfile
from pathlib import Path
from tools.cryptid_packet_support_v4 import packet,key
from tools.cryptid_trial import ROOT,save,sha,runtime_files

SEED=2026112601

def build():
    names=['Rina Sable','Oren Keel','Elin Cross','Daria Fen','Marek Lune'];random.Random(SEED).shuffle(names)
    actor,reporter,writer=names[:3];initials=''.join(w[0] for w in writer.split());rows=[]
    def src(body,ident='FRESH-3',**flags):return dict(id=ident,body_html=body,**flags)
    def add(family,q,sources,decision='complete',prop=None,witnesses=(),quals=(),missing=()):
        k=key(decision,prop,witnesses,quals);k['missing_fragments']=list(missing)
        rows.append({'question':q,'sources':sources,'key':k,'mechanism':'Fresh third-final transfer: '+family,'protected_operation':family+' exact source roles, polarity, qualifications, current host policy and missing obligations'})
    subject='the altitude memorandum';writing='The altitude memorandum was written on April 12.';publication='The altitude memorandum was published on April 13, 1909.'
    dp={'relation':'source_event_date_inventory','date_links':[{'requested_role':'writing','date_text':'April 12','year':None,'unstated_date_roles_established':False},{'requested_role':'publication','date_text':'April 13, 1909','year':1909,'unstated_date_roles_established':False}],'question_obligations_verified':True}
    add('MOTHMAN','What separate dates does the altitude memorandum record list for writing and publication?',[src('<article><section><p>'+writing+'</p><p>'+publication+'</p></section></article>')],prop=dp,witnesses=[writing,publication],quals=['No year is inherited'])
    anchor='The altitude memorandum was received on April 12, 1909.';relative='The altitude memorandum was written the following day.'
    rp=dict(dp,date_links=[{'requested_role':'writing','date_text':'the following day','year':None,'unstated_date_roles_established':False}])
    add('MOTHMAN','Distinguish the writing dates in the altitude memorandum record.',[src('<section><p>'+anchor+'</p><p>'+relative+'</p></section>')],prop=rp,witnesses=[anchor,relative],quals=['historical truth'])
    add('MOTHMAN','Distinguish the sending dates in the altitude memorandum record.',[src('<p>'+writing+'</p>')],'withhold')
    obj='the opal survey';text=actor+' published '+obj+'.';ap={'relation':'source_action_assertion','actor_text':actor,'action':'publish','object_text':obj,'negative':False,'unresolved_reference':False}
    add('JACKALOPE','According to the record, which individual published the opal survey?',[src('<section><article><p>'+text+'</p></article></section>')],prop=ap,witnesses=[text],quals=['Source-attributed statement','not independently verified'])
    dated='On May 10, '+text;tp=dict(ap,temporal_qualification_text='On May 10')
    add('JACKALOPE','Who was it that published the opal survey before May 9?',[src('<article><p>'+dated+'</p></article>')],'partial',tp,[dated],['Source-attributed statement','not independently verified'],['before May 9'])
    add('JACKALOPE','Do these records independently establish actual publication of the opal survey?',[src('<p>'+text+'</p>')],'withhold')
    obj='the pearl register';quoted='“'+actor+' wrote '+obj+',” '+reporter+' does not report.'
    report=lambda t:'<section><p>Report.</p><p>Written by '+writer+'.</p><p>'+t+'</p></section>'
    q=f'What does {reporter} report about whether {actor} wrote {obj}?'
    report_prop={'relation':'source_attributed_report_content','reporter':reporter,'author':actor,'object':obj,'outer_negative':True,'inner_negative':None,'inner_polarity':'unasserted','content_asserted_by_reporter':False,'conditions':[],'actual_authorship_established':False,'completion_established':False}
    add('YETI',q,[src(report(quoted))],prop=report_prop,witnesses=[quoted],quals=['Source-scoped reporting statement','Independent authorship'])
    conditional='If the seal is intact, '+reporter+' would not report, “'+actor+' did not write '+obj+'.”';cp=dict(report_prop,conditions=['If the seal is intact'],conditional_content_negative=True)
    add('YETI',f'What conditional authorship statement does {reporter} report about {obj}?',[src(report(conditional))],prop=cp,witnesses=[conditional],quals=['Source-scoped reporting statement','Independent authorship'])
    add('YETI',q.replace(reporter,writer),[src(report(quoted))],'withhold')
    gloss=f'Initials "{initials}" identifies {writer} in this record.';title=f'Title "Recorder" identifies {writer} in this record.';ref={'relation':'documentary_reference_identity','reference':initials,'referent':writer,'source_id':'REF-3'}
    add('SASQUATCH',f'Who does "{initials}" identify in source REF-3?',[src('<article><p>'+gloss+'</p><p>'+title+'</p></article>','REF-3')],prop=ref,witnesses=[gloss],quals=['Historical identity and independent corroboration remain unverified'])
    prose=f'In this record, {initials} is the initials of {writer}.'
    add('SASQUATCH',f'To whom does "{initials}" refer in source REF-3?',[src('<section><p>'+prose+'</p></section>','REF-3')],prop=ref,witnesses=[prose],quals=['Historical identity and independent corroboration remain unverified'])
    other=f'Initials "{initials}" identifies {actor} in this record.'
    add('SASQUATCH',f'Who does "{initials}" identify in source REF-3?',[src('<p>'+gloss+'</p><p>'+other+'</p>','REF-3')],'withhold')
    date='November 3, 1881';date_first='On '+date+', this letter was written.';plain='This letter was written on '+date+'.';count='The consignment contains eight crates for the lower quay.';fix='In my letter of '+date+', the count should read eleven crates. The destination remains the lower quay.'
    letter=lambda t:'<article><p>Dear '+reporter+':</p><p>'+t+'</p><p>Sincerely,<br>'+actor+'</p></article>'
    cq='What count does the later statement correct, and which destination does it retain?';cprop={'relation':'source_scoped_count_correction','previous_count':'eight','replacement_count':'eleven','unit':'crates','destination_retained':'the lower quay','target_writing_date':date,'execution_established':False};cqual=['Source correction statement only','does not establish dispatch, receipt or actual cargo']
    add('CHUPACABRA',cq,[src(letter(date_first+' '+count),'ORIG-3'),src(letter(fix),'FIX-3')],prop=cprop,witnesses=[date_first,count,fix],quals=cqual)
    correction=letter(fix).replace('<p>Sincerely,','<p>The carrier is separately named as the sky courier.</p><p>Sincerely,')
    add('CHUPACABRA',cq,[src(letter(plain+' '+count),'ORIG-3'),src(correction,'FIX-3')],prop=cprop,witnesses=[plain,count,fix],quals=cqual)
    add('CHUPACABRA',cq,[src(letter(plain+' '+count),'ORIG-3'),src(letter(plain+' '+count.replace('eight','nine')),'OTHER-3'),src(letter(fix),'FIX-3')],'withhold')
    request=actor+' requested that '+reporter+' send the violet atlas to the headland station.';dispatch='In response to request source ASK-3, '+reporter+' sent the violet atlas to the headland station.';receipt='Referring to dispatch source SEND-3, '+writer+' reported receiving the violet atlas at the headland station from '+reporter+'.';sources=[src('<section><p>'+t+'</p></section>',i) for i,t in zip(['ASK-3','SEND-3','RECV-3'],[request,dispatch,receipt])]
    chain={'relation':'documentary_request_dispatch_receipt','sender':reporter,'object':'the violet atlas','destination':'the headland station','reported_by':writer}
    contextual=[dict(s) for s in sources];contextual[0]['body_html']='<p>Collection note.</p>'+contextual[0]['body_html']
    add('KRAKEN','What request, dispatch and reported receipt do sources ASK-3, SEND-3 and RECV-3 explicitly link?',contextual,prop=chain,witnesses=[request,dispatch,receipt],quals=['cited source statements only'])
    prefixq='For sources ASK-3, SEND-3 and RECV-3, trace the checked request, dispatch and reported receipt and identify unresolved links. Was the material read and the task completed?';prefix={'relation':'documentary_chain_prefix','verified_roles':['request','dispatch'],'sender':reporter,'object':'the violet atlas','destination':'the headland station','completion_established':False,'receipt_independently_verified':False}
    add('KRAKEN',prefixq,sources[:2],'partial',prefix,[request,dispatch],['cited source statements only','Reading, acknowledgment and task completion remain unproved'],['receipt','read','complet'])
    competing='In response to request source ASK-3, '+reporter+' sent the violet atlas to the inland office.'
    add('KRAKEN',prefixq,sources+[src('<p>'+competing+'</p>','ALT-3')],'partial',dict(prefix,verified_roles=['request'],competing_links=True),[request],['cited source statements only'],['competing','receipt'])
    obj='the violet register';text=actor+' wrote '+obj+'.';action={'relation':'source_action_assertion','actor_text':actor,'action':'write','object_text':obj,'negative':False,'unresolved_reference':False}
    dl='<section><dl data-layer="correspondence"><dt>From</dt><dd>'+reporter+'</dd><dt>To</dt><dd>'+writer+'</dd></dl><p>'+text+'</p></section>'
    add('NESSIE','Who wrote the violet register?',[src(dl)],prop=action,witnesses=[text],quals=['Source-attributed statement','not independently verified'])
    add('NESSIE','Who wrote the violet register?',[src(dl.replace('<dd>'+reporter+'</dd>','<dd><b>'+reporter+'</b></dd>'))],prop=action,witnesses=[text],quals=['Source-attributed statement','not independently verified'])
    add('NESSIE','Who wrote the violet register?',[src('<private visibility="public">'+dl+'</private>',external='no')],'withhold');rows[-1]['profile']='external'
    tq=f'What intention does the record attribute to {actor} concerning the headland?';positive=actor+' intended to inspect the headland.';negative=actor+' did not intend to inspect the headland.'
    mp={'relation':'source_modality_assertion','actor':actor,'modality':'intention','source_form':'report','source_writer_or_unknown':writer,'task_actor':actor,'task_action':'inspect','task_object':'the headland','outer_negative':False,'conditions':[],'completion_asserted_by_source':False,'execution_independently_verified':False}
    filler=[src('<p>Cabinet leaf. </p>'*40,'FILL-3-'+str(n)) for n in range(6)]
    add('THUNDERBIRD',tq,[src(report(positive),'POS-3')]+filler+[src(report(negative),'NEG-3')],'conflict')
    rows[-1]['key']['claims']=[{'proposition':mp,'qualification_fragments':['Source-attributed','not independently verified'],'complete_witnesses':[positive]},{'proposition':dict(mp,outer_negative=True),'qualification_fragments':['Source-attributed','not independently verified'],'complete_witnesses':[negative]}]
    long=actor+' did not intend to inspect the headland '+('under further qualifications '*100)+'.'
    add('THUNDERBIRD',tq,[src(report(positive),'POS-3'),src(report(long),'LONG-3')],'partial',mp,[positive],['Source-attributed','not independently verified'],['qualification'])
    add('THUNDERBIRD',tq,[src(report(positive),'POS-3')]+filler+[src('<p>Nothing else is specified.</p>','FILL-LAST'),src(report(negative),'NEG-3')],'withhold')
    assert len(rows)==24
    return rows

def main():
    home=ROOT/'evaluation/cryptid/revision3/fresh';home.mkdir();stage=Path('/workspace/cryptid-custody/revision3-fresh-build');commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    packet(stage,'FINALNEXT',build(),commit,'tools/cryptid_revision3_fresh.py',True)
    with zipfile.ZipFile(home/'transfer-sealed.zip','x',compression=zipfile.ZIP_DEFLATED) as archive:
        for p in sorted(stage.rglob('*')):
            if p.is_file():archive.write(p,str(p.relative_to(stage)))
    save(home/'transfer-seal.json',{'packet_sha256':sha(home/'transfer-sealed.zip'),'cases':24,'generator_seed':SEED,'seed_usage':'Deterministic PRNG shuffles new actor names; structures/purposes also differ, not an independent or blind sample','generator_sha256':sha(Path(__file__)),'candidate_native_before_preparation':{str(p.relative_to(ROOT)):sha(p) for p in runtime_files(ROOT)},'preparation':'Same operator; generator templates visible. Instance bytes/key not reopened until committed candidate freeze. Independent preparation/blinding/scoringNOT_RUN.','acceptance_policy':'New temporal/multipart partials require exact supported claims, explicit missing obligations and no complete-answer flag; old keys unchanged.','open_after':'Revised committed full-source ZIP freeze; execute once, retain misses and disagreements'})
    shutil.rmtree(stage)

if __name__=='__main__':main()
