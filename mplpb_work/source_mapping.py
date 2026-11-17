"""Reversible, gated prose mappings. Lexical structures are candidates, not facts.

This module verifies quote fidelity separately from semantic relationships. It
uses the existing passage index and never writes source fields or claim support.
"""
import copy
import hashlib
import json
import re
from mplpb_answers.body_text import body_text, VERSION as BODY_VERSION
from mplpb_answers.evidence_contract import ReaderError
from mplpb_answers.passages import PassageIndex
from mplpb_combined.reader import PROFILES, DEFAULT_PROFILE, terms
from .historical_verifier import verification_snapshot

VERSION = 'reversible-prose-map-v1'
CORRECTION = re.compile(r'\b(?:reconsider(?:ed|ing)?|correct(?:ed|ion|ions)?|retract(?:ed|ion)?|recant(?:ed)?|mistaken|erroneous|errat[au]|revis(?:ed|ion)|amend(?:ed|ment)|withdraw(?:n)?|withdrew)\b', re.I)
EVENT = re.compile(r'\b(?:wrote|received|sent|published|read|replied|reported|surrendered|evacuated|aborted|reconsidered|corrected|retracted)\b', re.I)
CONTRADICTION = re.compile(r'\b(?:contradict(?:ed|ion)?|disagree(?:d|ment)?|inconsistent|denied)\b', re.I)
DATES = re.compile(r'\b(?:\d{4}-\d{2}-\d{2}|(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}(?:st|nd|rd|th|d)?(?:,)?(?:\s+\[?\d{4}\]?)?)\b',re.I)
REFERENCE = re.compile(r'\b(?:earlier|previous|former|last|your|my)\s+(?:letter|note|conclusion|statement|account|opinion|report)|\brepl(?:y|ied)\b', re.I)
QUALIFIER = re.compile(r'\b(?:not|never|no|if|perhaps|may|might|could|alleged|uncertain|unknown|suppose)\b', re.I)
ENTITY = re.compile(r'\b[A-Z][a-z]{2,}(?:\s+[A-Z][a-z]{2,}){0,2}\b')


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()


def _profile(profile):
    profile = PROFILES[profile] if isinstance(profile,str) else profile or PROFILES[DEFAULT_PROFILE]
    if profile.name not in PROFILES or profile != PROFILES[profile.name]:
        raise ValueError('Choose a known delivery profile')
    return profile


def _state(root,question,profile):
    value=verification_snapshot(root,question,profile)
    value.pop('root')  # Portability within the same pinned collection, not authority.
    return value


def anchor(passage):
    return {'source_id':passage['source_id'],'path':passage['path'],'hash':passage['hash'],
            'body_start':passage['body_start'],'body_end':passage['body_start']+len(passage['text']),
            'body_projection':BODY_VERSION,'quote':passage['text']}


def _item(kind,evidence,value,state,**extra):
    result={'kind':kind,'value':value,'evidence':evidence,'source_state':state,
        'operation':'bounded-lexical-cue-v1','verification':{'quote_fidelity':'verified_at_creation',
        'semantic_relationship':'NOT VERIFIED','historical_truth':'NOT VERIFIED'},
        'answer_supported':False,'content_truth_verified':False,
        'unresolved':['Lexical cues do not establish event identity, chronology, correction scope or causality.'],**extra}
    result['mapping_id']=digest(result)
    return result


def context_windows(index,passages,max_chars,max_passages,flank=500):
    """Recover neighboring source text across layout/line passage boundaries.

    This is bounded context expansion, not a semantic sentence completion.
    Original retrieval order and all gate decisions remain governing.
    """
    bodies={r.path:body_text(r.body_html) for r in index.records}
    selected=[];used=0
    for p in passages:
        if p.get('retrieval_score') is not None and p['retrieval_score']<=0:continue
        body=bodies[p['path']];start=p['body_start'];end=start+len(p['text'])
        if any(x['path']==p['path'] and x['body_start']<=start and x['body_start']+len(x['text'])>=end for x in selected):continue
        remaining=max_chars-used
        if remaining<end-start or len(selected)>=max_passages:continue
        margin=min(flank,max(0,(remaining-(end-start))//2))
        a=max(0,start-margin);b=min(len(body),end+margin)
        quote=body[a:b]
        item=dict(p,body_start=a,text=quote,context_truncated=(a>0 or b<len(body)),
                  context_operation='exact-canonical-neighbor-window-v1')
        item['id']=digest({'source':p['path'],'hash':p['hash'],'start':a,'text':quote})
        selected.append(item);used+=len(quote)
    return selected


def derive(index,passages,*,max_items=80):
    """Map retrieved contexts; antecedent search is limited to this gated index.

    All sentences remain full supporting contexts. No shortened name, date or
    verb excerpt can replace its context or erase its qualifications.
    """
    if not 1 <= max_items <= 160:raise ValueError('Invalid mapping budget')
    state=_state(index.root,index.question,index.profile)
    mappings=[];relationships=[]
    for passage in passages:
        evidence=[anchor(passage)];quote=passage['text']
        qualifiers=[m[0] for m in QUALIFIER.finditer(quote)]
        common={'qualification_cues':qualifiers,'conflicting_evidence':[],
                'conflict_search':'NOT EXHAUSTIVE; no inferred absence of conflict'}
        mappings.append(_item('statement_appearance',evidence,quote,state,**common))
        for name in list(dict.fromkeys(m[0] for m in ENTITY.finditer(quote)))[:6]:
            mappings.append(_item('entity_appearance_candidate',evidence,name,state,**common))
        if DATES.search(quote):
            mappings.append(_item('date_appearance_candidate',evidence,[m[0] for m in DATES.finditer(quote)],state,date_roles='unresolved',normalized_event_time=None,**common))
        if CONTRADICTION.search(quote):
            mappings.append(_item('disagreement_language_candidate',evidence,[m[0] for m in CONTRADICTION.finditer(quote)],state,conflict_established=False,**common))
        if EVENT.search(quote):
            mappings.append(_item('event_appearance_candidate',evidence,
                [m[0] for m in EVENT.finditer(quote)],state,event_identity=None,date_roles='unresolved',**common))
        if CORRECTION.search(quote) or REFERENCE.search(quote):
            mappings.append(_item('correction_or_correspondence_candidate',evidence,
                [m[0] for m in CORRECTION.finditer(quote)],state,
                predecessor=None,correction_scope='unresolved',supersession_applied=False,**common))
            # Search ordinary prose for potential antecedent context. This is an
            # overlapping-vocabulary lookup, not a claim about direction/date.
            wanted=terms(quote)&terms(index.question)
            if len(wanted)>=2:
                ranked=sorted((len(wanted & terms(p['text'])),p['path'],p['body_start'],p)
                              for p in index.passages if not (p['path']==passage['path'] and p['body_start']<passage['body_start']+len(quote) and passage['body_start']<p['body_start']+len(p['text'])))
                for score,_,_,other in reversed(ranked[-2:]):
                    if score<2:continue
                    relationships.append(_item('possible_related_context',evidence+[anchor(other)],
                        {'shared_query_terms':sorted(wanted&terms(other['text']))},state,
                        operation_basis='shared lexical evidence only',direction=None,causality='NOT ESTABLISHED',
                        predecessor_resolved=False,**common))
        if len(mappings)>=max_items:break
    return {'schema':VERSION,'mappings':mappings[:max_items], 'relationships':relationships[:12],
        'answer_supported':False,'content_truth_verified':False,'semantic_verification':'NOT RUN',
        'budget_truncated':len(mappings)>max_items or len(relationships)>12,
        'notice':'Reversible quote mappings and candidate structures; no verified event identity, correction or causal relationship.'}


def reconstruct(root,question,mapping,profile=None):
    """Re-read currently eligible sources; never trust cached verification flags."""
    profile=_profile(profile)
    rejected={'status':'invalidated','passages':[],'quote_fidelity':False,
              'semantic_relationship_verified':False,'answer_supported':False,'content_truth_verified':False}
    if not isinstance(mapping,dict):return rejected
    unsigned=copy.deepcopy(mapping);identity=unsigned.pop('mapping_id',None)
    if identity!=digest(unsigned) or mapping.get('answer_supported') is not False:return rejected
    before=_state(root,question,profile)
    if before!=mapping.get('source_state'):return dict(rejected,reason='source_or_policy_changed')
    try:index=PassageIndex(root,question,profile)
    except ReaderError as exc:return dict(rejected,reason=exc.code)
    by_path={r.path:r for r in index.records};result=[]
    evidence=mapping.get('evidence')
    if not isinstance(evidence,list) or not 1<=len(evidence)<=2:return rejected
    for e in evidence:
        rec=by_path.get(e.get('path'))
        if rec is None or rec.id!=e.get('source_id') or rec.hash_actual!=e.get('hash'):return rejected
        a,b=e.get('body_start'),e.get('body_end');body=body_text(rec.body_html)
        if type(a) is not int or type(b) is not int or not 0<=a<b<=len(body):return rejected
        if e.get('body_projection')!=BODY_VERSION or body[a:b]!=e.get('quote'):return rejected
        result.append(dict(e,quote=body[a:b]))
    if not index.unchanged() or _state(root,question,profile)!=before:return dict(rejected,reason='source_changed')
    return {'status':'reconstructed','passages':result,'quote_fidelity':True,
            'semantic_relationship_verified':False,'answer_supported':False,'content_truth_verified':False}


def relationship_graph(index, rich, passages, *, max_nodes=160, max_edges=160):
    """Inspection view of existing proposition mappings, never identity merging.

    Documentary appearances and event candidates have separate nodes. Edges
    retain complete existing reversible mappings and current state dependencies.
    """
    nodes=[];edges=[];seen=set();truncated=False
    def node(identifier,kind,**value):
        nonlocal truncated
        if identifier in seen:return identifier
        if len(nodes)>=max_nodes:truncated=True;return None
        seen.add(identifier);nodes.append(dict(id=identifier,kind=kind,**value));return identifier
    def edge(left,right,kind,item):
        nonlocal truncated
        if not left or not right:return
        if len(edges)>=max_edges:truncated=True;return
        edges.append({'from':left,'to':right,'type':kind,'evidence':item['evidence'],
            'mapping_id':item['mapping_id'],'source_state':item['source_state'],
            'interpretation_basis':item.get('operation_basis','finite candidate extraction'),
            'unresolved_issues':['person/event identity not established','intermediate links not supplied by similarity'],
            'source_support_established':False,'historical_truth_independently_verified':False})
    ids={}
    for item in rich.get('propositions',[]):
        e=item['evidence'][0];v=item['value'];occurrence=digest({'path':e['path'],'hash':e['hash'],'start':e['body_start']})
        document=node(occurrence,'document_occurrence',source_id=e['source_id'],hash=e['hash'],evidence=item['evidence'])
        statement=node(item['mapping_id'],'source_statement_candidate',proposition=v,evidence=item['evidence'])
        event=node('event:'+item['mapping_id'],'event_candidate',identity=None,independent_occurrence_verified=False)
        ids[item['mapping_id']]=statement;edge(document,statement,'contains_statement',item);edge(statement,event,'describes_possible_event',item)
        if v.get('actor'):
            mention=node('mention:'+item['mapping_id'],'actor_mention',literal_text=v['actor'],identity=None)
            edge(mention,statement,'candidate_actor_role',item)
    for item in rich.get('connections',[]):
        value=item['value'];refs=[ids[x] for x in value.values() if isinstance(x,str) and x in ids]
        if len(refs)>=2:edge(refs[0],refs[1],item['kind'],item)
    dates=[]
    for item in rich.get('propositions',[]):
        for cue in item['value'].get('date_candidates',[]):
            dates.append({'expression':cue,'proposition':item['mapping_id'],'evidence':item['evidence'],
                          'normalized_event_time':None,'chronology_established':False})
    return {'schema':'derived-documentary-graph-v1','nodes':nodes,'edges':edges,'date_appearances':dates[:64],
            'budget_truncated':truncated or len(dates)>64,'event_identity_merges':0,
            'answer_supported':False,'source_support_established':False,'historical_truth_independently_verified':False,
            'notice':'Reversible candidate graph. Shared wording, subjects and dates never merge historical events.'}
