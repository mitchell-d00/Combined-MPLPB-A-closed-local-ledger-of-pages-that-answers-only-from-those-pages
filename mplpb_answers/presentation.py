"""Deterministic presentation of native proof and its boundaries."""
from copy import deepcopy

from .evidence_contract import pin

LAYOUTS = ('compact', 'stacked')
FOLLOW_UP_FLAGS = ('auto', 'none', 'lookup', 'investigate', 'assisted')
SEAM_FLAGS = frozenset({
    'current', 'retired', 'eligible', 'conflict', 'seam:handoff',
    'seam:interpretation', 'seam:discovery', 'seam:verification',
    'pass:source-body', 'pass:inspection', 'pass:history', 'boundary:scope',
    'boundary:open', 'boundary:warning', 'relation:checked', 'candidate:locator',
    *FOLLOW_UP_FLAGS,
})


def system_tags(observation, decision, requested, selected):
    """Compute active presentation flags from the Observer and Judge records."""
    seam = {
        'interpretation': 'seam:interpretation',
        'passage_admission': 'seam:discovery',
        'documentary_verification': 'seam:verification',
    }.get(observation['stopped_at'])
    tags = {'current', 'seam:handoff', requested}
    if seam:
        tags.add(seam)
    if selected:
        tags.update(('pass:inspection', selected))
    if observation['strict_kind'] == 'conflict':
        tags.add('conflict')
    if decision['warnings'] or decision['unresolved']:
        tags.add('boundary:warning')
    if decision['unresolved']:
        tags.add('boundary:open')
    if any(warning['code'] == 'source_scope' for warning in decision['warnings']):
        tags.add('boundary:scope')
    if any(claim['citations'] for claim in decision['claims']):
        tags.update(('eligible', 'pass:source-body'))
    if any((claim.get('proposition') or {}).get('relation') for claim in decision['claims']):
        tags.add('relation:checked')
    return sorted(tags)


def investigation_hint(contract):
    """Suggest a proof step. Only existing strict citations can accompany it."""
    diagnostic = contract['diagnostic']
    if contract['answer_supported'] or diagnostic['category'] in {
            'absent_eligible_source', 'source_state_changed', 'flag_mismatch'}:
        return None
    if contract['kind'] == 'conflict':
        step = 'Compare the cited statements and check which scope each one names.'
    elif contract['kind'] == 'partial_answer':
        step = 'Look for an explicit source link that establishes the unresolved part.'
    elif diagnostic['code'] == 'interpretation_unsupported':
        step = 'Try identifying the kind of proof the question needs, such as a date, duration, or relationship.'
    else:
        step = 'Inspect the existing evidence for a passage that directly addresses the question.'
    citations = [cite for claim in contract['claims']
                 if claim.get('source_support_established') is True
                 for cite in claim['citations']]
    return {'label': 'Educated guess · what to check next', 'seam': diagnostic['code'],
            'text': step, 'citations': deepcopy(citations), 'answer_supported': False}


def observe(contract, documentary_plan, discovery=None):
    """Record native decisions alongside optional evaluation-only diagnostics."""
    diagnostic = contract['diagnostic']
    stopped = ('interpretation' if diagnostic['code'] == 'interpretation_unsupported'
               else None if contract['answer_supported'] else diagnostic.get('stage'))
    return {
        'question': contract['question'],
        'documentary_plan': documentary_plan,
        'native_question_parts': contract.get('question_parts', []),
        'discovery': discovery,
        'strict_kind': contract['kind'],
        'stopped_at': stopped,
        'answer_supported': contract['answer_supported'],
        'diagnostic': diagnostic,
        'strict_claims': deepcopy(contract['claims']),
        'unresolved': deepcopy(contract['missing']),
        'truth_verified': contract['verification']['truth_verified'],
    }


def judge(observation):
    """Select boundaries from trusted observations and carry native claims only."""
    kind = observation['strict_kind']
    code = observation['diagnostic']['code']
    discovery = observation['discovery']
    warnings = []
    if observation['diagnostic']['category'] == 'absent_eligible_source':
        warnings.append({'code': 'no_eligible_evidence',
                         'text': 'No eligible source evidence could be served for this question.'})
    if code == 'interpretation_unsupported':
        warnings.append({'code': 'proof_rule_missing',
                         'text': 'Strict Ask could not turn this question into a proof check.'})
    if discovery and discovery['found_under_budget'] < discovery['reference_spans']:
        warnings.append({'code': 'search_span_missed',
                         'text': 'The search probe missed required passages at this budget.'})
    if discovery and discovery['split_quote_failures']:
        warnings.append({'code': 'quote_unit_boundary',
                         'text': 'One combined quote crosses a statement boundary. Its separate pieces passed.'})
    claims = observation['strict_claims']
    if kind == 'conflict':
        warnings.append({'code': 'conflicting_witnesses',
                         'text': 'The source statements compete. There is no single verified answer.'})
        heading = 'Competing source statements'
    elif kind == 'partial_answer':
        warnings.append({'code': 'required_part_unresolved',
                         'text': 'The cited evidence verifies only part of the requested answer.'})
        claims = [c for c in claims if c.get('source_support_established') is True]
        heading = 'Verified parts'
    elif kind == 'supported_answer' and observation['answer_supported']:
        heading = 'Source-supported answer'
    else:
        heading, claims = 'No complete answer established', []
    claims = [c for c in claims if c.get('citations')]
    if claims and not observation['truth_verified']:
        warnings.append({'code': 'source_scope', 'text':
                         'The checks establish what the cited records say. Outside-world confirmation remains open.'})
    unresolved = observation['unresolved']
    if not unresolved and kind != 'supported_answer':
        unresolved = [observation['diagnostic']['message']]
    return {'heading': heading, 'claims': deepcopy(claims), 'unresolved': deepcopy(unresolved),
            'warnings': warnings, 'answer_supported': observation['answer_supported']}


def present(decision, model_reply=None):
    """The model can choose a layout. The Judge supplies every displayed word."""
    accepted = isinstance(model_reply, str) and model_reply.strip() in LAYOUTS
    layout = model_reply.strip() if accepted else 'compact'
    lines = [decision['heading']]
    for claim in decision['claims']:
        lines.append(claim['text'])
        lines.extend('Scope: ' + qualifier for qualifier in claim.get('qualifiers', []))
        lines.extend('Boundary: ' + warning['text'] for warning in decision['warnings']
                     if warning['code'] == 'source_scope')
        for cite in claim['citations']:
            lines.append(f"[{cite['source_id']} {cite['hash']}] {cite['quote']}")
    lines.extend('Open: ' + gap for gap in decision['unresolved'])
    lines.extend('Boundary: ' + warning['text'] for warning in decision['warnings']
                 if warning['code'] != 'source_scope')
    separator = '\n\n' if layout == 'stacked' else '\n'
    return {'layout': layout, 'model_layout_accepted': accepted,
            'text': separator.join(lines), 'decision_sha256': pin(decision),
            'answer_supported': decision['answer_supported']}
