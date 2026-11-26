"""Freeze source restriction heads/length controls before further scope repair."""
import copy,html,json
from tools.bunyip_packets import ROOT,HOME,BASE,save,sha
from tools.cryptid_packet_support_v4 import packet

def main():
    q='Who does Lark Basin Cooperative belong to?';fact='Nadia Flint owns Lark Basin Cooperative.';rows=[]
    cases=[]
    for head in ['Only if','Provided that','Subject to']:
        for repetitions in [0,50]:cases.append(([head+' the permit is valid'+(' and the gate is clear'*repetitions)+'.',fact],False))
    cases.append((['The independent inventory note records '+('blue covers '*100)+'in storage.',fact],True))
    for lines,positive in cases:
        for rendering in ['paragraphs','plain']:
            body=''.join('<p>'+html.escape(s)+'</p>' for s in lines) if rendering=='paragraphs' else '<pre>'+html.escape('\n'.join(lines))+'</pre>'
            key={'decision':'complete' if positive else 'withhold','complete_witnesses':[fact] if positive else [],'proposition':{},'literal_claim':True,'truth_verified':False,'qualification_fragments':[],'date_roles':{},'withholding_conditions':['governing restriction cannot disappear beyond an arbitrary prefix length']}
            rows.append({'question':q,'sources':[{'id':'GUARD-1','body_html':body}],'key':key,'mechanism':'source_governor_boundary','protected_operation':'A bare fact under an unresolved conditional governor is not unconditional; unrelated long context remains admissible','rendering':rendering})
    folder=HOME/'governor-wrap';packet(folder,'BUNYIPG',rows,BASE,'tools/bunyip_governor_wrap.py');reg=json.load(open(folder/'registry.json'))
    for r,s in zip(reg['cases'],rows):r.update(rendering=s['rendering'],question_group='source_governor_boundary')
    save(folder/'registry.json',reg);seal=json.load(open(folder/'freeze.json'));seal['registry_sha256']=sha(folder/'registry.json');seal['harness']['tools/bunyip_score.py']=sha(ROOT/'tools/bunyip_score.py');save(folder/'freeze.json',seal);save(folder/'exposure.json',{'stage':'Frozen after C2core/scope controls, before C2 governor diagnostic and C3 source repair','same_operator':True,'independent_adjudication':'NOT_RUN'});print(len(rows),'governor controls')
if __name__=='__main__':main()
