"""D%: original randomized prose challenges, sealed scoring, isolated execution.

Synthetic source-assertion tests, not real historical accuracy or human review.
No runtime answer engine is modified or supplied with expected outcomes.
"""
import argparse
from collections import Counter
from datetime import date, timedelta
import hashlib
import json
from pathlib import Path
import platform
import random
import secrets
import shutil
import subprocess
import sys
import tempfile
import textwrap
import time

ROOT=Path(__file__).resolve().parents[1]
VERSION='dpercent-v1'
ACTORS=('Mira Vale','Ivo Hart','Nora Wells','Tess Rowan','Edda Marén','Owen Pike','Lea Stone','Arun Moss','Mina Cole','Iris Beck','May Reed','Noel Ash')
OBJECTS=('alder memorandum','harbor report','canal register','copper survey report','northern field notebook','orchard inventory','coastal dispatch','museum catalogue')
LAYOUTS=('letter','mail','plain','markdown')
# The family changes semantics, not just a name. No word/grammar acceptance filter.
FAMILIES={
 'exact_anchor':'answer','header_location':'answer','direct_action':'answer','passive_action':'answer','reported_statement':'answer','negated_statement':'answer',
 'instruction_statement':'answer','explicit_cause':'answer','date_roles':'answer','wording_change':'answer',
 'partial_correction':'answer','earliest_observed':'answer','explicit_chain':'answer','identical_wording':'answer','editorial_competition':'answer',
 'negated_execution':'refuse','conditional_execution':'refuse','intention_execution':'refuse','reported_execution':'refuse',
 'chronology_causation':'refuse','subject_identity':'refuse','ambiguous_pronoun':'refuse','missing_bridge':'refuse',
 'ambiguous_correction':'refuse','competing_accounts':'refuse','restricted_source':'refuse','corrupted_source':'refuse',
 'withdrawn_source':'refuse','absent_anchor':'refuse','embedded_identifier':'refuse','historical_priority':'refuse'}
LIMITS={'cases':4096,'packet_bytes':128*1024**2,'files':100000,'result_bytes':8*1024**2,'total_result_bytes':256*1024**2,'wall_seconds':45}
# All these dimensions produce distinct layouts/questions, independently of names.
STRUCTURAL_COMBINATIONS=len(FAMILIES)*2*3*3*3  # Conservative design cells;excludes actor/date/layout/wrapping expansion.


def sha(raw):return hashlib.sha256(raw).hexdigest()
def read(path):
    from mplpb_answers.evidence_contract import loads
    return loads(Path(path).read_text())
def save(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x',encoding='utf-8') as stream:json.dump(value,stream,indent=2,ensure_ascii=False,allow_nan=False);stream.write('\n')
def files(root):
    return {str(p.relative_to(root)):sha(p.read_bytes()) for p in sorted(Path(root).rglob('*')) if p.is_file()}


class Dice:
    def __init__(self,seed):self.rng=random.Random(seed);self.rolls=[]
    def choose(self,label,values):
        # Rejection sampling: no modulo bias and no source-language filtering.
        width=1
        while 100**width<len(values):width+=1
        ceiling=100**width//len(values)*len(values)
        while True:
            digits=[self.rng.randrange(100)+1 for _ in range(width)];n=0
            for digit in digits:n=n*100+digit-1
            self.rolls.append({'chart':label,'rolls':digits,'accepted':n<ceiling})
            if n<ceiling:return values[n%len(values)]

    def shuffle(self,label,values):
        pool=list(values);result=[]
        while pool:
            i=self.choose(label,tuple(range(len(pool))));result.append(pool.pop(i))
        return result


def case_material(number,family,dice):
    actor=dice.choose('actor',ACTORS);other=dice.choose('other_actor',tuple(a for a in ACTORS if a!=actor))
    obj=dice.choose('subject',OBJECTS);layout=dice.choose('layout',LAYOUTS);newline=dice.choose('line_ending',('\n','\r\n'))
    extension=dice.choose('extension',('.txt','.md','.text'));width=dice.choose('wrapping',(0,31,57,79))
    query=dice.choose('question_structure',(0,1,2));noise=dice.choose('distractor_count',(1,3,7));variant=dice.choose('scope_structure',(0,1,2))
    when=date(1840,1,1)+timedelta(days=dice.choose('date_offset',tuple(range(3600))))
    written=when.strftime('%B %d, %Y');event=(when-timedelta(days=3)).strftime('%B %d, %Y')
    third=dice.choose('third_actor',tuple(a for a in ACTORS if a not in (actor,other)))
    message='MAIL-'+str(10000+number);old,new=dice.choose('quantities',(('twelve','fourteen'),('six','nine'),('twenty','seventeen')))
    action=f'{actor} wrote the {obj}.';texts=[];refs=[];propositions=[];policy={};structural={}
    def add(text,reference=True,**extra):
        index=len(texts)+1;texts.append({'text':text,'source_class':'original',**extra})
        if reference:refs.append(index)
        return index
    who=(f'Who wrote the {obj}?',f'According to the record, who wrote the {obj}?',f'Which writer does the record identify for the {obj}?')[query]
    question=who
    if family=='exact_anchor':
        add(action+' The harbor lantern remained lit beneath the northern awning.')
        question='Which source contains the exact words \"The harbor lantern remained lit beneath the northern\"? Locate the words only.'
    elif family=='header_location':
        layout='mail';add(action);question=f'Which record is from {actor}, to {other}, written on {written}? Locate the complete header.'
    elif family in {'direct_action','editorial_competition'}:
        add(action);propositions=[{'relation':'source_action_assertion','actor_text':actor,'action':'write','object_text':'the '+obj,'negative':False}]
        if family=='editorial_competition':
            for _ in range(3):add(f'Editorial speculation: {other} might have written the {obj}, although this is not established.',False,source_class='commentary')
    elif family=='passive_action':
        add(f'The {obj} was written by {actor}.');propositions=[{'actor_text':actor,'action':'write','object_text':'The '+obj,'negative':False}]
    elif family=='reported_statement':
        add((f'{other} reported that {actor} wrote the {obj}.',f'{other} said, "{actor} wrote the {obj}."',f'According to {other}, {actor} wrote the {obj}.')[variant])
        question=f'What does {other} report about the writer of the {obj}, without independently verifying the event?'
    elif family=='negated_statement':
        add(f'{actor} did not write the {obj}.');question=f'What does the record deny about {actor} and the {obj}?'
        propositions=[{'relation':'source_action_assertion','actor_text':actor,'action':'write','object_text':'the '+obj,'negative':True}]
    elif family=='instruction_statement':
        layout='mail'  # The question requires an explicit writer and addressee.
        add(f'I have told {third} to send you a copy of the {obj} by post (if possible).')
        question=f'What arrangement does the dated letter from {actor} to {other} state, without asserting delivery?'
    elif family=='explicit_cause':
        add(f'The inspection was canceled because of damage to the bridge.');question='According to the report, why was the inspection canceled?'
        propositions=[{'relation':'source_causal_assertion','action_text':'canceled','cause_text':'damage to the bridge','negative':False}]
    elif family=='date_roles':
        add(f'On {event}, {actor} sent the {obj}. This record was written on {written}.')
        question=f'Distinguish the reported sending date and the writing date for the {obj}.'
    elif family=='wording_change':
        add(f'The notice describes {old} crates for the east depot.');add(f'The notice describes {new} crates for the east depot.')
        question='Compare the two notices: which quantity wording differs and which destination wording is identical?'
    elif family=='partial_correction':
        add(f'This letter was written on {event}. The consignment contains {old} crates for the east depot.',_date=event)
        add(f'In my letter of {event}, the count should read {new} crates. The destination remains the east depot.')
        question='What count does the later statement correct, and which destination does it retain?'
    elif family=='earliest_observed':
        add(f'This record was written on {event}. I recorded an idea about the {obj}.',_date=event)
        add(f'This record was written on {written}. I recorded an idea about the {obj}.')
        question='Which writing date is earliest among these two records? Do not infer who conceived the idea first in history.'
    elif family=='explicit_chain':
        add(f'On {event}, {actor} asked {other} to send the {obj} to the east depot.')
        add(f'In response to that request of {event}, I, {other}, sent the {obj} to the east depot.',_writer=other,_recipient=actor)
        add(f'The east depot reported receiving the {obj} sent by {other} in response to the request of {event}.')
        question='According to these records, trace the explicitly linked request, dispatch and reported receipt. Preserve attribution.'
    elif family=='identical_wording':
        add(action);add(action);question='Do the two documentary appearances contain identical wording? Compare text only, not event identity.'
        structural={'same_body':[[1,2]]}
    elif family=='negated_execution':add(f'{actor} did not send the {obj}.');question=f'Which record establishes that {actor} sent the {obj}?'
    elif family=='conditional_execution':
        add((f'If the permit arrives, {actor} will send the {obj}.',f'{actor} would send the {obj} only if the permit arrived.',f'Unless the permit is denied, {actor} may send the {obj}.')[variant]);question=f'Which record establishes completed delivery of the {obj}?'
    elif family=='intention_execution':
        add((f'{actor} planned to send the {obj}.',f'{actor} hoped to send the {obj}.',f'{actor} asked {other} to send the {obj}.')[variant]);question=f'Was the proposed sending of the {obj} carried out? Establish execution.'
    elif family=='reported_execution':
        add(f'{other} claimed that {actor} sent the {obj}; the register contains no independent receipt.')
        question=f'What independently verifies completed delivery of the {obj}, beyond the reported claim?'
    elif family=='chronology_causation':
        add('The lamp went out before the departure bell rang.');question='Establish that the lamp going out caused the departure bell to ring.'
    elif family=='subject_identity':
        add(f'{actor} described an inspection of the east depot.');add(f'{other} described an inspection of the west depot.')
        question='Establish that these two records with the same subject describe one and the same inspection event.'
        structural={'forbid_event_merge':True}
    elif family=='ambiguous_pronoun':
        add(f'{actor} met {other}. They discussed the {obj}. He sent it that evening.')
        question=f'Identify with certainty which of the two people sent the {obj}.'
    elif family=='missing_bridge':
        add(f'{actor} asked {other} to send the {obj}.');add(f'The depot reported receiving a copy of the {obj}, but the sender was not recorded.')
        question=f'Establish that {other} executed this request and caused that recorded receipt, including the missing dispatch link.'
    elif family=='ambiguous_correction':
        add(f'My earlier letter lists {old} crates for the east depot.');add(f'My earlier letter lists {old} crates for the west depot.')
        add(f'My earlier letter is mistaken; the count should read {new}.')
        question='Identify exactly which earlier letter is corrected and which destination is affected.'
    elif family=='competing_accounts':
        add(f'{actor} wrote the {obj}.');add(f'{other} wrote the {obj}.');question=f'Which competing writer account about the {obj} is historically true? Establish one as correct.'
    elif family=='restricted_source':
        add(action,external='no');policy={'profile':'external'};question=who
    elif family=='corrupted_source':add(action,corrupt=True);question=who
    elif family=='withdrawn_source':add(action,retired=True);question=who
    elif family=='absent_anchor':
        add(action,False);question=f'Which source establishes the nonexistent ZQX{number:06d} claim?'
    elif family=='embedded_identifier':
        add(action);add(action);add('Documentation example, not another communication.\n```text\nMessage-ID: '+message+'\n'+action+'\n```',False,source_class='commentary')
        question='Establish that all three appearances are three independent communications and corroborating events.'
        structural={'embedded_not_primary':3}
    elif family=='historical_priority':
        add(f'On {written}, {actor} recorded an idea about the {obj}.');question=f'Prove that {actor} was the first person anywhere to conceive this idea, using only this record.'
    else:raise ValueError('Unknown case family')
    sources=[];key_sources=[]
    for i,item in enumerate(texts,1):
        body=item.pop('text');writer=item.pop('_writer',actor);recipient=item.pop('_recipient',other);dateline=item.pop('_date',written)
        if layout=='letter':prefix=f'{writer.upper()} TO {recipient.upper()}. {dateline}\nDear colleague,\n\n'
        elif layout=='mail':prefix=f'From: {writer}\nTo: {recipient}\nDate written: {dateline}\nSubject: Archive notice\nMessage-ID: {message}\n\n'
        elif layout=='markdown':prefix=f'# Archival transcript\n\nWritten {dateline}.\n\n'
        else:prefix=''
        # Illustrations retain their own explicit quotation/example scope.
        if family=='embedded_identifier' and i==3:prefix=''
        elif family in {'wording_change','subject_identity','identical_wording'}:
            prefix=f'From: {actor}\nTo: {other}\nDate written: {written}\nSubject: Archive notice\nMessage-ID: {message if family!="subject_identity" else message+str(i)}\n\n'
        if width:body='\n'.join(textwrap.fill(line,width=width,break_long_words=False,break_on_hyphens=False) if line and not line.startswith(('```','Message-ID:')) else line for line in body.split('\n'))
        text=(prefix+body+'\n').replace('\n',newline)
        source={'path':f'sources/record-{i:02d}{extension}',**item};sources.append((source,text.encode()))
        key_sources.append({'source_id':f'SOURCE-{i:04d}','path':source['path'],'raw_quote':text,'evidence_text':body,'source_class':source['source_class']})
    for i in range(noise):
        text=f'Inventory leaf {i+1}. The archive cupboard held a woolen cover beside an unrelated register. No dispatch is recorded here.\n'
        source={'path':f'sources/inventory-{i:02d}.txt','source_class':'original'};sources.append((source,text.encode()))
    profile=policy.get('profile',dice.choose('profile',('internal','lab')))
    # Question wrappers alter syntax, never discard difficult words or cases.
    if family not in {'direct_action','restricted_source','corrupted_source','withdrawn_source'}:
        question=('Please assess this from the provided records: '+question if query==1 else
                  question+' Keep unknown matters unresolved.' if query==2 else question)
    case={'id':f'DP{number:05d}','question':question,'profile':profile,'sources':[s for s,_ in sources],
          'budget':{'passages':12,'characters':8000}}
    key={'id':case['id'],'family':family,'expected':FAMILIES[family],
         'required_propositions':propositions,'reference_sources':[f'SOURCE-{i:04d}' for i in refs] if family not in {'restricted_source','corrupted_source','withdrawn_source'} else [],
         'source_facts':key_sources,'structural_expectations':structural,
         'answer_scope':'What the eligible fictional records establish,not independently verified historical truth.',
         'automatic_answer_matcher':'typed_proposition_v1' if propositions else 'quotation_location' if family=='exact_anchor' else 'requires_semantic_review',
         'literal_anchor':'The harbor lantern remained lit beneath the northern' if family=='exact_anchor' else None}
    return case,sources,key


def prepare(out,custodian,*,count=112,seed=None):
    out=Path(out).resolve();custodian=Path(custodian).resolve()
    if type(count) is not int or not 1<=count<=LIMITS['cases']:raise ValueError('Cases must be1–4096')
    if out==custodian or out in custodian.parents or custodian in out.parents:raise ValueError('Keep key and packets in disjoint directories')
    if custodian==ROOT or ROOT in custodian.parents:raise ValueError('Keep the private scoring key outside the repository')
    seed=secrets.randbits(128) if seed is None else seed
    if type(seed) is not int or not 0<=seed<2**128:raise ValueError('Seed must be a128-bit nonnegative integer')
    out.mkdir(parents=True,exist_ok=False);custodian.mkdir(mode=0o700,parents=True,exist_ok=False)
    dice=Dice(seed);schedule=[list(FAMILIES)[i%len(FAMILIES)] for i in range(count)]
    schedule=dice.shuffle('family_schedule',schedule);keys=[];total=0;file_count=0
    for i,family in enumerate(schedule,1):
        case,documents,key=case_material(i,family,dice);folder=out/'packets'/case['id'];folder.mkdir(parents=True)
        for source,raw in documents:
            total+=len(raw);file_count+=1
            if total>LIMITS['packet_bytes'] or file_count>LIMITS['files']:raise ValueError('Generated packet budget exceeded;partial preparation retained')
            p=folder/source['path'];p.parent.mkdir(exist_ok=True);p.write_bytes(raw)
        save(folder/'case.json',case);keys.append(key)
    save(custodian/'key.json',{'schema':VERSION+'-key','cases':keys});(custodian/'key.json').chmod(0o600)
    save(custodian/'dice.json',{'seed':str(seed),'rolls':dice.rolls,'sampling':'Stratified family coverage;unbiased d100 table selection,rejection sampling,no grammar filters.'})
    save(out/'protocol.json',{'schema':VERSION,'cases':count,'source_kind':'Original developer-authored fictional prose;not authentic historical documents.',
                            'structural_combination_lower_bound':STRUCTURAL_COMBINATIONS,
                            'structural_dimensions':{'families':len(FAMILIES),'layouts':4,'line_endings':2,'extensions':3,'wrapping':4,'question_structures':3,'distractor_counts':3},
                            'no_language_acceptance_filter':True,'limits':LIMITS,'independent_validation':'NOT RUN'})
    seal={'schema':VERSION+'-seal','public_files':files(out),'key_sha256':sha((custodian/'key.json').read_bytes()),
          'dice_sha256':sha((custodian/'dice.json').read_bytes()),'generator_sha256':sha(Path(__file__).read_bytes()),
          'worker_sha256':sha((ROOT/'tools/dpercent_worker.py').read_bytes()),'seed_commitment':sha(str(seed).encode()),
          'source_bytes':total,'source_files':file_count}
    save(out/'seal.json',seal);save(custodian/'public-seal-copy.json',seal);return seal


def verify(out,custodian=None):
    out=Path(out);seal=read(out/'seal.json');actual=files(out);actual.pop('seal.json',None)
    if actual!=seal['public_files']:raise ValueError('Frozen packet bytes changed')
    if custodian:
        if sha((Path(custodian)/'key.json').read_bytes())!=seal['key_sha256']:raise ValueError('Scoring key changed')
        if sha((Path(custodian)/'dice.json').read_bytes())!=seal['dice_sha256']:raise ValueError('Dice record changed')
    return seal


def _worker_limits():
    from tools.study_sandbox import _limits
    import resource
    _limits();resource.setrlimit(resource.RLIMIT_CPU,(30,30))
    resource.setrlimit(resource.RLIMIT_FSIZE,(LIMITS['result_bytes'],LIMITS['result_bytes']))


def run(out,output,*,implementation=ROOT,max_cases=None):
    from tools.study_sandbox import command,_limits
    from tools.unprepared_challenge import code_pins
    out=Path(out).resolve();output=Path(output).resolve();implementation=Path(implementation).resolve();seal=verify(out)
    if not shutil.which('bwrap'):raise ValueError('Linux bubblewrap required;no direct fallback')
    selected=sorted((out/'packets').iterdir())
    if max_cases is not None:
        if type(max_cases) is not int or not 1<=max_cases<=len(selected):raise ValueError('Invalid case limit')
        selected=selected[:max_cases]
    output.mkdir(parents=True,exist_ok=False);initial=code_pins(implementation);rows=[];output_bytes=0
    revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=implementation,text=True).strip()
    with tempfile.TemporaryDirectory(prefix='dpercent-execution-') as temp:
        code=Path(temp)/'code';code.mkdir()
        for pkg in ('mplpb_combined','mplpb_answers','mplpb_work'):
            shutil.copytree(implementation/pkg,code/pkg,ignore=shutil.ignore_patterns('__pycache__'))
        # Only this worker,not generator,scorer,questions manifest,key or dice records.
        worker=(ROOT/'tools/dpercent_worker.py').read_text()
        if sha(worker.encode())!=seal['worker_sha256']:raise ValueError('Frozen worker changed')
        for folder in selected:
            if output_bytes>=LIMITS['total_result_bytes']:break
            dest=output/folder.name;dest.mkdir();start=time.perf_counter()
            try:
                with (dest/'worker.log').open('xb') as log:
                    result=subprocess.run(command(shutil.which('bwrap'),code,folder,dest,worker),
                                          stdout=log,stderr=subprocess.STDOUT,timeout=LIMITS['wall_seconds'],preexec_fn=_worker_limits)
                if result.returncode:raise ValueError('Worker exit '+str(result.returncode))
                data=(dest/'result.json').read_bytes();output_bytes+=len(data)
                if len(data)>LIMITS['result_bytes']:raise ValueError('Result budget exceeded')
                value=read(dest/'result.json');row={'case_id':folder.name,'execution':'completed','sha256':sha(data)}
            except (ValueError,OSError,subprocess.SubprocessError) as error:
                row={'case_id':folder.name,'execution':'failed','error':str(error)}
                (dest/'failure.json').write_text(json.dumps(row)+'\n')
            row['parent_wall_seconds']=time.perf_counter()-start;rows.append(row)
            save_partial={'schema':VERSION+'-run','packet_seal_sha256':sha((out/'seal.json').read_bytes()),'runtime_sha256':initial,
                          'checkout_revision':revision,'environment':{'python':sys.version,'platform':platform.platform(),'machine':platform.machine()},
                          'generator_mounted':False,'scoring_key_mounted':False,'network_isolated':True,'cases':rows,
                          'total_planned_cases':len(list((out/'packets').iterdir())),'partial':len(rows)<len(list((out/'packets').iterdir()))}
            (output/'run.json').write_text(json.dumps(save_partial,indent=2)+'\n')
            print(folder.name,row['execution'],flush=True)
    verify(out)
    if code_pins(implementation)!=initial:raise ValueError('Implementation changed during execution')
    return read(output/'run.json')


def _normal(value):
    return ' '.join(str(value).casefold().strip(' .').split())


def score(out,custodian,output,report_path):
    out=Path(out);output=Path(output);verify(out,custodian)
    record=read(output/'run.json')
    if record['packet_seal_sha256']!=sha((out/'seal.json').read_bytes()):raise ValueError('Run seal differs')
    keys={k['id']:k for k in read(Path(custodian)/'key.json')['cases']};rows=[]
    # Only the post-run scorer opens the key. No runtime keys or model judgments.
    for entry in record['cases']:
        key=keys[entry['case_id']];row={'id':key['id'],'family':key['family'],'expected':key['expected'],'execution':entry['execution']}
        if entry['execution']!='completed':row.update(outcome='execution_failure');rows.append(row);continue
        path=output/key['id']/'result.json'
        if sha(path.read_bytes())!=entry['sha256']:raise ValueError('Frozen execution output changed')
        data=read(path);answer=data['answer']
        if type(answer.get('answer_supported')) is not bool:
            row.update(execution='failed',outcome='invalid_output');rows.append(row);continue
        supported=answer['answer_supported']
        propositions=[c['proposition'] for c in answer.get('claims',[]) if c.get('source_support_established') is True and isinstance(c.get('proposition'),dict)]
        quote_valid=True
        sources={s['source_id']:s for s in data['source_receipts']}
        for claim in answer.get('claims',[]):
            if claim.get('source_support_established') is True and not claim.get('citations'):quote_valid=False
            for cite in claim.get('citations',[]):
                src=sources.get(cite.get('source_id'));a=cite.get('body_start');b=cite.get('body_end')
                if (not src or src['hash']!=cite.get('hash') or type(a) is not int or type(b) is not int
                        or not 0<=a<b<=len(src['canonical_body']) or src['canonical_body'][a:b]!=cite.get('quote')):quote_valid=False
        if supported and not answer.get('claims'):quote_valid=False
        targets=key['required_propositions']
        matches=bool(targets) and all(any(all(k in p and ((type(p[k]) is bool and p[k] is v) if type(v) is bool else isinstance(p[k],str) and _normal(p[k])==_normal(v)) for k,v in target.items()) for p in propositions) for target in targets)
        if key['automatic_answer_matcher']=='quotation_location':
            # This contract asks for literal location,not a historical relationship.
            matches=any(cite.get('source_id') in key['reference_sources'] and key['literal_anchor'] in ' '.join(cite.get('quote','').split()) for claim in answer.get('claims',[]) for cite in claim.get('citations',[]))
        # An unsupported semantic shape is not awarded credit for matching words.
        correct=supported and matches and quote_valid and key['expected']=='answer'
        if supported and key['expected']=='refuse':outcome='false_alarm'
        elif correct:outcome='detected_answer'
        elif supported:outcome='supported_semantics_unscored' if not targets else 'incorrect_supported_answer'
        elif key['expected']=='answer':outcome='over_refusal'
        else:outcome='appropriate_refusal'
        row.update(kind=answer.get('kind'),answer_supported=supported,typed_proposition_match=matches,
                   quotation_fidelity=quote_valid,outcome=outcome,checked_partial=answer.get('kind')=='partial_answer')
        row['retrieval']={}
        for method,pack in data['retrieval'].items():
            ranked=list(dict.fromkeys(p['source_id'] for p in pack['passages']));refs=key['reference_sources']
            evidence=[s for s in key.get('source_facts',[]) if s['source_id'] in refs]
            covered=sum(any(p['source_id']==s['source_id'] and ' '.join(s['evidence_text'].split()) in ' '.join(p['text'].split()) for p in pack['passages']) for s in evidence)
            row['retrieval'][method]={'rank_one':bool(ranked and ranked[0] in refs) if refs else None,
                'complete_statement_coverage':covered/len(evidence) if evidence else None,
                **{'recall_at_'+str(k):len(set(ranked[:k])&set(refs))/len(refs) if refs else None for k in (1,5,10)}}
        row['measurements']=data.get('measurements',{})
        rows.append(row)
    attempted={r['id'] for r in rows}
    rows.extend({'id':k['id'],'family':k['family'],'expected':k['expected'],'execution':'not_run','outcome':'not_run'} for k in keys.values() if k['id'] not in attempted)
    positives=[r for r in rows if r['expected']=='answer'];negatives=[r for r in rows if r['expected']=='refuse']
    tp=sum(r['outcome']=='detected_answer' for r in positives);fp=sum(r['outcome']=='false_alarm' for r in negatives)
    failed=sum(r['execution']!='completed' for r in rows);complete=failed==0
    metrics={'answer_cases':len(positives),'refuse_cases':len(negatives),'correct_complete_answers':tp,'false_alarms':fp,
        'E':tp/len(positives) if positives and complete else None,'F':fp/len(negatives) if negatives and complete else None,
        'E_lower_bound':tp/len(positives) if positives else None,
        'E_output':sum(r.get('answer_supported',False) for r in positives)/len(positives) if positives and complete else None,
        'false_alarm_observed_on_completed':fp/sum(r['execution']=='completed' for r in negatives) if any(r['execution']=='completed' for r in negatives) else None,
        'over_refusals':sum(r['outcome']=='over_refusal' for r in rows),'appropriate_refusals':sum(r['outcome']=='appropriate_refusal' for r in rows),
        'execution_failures':failed,'unscored_supported':sum(r['outcome']=='supported_semantics_unscored' for r in rows),
        'complete_decision_match':bool(complete and tp==len(positives) and fp==0),
        'historical_accuracy':None,'independent_semantic_review':'NOT RUN',
        'caution':'E counts independently matched typed source propositions,not merely positive support flags;unsupported matcher shapes remain unscored.'}
    metrics['outcomes']=dict(Counter(r['outcome'] for r in rows))
    metrics['by_family']={family:dict(Counter(r['outcome'] for r in rows if r['family']==family)) for family in sorted({r['family'] for r in rows})}
    metrics['retrieval']={}
    for method in ('native_facets','simple_bm25'):
        metrics['retrieval'][method]={}
        for name in ('recall_at_1','recall_at_5','recall_at_10','complete_statement_coverage'):
            values=[r.get('retrieval',{}).get(method,{}).get(name) for r in rows]
            measured=[v for v in values if v is not None]
            metrics['retrieval'][method][name]={'mean':sum(measured)/len(measured) if measured else None,'cases':len(measured)}
    measured=[r['measurements'] for r in rows if r.get('measurements')]
    metrics['resources']={name:sum(m[name] for m in measured) if measured else None for name in ('cpu_seconds','wall_seconds','explicit_original_read_calls','explicit_original_bytes_read')}
    metrics['resources'].update(peak_worker_rss_bytes=max((m['peak_rss_bytes'] for m in measured),default=None),measured_cases=len(measured),total_pipeline_source_bytes_read=None,human_review_seconds=None)
    result={'schema':VERSION+'-score','run_sha256':sha((output/'run.json').read_bytes()),'scorer_sha256':sha(Path(__file__).read_bytes()),'metrics':metrics,'cases':rows,
            'definitions':{'E':'Correct complete supported answers / all expected-answer cases executed or attempted.',
                           'F':'Any supported answer / expected-refuse cases;execution failures are retained and separately counted.',
                           'failure_policy':'Do not interpret F as safety certification when execution failures exist.'},
            'scope':'Developer-generated synthetic documentary assertions;not real historical truth or independent human evaluation.'}
    save(report_path,result);return result


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='command',required=True)
    prep=sub.add_parser('prepare');prep.add_argument('--out',type=Path,required=True);prep.add_argument('--custodian',type=Path,required=True);prep.add_argument('--cases',type=int,default=112);prep.add_argument('--seed',type=int)
    execute=sub.add_parser('run');execute.add_argument('--packets',type=Path,required=True);execute.add_argument('--out',type=Path,required=True);execute.add_argument('--implementation',type=Path,default=ROOT);execute.add_argument('--limit',type=int)
    scoring=sub.add_parser('score');scoring.add_argument('--packets',type=Path,required=True);scoring.add_argument('--custodian',type=Path,required=True);scoring.add_argument('--run',type=Path,required=True);scoring.add_argument('--out',type=Path,required=True);scoring.add_argument('--require-perfect',action='store_true')
    a=p.parse_args(argv)
    if a.command=='prepare':r=prepare(a.out,a.custodian,count=a.cases,seed=a.seed);print(json.dumps({'schema':VERSION,'cases':a.cases,'structural_combinations':STRUCTURAL_COMBINATIONS,'key_sha256':r['key_sha256']},indent=2))
    elif a.command=='run':
        result=run(a.packets,a.out,implementation=a.implementation,max_cases=a.limit)
        return int(any(c['execution']!='completed' for c in result['cases']))
    else:
        result=score(a.packets,a.custodian,a.run,a.out);print(json.dumps(result['metrics'],indent=2))
        if a.require_perfect and not result['metrics']['complete_decision_match']:return 1
    return 0


if __name__=='__main__':raise SystemExit(main())
