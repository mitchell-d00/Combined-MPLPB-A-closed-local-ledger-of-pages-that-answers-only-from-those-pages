"""Bounded source-scoped correction links, never inferred record replacement."""
import re
from . import documentary_verify as kernel
from .body_text import body_text
from .passages import PassageIndex
from .source_attribution import unqualified_span

_DATE=kernel.DATE_EXPRESSION
_WRITING=re.compile(r'This\s+letter\s+was\s+written\s+on\s+(?P<date>'+_DATE+r')\.',re.I)
_COUNT=re.compile(r'The\s+(?P<object>[A-Za-z][A-Za-z\s-]{0,60}?)\s+contains\s+(?P<count>[A-Za-z0-9\s-]{1,70}?)\s+(?P<unit>[a-z]{2,30})\s+for\s+(?P<destination>[^.!?;:]{2,120})\.',re.I)
_CORRECTION=re.compile(r'In\s+my\s+letter\s+of\s+(?P<date>'+_DATE+r'),\s+the\s+count\s+should\s+read\s+(?P<count>[A-Za-z0-9\s-]{1,70}?)\s+(?P<unit>[a-z]{2,30})\.(?:\s+The\s+destination\s+remains\s+(?P<destination>[^.!?;:]{2,120})\.)?',re.I)
_UNCERTAIN=re.compile(r'\b(?:if|unless|would|could|possibly|perhaps|allegedly|reported|not|never|denied|revoked|retracted|superseded)\b',re.I)
def clean(value):return ' '.join(value.split())
def verify(index,max_passages,max_chars):
    q=kernel.source_question(index.question)
    if not re.fullmatch(r'What count does the later statement correct, and which destination does it retain\?',q,re.I):return None
    fresh=PassageIndex(index.root,index.question,index.profile)
    if len(fresh.records)>8 or sum(len(r.body_html) for r in fresh.records)>200000:return 'abstain','reference_scan_budget',{}
    originals=[];corrections=[];used=0
    for r in fresh.records:
        body=body_text(r.body_html);used+=sum(1 for _ in kernel.units(body))
        if used>1000:return 'abstain','reference_scan_budget',{}
        if r.kind!='page' or r.derived_from or r.fields.get('corrects-field'):continue
        dates=list(_WRITING.finditer(body));counts=list(_COUNT.finditer(body));changes=list(_CORRECTION.finditer(body))
        relevant=bool(dates or counts or changes)
        if relevant and (_UNCERTAIN.search(body) or kernel.possible_refutation(body)):
            return 'abstain','correction_scope_unresolved',{}
        for m in changes:
            if m.end()-m.start()<=2200 and unqualified_span(r,body,*m.span()):corrections.append((r,body,m))
        if len(dates)==1 and len(counts)==1 and all(unqualified_span(r,body,*m.span()) for m in (dates[0],counts[0])):
            originals.append((r,body,dates[0],counts[0]))
    if len(corrections)!=1:return None
    r,body,change=corrections[0];target=kernel._date_value(clean(change['date']))
    if not target or target['year'] is None:return None
    matches=[o for o in originals if kernel._date_value(clean(o[2]['date']))==target]
    if len(matches)!=1:return None
    original,earlier,date,count=matches[0]
    if original.id==r.id or clean(count['unit']).casefold()!=clean(change['unit']).casefold():return None
    destination=clean(change['destination']) if change['destination'] else None
    if destination is not None and destination.casefold()!=clean(count['destination']).casefold():return None
    witnesses=[kernel.citation(original,earlier,*m.span()) for m in (date,count)]+[kernel.citation(r,body,*change.span())]
    if len(witnesses)>max_passages or sum(len(c['quote']) for c in witnesses)>max_chars:return 'abstain','reader_budget_exceeded',{}
    if not fresh.unchanged() or not index.unchanged():return 'abstain','source_changed',{}
    value={'relation':'source_scoped_count_correction','previous_count':clean(count['count']),'replacement_count':clean(change['count']),'unit':clean(count['unit']),'destination_retained':destination,'target_writing_date':clean(date['date']),'execution_established':False,'original_source_id':original.id,'correction_source_id':r.id,'historical_truth_independently_verified':False}
    same=value['previous_count'].casefold()==value['replacement_count'].casefold()
    text=('The correction explicitly repeats ' if same else 'The correction changes the stated count from '+value['previous_count']+' to ')+value['replacement_count']+' '+value['unit']+'.'
    if destination:text+=' It explicitly retains the destination '+destination+'.'
    claim={'text':text,'proposition':value,'citations':witnesses,'source_support_established':True,'historical_truth_independently_verified':False,'qualifiers':['Source correction statement only; corrected count does not establish dispatch, receipt or actual cargo.','The first-person reference is bound only by the unique explicit writing date among eligible sources; writer identity is unresolved.']}
    evidence={'claims':[claim],'text':text,'answer_supported':destination is not None,'missing':[] if destination else ['The retained destination is unresolved.'],'sources':[s for s in fresh.sources if s['path'] in {c['path'] for c in witnesses}]}
    return ('supported_answer' if destination else 'partial_answer'),'source_correction_verified',evidence
