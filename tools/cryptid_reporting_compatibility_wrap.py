"""Freeze literal-content/reporting-layer contrasts before compatibility repair."""
from pathlib import Path
import json,subprocess
from tools.cryptid_packet_support_v4 import packet,key
from tools.cryptid_trial import ROOT,read,sha

def main():
    folder=ROOT/'evaluation/cryptid/revision3/reporting-compatibility-wrap';specs=[]
    # Each item: outer denial, literal embedded denial, explicit condition.
    pairs=[((False,False,''),(True,False,''),'conflict'),((False,True,''),(True,True,''),'conflict'),((False,False,''),(True,True,''),'complete'),((False,True,''),(True,False,''),'complete'),((True,False,''),(True,True,''),'complete'),((False,False,'If the seal is intact'),(True,False,'If the seal is intact'),'conflict'),((False,False,'If the seal is intact'),(True,False,'If the seal is opened'),'complete'),((False,False,''),(False,True,''),'conflict')]
    for left,right,decision in pairs:
        sources=[];expected=[]
        for n,(outer,inner,condition) in enumerate([left,right],1):
            payload='Marin Holt '+('did not write' if inner else 'wrote')+' the ridge register'
            if condition:text=condition+', Leda Voss '+('would not report' if outer else 'would report')+' that '+payload+'.'
            else:text='Leda Voss '+('did not say' if outer else 'said')+', “'+payload+'.”'
            prop={'relation':'source_attributed_report_content','reporter':'Leda Voss','author':'Marin Holt','object':'the ridge register','outer_negative':outer,'embedded_content_negative':inner,'inner_negative':None if outer or condition else inner,'inner_polarity':'unasserted' if outer or condition else 'negative' if inner else 'affirmative','content_asserted_by_reporter':not outer and not condition,'conditions':[condition] if condition else [],'actual_authorship_established':False,'completion_established':False}
            expected.append({'proposition':prop,'qualification_fragments':['Source-scoped reporting statement','Independent authorship'],'complete_witnesses':[text]})
            sources.append({'id':'RPT-'+str(n),'body_html':'<p>Report.</p><p>Written by Quentin Moss.</p><p>'+text+'</p>'})
        k=key(decision);k['claims']=expected
        q='What conditional authorship statement does Leda Voss report about the ridge register?' if left[2] else 'What does Leda Voss report about whether Marin Holt wrote the ridge register?'
        specs.append({'question':q,'sources':sources,'key':k,'mechanism':'Reporting-layer denial compares the same embedded proposition; denying the opposite report is compatible, not a conflict','protected_operation':'Literal embedded polarity, assertion status and condition scope are separate; no inferred historical truth'})
    base=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();packet(folder,'YETI',specs,base,'tools/cryptid_reporting_compatibility_wrap.py');registry=read(folder/'registry.json');keys=read(folder/'key.json');updated={}
    for number,row in enumerate(registry['cases'],150):
        old=row['id'];ident=f'CRYPT-YETI-{number:04d}';p=folder/'inputs'/old;p.rename(folder/'inputs'/ident);case=read(folder/'inputs'/ident/'case.json');case['id']=ident;(folder/'inputs'/ident/'case.json').write_text(json.dumps(case,indent=2)+'\n');row.update(id=ident,packet=str((folder/'inputs'/ident).relative_to(ROOT)));row['files']['case.json']=sha(folder/'inputs'/ident/'case.json');updated[ident]=keys[old]
    for name,value in [('registry.json',registry),('key.json',updated)]: (folder/name).write_text(json.dumps(value,indent=2)+'\n')
    seal=read(folder/'freeze.json');seal.update(registry_sha256=sha(folder/'registry.json'),key_sha256=sha(folder/'key.json'));(folder/'freeze.json').write_text(json.dumps(seal,indent=2)+'\n')
    (folder/'representation-v2.json').write_text(json.dumps({'version':'source-report-content-polarity-v2','new_field':'embedded_content_negative: literal payload polarity, never an assertion that the payload is true','legacy_fields':'inner_negative remainsnull andinner_polarity remainsunasserted whenouterdenial/condition doesnotassertpayload; oldvaluesunchanged','compatibility':'Compare literal payload and outer reporting sign under the same conditions. Denying a different/opposite embedded report is compatible. Two affirmative opposed contents conflict at content layer. Different conditions are not silently unified.','migration':'An additive field must be source-checked against the complete eligible witness; stripping it for legacy semantic comparison does not permit any other claim/citation/qualification change. Original exact scores and incorrect conflict key remain unchanged.','baseline_scoring':'Full v2structured score can fail because C1 lacks the field. Report comparison decision accuracy separately; do not call every missing-field flag a false source fact.','independent_semantic_adjudication':'NOT_RUN'},indent=2)+'\n')

if __name__=='__main__':main()
