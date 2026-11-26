"""Freeze a quoted-condition contrast before the shared scope repair."""
import json
from tools.bunyip_packets import ROOT,HOME,BASE,save,sha
from tools.cryptid_packet_support_v4 import packet

def main():
    fact='Nadia Flint owns Lark Basin Cooperative.';q='Who does Lark Basin Cooperative belong to?';rows=[]
    for rendering,body in [('paragraphs','<blockquote><p>Only if the permit is valid.</p></blockquote><p>'+fact+'</p>'),('plain','<pre>“Only if the permit is valid.”\n'+fact+'</pre>')]:
        rows.append({'question':q,'sources':[{'id':'CONTEXT-1','body_html':body}],'key':{'decision':'complete','complete_witnesses':[fact],'proposition':{},'literal_claim':True,'qualification_fragments':[],'date_roles':{}},'mechanism':'quoted_governor','protected_operation':'Quoted unrelated material does not become an outer source condition; preserve explicit outer assertion','rendering':rendering})
    folder=HOME/'quoted-governor';packet(folder,'BUNYIPQ',rows,BASE,'tools/bunyip_quoted_governor.py');reg=json.load(open(folder/'registry.json'))
    for r,s in zip(reg['cases'],rows):r.update(rendering=s['rendering'],question_group='quoted_governor')
    save(folder/'registry.json',reg);seal=json.load(open(folder/'freeze.json'));seal['registry_sha256']=sha(folder/'registry.json');seal['harness']['tools/bunyip_score.py']=sha(ROOT/'tools/bunyip_score.py');save(folder/'freeze.json',seal)
if __name__=='__main__':main()
