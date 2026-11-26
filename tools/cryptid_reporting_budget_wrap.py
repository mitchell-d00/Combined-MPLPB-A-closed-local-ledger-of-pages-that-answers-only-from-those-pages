"""Post-analysis development controls for the unchanged source-unit cap."""
from tools.cryptid_revision3_packets import freeze,HOME
from tools.cryptid_packet_support_v4 import key
from tools.cryptid_trial import read,sha
from pathlib import Path
import json

def main():
    text='“Marin Holt did not write the ridge register,” Leda Voss did not report.'
    prop={'relation':'source_attributed_report_content','reporter':'Leda Voss','author':'Marin Holt','object':'the ridge register','outer_negative':True,'inner_negative':None,'inner_polarity':'unasserted','content_asserted_by_reporter':False,'conditions':[],'actual_authorship_established':False,'completion_established':False}
    specs=[]
    for filler,decision in [(997,'complete'),(998,'withhold')]:
        raw='<p>Report.</p><p>Written by Quentin Moss.</p><p>'+text+'</p>'+'<p>Cabinet leaf.</p>'*filler
        specs.append({'question':'What does Leda Voss report about whether Marin Holt wrote the ridge register?','sources':[{'id':'RPT-1','body_html':raw}],'key':key(decision,prop if decision=='complete' else None,[text] if decision=='complete' else [],['Source-scoped reporting statement','Independent authorship']),'mechanism':'A byline/curly-quotation boundary counts as two units, preserving the fixed1000unit cap','protected_operation':'1000completeunits may prove a reporting statement;1001units must stop explicitly, never silently skip counterevidence'})
    folder=HOME/'reporting-budget-wrap';freeze(folder,'YETI',specs,140)
    seal=read(folder/'freeze.json');seal['harness']['tools/cryptid_reporting_budget_wrap.py']=sha(Path(__file__));(folder/'freeze.json').write_text(json.dumps(seal,indent=2)+'\n')
    (folder/'custody.json').write_text(json.dumps({'exposure':'Post-candidate diagnostic development controls prepared after observing4unit-counter differences; not fresh transfer','reader_baseline':'1251unchanged old reader, rerun from full source extraction','native_candidate':'LOCAL-REV3-C1 already implemented; no source edits informed by these controls'},indent=2)+'\n')

if __name__=='__main__':main()
