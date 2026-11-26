"""Post-C1 development scope controls, frozen before any scope repair."""
import copy,hashlib,json
from pathlib import Path
from tools.bunyip_packets import ROOT,HOME,BASE,save,sha
from tools.cryptid_packet_support_v4 import packet

def main():
    base=json.load(open(HOME/'development/key.json'));template=next(v for v in base.values() if v['literal_claim'] and v['decision']=='complete');rows=[]
    cases=[('Who owns Blue Heron Studio?',['Kira Lane reported that Mira Stone owns Blue Heron Studio.'],False,False,{}),('Who does Blue Heron Studio belong to?',['Only if the permit is approved.','Mira Stone owns Blue Heron Studio.'],False,False,{}),('Who owns Blue Heron Studio?',['Unless the permit is denied.','Mira Stone owns Blue Heron Studio.'],False,False,{}),('Who owns Blue Heron Studio?',['Mira Stone owns Blue Heron Studio.'],False,True,{}),('What kind of place is Amber Hollow?',['Only if the license is granted.','Amber Hollow is a community garden.'],False,False,{}),('When does Blue Heron Office open?',['Only if staffing is sufficient.','Name: Blue Heron Office','Opening time: 09:15'],False,False,{}),('Who does Blue Heron Studio belong to?',['The public gate is closed.','Mira Stone owns Blue Heron Studio.'],True,False,{}),('Who does Blue Heron Studio belong to?',['Mira Stone owns Blue Heron Studio.'],False,False,{'not_for':'belong'}),('Who does Blue Heron Studio belong to and who operates it?',['Mira Stone owns Blue Heron Studio.'],False,False,{}),('Who does Blue Heron Studio belong to before April 2?',['Mira Stone owns Blue Heron Studio.'],False,False,{}),('Is Amber Hollow a community garden?',['Amber Hollow is a railway station.'],False,False,{}),('What kind of place is Amber Hollow?',['Amber Hollow is a community garden.'],False,True,{})]
    import html
    for q,lines,positive,quoted,flags in cases:
        for rendering in ['paragraphs','plain']:
            body=''.join('<p>'+html.escape(s)+'</p>' for s in lines) if rendering=='paragraphs' else '<pre>'+html.escape('\n'.join(lines))+'</pre>'
            if quoted:body='<blockquote>'+body+'</blockquote>'
            key=copy.deepcopy(template);key.update(decision='complete' if positive else 'withhold',complete_witnesses=[lines[-1]] if positive else [],literal_claim=True,proposition={},date_roles={})
            rows.append({'question':q,'sources':[dict(id='SCOPE-1',body_html=body,**flags)],'key':key,'mechanism':'scope_wrap','protected_operation':'Keep outer report, quotation, governing condition, original policy phrase and every requested obligation','rendering':rendering})
    folder=HOME/'scope-wrap';packet(folder,'BUNYIPW',rows,BASE,'tools/bunyip_scope_wrap.py')
    registry=json.load(open(folder/'registry.json'))
    for row,s in zip(registry['cases'],rows):row.update(rendering=s['rendering'],question_group='scope_wrap')
    save(folder/'registry.json',registry);seal=json.load(open(folder/'freeze.json'));seal['registry_sha256']=sha(folder/'registry.json');seal['harness']['tools/bunyip_score.py']=sha(ROOT/'tools/bunyip_score.py');save(folder/'freeze.json',seal)
    save(folder/'exposure.json',{'prepared':'After initial C1 102-case result, before C1 scope diagnostic and any further native repair','not_preimplementation_controls_for_C1':True,'independent_adjudication':'NOT_RUN'})
    print(len(rows),'development Wrap executions frozen')
if __name__=='__main__':main()
