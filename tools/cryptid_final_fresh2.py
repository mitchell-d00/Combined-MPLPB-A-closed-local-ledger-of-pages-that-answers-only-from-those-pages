"""Fresh cross-family contrasts after consuming the first final packet.

Same-operator visible templates; no independent preparation or blinding.
"""
from pathlib import Path
import shutil,zipfile,subprocess
from tools.cryptid_packet_support_v4 import packet,key
from tools.cryptid_trial import ROOT,save,sha

def build():
    rows=[];actor='Cora Lynn Vale';obj='the western ridge'
    def src(text,ident='FRESH-DOC',**flags):return dict(id=ident,body_html=text,**flags)
    def add(family,q,sources,decision='complete',prop=None,witnesses=(),quals=()):
        rows.append(dict(question=q,sources=sources,key=key(decision,prop,witnesses,quals),mechanism='Fresh cross-family second packet: '+family,protected_operation='Exact actor, source scope, qualifications, citation and host state; '+family))
    text='The upland memorandum was written on October 3.'
    dp={'relation':'source_event_date_inventory','date_links':[{'requested_role':'writing','date_text':'October 3','year':None,'unstated_date_roles_established':False}],'question_obligations_verified':True}
    q='Distinguish the writing dates in the upland memorandum record.'
    add('MOTHMAN',q,[src('<article><section><p>Page reviewed on October 9, 2020.</p><p>'+text+'</p></section></article>')],prop=dp,witnesses=[text],quals=['No year is inherited'])
    add('MOTHMAN',q,[src('<section><p>The upland memorandum was received on October 3.</p></section>')],'withhold')
    text=actor+' surveyed '+obj+'.';ap={'relation':'source_action_assertion','actor_text':actor,'action':'survey','object_text':obj,'negative':False,'unresolved_reference':False}
    add('JACKALOPE','According to the record, which individual surveyed the western ridge?',[src('<article><p>'+text+'</p></article>')],prop=ap,witnesses=[text],quals=['Source-attributed statement','not independently verified'])
    add('JACKALOPE','Who surveyed the western ridge before September 4?',[src('<article><p>'+text+'</p></article>')],'withhold')
    text='Nora Finch did not say, “Ida Pell did not write the marsh register.”'
    rp={'relation':'source_attributed_report_content','reporter':'Nora Finch','author':'Ida Pell','object':'the marsh register','inner_negative':True,'outer_negative':True,'conditions':[],'actual_authorship_established':False,'completion_established':False}
    report='<article><p>Report.</p><p>Written by Cora Lynn Vale</p><p>'+text+'</p></article>'
    add('YETI','What does Nora Finch report about whether Ida Pell wrote the marsh register?',[src(report)],prop=rp,witnesses=[text],quals=['Source-scoped reporting statement','Independent authorship'])
    add('YETI','Did the field party complete the marsh inspection?',[src('<section><p>Cora Lynn Vale predicted that the field party would inspect the marsh.</p></section>')],'withhold')
    text='Surname "Vale" identifies Cora Lynn Vale in this record.';ref={'relation':'documentary_reference_identity','reference':'Vale','referent':actor,'source_id':'FRESH-DOC'}
    add('SASQUATCH','To whom does "Vale" refer in source FRESH-DOC?',[src('<section><p>'+text+'</p></section>')],prop=ref,witnesses=[text],quals=['Historical identity and independent corroboration remain unverified'])
    add('SASQUATCH','To whom does "Vale" refer in source FRESH-DOC?',[src('<p>'+text+'</p><p>Surname "Vale" identifies Adrian Vale in this record.</p>')],'withhold')
    date='August 9, 1861';writing='This letter was written on '+date+'.';count='The consignment contains twenty barrels for the inland depot.';correction='In my letter of '+date+', the count should read twenty barrels. The destination remains the inland depot.'
    def letter(t,name):return '<section><p>Dear Nora Finch:</p><p>'+t+'</p><p>Yours truly,<br>'+name+'</p></section>'
    cp={'relation':'source_scoped_count_correction','previous_count':'twenty','replacement_count':'twenty','unit':'barrels','destination_retained':'the inland depot','target_writing_date':date,'execution_established':False}
    cq='What count does the later statement correct, and which destination does it retain?'
    sources=[src(letter(writing+' '+count,actor),'FIRST'),src(letter(correction,actor),'SECOND')]
    add('CHUPACABRA',cq,sources,prop=cp,witnesses=[writing,count,correction],quals=['Source correction statement only','does not establish dispatch, receipt or actual cargo'])
    add('CHUPACABRA',cq,[dict(sources[0]),src(letter(correction,'CV'),'SECOND')],'withhold')
    texts=['Cora Lynn Vale requested that Adrian Vale send the marsh map to the inland depot.','In response to request source FIRST, Adrian Vale sent the marsh map to the inland depot.','Referring to dispatch source SECOND, Nora Finch reported receiving the marsh map at the inland depot from Adrian Vale.'];sources=[src('<article><section><p>'+t+'</p></section></article>',i) for i,t in zip(['FIRST','SECOND','THIRD'],texts)]
    kp={'relation':'documentary_request_dispatch_receipt','sender':'Adrian Vale','object':'the marsh map','destination':'the inland depot','reported_by':'Nora Finch'}
    kq='What request, dispatch and reported receipt do sources FIRST, SECOND and THIRD explicitly link?'
    add('KRAKEN',kq,sources,prop=kp,witnesses=texts,quals=['cited source statements only'])
    restricted=[dict(s) for s in sources];restricted[1]['external']='no';add('KRAKEN',kq,restricted,'withhold');rows[-1]['profile']='external'
    text='Cora Lynn Vale surveyed the western ridge.'
    dl='<section><dl class="correspondence"><dt>FROM</dt><dd>Nora Finch</dd><dt>TO</dt><dd>Adrian Vale</dd><dt>Message-ID</dt><dd>UPLAND-61</dd></dl><p>'+text+'</p></section>'
    add('NESSIE','Who surveyed the western ridge?',[src(dl)],prop=ap,witnesses=[text],quals=['Source-attributed statement','not independently verified'])
    add('NESSIE','Who surveyed the western ridge?',[src(dl.replace('</dl>','<dt>Subject</dt><dd>if the council agrees</dd></dl>'))],'withhold')
    tq='What intention does the record attribute to Cora Lynn Vale concerning the marsh?';positive='Cora Lynn Vale intended to inspect the marsh.';negative='Cora Lynn Vale did not intend to inspect the marsh.'
    def minutes(t):return '<article><p>Meeting minutes.</p><p>Recorded by Nora Finch.</p><p>'+t+'</p></article>'
    mp={'relation':'source_modality_assertion','actor':actor,'modality':'intention','source_form':'minutes','source_writer_or_unknown':'Nora Finch','task_actor':actor,'task_action':'inspect','task_object':'the marsh','conditions':[],'completion_asserted_by_source':False,'execution_independently_verified':False}
    add('THUNDERBIRD',tq,[src(minutes(positive))]+[src('<p>Nothing else is specified.</p>','FILL'+str(n)) for n in range(6)],prop=mp,witnesses=[positive],quals=['Source-attributed','not independently verified'])
    add('THUNDERBIRD',tq,[src(minutes(positive))]+[src('<p>Nothing else is specified.</p>','FILL'+str(n)) for n in range(7)]+[src(minutes(negative),'LAST')],'withhold')
    assert len(rows)==16
    return rows

def main():
    home=ROOT/'evaluation/cryptid/final/fresh2';home.mkdir(exist_ok=False);stage=Path('/workspace/cryptid-custody/final-fresh2-build');base=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    packet(stage,'FINAL2',build(),base,'tools/cryptid_final_fresh2.py',True)
    with zipfile.ZipFile(home/'transfer-sealed.zip','x',compression=zipfile.ZIP_DEFLATED) as z:
        for p in sorted(stage.rglob('*')):
            if p.is_file():z.write(p,str(p.relative_to(stage)))
    save(home/'transfer-seal.json',{'packet_sha256':sha(home/'transfer-sealed.zip'),'cases':16,'generator_seed':2026112513,'generator_sha256':sha(Path(__file__)),'families':8,'preparation':'Same-operator templates visible. Fresh packet bytes/structures/key prepared before candidate freeze, not reopened during implementation. Independent preparation/blinding/scoring NOT_RUN.','open_after':'Second committed full source ZIP freeze','purpose':'New cross-family evidence after initial final packet consumed by boundary repair; small fixed-template scope, not general coverage.'})
    shutil.rmtree(stage)

if __name__=='__main__':main()
