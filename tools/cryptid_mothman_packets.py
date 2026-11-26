"""Same-operator date-role development and sealed transfer preparation, seed 2026112502."""
import hashlib
import html
import json
from pathlib import Path
import shutil
import zipfile
from tools.cryptid_trial import ROOT, save, sha, snapshot, digest

HOME=ROOT/'evaluation/cryptid/mothman'
BASE='c01021c0b9983f9a607fbe782dea7ed5872d1f11'
BUDGET={'cpu_seconds':30,'wall_seconds':45,'records':8,'scan_characters':200000,'units':1000,'passages':12,'characters':8000}
TOOLS=['tools/cryptid_trial.py','tools/cryptid_score.py','tools/cryptid_mothman_packets.py','tools/bubble_wrap_adapter.py','tools/bubble_wrap_worker.py','tools/pole_worker.py','tools/study_sandbox.py']


def build(folder,held=False):
    rows=[];key={}
    def add(question,bodies,expected=None,origin=None,withdraw=False):
        ident='CRYPT-MOTHMAN-'+('T' if held else '')+f'{len(rows)+1:04d}'
        packet=folder/'inputs'/ident
        if origin:
            source=ROOT/'evaluation/current-failure-inventory'/origin['input_path'];shutil.copytree(source,packet)
            assert snapshot(packet)==origin['files']
        else:
            sources=[{'id':f'DOC-{i+1}','body_html':b,'withdraw':withdraw} for i,b in enumerate(bodies)]
            save(packet/'case.json',{'id':ident,'adapter_mode':'documentary','question':question,'sources':sources,'budget':{'passages':12,'characters':8000},'profile':'internal','discovery':True})
        k={'decision':'answer' if expected else 'withhold','expected_date_links':expected or [],'required_qualifications':['source_attributed_dates','year_not_inherited','no_transmission_or_event_from_writing','historical_truth_not_verified'],'withholding_conditions':['role_not_explicit','nonunique_owner','quoted_or_conditional_or_negated_event','ineligible_or_changed_source']}
        key[ident]=k
        rows.append({'id':ident,'family':'MOTHMAN','packet':str(packet.relative_to(ROOT)) if not held else 'inputs/'+ident,
                     'files':snapshot(packet),'semantic_input_hash':digest({'question':question,'files':snapshot(packet)}),
                     'origin':origin or {'test':'fresh same-operator contrasting date-role examples','prs':[103,104]},
                     'mechanism':'Explicit date roles are absent from planning and writing-date proof; role distinctions must be witnessed.',
                     'protected_operation':'Complete question -> explicit date roles -> eligible complete source scan -> exact witnesses',
                     'baseline_commit':BASE,'budgets':BUDGET,'expected_key_id':ident,'candidate':'NOT_RUN','custody':'same-operator; no independent preparation/blinding/adjudication','raw_output_lookup':'runs/RUN/'+ident+'/result.json','score_lookup':'scores/RUN.json'})
    if not held:
        selection=json.loads((ROOT/'evaluation/current-failure-inventory/selection.json').read_text())
        dates=[('September 22, 1840','September 25, 1840'),('September 29, 1845','October 02, 1845'),('November 29, 1845','December 02, 1845'),('May 20, 1847','May 23, 1847'),('October 17, 1847','October 20, 1847')]
        for c,(sent,written) in zip([c for c in selection['cases'] if c['family']=='date_roles'],dates,strict=True):
            case=json.loads((ROOT/'evaluation/current-failure-inventory'/c['input_path']/'case.json').read_text())
            add(case['question'],[],[['sending',sent,int(sent[-4:])],['writing',written,int(written[-4:])]],origin=c)
        task='the cedar memorandum';base='On March 4, 1862, Mara Ellis sent '+task+'. This record was written on March 7, 1862.'
        q='Distinguish the reported sending date and the writing date for '+task+'.'
        add(q,['<pre>'+base+'</pre>'],[['sending','March 4, 1862',1862],['writing','March 7, 1862',1862]])
        specs=[('writing','This record was written on April 6, 1870.','April 6, 1870',1870),('writing','This record was written on April 6.','April 6',None),('sending','On April 7, 1870, Mara Ellis sent the cedar memorandum.','April 7, 1870',1870),('receipt','On April 8, 1870, Tessa Crane received the cedar memorandum.','April 8, 1870',1870),('publication','On April 9, 1870, The coastal press published the cedar memorandum.','April 9, 1870',1870),('review','This page was last reviewed on April 10, 1870.','April 10, 1870',1870),('catalogue','Citation: Memorandum; April 11, 1870; the cedar memorandum.','April 11, 1870',1870)]
        for role,statement,date,year in specs:
            content='<p>The cedar memorandum is retained in this record.</p><p>'+statement+'</p>'
            add('Distinguish the '+role+' dates in the cedar memorandum record.',[content],[[role,date,year]])
        add('Distinguish the arrival and departure dates in the cedar memorandum record.',['<p>On April 12, 1870, Mara Ellis arrived at the cedar memorandum office.</p><p>On April 13, 1870, Mara Ellis departed the cedar memorandum office.</p>'],[['arrival','April 12, 1870',1870],['departure','April 13, 1870',1870]])
        add('Distinguish the surrender and evacuation dates in the cedar fort record.',['<p>On April 14, Mara Ellis surrendered the cedar fort, evacuating the fort on the following day.</p>'],[['surrender','April 14',None],['evacuation','the following day',None]])
        add(q,['<p>On March 4, 1862, Mara Ellis sent the cedar memorandum.</p><p>This record was written on March 7, 1862.</p><p>This page was last reviewed on May 1, 2025.</p>'],[['sending','March 4, 1862',1862],['writing','March 7, 1862',1862]])
        for content in ['<p>The cedar memorandum.</p><blockquote>'+base+'</blockquote>',
                        '<p>The cedar memorandum.</p><p>Example: '+base+'</p>',
                        '<p>The cedar memorandum.</p><p>If approval is granted.</p><p>'+base+'</p>',
                        '<p>On March 4, 1862, Mara Ellis did not send the cedar memorandum. This record was written on March 7, 1862.</p>',
                        '<p>On March 4, 1862, Mara Ellis planned to send the cedar memorandum. This record was written on March 7, 1862.</p>',
                        '<p>'+base+' This record was written on March 8, 1862.</p>',
                        '<p>Date: March 7, 1862. The cedar memorandum.</p>',
                        '<p>On March 4, 1862, Mara Ellis sent the cedar memorandum. This page was last reviewed on March 7, 1862.</p>']:
            add(q,[content])
        add(q,['<p>'+base+'</p>'],withdraw=True)
        add(q,['<p>'+base+'</p>','<p>On March 5, 1862, Mara Ellis sent the cedar memorandum. This record was written on March 8, 1862.</p>'])
        add('Distinguish the sending and receipt dates in the cedar memorandum record.',['<p>The cedar memorandum. This record was written on March 7, 1862.</p>'])
        add('Distinguish the writing dates in the cedar memorandum record, and prove that the voyage occurred.',['<p>The cedar memorandum. This record was written on March 7, 1862.</p>'])
    else:
        # These sentence structures are not the development templates. Actor/task
        # substitutions alone would not constitute this limited transfer test.
        for noun,day in [('amber survey',16),('marsh log',21)]:
            for role,statement in [('writing',f'The {noun} was written on June {day}, 1884.'),('sending',f'The {noun} was sent on June {day}, 1884.'),('receipt',f'The {noun} was received on June {day}, 1884.'),('publication',f'The {noun} was published on June {day}, 1884.')]:
                question=f'Distinguish the {role} dates in the {noun} record.'
                add(question,['<p>'+statement+'</p>'],[[role,f'June {day}, 1884',1884]])
                add(question,['<p>The '+noun+'.</p><blockquote>'+statement+'</blockquote>'])
    save(folder/'registry.json',{'schema':'cryptid-case-registry-v1','family':'MOTHMAN','exposure':'same-operator generated; templates visible; exact transfer case bytes unopened after sealing until committed candidate' if held else 'development fully exposed; five original frozen cases unchanged','cases':rows})
    save(folder/'key.json',key)
    save(folder/'freeze.json',{'generator_seed':2026112502,'registry_sha256':sha(folder/'registry.json'),'key_sha256':sha(folder/'key.json'),'harness':{p:sha(ROOT/p) for p in TOOLS},'baseline_reader_commit':BASE,'independence':'NOT_RUN'})


def main():
    HOME.mkdir(parents=True,exist_ok=False);build(HOME/'development')
    held=Path('/workspace/cryptid-custody/mothman-sealed-build');build(held,True)
    with zipfile.ZipFile(HOME/'transfer-sealed.zip','x',compression=zipfile.ZIP_DEFLATED) as z:
        for p in sorted(held.rglob('*')):
            if p.is_file():z.write(p,str(p.relative_to(held)))
    save(HOME/'transfer-seal.json',{'packet_sha256':sha(HOME/'transfer-sealed.zip'),'cases':16,'preparation':'same-operator program-generated; templates visible, no independence claim','packet_opened_after_preparation':False,'open_after':'committed candidate ZIP freeze','generator_seed':2026112502})
    shutil.rmtree(held)
    print('Frozen development and sealed transfer; transfer bytes not reopened.')

if __name__=='__main__':main()
