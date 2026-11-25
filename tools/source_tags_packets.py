"""Freeze source-tag comparisons; keys stay outside the native worker."""
import copy
import hashlib
from html import escape
import json
from pathlib import Path
import random
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from mplpb_combined.ledger import write
from mplpb_answers.body_text import body_text

VARIANTS = ['valid', 'wrong_reporter', 'wrong_inner_actor', 'wrong_object',
            'wrong_polarity', 'wrong_condition', 'wrong_relation', 'altered_quote',
            'wrong_hash', 'shifted_coordinate', 'forged_access', 'cyclic_containment']

def dump(p, v):
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('x') as f: json.dump(v, f, indent=2, ensure_ascii=False);f.write('\n')

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def generate(destination, transfer=False):
    rng=random.Random('SOURCE-TAGS-01-transfer-2b7d' if transfer else 'SOURCE-TAGS-01-dev-951e')
    names=['Amara Voss','Hugo Ferrer','Leila Bhandari','Dario Solis','Nadia Rhee','Enzo Vidal']
    if transfer:names=['Iona Farouk','Mateo Sato','Elina Brooks','Ravi Dumas','Nora Mendes','Petra Imani']
    objects=['tidal register','copper inventory','winter ledger','harbour catalogue']
    if transfer:objects=['orchard census','glacier log','canal survey','quarry register']
    keys=[];manifest=[]
    for genre in ['letter','minutes','report']:
      for form in range(2):
       for variant in (['valid','wrong_inner_actor','wrong_hash','altered_quote'] if transfer else VARIANTS):
        ident=('ST-T-' if transfer else 'ST-D-')+str(len(keys)+1).zfill(3)
        reporter,author,writer=rng.sample(names,3);obj='the '+rng.choice(objects)
        if transfer:
            statement=(f'According to {reporter}, {author} wrote {obj}.' if not form
                       else f'The statement that {author} wrote {obj} was reported by {reporter}.')
        else:
            statement=(f'{reporter} reported that {author} wrote {obj}.' if not form
                       else f'{reporter} stated, “{author} did not write {obj}.”')
        negative=bool(form and not transfer)
        header=(f'From: {writer}\nTo: Ada Moreno\nDate: March 4, 1924' if genre=='letter'
                else f'Meeting minutes.\nRecorded by {writer}' if genre=='minutes'
                else f'Report.\nWritten by {writer}')
        # Ordinary source paragraphs retain the byline layout. Tags never add text.
        source=header+'\n'+statement
        folder=destination/'inputs'/ident
        record=write(folder/'ledger',doc_id='SOURCE-1',title='Synthetic archive',scope='documentary originals',
                     body_html='<pre>'+escape(source)+'</pre>',origin='machine',external='yes',when='2026-11-25T17:31Z')
        body=body_text(record.body_html);start=body.index(statement);end=start+len(statement)
        def span(text, lo=0):
            a=body.index(text,lo);encoded=escape(text);b=record.body_html.index(encoded)
            return {'body_start':a,'body_end':a+len(text),'quote':text,
                    'original_start_byte':len(record.body_html[:b].encode()),
                    'original_end_byte':len(record.body_html[:b+len(encoded)].encode())}
        proposition={'reporter':reporter,'author':author,'inner_action':'write','object':obj,
                     'inner_negative':negative,'outer_negative':False,'conditions':[],
                     'content_asserted_by_reporter':True,'actual_authorship_established':False,
                     'source_writer_or_unknown':writer,'relation':'source_attributed_report_content',
                     'source_voice':'source_reports_named_speaker','reporting_layer':'source_scoped_report_content',
                     'completion_established':False,'historical_truth_independently_verified':False}
        nodes=[{'id':'D1','kind':'document','parent':None,'body_start':0,'body_end':len(body)},
               {'id':'C1','kind':'statement','parent':'D1',**span(statement)},
               {'id':'P1','kind':'person','parent':'C1',**span(reporter,start)},
               {'id':'P2','kind':'person','parent':'C1',**span(author,start)},
               {'id':'O1','kind':'object','parent':'C1',**span(obj,start)}]
        packet={'schema':'source-linked-proposals-v1','source':{'id':record.id,'path':record.path,'hash':record.hash_actual,
                   'body_html_sha256':hashlib.sha256(record.body_html.encode()).hexdigest()},
                'nodes':nodes,'relations':[{'witness':'C1','subject':'P2','reported_by':'P1','object':'O1','proposition':proposition}]}
        if variant=='wrong_reporter':proposition['reporter']=writer
        elif variant=='wrong_inner_actor':proposition['author']=writer
        elif variant=='wrong_object':proposition['object']='the missing register'
        elif variant=='wrong_polarity':proposition['inner_negative']=not negative
        elif variant=='wrong_condition':proposition['conditions']=['If permission is granted']
        elif variant=='wrong_relation':proposition['relation']='independently_established_authorship'
        elif variant=='altered_quote':nodes[1]['quote']=statement.replace(author,writer)
        elif variant=='wrong_hash':packet['source']['hash']='sha256:'+'0'*64
        elif variant=='shifted_coordinate':nodes[1]['body_start']+=1
        elif variant=='forged_access':packet['source']['visibility']='public';packet['private']=False
        elif variant=='cyclic_containment':nodes[1]['parent']='P2'
        question=f'What does {reporter} report about the writer of {obj}, without independently verifying the event?'
        dump(folder/'question.json',{'question':question});dump(folder/'tags.json',packet)
        keys.append({'id':ident,'raw_supported':True,'tags_accepted':variant=='valid','variant':variant,'genre':genre})
        manifest.append({'id':ident,'genre':genre,'form':form,'variant':variant,'files':{str(p.relative_to(folder)):digest(p) for p in sorted(folder.rglob('*')) if p.is_file()}})
    dump(destination/'key.json',keys);dump(destination/'manifest.json',{'cases':manifest,'same_operator':True,'independent_preparation':'NOT_RUN'})
    dump(destination/'seal.json',{'seed':'SOURCE-TAGS-01-transfer-2b7d' if transfer else 'SOURCE-TAGS-01-dev-951e',
                                'manifest_sha256':digest(destination/'manifest.json'),'key_sha256':digest(destination/'key.json')})

if __name__=='__main__':
    generate(Path(sys.argv[1]), '--transfer' in sys.argv)
