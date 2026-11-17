"""Query-facet retrieval over the existing eligible index, never answer proof.

Headings guide discovery only. Output quotes always come from the unchanged
canonical body projection. No reference set, source-name list or gold offsets
are accepted. Exact-field routes retain the original unranked contract.
"""
from collections import Counter
from html import escape
from html.parser import HTMLParser
import math
import re
from .body_text import body_text
from mplpb_combined.reader import terms

VERSION='eligible-prose-facets-v1'
# Small, declared retrieval-only vocabulary; these are not semantic assertions.
EXPANSIONS={
    'arrang':{'tell','told','send','sent','request','instruct'},
    'receiv':{'send','sent','copy'},'deliver':{'send','sent','post'},
    'evacuat':{'march','marched','left','withdraw'},'withdrawal':{'withdraw','left','march'},
    'slav':{'slavery','enslaved'},'slavery':{'slave','enslaved'},
    'correct':{'correcting','corrected','reconsidered','mistaken','amended'},
    'contradict':{'disagree','denied','inconsistent'},
    'introduct':{'opening','beginning'},'open':{'first','truth'},
}
QUESTION_WORDS={'Who','What','Which','When','Where','Why','How','Does','Did','Can','Could','Is','Are','The','Compare','Separate','Distinguish','According','Provide','Show'}


def metadata(record):
    class Headings(HTMLParser):
        def __init__(self):super().__init__();self.parts=[];self.active=False;self.current=[];self.headings=[];self.transcript=None
        def handle_starttag(self,t,attrs):
            if t in {'h1','h2','h3','h4'}:self.active=True;self.current=[]
            self.parts.append('<'+t+'>')
        def handle_endtag(self,t):
            self.parts.append('</'+t+'>')
            if t in {'h1','h2','h3','h4'} and self.active:
                text=' '.join(self.current).strip();self.headings.append(text)
                if text.casefold() in {'transcript','transcription'}:
                    prefix=body_text(''.join(self.parts));self.transcript=len(prefix)+bool(prefix)
                self.active=False
        def handle_data(self,t):
            if self.active:self.current.append(t)
            self.parts.append(escape(t,quote=False))
    p=Headings();p.feed(record.body_html);p.close()
    return {'heading_terms':terms(' '.join(p.headings)[:6000]),'transcript_start':p.transcript}


def retrieve(index,max_passages=12,max_chars=12000,seed=None):
    if index.exact_status:return index.retrieve([index.question],max_passages,max_chars)
    if not 1<=max_passages<=64 or not 1000<=max_chars<=64000:raise ValueError('Invalid retrieval budget')
    question=index.question;query=terms(question);expanded=set(query)
    for token in query:
        for value in EXPANSIONS.get(token,set()):expanded.update(terms(value))
    entities=set().union(*(terms(x) for x in re.findall(r'\b[A-Z][a-z]+\b',question) if x not in QUESTION_WORDS))
    clauses=[terms(x) for x in re.split(r'[?;]|\b(?:and|or|rather than|without)\b',question,flags=re.I) if len(terms(x))>=2]
    facets=[query]+clauses[:3]
    from .documentary import plan
    obligations=plan(question) or []
    for goal in obligations:
        facet=terms(goal['question'])
        if facet and facet not in facets:facets.append(facet)
    facets=facets[:5]
    rows=[Counter(terms(token).pop() for token in re.findall(r'[^\W_]+',p['text']) if len(terms(token))==1) for p in index.passages]
    n=len(rows);df=Counter(t for row in rows for t in row);lengths=[sum(c.values()) for c in rows];avg=sum(lengths)/max(1,n)
    idf={t:math.log(1+(n-df[t]+.5)/(df[t]+.5)) for t in expanded|entities}
    info={r.path:metadata(r) for r in index.records}
    doc_terms={r.path:terms(body_text(r.body_html)) for r in index.records}
    doc_df=Counter(t for row in doc_terms.values() for t in row)
    doc_entity={p:sum(math.log(1+len(info)/doc_df[t]) for t in entities if t in ts) for p,ts in doc_terms.items()}
    heading_scores={p:sum(1 for t in query if t in m['heading_terms']) for p,m in info.items()}
    routing=set().union(*(m['heading_terms'] for m in info.values())) if info else set()
    instructions=terms('compare final wording remained distinguish separate identify named personally original record transcript passage pages question alone every whether rather establish')
    focus=expanded-routing-instructions
    raw=[]
    for i,(p,row) in enumerate(zip(index.passages,rows)):
        score=sum(idf[t]*row[t]*2.2/(row[t]+1.2*(.25+.75*lengths[i]/max(avg,1)))*(1 if t in query else .35) for t in expanded if row[t])
        entity_score=sum(idf[t] for t in entities if row[t])
        header=bool(re.search(r'(?m)^[A-Z][A-Z .’\'-]{3,80}\s+TO\s+[A-Z][A-Z .’\'-]{3,80}',p['text']))
        header_bonus=4 if header and query & terms('letter correspondence note sent receive book') else 0
        # Documentary scope is a discovery boost, never an eligibility filter.
        focus_score=sum(idf[t]*row[t]*2.2/(row[t]+1.2*(.25+.75*lengths[i]/max(avg,1))) for t in focus if row[t])
        # Discover a document by its identity; rank its evidence by the subject
        # being asked about. Otherwise navigation repeating the title wins.
        score=.2*score+2*focus_score+entity_score+2*heading_scores[p['path']]+doc_entity[p['path']]+header_bonus
        if len(row)<30 and not (set(row)&focus):score*=.2
        raw.append((score,i))
    # Reciprocal rank fusion gives each clause a chance instead of requiring a
    # long mixed question to match one passage. It does not connect the clauses.
    fused=Counter()
    for facet in facets:
        ordered=sorted(raw,key=lambda si:(-(si[0]+sum(idf.get(t,0) for t in facet if rows[si[1]][t])),index.passages[si[1]]['path'],index.passages[si[1]]['body_start']))
        for rank,(_,i) in enumerate(ordered):fused[i]+=1/(20+rank)
    if seed:
        positions={p['id']:i for i,p in enumerate(index.passages)}
        for rank,p in enumerate(seed['passages']):
            if p['id'] in positions:fused[positions[p['id']]]+=.1/(20+rank)
    ordered=sorted(raw,key=lambda si:(-fused[si[1]],-si[0],index.passages[si[1]]['path'],index.passages[si[1]]['body_start']))
    # Retain separate source/section appearances; do not erase contradictory
    # evidence through a one-winner route. No completeness claim follows.
    selected=[];used=0;seen=set()
    def add(i,reason):
        nonlocal used
        p=index.passages[i]
        if i in seen or len(selected)>=max_passages or used+len(p['text'])>max_chars:return
        if not (terms(p['text'])&expanded):return
        selected.append(dict(p,retrieval_score=next(s for s,j in raw if j==i),retrieval_reason=reason))
        used+=len(p['text']);seen.add(i)
    relevant_paths=sorted(info,key=lambda p:(-(heading_scores[p]*2+doc_entity[p]),p))
    strongest=max((heading_scores[p]*2+doc_entity[p] for p in info),default=0)
    for path in relevant_paths if strongest>0 else []:
        if strongest and heading_scores[path]*2+doc_entity[path]<strongest*.45:continue
        ranked=[i for _,i in ordered if index.passages[i]['path']==path]
        if ranked:add(ranked[0],'source-facet')
        start=info[path]['transcript_start']
        if start is not None:
            original=[i for i in ranked if index.passages[i]['body_start']>=start]
            if original:add(original[0],'declared-transcript-section-discovery-only')
    obligation_diagnostics=[]
    for goal in obligations:
        wanted=terms(goal['question'])
        ranked=sorted(ordered,key=lambda si:(-len(wanted&set(rows[si[1]])),-si[0]))
        if ranked:add(ranked[0][1],'independent-question-obligation')
        obligation_diagnostics.append({'question':goal['question'],'kind':goal['kind'],
            'status':'bounded_search_only','source_support_established':False})
    for _,i in ordered:add(i,'query-facet-rank-fusion')
    paths={p['path'] for p in selected}
    return {'passages':selected,'sources':[s for s in index.sources if s['path'] in paths],
        'eligible_pages':len(index.sources),'total_passages':len(index.passages),'search_complete':False,
        'queries':[question],'ranking':VERSION,'corpus_snapshot':index.gate.corpus_snapshot,
        'independence_verified':False,'routing_metadata_is_answer_evidence':False,
        'query_expansion_terms':sorted(expanded-query),'facets':[sorted(f) for f in facets],
        'obligations':obligation_diagnostics,'omitted_passages':len(index.passages)-len(selected),
        'search_scope':'Currently eligible indexed passages only; bounded selection cannot establish historical absence.'}
