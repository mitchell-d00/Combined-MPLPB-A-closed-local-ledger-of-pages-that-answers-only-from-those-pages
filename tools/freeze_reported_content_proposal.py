"""Freeze a proposed next test; this file does not implement reader behavior."""
import argparse
import hashlib
import json
from pathlib import Path
import random


def save(path, value):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x') as f:
        f.write(json.dumps(value,indent=2,ensure_ascii=False)+'\n')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare(a):
    root=a.inventory
    selection=json.loads((root/'selection.json').read_text())
    old=[r for r in selection['cases'] if r['family']=='reported_statement']
    fresh=json.loads((root/'fresh-contrasts/selection.json').read_text())['cases']
    matched=json.loads((root/'matched-contrasts/selection.json').read_text())['cases']
    assert len(old)==5 and len(fresh)==13 and len(matched)==2
    a.custody.mkdir(mode=0o700)
    primary=[r['id'] for r in old]+['FRESH-01','FRESH-02','FRESH-03','FRESH-04','FRESH-06']
    development=[]
    for row in old+fresh+matched:
        source=(root if row in old else root/'fresh-contrasts' if row in fresh else root/'matched-contrasts')/row['input_path']
        case=json.loads((source/'case.json').read_text())
        development.append({'id':row['id'],'origin':str(source.relative_to(root)),
            'primary_target':row['id'] in primary,'expected':row['expected'],
            'question':case['question'],'source_files':{str(p.relative_to(source)):sha(p) for p in source.rglob('*') if p.is_file()}})
    # These templates are visible to the preparer/implementer. Instance bytes,
    # their key and baseline outputs must stay sealed until a future candidate.
    rng=random.Random(a.seed)
    names=['Eira Solberg','Tariq Belen','Lucía Torre','Niko Grant','Hana Rios','Saïd Amir','Ida Morgen','Leon Okada']
    objects=['reef census','quarry register','harvest chronicle','astronomy catalogue','railway notebook','dune inventory']
    cases=[];keys=[]
    for genre in ['letter','minutes','report']:
        for structure in ['postposed_quotation','passive_reporting_clause']:
            writer,reporter,author,absent=rng.sample(names,4);obj=rng.choice(objects)
            for variant in ['affirmative','wrong_reporter','inner_denial','unsupported_actual_authorship']:
                ident='RC-T%03d'%(len(cases)+1);negative=variant=='inner_denial'
                if structure=='postposed_quotation':
                    sentence=f'“The {obj} was '+('not ' if negative else '')+f'written by {author},” {reporter} reported.'
                else:
                    sentence=f'The statement that {author} '+('did not write' if negative else 'wrote')+f' the {obj} was reported by {reporter}.'
                heading={'letter':f'From: {writer}\nTo: Archive clerk\n','minutes':f'Meeting minutes.\nRecorder: {writer}\n','report':f'Report.\nWritten by {writer}\n'}[genre]
                raw=(heading+'\n'+sentence+'\n').encode()
                folder=a.custody/'transfer/inputs'/ident;(folder/'sources').mkdir(parents=True)
                (folder/'sources/original.txt').write_bytes(raw)
                requested=absent if variant=='wrong_reporter' else reporter
                question=f'What does {requested} report about the writer of the {obj}, without independently verifying the event?'
                if variant=='unsupported_actual_authorship':
                    question=f'Do these records independently establish that {author} actually wrote the {obj}?'
                case={'id':ident,'question':question,'profile':'internal','sources':[{'path':'sources/original.txt','source_class':'original','external':'yes'}],
                      'budget':{'passages':12,'characters':8000}}
                save(folder/'case.json',case)
                hashes={str(p.relative_to(folder)):sha(p) for p in folder.rglob('*') if p.is_file()}
                cases.append({'id':ident,'genre':genre,'structure':structure,'variant':variant,'files':hashes})
                keys.append({'id':ident,'supported_source_content_target':variant in {'affirmative','inner_denial'},
                    'reporter':reporter,'source_header_writer':writer,'attributed_author':author,'object':'the '+obj,
                    'inner_action':'write','inner_negative':negative,'actual_authorship_established':False,
                    'source_voice':'source_reports_named_speaker','full_governing_clause':sentence,
                    'expected_scope':'report content only; no historical authorship or execution certification'})
    save(a.custody/'transfer-key.json',keys)
    save(a.output/'development.json',development)
    save(a.output/'transfer-seal.json',{'seed':a.seed,'cases':cases,'key_sha256':sha(a.custody/'transfer-key.json'),
        'generator_sha256':sha(Path(__file__)),'instances_opened_by_implementer':False,
        'templates_visible':True,'preparer':'Betty, same operator','independent_preparation':'NOT_RUN','blinding':'NOT_RUN',
        'reserved_structures':'Postposed quoted passive authorship; passive outer reporting of active authorship. Do not use in development examples or supplementary controls. If consumed, freeze a fresh transfer set before any further repair.'})
    save(a.output/'preservation.json',{'baseline_commit':selection['baseline_commit'],
        'native_runtime_sha256':selection['baseline_runtime_sha256'],
        'unchanged_historical_cases':selection['cases'],'fresh_controls':fresh+matched,
        'pe02':'All17 complete contracts and discovery arrays, under original private/public source restrictions.',
        'attribution':'Original48, consumed first24 and consumed fresh24, under their development freeze descriptors.',
        'native_targeted':'All28 signed/advice/presentation/erratum/focus controls plus28 source-attribution controls.',
        'valid_complete_answers_to_preserve':13,'known_valid_partials_to_preserve':4,
        'non_support_controls_to_preserve':60,'budgets_changed':False})
    save(a.output/'freeze.json',{'baseline_commit':selection['baseline_commit'],'stage':'PROPOSAL_ONLY; no reader repair implemented',
        'primary_development_targets':primary,'development_cases':len(development),'transfer_cases':24,
        'development_sha256':sha(a.output/'development.json'),'transfer_seal_sha256':sha(a.output/'transfer-seal.json'),
        'preservation_sha256':sha(a.output/'preservation.json'),'generator_sha256':sha(Path(__file__)),
        'rule_sha256':sha(a.rule),'seed':a.seed,'budget':{'records':8,'scan_characters':200000,'units':1000,'passages':12,'output_characters':8000},
        'independent_historical_accuracy':'NOT_RUN','independent_semantic_adjudication':'NOT_RUN',
        'outside_custodian_scoring':'NOT_RUN','native_oocc':'NOT_RUN'})
    print('Frozen proposal: twenty development cases, ten primary targets and twenty-four unopened transfer instances. No reader behavior implemented.')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['inventory','output','custody','rule']:
        p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--seed',required=True);prepare(p.parse_args())
