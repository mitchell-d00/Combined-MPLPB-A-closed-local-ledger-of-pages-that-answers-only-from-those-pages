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
    from .source_mapping import relationship_graph
    mapping['relationship_graph']=relationship_graph(index,mapping['proposed_reconstruction'],pack['passages'])
    # Keep structure/layers separate from propositions and historical authority.
    mapping['source_unit_index']=index.documentary_units(max_chars=200000,max_units=1000)
    if not index.unchanged() or verification_snapshot(root,question,profile)!=initial:
        return dict(empty,status='source_changed',source_state_current=False)
    return dict(empty,status='candidate_contexts' if candidates else 'no_matching_contexts',candidates=candidates,
                source_state_current=True,information_map=mapping,search_complete=pack['search_complete'],
                budgets={'max_passages':max_passages,'max_characters':max_chars},
                retrieval_method=pack['ranking'],retrieval_discovery={k:v for k,v in pack.items() if k in {'query_expansion_terms','facets','routing_metadata_is_answer_evidence'}})


def reconstruct_report(root,question,profile=None,*,max_passages=12,max_chars=12000,reader=None,inspection=None):
    """Existing native answers and reversible research views, with final gate."""
    from mplpb_answers.pipeline import answer_query
    profile=profile or PROFILES[DEFAULT_PROFILE]
    before=verification_snapshot(root,question,profile)
    answer=answer_query(root,question,profile,max_passages=max_passages,max_chars=max_chars).contract
    candidates=discover(root,question,profile,max_passages=max_passages,max_chars=max_chars)
    pinned = None
    if inspection is not None:
        from .pinned_documentary_inspection import inspect
        operation, source_ids = inspection
        pinned = inspect(root, question, profile, operation, source_ids, max_passages, max_chars)
    assisted=None
    if reader is not None:
        # The existing reader validates schema, exact anchors and model pins.
        # Its output stays explicitly model-assisted even after favorable review.
        assisted=answer_query(root,question,profile,mode='assisted',reader=reader,
                             max_passages=max_passages,max_chars=max_chars).contract
    if verification_snapshot(root,question,profile)!=before:
        return {'schema':'historical-reconstruction-report-v1','question':question,'status':'source_changed',
                'native_answer':None,'candidate_analysis':None,'model_candidates':None,'answer_supported':False}
    report = {'schema':'historical-reconstruction-report-v1','question':question,'status':'research_report',
            'native_answer':answer,'candidate_analysis':candidates,'model_candidates':assisted,
            'answer_supported':answer['answer_supported'],'historical_truth_independently_verified':False,
            'notice':'Checked source assertions, reversible candidate graphs, model interpretations and historical truth have separate authority.'}
    if pinned is not None:
        report['pinned_inspection'] = pinned
    return report


def render_reconstruction(report):
    """Render existing checked/candidate states without deriving new support.

    This is a snapshot for inspection. Rerun reconstruct_report to recheck state.
    """
    lines = ['HISTORICAL RESEARCH REPORT', 'Question: '+report['question']]
    if report['status'] != 'research_report':
        return '\n'.join(lines + ['Source state changed; no old evidence accepted.'])
    answer = report['native_answer']
    lines += ['Result: '+answer['kind'],
              'Snapshot only; rerun this command to recheck current eligibility.',
              answer.get('source_assurance', {}).get('notice',
                  'Source assertions do not independently establish historical truth.')]
    obligations = answer.get('documentary_support', {}).get('obligations', [])
    if obligations:
        lines.append('Question parts:')
        for goal in obligations:
            refs = ', '.join(str(i+1) for i in goal.get('evidence_claim_indices', [])) or 'none displayed'
            lines += ['- '+goal['question']+' ['+goal['status']+']; evidence: '+refs]
            if goal.get('undisplayed_evidence_count'):
                lines.append('  Additional evidence exceeds the display budget.')
    lines.append('Checked documentary evidence:')
    for i, claim in enumerate(answer['claims'], 1):
        # Assisted proposals are rendered separately, never under this heading.
        lines.append(str(i)+'. '+claim['text'])
        for qualifier in claim.get('qualifiers', []):lines.append('   Qualification: '+qualifier)
        for cite in claim.get('citations', []):
            lines.append('   ['+cite['source_id']+'@'+cite['hash']+' '+cite['path']+
                         ' canonical '+str(cite.get('body_start', cite.get('start')))+':'+
                         str(cite.get('body_end', cite.get('end')))+']')
            lines.append('   '+cite['quote'])
    if not answer['claims']:lines.append('None established.')
    for cite in answer.get('documentary_support', {}).get('alternative_evidence', []):
        lines += ['Alternative/qualifying evidence ['+cite['source_id']+'@'+cite['hash']+']:', cite['quote']]
    if answer.get('missing'):lines += ['Unresolved:']+['- '+m for m in answer['missing']]
    if answer.get('diagnostic'):lines.append('Diagnostic: '+answer['diagnostic']['code']+' — '+answer['diagnostic']['message'])
    pinned = report.get('pinned_inspection')
    if pinned:
        lines += ['Selected-source inspection [' + pinned['status'] + ']', pinned['operation']]
        for witness in pinned['citations']:
            lines += ['[' + witness['source_id'] + '@' + witness['hash'] + ']', witness['quote']]
        if 'identical_canonical_text' in pinned:
            lines.append('Identical canonical text: ' + str(pinned['identical_canonical_text']))
            for hunk in pinned['alignment']:
                if hunk['operation'] != 'equal':
                    lines += ['Source A: ' + hunk['left_text'], 'Source B: ' + hunk['right_text']]
        if pinned.get('earliest_sources'):
            lines.append('Earliest declared writing date among selected sources: ' + ', '.join(pinned['earliest_sources']))
        if pinned['missing']:
            lines.append('Unresolved: ' + ', '.join(pinned['missing']))
    candidates = report.get('candidate_analysis') or {}
    graph = (candidates.get('information_map') or {}).get('relationship_graph') or {}
    lines += ['Candidate historical interpretation: '+str(len(graph.get('edges', [])))+
              ' graph edges; unverified and never promoted to source support.',
              'Candidate search complete: '+str(candidates.get('search_complete', False))]
    if report.get('model_candidates'):
        lines.append('Model proposals are present in JSON output; they are not checked historical conclusions.')
    return '\n'.join(lines)
