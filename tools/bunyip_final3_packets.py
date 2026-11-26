"""Seal fresh source-language/composition cases before optional-metadata repair."""
import html,json,shutil,zipfile
from pathlib import Path
from tools.bunyip_packets import ROOT,HOME,save,sha
from tools.cryptid_packet_support_v4 import packet
GEN='tools/bunyip_final3_packets.py';BASE='d0a790b0e331515f55cad8ea70d4c0a8e5e499c7'
def main():
    rows=[]
    def add(group,q,lines,witnesses,prop=None,decision='complete',date_roles=None):
        for rendering in ['paragraphs','plain']:
            body='<article><section>'+''.join('<p>'+html.escape(s)+'</p>' for s in lines)+'</section></article>' if rendering=='paragraphs' else '<div><pre>'+html.escape('\n'.join(lines))+'</pre></div>'
            rows.append({'question':q,'sources':[{'id':'SOURCE-1','title':'Transfer source','body_html':body}],'key':{'decision':decision,'complete_witnesses':witnesses if decision=='complete' else [],'proposition':prop or {},'literal_claim':group in {'owner','classification'},'qualification_fragments':['Source-attributed statement only','does not establish execution'] if group=='instruction' else [],'date_roles':date_roles or {}},'rendering':rendering,'mechanism':group,'protected_operation':'Whole original question, source-linked relation/role and literal witnesses; no inferred execution, identity or date role.'})
    own='Bracken Studio belongs to Senna Holt.';q='According to the source, which person owns Bracken Studio?'
    add('owner',q,[own],[own]);add('owner',q,['Bracken Studio does not belong to Senna Holt.'],[],decision='withhold')
    kind='Juniper Grove is a botanical garden.'
    add('classification','According to this record, how is Juniper Grove described?',[kind],[kind]);add('classification','According to this record, is Juniper Grove a railway station?',[kind],[],decision='withhold')
    written='The reef letter was written on April 24, 1910.';received='The reef letter was received on April 30, 1910.';q='According to this source, on what date was the reef letter written?'
    add('writing_date',q,[received,written],[written],{'relation':'source_event_date_inventory'},date_roles={'writing':'April 24, 1910'});add('writing_date',q,[received],[],decision='withhold')
    instruction='Senna Holt instructed the bridge team to inspect the island pier.'
    prop={'relation':'source_modality_assertion','actor':'Senna Holt','modality':'instruction','task_actor':'the bridge team','task_action':'inspect','task_object':'the island pier','outer_negative':False,'content_negative':False,'completion_asserted_by_source':False,'execution_independently_verified':False,'conditions':[]}
    add('instruction','Which task did Senna Holt give the bridge team?',[instruction],[instruction],prop);add('instruction','Did the bridge team inspect the island pier?',[instruction],[],decision='withhold')
    stage=Path('/workspace/cryptid-custody/bunyip-final3-sealed-build');packet(stage,'BUNYIPX',rows,BASE,GEN,held=True)
    reg=json.loads((stage/'registry.json').read_text())
    for r,s in zip(reg['cases'],rows):r.update(rendering=s['rendering'],question_group=s['mechanism'])
    save(stage/'registry.json',reg);seal=json.loads((stage/'freeze.json').read_text());seal['registry_sha256']=sha(stage/'registry.json');seal['harness']['tools/bunyip_score.py']=sha(ROOT/'tools/bunyip_score.py');save(stage/'freeze.json',seal)
    home=HOME/'fresh3';home.mkdir(exist_ok=False)
    with zipfile.ZipFile(home/'transfer-sealed.zip','x',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(stage.rglob('*')):
            if p.is_file():z.write(p,str(p.relative_to(stage)))
    save(home/'transfer-seal.json',{'packet_sha256':sha(home/'transfer-sealed.zip'),'protocol_seed':2026112612,'generator_sha256':sha(ROOT/GEN),'cases':len(rows),'generation':'Deterministic templates, no random sampling. Seed is a protocol identifier.','custody':'Same operator, visible templates; new source belongs-to wording, composed question forms, reversed date-role order and nested source layout. Independent preparation/blinding/adjudication NOT_RUN. Bytes not reopened after seal until committed ZIP.','opening':'NOT_RUN'});shutil.rmtree(stage);print('Sealed',len(rows),'fresh cases before native compatibility repair')
if __name__=='__main__':main()
