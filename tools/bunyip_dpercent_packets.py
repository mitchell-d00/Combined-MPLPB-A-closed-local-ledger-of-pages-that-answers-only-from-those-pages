"""Bunyip packet authoring only: unchanged D% worker/runner and existing scorer.

Dice Bag custody: seal public inputs and separate key; replay original questions
before reveal. D20 matched conditions are unique/competing/missing/retired.
Fresh wording is separately written here, same operator, never independent.
"""
import argparse
from pathlib import Path
from tools import dpercent as D

def prepare(public, custody, *, transfer=False):
    public=Path(public);custody=Path(custody)
    assert not public.exists() and not custody.exists()
    assert D.ROOT not in custody.resolve().parents
    public.mkdir(parents=True);custody.mkdir(parents=True,mode=0o700)
    studio,owner,place,office,actor,team,task=(
        ('Copper Fern Workshop','Selene Marsh','Larch Hollow','Cedar Office','Anika West','the survey team','the eastern pier') if not transfer else
        ('Silver Reed Studio','Tarin Beck','Willow Common','Meadow Office','Petra Lane','the coastal crew','the northern quay'))
    canon={
        'ownership':f'Who owns {studio}?',
        'classification':f'What is {place}?',
        'opening':f'When does {office} open?',
        'instruction':f'What instruction does the record attribute to {actor} concerning {task}?'}
    development={
        'ownership':[f'Who is {studio} owned by?',f'Whose property is {studio}?',f'Which person is the owner of {studio}?'],
        'classification':[f'How would you classify {place}?',f'What category does {place} fall into?',f'What type of place is {place}?'],
        'opening':[f'What is the opening time of {office}?',f'What is the opening time for {office}?',f'What time is listed for {office} to open?'],
        'instruction':[f'What directions did {actor} give {team} about {task}?',f'What did {actor} tell {team} to do about {task}?',f'What task did {actor} assign to {team} concerning {task}?']}
    # Different interrogative structures, not new names within the above forms.
    fresh={
        'ownership':[f'According to this record, whose property is {studio}?',f'Who, according to the source, owns {studio}?'],
        'classification':[f'In this record, how would you classify {place}?',f'Under what category is {place} described?'],
        'opening':[f'According to the source, what time is listed for {office} to open?',f'At which time does {office} open?'],
        'instruction':[f'According to this source, what directions did {actor} give {team} about {task}?',f'Which task did {actor} give {team}?']}
    bodies={'ownership':[f'{owner} owns {studio}.'],'classification':[f'{place} is a community garden.'],
            'opening':[f'Name: {office}','Opening time: 08:35'],
            'instruction':[f'{actor} instructed {team} to inspect {task}.']}
    competitors={'ownership':[f'Other Person owns {studio}.'],'classification':[f'{place} is a railway station.'],
                 'opening':[f'Name: {office}','Opening time: 10:20'],
                 'instruction':[f'{actor} did not instruct {team} to inspect {task}.']}
    keys=[];pairs=[];number=0;total=0;source_files=0
    def add(family,q,lines,condition,layout,form):
        nonlocal number,total,source_files
        number+=1;ident=f'DP{number:05d}';folder=public/'packets'/ident
        sources=[];facts=[]
        contents=[lines]
        if condition=='competing':contents.append(competitors[family])
        if condition=='missing':contents=[['Inventory paperwork was scanned.']]
        for i,body in enumerate(contents,1):
            # Plain contiguous fields versus paragraph-separated statements.
            # The unchanged worker imports both as preformatted source text.
            text=('\n' if layout=='lines' else '\n\n').join(body)+'\n'
            path=f'sources/record-{i}.txt';p=folder/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
            source={'path':path,'source_class':'original'}
            if condition=='retired':source['retired']=True
            sources.append(source);total+=len(text.encode());source_files+=1
            facts.append({'source_id':f'SOURCE-{i:04d}','path':path,'evidence_text':text.strip(),'source_class':'original','raw_quote':text})
        D.save(folder/'case.json',{'id':ident,'question':q,'profile':'internal','sources':sources,'budget':{'passages':12,'characters':8000}})
        positive=condition=='unique';props=[]
        if family=='instruction':props=[{'relation':'source_modality_assertion','actor':actor,'modality':'instruction','task_actor':team,'task_action':'inspect','task_object':task,'completion_asserted_by_source':False,'execution_independently_verified':False}]
        keys.append({'id':ident,'family':family,'expected':'answer' if positive else 'refuse','required_propositions':props,
                     'reference_sources':['SOURCE-0001'] if positive else [],'source_facts':facts,'structural_expectations':{},
                     'automatic_answer_matcher':'typed_proposition_v1' if props else 'literal_field_set_v1',
                     'required_field_quotes':[('\n'.join(lines))],
                     'features':{'question_form':form,'field':family,'line_ending':'LF','fence':layout,'source_count':len(sources)}})
        pairs.append({'id':ident,'stable_id':f'CRYPT-BUNYIP-DP-{ "T" if transfer else "D"}{number:04d}',
                      'family':family,'question':q,'canonical_question':canon[family],'form':form,'layout':layout,'condition':condition,
                      'source_files_sha256':{s['path']:D.sha((folder/s['path']).read_bytes()) for s in sources},
                      'origin':'PR105 Bunyip, D% worker, Dice Bag custody and D20 matched conditions',
                      'protected_operation':'Original-question relation/arguments plus eligible exact witnesses; no execution promotion',
                      'expected_qualifications':'Instruction only; completion and independently verified truth remain unestablished' if family=='instruction' else 'Literal source assertion only; independently verified truth unestablished'})
    for family in canon:
        forms=[canon[family]]+(fresh if transfer else development)[family]
        for layout in ['lines','paragraphs']:
            for i,q in enumerate(forms):
                for condition in ['unique','competing','missing','retired']:add(family,q,bodies[family],condition,layout,'canonical' if i==0 else f'ordinary-{i}')
    # Whole-question contrasts: no normalized-away extra obligations or modifiers.
    for family in canon:
        for suffix in [' before May 2',' and who verified it',' if the permit is approved']:
            add(family,canon[family].rstrip('?')+suffix+'?',bodies[family],'qualified_request','lines','unsupported-extra')
    D.save(custody/'key.json',{'schema':'bunyip-dpercent-key-v1','cases':keys})
    D.save(custody/'dice.json',{'sampling':'Fixed fully enumerated authored matrix; no random draw or new-seed transfer claim','seed':None,'rolls':[]})
    D.save(custody/'pairing.json',{'cases':pairs,'same_operator':True,'separately_authored_wording':transfer,'independent_preparation':'NOT_RUN','independent_blinding':'NOT_RUN'})
    D.save(public/'protocol.json',{'cases':number,'limits':D.LIMITS,'worker':'tools/dpercent_worker.py','runner':'tools/dpercent.py','scorer':'tools/dpercent_expanded.py',
        'source_kind':'Authored synthetic source assertions','exposure':'separately authored transfer structures, same operator; visible source authoring code' if transfer else 'exposed development',
        'original_question_is_scored_target':True,'canonical_diagnostic_is_not_recovery':True,'layouts':'Text line/paragraph separation inside unchanged preformatted D% import; not a structured-HTML coverage claim'})
    seal={'public_files':D.files(public),'key_sha256':D.sha((custody/'key.json').read_bytes()),'dice_sha256':D.sha((custody/'dice.json').read_bytes()),
          'generator_sha256':D.sha(Path(__file__).read_bytes()),'worker_sha256':D.sha((D.ROOT/'tools/dpercent_worker.py').read_bytes()),
          'pairing_sha256':D.sha((custody/'pairing.json').read_bytes()),'source_bytes':total,'source_files':source_files}
    D.save(public/'seal.json',seal);D.save(custody/'public-seal-copy.json',seal)
    return seal

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--custody',type=Path,required=True);p.add_argument('--transfer',action='store_true');a=p.parse_args()
    print(prepare(a.out,a.custody,transfer=a.transfer))
