"""Reduction-to-determination: eligibility first, reproducible choice second.

This policy checks declared candidate contracts; it is not semantic entailment.
Source-specific gates must establish support before submitting a factual candidate.
"""
VERSION='reduction-to-determination-v2'
RULE='REDUCE-DETERMINE'


def determine(candidates, mode, turn=1):
    if mode not in {'chat','focus'}:raise ValueError('Unknown determination mode')
    ids=[c['id'] for c in candidates]
    if len(ids)!=len(set(ids)):raise ValueError('Candidate IDs must be unique')
    retained=[];removed=[]
    for candidate in sorted(candidates,key=lambda c:c['id']):
        reasons=list(candidate.get('failures',[]))
        basis=candidate.get('basis')
        if basis not in {'conversation','source_assertion','deduction','reference','procedure','uncertainty'}:
            reasons.append('Unknown response basis')
        if mode=='focus' and basis=='conversation' and not candidate.get('nonfactual_conversation'):
            reasons.append('Conversation must be explicitly separated from factual evidence')
        if basis in {'source_assertion','deduction'} and not candidate.get('support_checked'):
            reasons.append('Source-specific support checks have not passed')
        if basis=='source_assertion' and not candidate.get('sources'):reasons.append('No source pins')
        if basis=='deduction' and (not candidate.get('premises') or not candidate.get('rules')):
            reasons.append('A deduction requires explicit premises and rules')
        if basis=='deduction' and any(rule not in {'FACT-1','TYPE-1','TYPE-2'} for rule in candidate.get('rules',[])):
            reasons.append('Unknown inference rule')
        if reasons:removed.append({'id':candidate['id'],'reasons':reasons})
        else:retained.append(candidate)
    meanings={c.get('meaning',c['id']) for c in retained}
    selected=None
    if not retained:outcome='no_eligible_candidate'
    elif len(meanings)>1:outcome='clarify_or_present_alternatives'
    else:
        selected=retained[(max(1,turn)-1)%len(retained)]
        outcome='unique' if len(retained)==1 else 'equivalent_wording_selected'
    return selected,{'rule':RULE,'version':VERSION,'mode':mode,'outcome':outcome,
                     'retained':[c['id'] for c in retained],'eliminated':removed,
                     'selected':selected['id'] if selected else None,
                     'basis':selected['basis'] if selected else None,
                     'selection_order':'candidate ID; saved turn offset for equivalent wording',
                     'elimination_creates_evidence':False}


def wording(options, meaning, turn):
    candidate,trace=determine([{'id':str(i).zfill(4),'basis':'conversation','meaning':meaning,'text':text} for i,text in enumerate(options)],'chat',turn)
    return candidate['text'],trace


def adjudicate(result, mode):
    """Final mode guard; preserve refusals, alternatives and source provenance."""
    kind=result.get('kind');structure=result.get('response_structure',{})
    if result.get('scope_results'):
        result['scope_results']=[dict(item,response=adjudicate(item['response'],'focus')) for item in result['scope_results']]
    casual=(structure.get('intent','').startswith(('casual_','social_')) or kind=='smalltalk')
    basis='conversation' if casual else 'procedure'
    if kind in {'unsupported','clarify','ambiguous','not_in_corpus','unknown_relation','conflict'}:basis='uncertainty'
    elif kind=='federated_answers':basis='uncertainty'
    elif result.get('authority')=='lexical_reference':basis='reference'
    elif kind in {'return','summary','grounded_answer'}:basis='source_assertion'
    elif kind=='relations':
        inferred=any('TYPE-1' in r.get('rules',[]) or 'TYPE-2' in r.get('rules',[]) for r in result.get('relations',[]))
        basis='deduction' if inferred else 'source_assertion'
    elif result.get('authority')=='conversation_structure' and mode=='chat':basis='conversation'
    candidate={'id':'response','basis':basis,'meaning':kind,'sources':result.get('sources',[]),
               'support_checked':bool(result.get('sources')),
               'nonfactual_conversation':structure.get('factual_claims') is False and not result.get('sources'),
               'premises':[p for r in result.get('relations',[]) for p in r.get('premises',[])],
               'rules':[rule for r in result.get('relations',[]) for rule in r.get('rules',[])]}
    selected,trace=determine([candidate],mode)
    if selected is None:
        from tools import deterministic_mind as M
        result=M.reply('unsupported','No response meets the active mode’s requirements. In MPLPB focus mode, choose a supported page question; use Just chat for playful conversation.',result.get('context'),RULE,
                       suggestions=['show my MPLPB','just chat'],authority='unsupported')
    result['determination']=trace
    return result
