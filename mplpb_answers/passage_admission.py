"""Reader-owned proof-witness slots under one exact-span passage budget.

Discovery scores and sorter classes are reasons to inspect, never proof. Required
witnesses come from existing native rules; the independent kernel rechecks them.
"""
from .body_text import body_text
from .evidence_contract import ReaderError
from . import documentary_verify as kernel

VERSION='reader-witness-admission-v1'
SEARCH_ONLY={'synonym_or_shared_wording','synonym_search','shared_wording_review','shared_subject_review','quoted_identifier_review'}

from contextvars import ContextVar
from contextlib import contextmanager
import copy
HINTS=ContextVar('mplpb_source_suggestions',default=())


@contextmanager
def source_suggestions(hints=None):
    if hints is None:hints=[]
    if not isinstance(hints,(list,tuple)) or len(hints)>64 or any(not isinstance(h,dict) for h in hints):
        raise ValueError('Supply at most64 source-location suggestions')
    for hint in hints:
        if (any(not isinstance(hint.get(k),str) for k in ['source_id','path','hash','text'])
            or type(hint.get('body_start')) is not int or hint['body_start']<0):
            raise ValueError('A suggestion needs exact source ID/path/hash/text and a nonnegative character position')
    if sum(len(h.get('text','')) for h in hints if isinstance(h.get('text',''),str))>64000:
        raise ValueError('Source-location suggestion text exceeds64000 characters')
    copied=copy.deepcopy(hints)
    for i,hint in enumerate(copied):hint.setdefault('sorter_node_id','external-review-'+str(i))
    token=HINTS.set(tuple(copied))
    try:yield
    finally:HINTS.reset(token)


def pending_suggestions():return list(HINTS.get())


def key(span):
    return (span['source_id'],span['path'],span['hash'],span['body_start'],span['body_end'])


class Budget:
    def __init__(self,index,max_passages,max_chars):
        self.index=index;self.max_passages=max_passages;self.max_chars=max_chars
        self.records={r.path:r for r in index.records};self.bodies={p:body_text(r.body_html) for p,r in self.records.items()}
        self.spans={};self.roles={};self.blocked=[];self.review=[];self.review_keys=set();self.counter_did_not_fit=False
        self.duplicate_charges_avoided=0
        self.discovery={'rule':None,'body_prefix_characters':0,'pair_attempts':0,'max_body_prefix_characters':192000,'max_pair_attempts':32}

    def _validate(self,span):
        record=self.records.get(span.get('path'));a=span.get('body_start');b=span.get('body_end')
        if (not record or record.id!=span.get('source_id') or record.hash_actual!=span.get('hash')
            or type(a) is not int or type(b) is not int or not 0<=a<b<=len(self.bodies[record.path])
            or self.bodies[record.path][a:b]!=span.get('quote')):
            raise ReaderError('source_changed','A proposed reader witness does not match an eligible original')

    def offer(self,spans,role):
        unique={}
        for span in spans:self._validate(span);unique[key(span)]=span
        fresh={k:v for k,v in unique.items() if k not in self.spans}
        cost=sum(len(v['quote']) for v in fresh.values())
        if len(self.spans)+len(fresh)>self.max_passages or self.characters+cost>self.max_chars:
            self.blocked.append({'role':role,'spans':[{'source_id':s['source_id'],'path':s['path'],'hash':s['hash'],
                'body_start':s['body_start'],'body_end':s['body_end']} for s in spans],
                'new_passages':len(fresh),'new_characters':cost,'reason':'reader_passage_budget'})
            return False
        self.spans.update(fresh)
        self.duplicate_charges_avoided+=len(spans)-len(fresh)
        for k in unique:self.roles.setdefault(k,[]).append(role)
        return True

    @property
    def characters(self):return sum(len(v['quote']) for v in self.spans.values())

    def review_only(self,p,reason):
        k=(p.get('source_id'),p.get('path'),p.get('hash'),p.get('body_start'),p.get('id'))
        if k in self.review_keys:return
        self.review_keys.add(k)
        self.review.append({'source_id':p.get('source_id'),'path':p.get('path'),'hash':p.get('hash'),
            'body_start':p.get('body_start'),'body_end':p.get('body_start',0)+len(p.get('text','')),
            'sorter_node_id':p.get('sorter_node_id'),'suggestion_class':p.get('suggestion_class','unclassified_sorter_hint'),
            'reason':reason,'admitted':False,'answer_supported':False})

    def report(self):
        return {'schema':VERSION,'max_passages':self.max_passages,'max_characters':self.max_chars,
            'passages_admitted':len(self.spans),'characters_admitted':self.characters,
            'deduplication':'Exact source ID/path/hash/half-open span; different revisions and distinct nested spans remain distinct.',
            'duplicate_span_charges_avoided':self.duplicate_charges_avoided,
            'admitted':[dict(s,reader_roles=self.roles[k]) for k,s in self.spans.items()],
            'blocked':self.blocked,'review_only_hints':self.review,'review_only_hint_count':len(self.review),
            'search_only_hints_admitted':0,'relevant_counterevidence_did_not_fit':self.counter_did_not_fit,
            'reader_witness_discovery':self.discovery,
            'sorter_assigns_slots':False,'historical_truth_verified':False}


def comparison_plan(index,budget):
    """Locate native-rule witnesses without modifying or replacing the verifier.

    Body prefixes guide a bounded search only. The existing comparison_completion
    rule must recognize each proposed pair, then check() independently redoes it
    against a fresh index. No source identity or truth comes from these scores.
    """
    from .source_units import comparison_units
    from mplpb_combined.reader import terms
    request=kernel.comparison_request(index.question)
    if request is None or len(index.records)>32:return None
    budget.discovery['rule']='existing_source_framed_literal_comparison'
    candidates=[];prefix_chars=0
    for record in index.records:
        body=body_text(record.body_html);prefix=body[:6000];prefix_chars+=len(prefix)
        budget.discovery['body_prefix_characters']=prefix_chars
        wanted=terms(request['work_reference'])
        if not wanted or not wanted<=terms(prefix):continue
        units=[]
        for a,b,q in comparison_units(record):
            if a>=6000:break
            if b>6000:continue  # Never turn a cut source unit into a witness.
            if set(request['topic_terms'])<=terms(q):
                units.append((a,b,q))
                if len(units)>=4:break
        if units:candidates.append((record,body,units))
    attempts=0
    for i,(left,lb,left_units) in enumerate(candidates):
        for right,rb,right_units in candidates[i+1:]:
            for a,b,q in left_units:
                for lo,hi,t in right_units:
                    if attempts>=32:return None
                    attempts+=1;budget.discovery['pair_attempts']=attempts
                    recognized=kernel.comparison_completion(index,left,a,b,right,lo,hi)
                    if recognized is None:continue
                    all_spans=[kernel.citation(left,lb,a,b),kernel.citation(right,rb,lo,hi)]+recognized['citations']
                    if not budget.offer(all_spans,'required_source_framed_comparison_witnesses'):return None
                    passages=[{'id':'reader-witness-'+s['source_id']+'-'+str(s['body_start']),
                        'source_id':s['source_id'],'path':s['path'],'hash':s['hash'],'body_start':s['body_start'],
                        'text':s['quote'],'reader_witness_role':'native_comparison_dependency','retrieval_score':None} for s in all_spans]
                    proposal={'kind':'comparison_completion','source_id':left.id,'path':left.path,'hash':left.hash_actual,
                        'start':a,'end':b,'quote':q,'other':{'source_id':right.id,'path':right.path,'hash':right.hash_actual,
                        'start':lo,'end':hi,'quote':t}}
                    return {'passages':passages,'proposal':proposal,'selection_rule':recognized['proposition']['completion_rule'],
                        'discovery_prefix_characters':prefix_chars,'pair_attempts':attempts,
                        'answer_supported':False,'verification_required':True}
    return None


def candidate_allowed(index,passage,goals,budget,closed_plan=False):
    record=budget.records.get(passage.get('path'));a=passage.get('body_start');text=passage.get('text')
    if (not record or record.id!=passage.get('source_id') or record.hash_actual!=passage.get('hash')
        or type(a) is not int or not isinstance(text,str) or a<0
        or budget.bodies[record.path][a:a+len(text)]!=text):
        budget.review_only(dict(passage,body_start=a if type(a) is int else 0,text=text if isinstance(text,str) else ''),
                           'Source pin, eligibility or exact original span was not established.');return False
    if 'sorter_node_id' not in passage:return True
    classification=passage.get('suggestion_class','unclassified_sorter_hint')
    # Exact routing remains the existing eligible-source router's decision.
    # A class may name a reason; it cannot manufacture a matching question part.
    named=[passage.get('source_id'),passage.get('target_source_id')]
    requested=any(value and any(value in g['question'] for g in goals) for value in named)
    quoted=[]
    import re
    for g in goals:quoted+=re.findall(r'["“]([^"”]{2,500})["”]',g['question'])
    exact_quote=classification=='exact_quote_match' and any(q in passage['text'] for q in quoted)
    from mplpb_combined.reader import terms
    # This only permits native proposal inspection. admit_proposals still must
    # match an existing rule to a concrete question part before assigning slots.
    part_overlap=any(terms(g['question'])&terms(passage['text']) for g in goals if g['kind']!='unsupported')
    specific=classification in {'exact_source_id_match','exact_field_match','explicit_reference','possible_correction'} and (requested or part_overlap)
    if classification in SEARCH_ONLY or closed_plan or not (specific or exact_quote):
        budget.review_only(passage,'Search/review only, or no unresolved native question part requires this source.');return False
    return True


def admit_proposals(index,proposals,goals,relevant,budget,reserved=None):
    """Assign source-span dependencies to native question parts, then charge.

    Parsing here predicts which witnesses a native rule will need. It never
    creates a certificate; kernel.check receives only admitted proposals and
    independently reloads the originals and inspects contrary evidence.
    """
    rows=[];seen=set()
    for proposal in ([reserved] if reserved else [])+proposals:
        if proposal is None:continue
        identity=(proposal.get('kind'),proposal.get('source_id'),proposal.get('hash'),proposal.get('start'),proposal.get('end'),
                  str(proposal.get('other',{})))
        if identity in seen:continue
        seen.add(identity);record=budget.records.get(proposal.get('path'))
        if not record or record.id!=proposal.get('source_id') or record.hash_actual!=proposal.get('hash'):continue
        body=budget.bodies[record.path];a=proposal.get('start');b=proposal.get('end')
        if type(a) is not int or type(b) is not int or not 0<=a<b<=len(body) or body[a:b]!=proposal.get('quote'):continue
        kind=proposal['kind'];spans=[];value=None
        if kind=='date_inventory':
            inventory=kernel.date_inventory(index,record)
            if inventory:value=inventory['proposition'];spans=inventory['citations']
        elif kind=='letter_instruction':
            value=kernel.letter_assertion(body,a,b)
            if value:
                spans=[kernel.citation(record,body,a,value['header_end']),kernel.citation(record,body,value['statement_start'],b)]
                closure=kernel.arrangement_completion(index.question,record,body,a,b,value)
                if closure:spans.append(kernel.citation(record,body,closure['complete_letter_start'],closure['complete_letter_end']))
        elif kind in {'wording_comparison','comparison_completion'}:
            other=proposal.get('other',{});right=budget.records.get(other.get('path'));lo=other.get('start');hi=other.get('end')
            if (not right or right.id!=other.get('source_id') or right.hash_actual!=other.get('hash')
                or type(lo) is not int or type(hi) is not int or not 0<=lo<hi<=len(budget.bodies[right.path])
                or budget.bodies[right.path][lo:hi]!=other.get('quote')):continue
            spans=[kernel.citation(record,body,a,b),kernel.citation(right,budget.bodies[right.path],lo,hi)]
            if kind=='comparison_completion':
                closure=kernel.comparison_completion(index,record,a,b,right,lo,hi)
                if closure:spans+=closure['citations']
            value={'relation':'exact_wording_comparison'}
        elif kind=='relationship_statement':
            value=kernel.relationship_assertion(proposal['quote']);spans=[kernel.citation(record,body,a,b)]
        elif kind=='literal_location':
            value=kernel.literal_occurrence(index.question,proposal['quote']);spans=[kernel.citation(record,body,a,b)]
        else:
            value=kernel.action_assertion(proposal['quote']);spans=[kernel.citation(record,body,a,b)]
            value,context=kernel.local_referent_context(record,body,a,b,value)
            spans+=context
        if value is None or not spans:continue
        parts=[i for i,g in enumerate(goals) if relevant(g,{'proposition':value},index.question)]
        if not parts:continue
        rows.append((proposal,spans,parts))
    ordered=[];used=set()
    # First proposed witness set for every native question part precedes extra
    # same-part candidates. This is not a claim that its assertions are true.
    for part in range(len(goals)):
        row=next((i for i,(_,_,parts) in enumerate(rows) if part in parts),None)
        if row is not None and row not in used:ordered.append(row);used.add(row)
    ordered += [i for i in range(len(rows)) if i not in used]
    admitted=[]
    for i in ordered:
        proposal,spans,parts=rows[i]
        if budget.offer(spans,'native_rule_candidates_for_question_parts:'+','.join(map(str,parts))):admitted.append(proposal)
    return admitted[:12]


def output_budget(contract,max_passages,max_chars):
    """Final guard for every answer path, including non-documentary grammars.

    A claim is atomic: all its distinct source witnesses must fit. A repeated
    source span is charged once. This guard never certifies an assertion.
    """
    seen={};admitted=[];blocked=0
    for claim in contract.get('claims',[]):
        unique={}
        for citation in claim.get('citations',[]):
            a=citation.get('body_start',citation.get('start'));b=citation.get('body_end',citation.get('end'))
            identity=(citation.get('source_id'),citation.get('path'),citation.get('hash'),a,b)
            unique[identity]=citation.get('quote','')
        new={k:v for k,v in unique.items() if k not in seen}
        if len(seen)+len(new)>max_passages or sum(map(len,seen.values()))+sum(map(len,new.values()))>max_chars:
            blocked+=1;continue
        seen.update(new);admitted.append(claim)
    contract['passage_budget']={'max_passages':max_passages,'max_characters':max_chars,
        'distinct_citation_spans':len(seen),'citation_characters':sum(map(len,seen.values())),
        'blocked_atomic_claims':blocked,'deduplicated_before_charge':True}
    if not blocked:return False
    contract.update(claims=admitted,answer_supported=False,
        text='\n'.join(c['text'] for c in admitted),
        sources=list({(e.get('source_id'),e.get('path'),e.get('hash')):
            {'id':e.get('source_id'),'path':e.get('path'),'hash':e.get('hash')} for c in admitted for e in c.get('citations',[])}.values()))
    contract['missing'].append('Required source witnesses exceed the passage budget; incomplete evidence cannot establish completion.')
    if 'documentary_support' in contract:contract['documentary_support']['source_support_claims']=len(admitted)
    if not admitted:contract['verification']['structural']=False
    return True
