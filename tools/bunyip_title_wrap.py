"""Freeze display-title scope contrasts and fresh compositional transfer pre-C4."""
import copy,html,json,random,shutil,zipfile
from pathlib import Path
from tools.bunyip_packets import ROOT,HOME,save,sha,specs
from tools.cryptid_packet_support_v4 import packet
BASE='bfb469e6444c5194e57fb1c18c76af9f17a0e630'
GEN='tools/bunyip_title_wrap.py'
def freeze(folder,family,rows,held=False):
    packet(folder,family,rows,BASE,GEN,held=held);reg=json.loads((folder/'registry.json').read_text())
    for r,s in zip(reg['cases'],rows):r.update(rendering=s['rendering'],question_group=s['mechanism'])
    save(folder/'registry.json',reg);seal=json.loads((folder/'freeze.json').read_text());seal['registry_sha256']=sha(folder/'registry.json');seal['harness']['tools/bunyip_score.py']=sha(ROOT/'tools/bunyip_score.py');save(folder/'freeze.json',seal)
def main():
    rows=[];fact='Iona Reed owns Cedar Quay Printworks.';other='Moss Landing Studio is owned by Arun Lake.'
    cases=[('Public fictional collection','<h1>Public fictional collection</h1>',fact,True),('A fictional catalogue','<h1>A fictional catalogue</h1>',other,True),('Hypothetical fictional collection','<h1>Hypothetical fictional collection</h1>',fact,False),('Ordinary collection','<h1>Fictional ownership</h1>',fact,False),('Public fictional collection','<h1>Public fictional collection</h1><blockquote>',fact,False),('Public fictional collection','<h1>Public fictional collection</h1><p>Only if the permit is valid.</p>',fact,False),('Public fictional collection','<h1>Public fictional collection</h1><h2>Conditional ownership</h2>',fact,False),('Public fictional collection','<h1 class="quotation">Public fictional collection</h1>',fact,False)]
    for title,prefix,text,positive in cases:
        entity='Moss Landing Studio' if text==other else 'Cedar Quay Printworks';q='Who does '+entity+' belong to?'
        for rendering in ['paragraphs','plain']:
            body=prefix+('<p>'+html.escape(text)+'</p>' if rendering=='paragraphs' else '<pre>'+html.escape(text)+'</pre>')+('</blockquote>' if '<blockquote>' in prefix else '')
            rows.append({'question':q,'sources':[{'id':'TITLE-1','title':title,'body_html':body}],'key':{'decision':'complete' if positive else 'withhold','complete_witnesses':[text] if positive else [],'proposition':{},'literal_claim':True,'qualification_fragments':[],'date_roles':{}},'mechanism':'display_title_vs_semantic_scope','protected_operation':'A generated fictional display title does not deny literal source correspondence; hypothetical, quotation, conditional and body-heading scopes remain authoritative. No independent truth.','rendering':rendering})
    freeze(HOME/'title-wrap','BUNYIPH',rows)
    # Same-operator compositional transfer: unseen prefixed questions, new
    # document layout/header, actors and entities. Templates are visible.
    selected=[];seen=set();positive=specs(True)
    for group in ['owner','classification','opening_time','writing_date','report_negation','instruction']:
        for decision in ['complete','withhold']:
            candidate=next(copy.deepcopy(r) for r in positive if r['question_group']==group and r['key']['decision']==decision)
            for rendering in ['paragraphs','plain']:
                row=copy.deepcopy(candidate);row['rendering']=rendering
                # Reconstruct the alternate rendering from its matched original.
                original=next(r for r in positive if r['question']==candidate['question'] and r['rendering']==rendering);row['sources']=copy.deepcopy(original['sources'])
                prefix='According to '+{'owner':'this record','classification':'this source','opening_time':'the record','writing_date':'the source','report_negation':'the source','instruction':'this record'}[group]+', '
                q=row['question'];q=q[0].lower()+q[1:];row['question']=prefix+q
                replacements={'Larkspur':'Juniper Quay','Vera Quinn':'Iona Reed','Willow Reach':'Meadow Rise','sculpture park':'public arboretum','highland dispatch':'island memorandum','Nela Frost':'Cora Dale','Arlo Penn':'Cal Rook','Dara Elm':'Eira Ash','Iven Clay':'Arun Lake','lantern index':'harbor catalogue','Nora Field':'Alin Quill','western beacon':'southern signal tower','field team':'shore team'}
                serialized=json.dumps(row)
                for old,new in replacements.items():serialized=serialized.replace(old,new)
                row=json.loads(serialized);s=row['sources'][0];title='Fictional archive sheet' if group in {'owner','classification','opening_time'} else 'Filed documentary sheet';s['title']=title
                s['body_html']='<h1>'+title+'</h1><header>Catalogue slip.</header>'+s['body_html']
                row['mechanism']='composed_question_and_document_layers';row['protected_operation']='Original full question and reporting layer, explicit witnesses and source state; new display/quotation header cannot supply an answer.';selected.append(row)
    stage=Path('/workspace/cryptid-custody/bunyip-final2-sealed-build');freeze(stage,'BUNYIPN',selected,True)
    home=HOME/'fresh2';home.mkdir(exist_ok=False)
    with zipfile.ZipFile(home/'transfer-sealed.zip','x',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(stage.rglob('*')):
            if p.is_file():z.write(p,str(p.relative_to(stage)))
    save(home/'transfer-seal.json',{'packet_sha256':sha(home/'transfer-sealed.zip'),'seed':2026112611,'generator_sha256':sha(ROOT/GEN),'cases':len(selected),'custody':'Same-operator visible deterministic templates. Unseen composed question prefixes and header/body layouts; limited compositional transfer, no independent preparation/blinding/scoring. Instance/key bytes not reopened after seal until committed candidate ZIP.','opening':'NOT_RUN'});shutil.rmtree(stage)
    print('Frozen',len(rows),'title controls and',len(selected),'fresh transfer cases')
if __name__=='__main__':main()
