"""Coordinate bounded read-only paths while preserving the strict proof contract."""
from mplpb_combined import provenance_gate
from mplpb_combined import reader as ownership
from .pipeline import answer_query, _graph_withhold
from .presentation import FOLLOW_UP_FLAGS as PATHS


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


def _changed(result):
    result.update(status='source_changed', answer_supported=False, strict=None,
                  suggested_path=None, next_step='Retry after the source update completes.', inspection=None)
    return result


def _graph_blocked(native):
    result = {'schema': 'mplpb-advanced-v1', 'status': native.contract['kind'], 'answer_supported': False,
              'strict': native.contract, 'suggested_path': None, 'next_step': None,
              'inspection': None, 'flag_sync': native.sync}
    if native.contract['diagnostic']['code'] == 'source_changed':
        return _changed(result)
    return result


def advanced_query(root, question, profile=None, *, follow_up='auto', reader=None,
                   experience_graph=None):
    """Run strict Ask first, then at most one explicitly labeled inspection."""
    if follow_up not in PATHS:
        raise ValueError('Unknown follow-up path')
    if reader is not None and follow_up != 'assisted':
        raise ValueError('Choose the assisted follow-up to use a configured reader')
    if follow_up == 'assisted' and reader is None:
        raise ValueError('Assisted follow-up requires a configured local reader')
    profile = profile or ownership.PROFILES[ownership.DEFAULT_PROFILE]
    native = answer_query(root, question, profile, experience_graph=experience_graph)
    strict = native.contract
    if experience_graph is not None and (native.sync or {}).get('status') != 'matched':
        return _graph_blocked(native)
    suggested, next_step = _route(strict)
    prior = None
    seeds = []
    if experience_graph is not None:
        import sqlite3
        from . import experience_graph as graph
        graph_scope, graph_state = graph.graph_keys(root, native)
        try:
            prior = graph.previous(experience_graph, graph_scope, graph_state)
        except (OSError, ValueError, sqlite3.Error):
            native.sync = {'status': 'mismatch', 'reason': 'graph_unavailable', 'differences': []}
            return _graph_blocked(_graph_withhold(native, 'FLAG_MISMATCH',
                'The experience route could not be read.'))
        if follow_up == 'auto' and suggested == 'lookup' and prior and prior['flag'] in {'lookup', 'investigate'}:
            eligible = {source['id'] for source in native.gate['sources']}
            seeds = sorted(eligible.intersection(prior['candidates']))[:4]
            if seeds:
                suggested = 'investigate'
                next_step = 'The earlier pass located a candidate. Inspect eligible declared relationships.'
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
    if selected is None and experience_graph is None:
        return result

    candidates = []
    if selected == 'lookup':
        paths = {source['path'] for source in native.gate['sources']}
        candidate = ownership.answer(root, question, profile, _eligible_paths=paths)
        candidates = ([candidate.record.id] if candidate.kind == ownership.RETURN else
                      [record.id for record, _ in candidate.candidates])
        detail = {'kind': 'candidate_only' if candidate.kind == ownership.RETURN else candidate.kind,
                  'source_ids': candidates}
    elif selected == 'investigate':
        from mplpb_work.investigation import investigate
        detail = investigate(root, question, profile=profile, max_hops=1, max_sources=4,
                             **({'start_source_ids': seeds} if seeds else {}))
        candidates = seeds
    elif selected == 'assisted':
        detail = answer_query(root, question, profile, mode='assisted', reader=reader).contract

    if (provenance_gate.gather(root, question, profile).corpus_snapshot
            != native.gate['corpus_snapshot']):
        return _changed(result)

    if selected is not None:
        result['inspection'] = {'path': selected, 'answer_supported': False, 'detail': detail}
    if experience_graph is not None:
        from .documentary import plan
        from .presentation import judge, observe, present

        observation = observe(strict, plan(question))
        decision = judge(observation)
        pass_graph = graph.graph_nodes(observation, decision, follow_up, selected, prior, candidates,
                                       native.gate['corpus_snapshot'])
        try:
            pass_id = graph.append(experience_graph, graph_scope, graph_state, selected,
                                   candidates, prior, pass_graph)
        except (OSError, ValueError, sqlite3.Error):
            native.sync = {'status': 'mismatch', 'reason': 'graph_unavailable', 'differences': []}
            return _graph_blocked(_graph_withhold(native, 'FLAG_MISMATCH',
                'The inspection pass could not be recorded.'))
        fresh = provenance_gate.gather(root, question, profile)
        if (fresh.corpus_snapshot, fresh.policy) != (native.gate['corpus_snapshot'], native.gate['policy']):
            return _changed(result)
        native.sync = graph.recheck_path(experience_graph, native.sync)
        if native.sync['status'] != 'matched':
            return _graph_blocked(_graph_withhold(native, 'FLAG_MISMATCH',
                'Strict presentation was withheld because graph flags changed during inspection.'))
        inspected = graph.recheck_path(experience_graph, {'status': 'matched', 'pass_id': pass_id,
                                                           'path': pass_graph, 'scope': graph_scope,
                                                           'state': graph_state})
        if inspected['status'] != 'matched':
            native.sync = inspected
            return _graph_blocked(_graph_withhold(native, 'FLAG_MISMATCH',
                'The inspection pass did not match the active system flags.'))
        result['experience'] = {'status': 'ready', 'pass_id': pass_id,
                                'graph': pass_graph, 'presentation': present(decision)}
        result['flag_sync'] = native.sync
    if (experience_graph is not None and selected == 'assisted' and not strict['answer_supported']
            and detail['kind'] in {'model_assisted_answer', 'partial_answer'}
            and any(claim['citations'] for claim in detail['claims'])):
        result['inspection']['label'] = 'Educated guess · cited interpretation'
    return result
