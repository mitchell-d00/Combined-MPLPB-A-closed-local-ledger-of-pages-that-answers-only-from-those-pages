"""Freeze Bunyip source/question families and same-operator sealed transfer."""
import hashlib,html,json,random,shutil,subprocess,zipfile
from pathlib import Path
from tools.cryptid_packet_support_v4 import packet
ROOT=Path(__file__).resolve().parents[1];HOME=ROOT/'evaluation/cryptid/bunyip';BASE='ab8f73e83538d8e33e8d13df14c2f47b88054608';SEED=2026112607

def save(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def specs(transfer=False):
    r=random.Random(SEED);rows=[]
    def add(group,question,lines,witnesses,semantic=None,decision='complete',flags=None,profile='internal',note=''):
        for rendering in ['paragraphs','plain']:
            body='<article>'+''.join('<p>'+html.escape(t)+'</p>' for t in lines)+'</article>' if rendering=='paragraphs' else '<pre>'+html.escape('\n'.join(lines))+'</pre>'
            if flags and flags.get('quoted'):body='<blockquote>'+body+'</blockquote>'
            source={'id':'OFFICE-1' if group=='opening_time' else 'SRC-1','body_html':body,**{k:v for k,v in (flags or {}).items() if k!='quoted'}}
            expected={'decision':decision,'complete_witnesses':witnesses if decision=='complete' else [],'proposition':semantic or {},'literal_claim':group in {'owner','classification','opening_time'},'truth_verified':False,'qualification_fragments':(['Source-scoped reporting statement','Independent authorship'] if group in {'reported','report_negation'} else ['Source-attributed statement only','does not establish execution'] if group=='instruction' else []),'date_roles':{'writing':'April 12, 1909'} if group=='writing_date' and decision=='complete' else {},'note':note,'withholding_conditions':['wrong actor/entity/role','unproved requested truth/execution','ineligible or changed source','conditional bare fact','unresolved qualification']}
            rows.append({'question':question,'sources':[source],'profile':profile,'key':expected,'mechanism':group,'protected_operation':'Whole original question; exact relation/arguments and reporting layer; current eligible source witnesses; no inferred facts','origin':{'test':'Bunyip ordinary-language same-proposition variation','prs':[105]},'rendering':rendering,'question_group':group})
    names=[('Blue Heron Studio','Mira Stone','Amber Hollow','a community garden','Blue Heron Office'),('Cedar Vale Workshop','Tomas Reed','Silver Meadow','an artists cooperative','Cedar Vale Office')]
    if transfer:names=[('Larkspur Atelier','Vera Quinn','Willow Reach','a sculpture park','Larkspur Office')]
    for studio,owner,place,kind,office in names:
        own=owner+' owns '+studio+'.' if owner in {'Mira Stone','Vera Quinn'} else studio+' is owned by '+owner+'.'
        ownqs=[f'Who owns {studio}?',f'Who is the owner of {studio}?',f'Who does {studio} belong to?'] if not transfer else [f'To whom does {studio} belong?',f'Which person owns {studio}?']
        for q in ownqs:add('owner',q,[own],[own])
        classline=place+' is '+kind+'.'
        classqs=[f'What is {place}?',f'Is {place} {kind}?',f'What kind of place is {place}?'] if not transfer else [f'What type of place is {place}?',f'How is {place} described?']
        for q in classqs:add('classification',q,[classline],[classline])
        fields=['Name: '+office,'Opening time: 09:15']
        timeqs=['What is the Opening time of OFFICE-1?',f'When does {office} open?',f'What time does {office} open?'] if not transfer else [f'At what time does {office} open?',f'What are the opening hours of {office}?']
        for q in timeqs:add('opening_time',q,fields,fields)
    document='the estuary memorandum' if not transfer else 'the highland dispatch'
    writing=document[0].upper()+document[1:]+' was written on April 12, 1909.'
    dates=[writing,document[0].upper()+document[1:]+' was received on April 18, 1909.','The inspection occurred on March 3, 1909.','Publication date: May 2, 1909.']
    dateqs=[f'Distinguish the writing dates in {document} record.',f'On what date was {document} written?',f'When was {document} written?'] if not transfer else [f'What was the date of writing of {document}?',f'Give the date on which {document} was written.']
    for q in dateqs:add('writing_date',q,dates,[writing],{'relation':'source_event_date_inventory'})
    for negative,reporter,author,obj in [(False,'Leda Voss','Ida Keel','the cedar register'),(True,'Orin Falk','Pela Moss','the tidal notebook')]:
        if transfer:reporter,author,obj=r.choice(['Nela Frost','Arlo Penn']),r.choice(['Dara Elm','Iven Clay']),'the lantern index'
        group='report_negation' if negative else 'reported';statement=reporter+(' did not say that ' if negative else ' said that ')+author+' wrote '+obj+'.'
        prop={'relation':'source_attributed_report_content','reporter':reporter,'author':author,'object':obj,'outer_negative':negative,'embedded_content_negative':False,'inner_negative':None if negative else False,'content_asserted_by_reporter':not negative,'actual_authorship_established':False,'completion_established':False}
        qs=[f'What does {reporter} report about whether {author} wrote {obj}?',f'What did {reporter} '+('not say' if negative else 'say')+f' about {author} writing {obj}?',f'According to the record, what did {reporter} '+('not say' if negative else 'say')+f' about whether {author} wrote {obj}?'] if not transfer else [f'What did {reporter} '+('not state' if negative else 'state')+f' about whether {author} wrote {obj}?',f'According to this source, what did {reporter} '+('not report' if negative else 'report')+f' about {author} writing {obj}?']
        for q in qs:add(group,q,[statement],[statement],prop)
        if not transfer:
            for q in [f'Did {reporter} say something false about {author} writing {obj}?',f'Who actually wrote {obj}?',f'What did {reporter} not say about {author} writing {obj}?' if not negative else f'What did Other Person not say about {author} writing {obj}?']:
                add(group,q,[statement],[],decision='withhold')
        else:add(group,f'Does this establish that {author} actually wrote {obj}?',[statement],[],decision='withhold')
    instructor='Elin Cross' if not transfer else 'Nora Field';task='the northern bridge' if not transfer else 'the western beacon';team='the field team';instruction=instructor+' instructed '+team+' to inspect '+task+'.'
    prop={'relation':'source_modality_assertion','actor':instructor,'modality':'instruction','task_actor':team,'task_action':'inspect','task_object':task,'outer_negative':False,'content_negative':False,'completion_asserted_by_source':False,'execution_independently_verified':False,'conditions':[]}
    qs=[f'What instruction does the record attribute to {instructor} concerning {task}?',f'What did {instructor} instruct {team} to do concerning {task}?',f'What task did {instructor} assign to {team} concerning {task}?'] if not transfer else [f'What directions did {instructor} give {team} about {task}?',f'What did {instructor} tell {team} to do about {task}?']
    for q in qs:add('instruction',q,[instruction],[instruction],prop)
    add('instruction',f'Did {team} inspect {task}?',[instruction],[],decision='withhold')
    if not transfer:
        add('instruction',f'What did {instructor} instruct the inland team to do concerning {task}?',[instruction],[],decision='withhold')
        add('instruction',qs[0],[instruction],[],decision='withhold',flags={'external':'no'},profile='external')
    studio,owner,place,kind,office=names[0];own=owner+' owns '+studio+'.';classline=place+' is '+kind+'.'
    controls=[('owner',f'Who does Unknown Studio belong to?',[own],None),('owner',f'Who does {studio} belong to?',[owner+' does not own '+studio+'.'],None),('owner',f'Who does {studio} belong to?',[own],{'quoted':True}),('classification',f'Is {place} a railway station?',[classline],None),('classification',f'What kind of place is {place}?',[place+' is not '+kind+'.'],None),('classification',f'What kind of place is {place}?',['If the permit is approved, '+classline[0].lower()+classline[1:]],None),('opening_time',f'When does {office} open?',['Name: '+office,'Closing time: 09:15'],None),('opening_time',f'When does {office} open?',['Name: Other Office','Opening time: 09:15'],None),('opening_time',f'When does {office} open?',['Name: '+office,'Opening time: 09:15 only if approved'],None),('writing_date',f'When was {document} written?',[dates[1]],None),('writing_date','When was the absent memorandum written?',dates,None),('writing_date',f'When was {document} written?',['If approved, '+writing[0].lower()+writing[1:]],None)]
    for group,q,lines,flags in controls if not transfer else controls[2:3]+controls[3:4]+controls[6:7]+controls[9:10]:add(group,q,lines,[],decision='withhold',flags=flags)
    return rows

def main():
    HOME.mkdir(exist_ok=False)
    packet(HOME/'development','BUNYIP',specs(),BASE,'tools/bunyip_packets.py')
    for folder in [HOME/'development']:
        reg=json.loads((folder/'registry.json').read_text());ss=specs()
        for row,s in zip(reg['cases'],ss):row.update(rendering=s['rendering'],question_group=s['question_group'])
        save(folder/'registry.json',reg);freeze=json.loads((folder/'freeze.json').read_text());freeze['registry_sha256']=sha(folder/'registry.json');freeze['harness']['tools/bunyip_score.py']=sha(ROOT/'tools/bunyip_score.py');save(folder/'freeze.json',freeze)
    stage=Path('/workspace/cryptid-custody/bunyip-sealed-build');packet(stage,'BUNYIP',specs(True),BASE,'tools/bunyip_packets.py',held=True)
    reg=json.loads((stage/'registry.json').read_text())
    for row,s in zip(reg['cases'],specs(True)):row.update(rendering=s['rendering'],question_group=s['question_group'])
    save(stage/'registry.json',reg);freeze=json.loads((stage/'freeze.json').read_text());freeze['registry_sha256']=sha(stage/'registry.json');freeze['harness']['tools/bunyip_score.py']=sha(ROOT/'tools/bunyip_score.py');save(stage/'freeze.json',freeze)
    with zipfile.ZipFile(HOME/'transfer-sealed.zip','x',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(stage.rglob('*')):
            if p.is_file():z.write(p,str(p.relative_to(stage)))
    save(HOME/'transfer-seal.json',{'packet_sha256':sha(HOME/'transfer-sealed.zip'),'seed':SEED,'generator_sha256':sha(Path(__file__)),'cases':len(specs(True)),'custody':'Same operator, visible generator templates. Instance/key bytes not reopened after preparation until committed candidate ZIP. No independent preparation/blinding/adjudication.','opening':'NOT_RUN'});shutil.rmtree(stage)
    save(HOME/'protocol.json',{'baseline_main':'c01021c0b9983f9a607fbe782dea7ed5872d1f11','baseline_candidate':BASE,'falsifiable_mechanism':'Equivalent ordinary questions fail to preserve a requested relation and its arguments when proposing an existing proof operation; unsupported truth/execution and altered roles must never be normalized away. Source syntax/layout failures are measured separately.','acceptance':'Verified source-supported gains in ordinary wording; no lost valid support, no new unsupported claims, preserved complete qualifications/citations and required software gates pass. Remaining coverage misses are reported and do not alone prohibit an incremental release.','source_renderings':'Same statement lines: separate HTML paragraphs versus newline-preserving plain pre. Report separately; do not treat layout repeats as unique recovered questions.','budgets':'unchanged8records/200000chars/1000units/12passages/8000output;workerCPU30/wall45','independent_historical_semantic':'NOT_RUN','human_execution':'NOT_RUN'})
    print('Frozen',len(specs()),'development executions and',len(specs(True)),'sealed transfer executions')
if __name__=='__main__':main()
