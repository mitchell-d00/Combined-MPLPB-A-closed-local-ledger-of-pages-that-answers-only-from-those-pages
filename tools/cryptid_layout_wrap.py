"""Freeze contrasting definition-list boundaries after final transfer failure."""
from pathlib import Path
import json,subprocess
from tools.cryptid_packet_support_v4 import packet,key
from tools.cryptid_trial import ROOT,read,sha

def main():
    home=ROOT/'evaluation/cryptid/nessie/layout-wrap'
    actor='Mara Flint';statement=actor+' wrote the tidal index.'
    prop={'relation':'source_action_assertion','actor_text':actor,'action':'write','object_text':'the tidal index','negative':False,'temporal_qualification_text':'','unresolved_reference':False,'assertion_modality':'unconditional_source_assertion','event_identity':None}
    header='<dl><dt>From</dt><dd>Lina Mercer</dd><dt>To</dt><dd>Hugo Sato</dd>{}</dl>'
    body='<p>'+statement+'</p>'
    specs=[]
    variants=[
        (header.format('')+body,True),
        (header.format('<dt>Date</dt><dd>April 6, 1904</dd>')+body,True),
        (header.format('').replace('From','FROM').replace('To','TO')+body,True),
        ('<blockquote>'+header.format('')+body+'</blockquote>',False),
        ('<div class="quoted">'+header.format('')+body+'</div>',False),
        (header.format('<dt>Subject</dt><dd>If the permit is granted</dd>')+body,False),
        (header.format('<dt>Subject</dt><dd>unless the permit is withheld</dd>')+body,False),
        (header.format('<dt>From</dt><dd>Owen Kestrel</dd>')+body,False),
        (header.format('<dt>Note</dt><dd>Quoted instruction</dd>')+body,False),
        ('<dl><dt>From</dt><dd>Lina Mercer</dd></dl>'+body,False),
        (header.format('').replace('Lina Mercer','Lina <em>Mercer</em>')+body,False),
        (header.format('<dt>Subject</dt><dd>Unqualified correspondence</dd>')+body,True),
    ]
    for raw,positive in variants:
        specs.append({'question':'Who wrote the tidal index?','sources':[{'id':'DOCUMENT-1','body_html':raw}],'key':key('complete' if positive else 'withhold',prop if positive else None,[statement] if positive else [],['Source-attributed statement']),'mechanism':'Closed definition-list metadata must not become the actor of subsequent prose; retain outer quotation and conditional scope','protected_operation':'Native original-layout boundary and full-source governors, never metadata-as-person or inferred execution'})
    base=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    packet(home,'NESSIE',specs,base,'tools/cryptid_layout_wrap.py')
    registry=read(home/'registry.json');keys=read(home/'key.json');out={}
    for number,row in enumerate(registry['cases'],70):
        old=row['id'];ident=f'CRYPT-NESSIE-{number:04d}';folder=home/'inputs'/old;folder.rename(home/'inputs'/ident)
        case=read(home/'inputs'/ident/'case.json');case['id']=ident;(home/'inputs'/ident/'case.json').write_text(json.dumps(case,indent=2)+'\n')
        row.update(id=ident,packet=str((home/'inputs'/ident).relative_to(ROOT)));row['files']['case.json']=sha(home/'inputs'/ident/'case.json');out[ident]=keys[old]
    for name,value in [('registry.json',registry),('key.json',out)]: (home/name).write_text(json.dumps(value,indent=2)+'\n')
    seal=read(home/'freeze.json');seal.update(registry_sha256=sha(home/'registry.json'),key_sha256=sha(home/'key.json'));(home/'freeze.json').write_text(json.dumps(seal,indent=2)+'\n')

if __name__=='__main__':main()
