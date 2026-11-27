"""Bounded native source-denial/modality checks over independently reread bytes.

Question interpretation and ClaimFrame construction are proposals. This checker
reopens the original eligibility view, derives complete source units itself,
retains reporting/condition scope, and rechecks final state before serving.
"""
from dataclasses import replace
import re
from . import documentary_verify as kernel
from .body_text import body_text
from .claim_frame import ClaimFrame, VERSION as FRAME_VERSION
from .passages import PassageIndex
from .source_attribution import source_frame, unqualified_span

VERSION='bounded-source-claims-v1'
_KINDS={'instruction':'instruction','intention':'intention','recommendation':'recommendation',
        'forecast':'forecast','conditional statement':'conditional','completed action':'completed_action'}
_VERBS={'instructed':'instruction','instruct':'instruction','intended':'intention','intend':'intention',
        'recommended':'recommendation','recommend':'recommendation','forecast':'forecast','predicted':'forecast',
        'predict':'forecast','completed':'completed_action','complete':'completed_action'}
_COLLECTIVE=r'the(?: [a-z]+){0,6} (?:team|crew|delegation|committee|council|office|group|unit|staff|party)'
_RECIPIENT=rf'(?:{_COLLECTIVE}|(?-i:[A-Z][a-z]+(?: [A-Z][a-z]+){{0,3}}))'


def _name(value):
    return (len(value)<=120 and kernel.named_actor(value)
            and not set(kernel.normalized(value).split())&{'i','he','she','they','it','we','you','if','unless','not','no','only','never','neither','perhaps','possibly','allegedly','reportedly','apparently'})


def request(question):
    from .ordinary_questions import request as ordinary_request
    ordinary=ordinary_request(question)
    if ordinary and ordinary['kind']=='instruction':
        return {k:ordinary[k] for k in ('kind','actor','object','recipient')}
    q=kernel.source_question(question).strip().rstrip('? .')
    denied=re.fullmatch(r'What does the record deny about (.{2,120}?) and (.{2,220})',q,re.I)
    if denied and _name(denied[1]):return {'kind':'denial','actor':denied[1],'object':denied[2]}
    modal=re.fullmatch(r'What (instruction|intention|recommendation|forecast|conditional statement|completed action) does the record attribute to (.{2,120}?) concerning (.{2,220})',q,re.I)
    if modal and _name(modal[2]):return {'kind':_KINDS[modal[1].lower()],'actor':modal[2],'object':modal[3]}
    return None


def _task(text):
    negative=text.startswith('not ')
    if negative:text=text[4:]
    m=re.fullmatch(r'([a-z]{2,40}) (.{2,220})',text)
    if (not m or m[1] in {'the','a','an','to','that','if','unless','would','should','not','is','was','be','and','or','by','of','for'}
            or re.search(r'\b(?:and|or|if|unless|provided|because|would|should|may|might|could|not|never)\b',m[2])):return None
    return m[1],m[2],negative


def _modal(text):
    clean=' '.join(text.split());conditions=[]
    leading=re.fullmatch(r'((?:If|Unless) [^,.!?;:]{1,160}), (.+)',clean)
    if leading:conditions.append(leading[1]);clean=leading[2]
    trailing=re.fullmatch(r'(.+?) ((?:only if|if|unless) [^,.!?;:]{1,160})\.',clean)
    if trailing:clean=trailing[1]+'.';conditions.append(trailing[2])
    actor=kind=tail=recipient=None;outer=False;aspect=''
    verb=re.fullmatch(r'(.{2,120}?) (did not )?(instructed|instruct|intended|intend|recommended|recommend|forecast|predicted|predict|completed|complete) (.{2,600})\.',clean)
    nominal=re.fullmatch(r"(.{2,120}?)[’']s (?:stated )?(instruction|intention|recommendation|forecast)(?: to (.+?))? was (.+)\.",clean)
    given=re.fullmatch(r'The (instruction|recommendation|intention) (?:given by|from) (.{2,120}?)(?: to (.+?))? was (.+)\.',clean)
    perfect=re.fullmatch(r'(.{2,120}?) had completed (.{2,220})\.',clean)
    conditional=re.fullmatch(r'(.{2,120}?) would (.{2,220})\.',clean)
    if verb:
        actor,neg,word,tail=verb.groups();kind=_VERBS[word];outer=bool(neg)
        if outer and word not in {'instruct','intend','recommend','forecast','predict','complete'}:return None
    elif nominal:actor,word,recipient,tail=nominal.groups();kind=_KINDS[word]
    elif given:word,actor,recipient,tail=given.groups();kind=_KINDS[word]
    elif perfect:actor,tail=perfect.groups();kind='completed_action';aspect='past_perfect'
    elif conditional:actor,tail=conditional.groups();kind='conditional'
    else:return None
    if not _name(actor):return None
    if kind=='completed_action':
        if len(tail)>220 or re.search(r'\b(?:and|or|if|unless|not|would|might)\b',tail,re.I):return None
        return ClaimFrame(actor,'complete',tail,outer,kind,tuple(conditions),actor),aspect
    if kind in {'intention','instruction','recommendation'} and (tail.startswith('to ') or tail.startswith('not to ')):
        content_negative=tail.startswith('not to ');tail=tail[7:] if content_negative else tail[3:]
        recipient=recipient or (actor if kind=='intention' else None)
    else:
        content_negative=False
        if kind=='instruction':
            m=re.fullmatch(rf'({_RECIPIENT}) (not to|to) (.+)',tail)
            if not m:return None
            recipient,marker,tail=m.groups();content_negative=marker=='not to'
        elif kind in {'recommendation','forecast'}:
            m=re.fullmatch(rf'that ({_RECIPIENT}) '+(r'would ' if kind=='forecast' else '')+r'(.+)',tail)
            if not m:return None
            recipient,tail=m.groups()
        elif kind in {'conditional','intention'}:recipient=actor
    task=_task(tail)
    if not task or recipient is None:return None
    action,obj,negative=task
    return ClaimFrame(actor,action,obj,outer,kind,tuple(conditions),recipient,content_negative or negative),aspect


def _frame_units(record,body):
    info=None
    for form in ('letter','minutes','report'):
        found=source_frame(record,form)
        if found:_,info=found;break
    start,end=(info['start'],info['end']) if info else (0,len(body))
    return [(a+start,b+start,q) for a,b,q in kernel.units(body[start:end],record if start==0 and end==len(body) else None)],info


def _derive(record,body,unit,previous,info):
    a,b,text=unit
    if record.kind!='page' or record.derived_from or record.fields.get('corrects-field') or not unqualified_span(record,body,a,b):return None
    parsed=_modal(text)
    atomic=kernel.action_assertion(text) or kernel.relationship_assertion(text)
    if parsed:
        frame,aspect=parsed;value=None;extra=info['witnesses'] if info else []
    elif atomic and atomic.get('relation') in {'source_action_assertion','source_passive_action_assertion'} and not atomic.get('unresolved_reference'):
        frame=ClaimFrame.from_action(atomic);value=atomic;extra=[]
    else:
        return None
    prefix=body[max(0,a-200):a]
    governor=None
    if previous:
        lo,hi,q=previous
        if unqualified_span(record,body,lo,hi):
            m=re.fullmatch(r'((?:If|Unless) [^,.!?;:]{1,160})\.',q,re.I)
            if m:governor=m[1];extra=extra+[kernel.citation(record,body,lo,hi)]
    if governor:frame=replace(frame,conditions=(governor,)+frame.conditions)
    elif re.search(r'\b(?:if|unless)\b',prefix,re.I):return None
    if frame.modality=='assertion' and frame.conditions:return None
    if frame.modality=='conditional' and not frame.conditions:return None
    if value is None:
        value={'relation':'source_modality_assertion','actor':frame.actor,'modality':frame.modality,
               'source_form':info['form'] if info else 'unframed','source_writer_or_unknown':info['writer'] if info else None,
               'task_actor':frame.task_actor,'task_action':frame.action,'task_object':frame.object_text,
               'outer_negative':frame.negative,'content_negative':frame.content_negative,'conditions':list(frame.conditions),
               'completion_asserted_by_source':frame.modality=='completed_action' and not frame.negative,
               'execution_independently_verified':False,'historical_truth_independently_verified':False,
               'source_voice':'source_attributes_named_actor_modality','source_aspect':aspect,
               'actor_identity_independently_verified':False,'claim_frame_version':FRAME_VERSION}
    return frame,value,[kernel.citation(record,body,a,b)]+extra


def verify(index,max_passages,max_chars):
    goal=request(index.question)
    if goal is None:return None
    target_object=goal.get('object')
    fresh=PassageIndex(index.root,index.question,index.profile)
    if len(fresh.records)>8 or sum(len(r.body_html) for r in fresh.records)>200000:return 'abstain','reference_scan_budget',{}
    matches=[];used=0;unresolved=False;alternatives=[];unparsed_units=[]
    for record in fresh.records:
        body=body_text(record.body_html)
        # Layout witnesses consume the same source-unit budget as content.
        # A verified letter frame cannot hide its salutation/signature cost.
        for _ in kernel.units(body,record):
            used+=1
            if used>1000:return 'abstain','reference_scan_budget',{}
        units,info=_frame_units(record,body);previous=None
        if kernel.possible_refutation(body):unresolved=True
        for unit in units:
            a,b,text=unit
            unresolved_reference=bool(re.search(
                r'\b(?:this|that|earlier|previous|preceding|above)\b[^.!?]{0,100}'
                r'\b(?:revoked|rescinded|retracted|withdrawn|superseded|amended|canceled|cancelled)\b',text,re.I))
            if unresolved_reference:
                unresolved=True
                alternatives.append(kernel.citation(record,body,a,b))
            if b-a>2200:
                if (kernel.normalized(target_object) in kernel.normalized(text) if target_object else kernel.normalized(goal['actor']) in kernel.normalized(text)):
                    unresolved=True
                    unparsed_units.append({'source_id':record.id,'path':record.path,'hash':record.hash_actual,
                        'body_start':a,'body_end':b,'characters':b-a,'reason':'statement_phrase_budget',
                        'limit':2200,'claim_verified':False})
                previous=unit;continue
            derived=_derive(record,body,unit,previous,info);previous=unit
            if derived is None:
                if (kernel.normalized(goal['actor']) in kernel.normalized(text)
                        and (not target_object or kernel.normalized(target_object) in kernel.normalized(text))
                        and re.search(r'\b(?:not|never|intend\w*|instruct\w*|recommend\w*|forecast\w*|predict\w*|complet\w*|would)\b',text,re.I)):
                    unresolved=True
                continue
            frame,value,citations=derived
            if (kernel.normalized(frame.actor)!=kernel.normalized(goal['actor'])
                    or (target_object and kernel.normalized(frame.object_text)!=kernel.normalized(target_object))
                    or frame.modality!=('assertion' if goal['kind']=='denial' else goal['kind'])):continue
            if goal.get('recipient') and kernel.normalized(frame.task_actor)!=kernel.normalized(goal['recipient']):continue
            matches.append((frame,value,citations))
    if not fresh.unchanged() or not index.unchanged():return 'abstain','source_changed',{}
    if not matches:return None
    required_negative=goal['kind']=='denial'
    selected=[m for m in matches if m[0].negative==required_negative]
    if not selected:return None
    opposite=[m for m in matches if m[0].negative!=required_negative]
    if len(selected)!=1 or len(opposite)>1:return None
    chosen=selected+opposite;conflict=bool(opposite)
    spans={}
    for _,_,citations in chosen:
        for c in citations:spans[(c['path'],c['hash'],c['body_start'],c['body_end'])]=c
    for c in alternatives:spans[(c['path'],c['hash'],c['body_start'],c['body_end'])]=c
    if len(spans)>max_passages or sum(len(c['quote']) for c in spans.values())>max_chars:return 'abstain','reader_budget_exceeded',{}
    claims=[]
    for frame,value,citations in chosen:
        if frame.modality=='assertion':
            from .documentary import _claim
            claim=_claim({'proposition':value,'citations':citations,'verification':VERSION})
        else:
            text='The source states: '+citations[0]['quote']
            qualifiers=['Source-attributed statement only. Authenticated identity, historical truth and execution are not independently verified.']
            if frame.conditions:qualifiers.append('Source conditions (fulfillment unestablished): '+'; '.join(frame.conditions))
            if frame.modality!='completed_action':qualifiers.append('This stated modality does not establish execution or an agreement.')
            claim={'text':text,'proposition':value,'citations':citations,'source_support_established':True,
                   'historical_truth_independently_verified':False,'qualifiers':qualifiers}
        claims.append(claim)
    sources=[{'id':c['source_id'],'path':c['path'],'hash':c['hash']} for c in spans.values()]
    unique=[]
    for s in sources:
        if s not in unique:unique.append(s)
    missing=['A source qualification or revocation has an unresolved target; the stated claim is retained as a checked partial.'] if unresolved else []
    if unparsed_units:
        missing=['A source qualification or counterevidence unit exceeds the 2,200-character phrase limit; full proof is unresolved and the cited statement remains a checked partial.']
    result = ('conflict' if conflict else 'partial_answer' if unresolved else 'supported_answer'),('source_claim_conflict' if conflict else 'partial_source_phrase_budget' if unparsed_units else 'partial_source_claim' if unresolved else 'supported_source_claim'),{
        'answer_supported':not conflict and not unresolved,'claims':claims,'sources':unique,'missing':missing,
        'text':'\n'.join(c['text']+' '+' '.join(c['qualifiers']) for c in claims)+ ('\nUnresolved: '+missing[0] if missing else ''),
        'verification':{'structural':True,'semantic':VERSION,'truth_verified':False,'independence_verified':False},
        'documentary_support':{'original_question':index.question,'source_support_claims':len(claims),
            'claim_frame_version':FRAME_VERSION,'historical_truth_independently_verified':False,
            'scan_complete':True,'examined_units':used,'alternative_evidence':alternatives,'max_records':8,'max_source_characters':200000,
            'max_units':1000,'max_passages':max_passages,'max_characters':max_chars}}

    if unparsed_units:
        room=max(0,max_passages-len(spans))
        result[2]['documentary_support'].update(proof_complete=False,
            unparsed_relevant_units=unparsed_units[:room],omitted_unparsed_unit_locators=max(0,len(unparsed_units)-room),
            max_statement_characters=2200)
    return result
