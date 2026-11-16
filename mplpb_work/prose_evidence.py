"""Opt-in source-context discovery for unprepared prose, never reconstruction proof.

Dates, correction words and correspondence verbs are inspection cues. No cue
creates an event identity, causal edge, correction, supersession or answer.
"""
import re
from mplpb_answers.passages import PassageIndex
from mplpb_answers.evidence_contract import ReaderError
from mplpb_combined.reader import PROFILES,DEFAULT_PROFILE
from .historical_verifier import verification_snapshot

VERSION='unprepared-prose-candidates-v2'
DATE=re.compile(r'\b(?:\d{4}-\d{2}-\d{2}|(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}(?:st|nd|rd|th|d)?(?:,)?\s+\[?\d{4}\]?)\b',re.I)
CORRECTION=re.compile(r'\b(?:correct(?:ed|ing|ion|ions)?|revis(?:ed|ion|ions)|replace(?:d|ment)?|change(?:d|s)?|amend(?:ed|ment)?|errat[au])\b',re.I)
RELATION=re.compile(r'\b(?:wrote|written|read|received|sent|send|replied|published|reported|withdrawal|withdrew|superseded)\b',re.I)
UNCERTAIN=re.compile(r'\b(?:if|perhaps|may|might|could|alleged|reported|uncertain|unknown|suppose)\b',re.I)


def discover(root,question,profile=None,*,max_passages=12,max_chars=12000):
    profile=profile or PROFILES[DEFAULT_PROFILE]
    if profile.name not in PROFILES or profile!=PROFILES[profile.name]:raise ValueError('Choose a known delivery profile')
    empty={'schema':VERSION,'candidates':[],'answer_supported':False,'content_truth_verified':False,
           'event_identities':[],'relationships':[],'applied_corrections':[],
           'notice':'Lexically retrieved source context only. No event identity, chronology, correction or causal relationship is established.'}
    initial=verification_snapshot(root,question,profile)
    try:
        index=PassageIndex(root,question,profile)
        seed=index.retrieve([question],max_passages,max_chars)
        from mplpb_answers.prose_retrieval import retrieve
        pack=retrieve(index,max_passages,max_chars,seed=seed)
    except ReaderError as exc:return dict(empty,status=exc.code,source_state_current=False)
    from .source_mapping import context_windows
    pack['passages']=context_windows(index,pack['passages'],max_chars,max_passages)
    pack['search_complete']=False  # Bounded contexts never establish complete semantic search.
    candidates=[]
    for passage in pack['passages']:
        if passage.get('retrieval_score') is not None and passage['retrieval_score']<=0:continue
        quote=passage['text'];start=passage['body_start'];types=['source_context']
        mentions=[{'raw_text':m[0],'start':start+m.start(),'end':start+m.end(),
                   'date_role':'unresolved_document_event_publication_or_revision','normalized_event_time':None} for m in DATE.finditer(quote)]
        if mentions:types.append('dated_context')
        if CORRECTION.search(quote):types.append('possible_correction_context')
        if RELATION.search(quote):types.append('possible_correspondence_or_relationship_context')
        flags=['semantic_interpretation_not_verified']
        if mentions:flags.append('date_role_unresolved')
        if passage['context_truncated']:flags.append('context_window_incomplete')
        if UNCERTAIN.search(quote):flags.append('qualification_or_uncertainty_language_preserved')
        candidates.append({'candidate_id':passage['id'],'kind':'source_context_candidate','candidate_types':types,
            'source_id':passage['source_id'],'path':passage['path'],'hash':passage['hash'],
            'body_start':start,'body_end':start+len(quote),'quote':quote,
            'date_mentions':mentions,'uncertainty_flags':flags,'answer_supported':False,'content_truth_verified':False,
            'identity_resolution':'NOT ESTABLISHED','causal_inference':'PROHIBITED'})
    from .source_mapping import derive
    mapping=derive(index,pack['passages'])
    from .prose_relations import extract
    from .source_mapping import _state
    mapping['proposed_reconstruction']=extract(index,pack['passages'],_state(root,question,profile))
    if not index.unchanged() or verification_snapshot(root,question,profile)!=initial:
        return dict(empty,status='source_changed',source_state_current=False)
    return dict(empty,status='candidate_contexts' if candidates else 'no_matching_contexts',candidates=candidates,
                source_state_current=True,information_map=mapping,search_complete=pack['search_complete'],
                budgets={'max_passages':max_passages,'max_characters':max_chars},
                retrieval_method=pack['ranking'],retrieval_discovery={k:v for k,v in pack.items() if k in {'query_expansion_terms','facets','routing_metadata_is_answer_evidence'}})
