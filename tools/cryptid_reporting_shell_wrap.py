"""Freeze passive and present-tense reporting-negation contrasts before repair."""
from tools.cryptid_revision3_packets import freeze,HOME
from tools.cryptid_packet_support_v4 import key

def main():
    rows=[];actor='Asha Dell';reporter='Bela Neri';obj='the copper register'
    for outer in [False,True]:
        for inner in [False,True]:
            text='The statement that '+actor+(' did not write ' if inner else ' wrote ')+obj+(' was not reported' if outer else ' was reported')+' by '+reporter+'.'
            rows.append((text,outer,inner))
    for inner in [False,True]:
        payload=actor+(' did not write ' if inner else ' wrote ')+obj
        rows += [(reporter+' does not say that '+payload+'.',True,inner),(reporter+' does not state, “'+payload+'.”',True,inner)]
    specs=[]
    for text,outer,inner in rows:
        prop={'relation':'source_attributed_report_content','reporter':reporter,'author':actor,'object':obj,'outer_negative':outer,'inner_negative':None if outer else inner,'inner_polarity':'unasserted' if outer else 'negative' if inner else 'affirmative','content_asserted_by_reporter':not outer,'conditions':[],'actual_authorship_established':False,'completion_established':False}
        specs.append({'question':f'What does {reporter} report about whether {actor} wrote {obj}?','sources':[{'id':'RPT-1','body_html':'<p>'+text+'</p>'}],'key':key('complete',prop,[text],['Source-scoped reporting statement','Independent authorship']),'mechanism':'Passive and present reporting-shell negation must preserve outer denial and unasserted embedded content','protected_operation':'Shared reporting polarity operation across syntax; never independent authorship'})
    # freeze() hashes the packet generator; pin this supplementary generator too.
    freeze(HOME/'reporting-shell-wrap','YETI',specs,130)
    from tools.cryptid_trial import read,sha
    from pathlib import Path
    import json
    seal=read(HOME/'reporting-shell-wrap/freeze.json');seal['harness']['tools/cryptid_reporting_shell_wrap.py']=sha(Path(__file__));(HOME/'reporting-shell-wrap/freeze.json').write_text(json.dumps(seal,indent=2)+'\n')

if __name__=='__main__':main()
