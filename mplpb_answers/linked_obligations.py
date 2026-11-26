"""Preserve a checked documentary-chain prefix without inventing its bridges."""
from . import documentary_links as links
from . import documentary_verify as kernel
from .body_text import body_text
from .passages import PassageIndex

def verify_prefix(index,ids,extra,max_passages,max_chars):
    # A lexical scope match does not grant prose synthesis permission.
    if not index.profile.prose:return 'documentary_link_unverified',None,None
    fresh=PassageIndex(index.root,index.question,index.profile)
    if len(fresh.records)>8 or sum(len(r.body_html) for r in fresh.records)>200000:return 'reference_scan_budget',None,None
    if sum(sum(1 for _ in kernel.units(body_text(r.body_html))) for r in fresh.records)>1000:return 'reference_scan_budget',None,None
    records={i:next((r for r in fresh.records if r.id==i and r.kind=='page' and not r.derived_from and not r.fields.get('corrects-field')),None) for i in ids}
    result=links.chain(records,ids,max_passages,max_chars)
    if not result['steps']:return 'documentary_link_unverified',None,None
    first=result['steps'][0];competing=[]
    for record in fresh.records:
        if record.id in ids or record.derived_from or record.kind!='page':continue
        witness=links.whole_source(record,min(max_chars,4000))
        if not witness or kernel.context_ranges(record):continue
        match=links._DISPATCH.fullmatch(' '.join(witness['quote'].split()))
        if match and match['reference']==ids[0] and any(match[k]!=first[k] for k in ('sender','object','destination')):competing.append(witness)
    if competing:
        result['steps']=result['steps'][:1];result['citations']=result['citations'][:1]
        result['missing']=['dispatch: competing eligible statements disagree','reported receipt linked to the dispatch']
    if extra:result['missing']+=['Whether the material was read is unresolved.','Whether the task was completed is unresolved.']
    witnesses=result['citations']
    if len(witnesses)>max_passages or sum(len(c['quote']) for c in witnesses)>max_chars:return 'reader_budget_exceeded',None,None
    if not fresh.unchanged() or not index.unchanged():return 'source_changed',None,None
    roles=[s['role'] for s in result['steps']]
    proposition={'relation':'documentary_chain_prefix','verified_roles':roles,'steps':result['steps'],**{k:first[k] for k in ('sender','object','destination')},'completion_established':False,'receipt_independently_verified':False,'competing_links':bool(competing),'historical_truth_independently_verified':False}
    text='The cited records establish this source-scoped chain prefix: '+', '.join(roles)+'.'
    claim={'text':text,'proposition':proposition,'citations':witnesses,'source_support_established':True,'historical_truth_independently_verified':False,'qualifiers':['The proof covers the cited source statements only. Reading, acknowledgment and task completion remain unproved. Chronology alone supplies no link.']}
    evidence={'claims':[claim],'text':text,'answer_supported':not result['missing'],'missing':result['missing'],'sources':[s for s in fresh.sources if s['path'] in {c['path'] for c in witnesses}]}
    return ('documentary_chain_incomplete' if result['missing'] else 'supported_documentary_assertion'),evidence,None
