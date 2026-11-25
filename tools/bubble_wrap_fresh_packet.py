"""Freeze composition transfer after the first packet became development.

No instance/key inspection by the implementer before the next candidate freeze.
Templates remain same-operator visible: this is not independent blinding.
"""
import argparse
import hashlib
import json
from pathlib import Path
import random


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x') as f:f.write(json.dumps(d,indent=2,ensure_ascii=False)+'\n')


def prepare(a):
    rng=random.Random(a.seed);cases=[];keys=[]
    names=['Maren Dupont','Yusuf Imani','Ines Calder','Tavi Sorensen','Amara Nwosu','Keiko Bellamy','Paolo Winter','Sofia Rahman']
    objects=['glacier observations','harbour soundings','marsh census','woodland register','meteorology log','plateau survey']
    for genre in ['letter','minutes','report']:
        for structure in ['according_to_active','according_to_passive']:
            writer,reporter,author,absent=rng.sample(names,4);obj=rng.choice(objects)
            for variant in ['affirmative','wrong_reporter','inner_denial','unsupported_actual_authorship']:
                ident=f'RC2-T{len(cases)+1:03d}';negative=variant=='inner_denial'
                if structure=='according_to_active':
                    clause=f'According to {reporter},\n{author} '+('did not write' if negative else 'wrote')+f' the {obj}.'
                else:
                    clause=f'According to {reporter},\nthe {obj} was '+('not ' if negative else '')+f'written by {author}.'
                heading={'letter':f'From: {writer}\nTo: Records office\nDate written: November 09, 1862\n',
                         'minutes':f'Meeting minutes.\nRecorded by {writer}\n',
                         'report':f'Report.\nWritten by {writer}\n'}[genre]
                directory=a.custody/'transfer/inputs'/ident;(directory/'sources').mkdir(parents=True)
                (directory/'sources/original.txt').write_bytes((heading+'\n'+clause+'\n').encode())
                requested=absent if variant=='wrong_reporter' else reporter
                question=f'What does {requested} report about the writer of the {obj}, without independently verifying the event?'
                if variant=='unsupported_actual_authorship':question=f'Do these records independently establish that {author} actually wrote the {obj}?'
                save(directory/'case.json',{'id':ident,'question':question,'profile':'internal',
                     'sources':[{'path':'sources/original.txt','source_class':'original','external':'yes'}],
                     'budget':{'passages':12,'characters':8000}})
                files={str(p.relative_to(directory)):sha(p) for p in directory.rglob('*') if p.is_file()}
                cases.append({'id':ident,'genre':genre,'structure':structure,'variant':variant,'files':files})
                keys.append({'id':ident,'supported_source_content_target':variant in {'affirmative','inner_denial'},
                     'reporter':reporter,'attributed_author':author,'object':'the '+obj,'inner_action':'write',
                     'inner_negative':negative,'source_header_writer':writer,'actual_authorship_established':False,
                     'full_governing_clause':clause,'source_voice':'source_reports_named_speaker'})
    save(a.custody/'transfer-key.json',keys)
    save(a.output/'seal.json',{'seed':a.seed,'generator_sha256':sha(Path(__file__)),'cases':cases,
         'key_sha256':sha(a.custody/'transfer-key.json'),'instances_opened_by_implementer':False,
         'templates_visible':True,'preparer_and_scorer':'Betty, same operator',
         'transfer_scope':'New according-to outer framing composed with active/passive authorship and wrapped clauses; unpunctuated bylines. Not independent grammar novelty or collection transfer.',
         'reserved':'Do not exercise these according-to constructions in supplemental development before candidate freeze.',
         'independent_preparation':'NOT_RUN','independent_blinding':'NOT_RUN','independent_semantic_adjudication':'NOT_RUN'})
    save(a.output/'rule.json',{'mechanism':'Unpunctuated leading writer/recorder label merges with the first report statement. The complete report parser already handles the consumed clauses; unit boundaries must preserve documentary metadata without dropping a governor.',
         'native_repair_not_started':True,'first_failed_transfer':'Retain16/24, eight minutes/report misses, zero false support; consumed development only.',
         'budgets_unchanged':True,'expected':'Preserve every original decision/key; recover eight consumed misses through general metadata boundaries. Keep eligible writer/reporter/content roles and conditions separate.'})
    print('Fresh24 composition-transfer packet frozen; exact instance bytes/key remain unopened.')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for n in ['custody','output']:p.add_argument('--'+n,type=Path,required=True)
    p.add_argument('--seed',required=True);prepare(p.parse_args())
