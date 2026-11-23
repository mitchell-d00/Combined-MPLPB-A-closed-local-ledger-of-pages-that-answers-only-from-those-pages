"""Coordinate bounded read-only paths while preserving the strict proof contract."""
from mplpb_combined import provenance_gate
from mplpb_combined import reader as ownership
from .pipeline import answer_query

PATHS = ('auto', 'none', 'lookup', 'investigate', 'assisted')


def _route(strict):
    kind = strict['kind']
    category = strict['diagnostic']['category']
    if strict['answer_supported']:
        return None, None
    if category == 'source_state_changed':
        return None, 'Retry after the source update completes.'
    if category == 'absent_eligible_source':
        return None, 'Check the collection and source eligibility.'
    if kind == 'conflict':
        return None, 'Review the competing sources or specify the intended record.'
    if kind == 'clarify' or category == 'clarification_required':
        return None, 'Clarify the subject, source, or requested scope.'
    if category == 'index_exhaustion':
        return None, 'Narrow the question or split its evidence requirements.'
    if kind == 'partial_answer':
        return 'investigate', 'Inspect the declared links for the unresolved part.'
    return 'lookup', 'Find an eligible record to inspect. Use investigation to follow its declared links.'


def advanced_query(root, question, profile=None, *, follow_up='auto', reader=None):
    """Run strict Ask first, then at most one explicitly labeled inspection."""
    if follow_up not in PATHS:
        raise ValueError('Unknown follow-up path')
    if reader is not None and follow_up != 'assisted':
        raise ValueError('Choose the assisted follow-up to use a configured reader')
    if follow_up == 'assisted' and reader is None:
        raise ValueError('Assisted follow-up requires a configured local reader')
    profile = profile or ownership.PROFILES[ownership.DEFAULT_PROFILE]
    native = answer_query(root, question, profile)
    strict = native.contract
    suggested, next_step = _route(strict)
    if follow_up == 'auto':
        selected = suggested
    elif follow_up == 'none' or strict['diagnostic']['category'] in {
        'source_state_changed', 'absent_eligible_source'
    }:
        selected = None
    elif follow_up == 'assisted' and (strict['answer_supported'] or strict['kind'] in {'conflict', 'clarify'}
                                      or strict['diagnostic']['category'] == 'clarification_required'):
        selected = None
    else:
        selected = follow_up

    result = {'schema': 'mplpb-advanced-v1', 'status': strict['kind'],
              'answer_supported': strict['answer_supported'], 'strict': strict,
              'suggested_path': suggested, 'next_step': next_step, 'inspection': None}
    if selected is None:
        return result

    if selected == 'lookup':
        paths = {source['path'] for source in native.gate['sources']}
        candidate = ownership.answer(root, question, profile, _eligible_paths=paths)
        candidates = ([candidate.record.id] if candidate.kind == ownership.RETURN else
                      [record.id for record, _ in candidate.candidates])
        detail = {'kind': 'candidate_only' if candidate.kind == ownership.RETURN else candidate.kind,
                  'source_ids': candidates}
    elif selected == 'investigate':
        from mplpb_work.investigation import investigate
        detail = investigate(root, question, profile=profile, max_hops=1, max_sources=4)
    else:
        detail = answer_query(root, question, profile, mode='assisted', reader=reader).contract

    if (provenance_gate.gather(root, question, profile).corpus_snapshot
            != native.gate['corpus_snapshot']):
        result.update(status='source_changed', answer_supported=False, strict=None,
                      suggested_path=None, next_step='Retry after the source update completes.')
        return result

    result['inspection'] = {'path': selected, 'answer_supported': False, 'detail': detail}
    return result
