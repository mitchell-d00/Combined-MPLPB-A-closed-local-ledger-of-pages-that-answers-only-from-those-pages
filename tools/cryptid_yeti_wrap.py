"""Separately frozen reporting/content polarity composition controls."""
from tools.cryptid_trial import ROOT,save,sha,snapshot,digest
from tools.cryptid_yeti_packets import report,TOOLS,BASE
HOME=ROOT/'evaluation/cryptid/yeti/wrap'


def main():
    HOME.mkdir(exist_ok=False);rows=[];keys={};actor='Mara Flint';author='Ivo Keene';obj='the marine index'
    cases=[(f'{actor} did not report that {author} did not write {obj}.','denial_of_reporting',False),
           (f'{actor} said, "{author} did not write {obj}."','reported_denial',False),
           (f'If the permit is granted, {actor} would not report that {author} did not write {obj}.','conditional_reporting',True),
           (f'{actor} would not report that {author} did not write {obj}.','withhold',False)]
    for n,(statement,kind,conditional) in enumerate(cases,53):
        ident=f'CRYPT-YETI-{n:04d}';q=f'What conditional authorship statement does {actor} report about {obj}?' if conditional else f'What does {actor} report about whether {author} wrote {obj}?'
        packet=HOME/'inputs'/ident
        save(packet/'case.json',{'id':ident,'adapter_mode':'documentary','question':q,'sources':[{'id':'DOCUMENT-1','body_html':'<pre>Report.\nWritten by Owen Kestrel.\n'+statement+'</pre>'}],'profile':'internal','budget':{'passages':12,'characters':8000}})
        if kind=='withhold':key={'decision':'withhold','claims':[],'missing_fragments':[]}
        else:
            c=report(actor,author,obj,statement,kind)
            if conditional:c['proposition'].update(outer_negative=True,conditional_content_negative=True)
            key={'decision':'complete','claims':[c],'missing_fragments':[]}
        keys[ident]=key;rows.append({'id':ident,'family':'YETI','packet':str(packet.relative_to(ROOT)),'files':snapshot(packet),'semantic_input_hash':digest({'question':q,'source':statement}),'origin':{'test':'double negation and quoted/conditional reporting layer composition','related_prs':[103]},'mechanism':'Negating reporting never asserts or reverses its unasserted payload','protected_operation':'Separate reporting polarity from payload polarity and preserve full governor','baseline_commit':BASE,'budgets':{'records':8,'scan_characters':200000,'units':1000,'passages':12,'characters':8000,'cpu_seconds':30,'wall_seconds':45},'custody':'same-operator; expectations from requested actor/layer and exact witnesses'})
    save(HOME/'registry.json',{'schema':'cryptid-case-registry-v1','family':'YETI','exposure':'development exposed; separately frozen before native changes','cases':rows})
    save(HOME/'key.json',keys)
    save(HOME/'freeze.json',{'registry_sha256':sha(HOME/'registry.json'),'key_sha256':sha(HOME/'key.json'),'harness':{p:sha(ROOT/p) for p in TOOLS+['tools/cryptid_yeti_wrap.py']},'baseline_reader_commit':BASE,'independence':'NOT_RUN'})

if __name__=='__main__':main()
