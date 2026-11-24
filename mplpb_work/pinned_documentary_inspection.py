"""Opt-in checks over explicitly selected source occurrences."""
from datetime import date
import re

from mplpb_answers.documentary_links import chain as _chain, whole_source as _whole_source
from mplpb_answers.documentary_verify import wording_difference
from mplpb_answers.evidence_contract import ReaderError
from mplpb_answers.passages import PassageIndex
from mplpb_answers.pipeline import answer_query

_LENGTHS = {'wording': 2, 'writing_dates': 2, 'request_dispatch_receipt': 3}
_SOURCE_ID = re.compile(r'[A-Za-z0-9][A-Za-z0-9._-]{0,99}')


def _wording(records, source_ids, max_passages, max_chars):
    if max_passages < 2:
        return {'missing': ['room for both source citations']}
    witnesses = [_whole_source(records.get(ident), max_chars) for ident in source_ids]
    if not all(witnesses):
        return {'missing': ['two complete eligible source bodies within the evidence budget']}
    left, right = (witness['quote'] for witness in witnesses)
    result = wording_difference(left, right)
    if result is None or len(left) + len(right) > max_chars:
        return {'missing': ['both complete bodies within the comparison budget']}
    return {'citations': witnesses, 'alignment': result['alignment'],
            'identical_canonical_text': left == right,
            'comparison_scope': 'canonical text of the two selected source bodies'}


def _writing_dates(index, records, source_ids, max_passages, max_chars):
    observed, witnesses, missing = [], [], []
    for ident in source_ids:
        if ident not in records:
            missing.append('eligible source ' + ident)
            continue
        answer = answer_query(index.root, index.question, index.profile, record_id=ident,
                              field='Date Written', max_passages=max_passages,
                              max_chars=max_chars).contract
        if answer['diagnostic']['code'] == 'source_changed':
            return {'missing': [], 'status': 'source_changed'}
        claims = answer['claims']
        if not answer['answer_supported'] or len(claims) != 1:
            missing.append('one explicit writing date in ' + ident)
            continue
        match = re.fullmatch(r'Date Written:\s*(\d{4}-\d{2}-\d{2})', claims[0]['text'], re.I)
        checked = claims[0]['citations']
        if not match or len(checked) != 1 or checked[0]['source_id'] != ident:
            missing.append('one ISO calendar writing date in ' + ident)
            continue
        try:
            value = date.fromisoformat(match[1]).isoformat()
        except ValueError:
            missing.append('valid calendar writing date in ' + ident)
            continue
        if len(witnesses) == max_passages or sum(len(c['quote']) for c in witnesses + checked) > max_chars:
            missing.append('room for the writing-date citation in ' + ident)
            continue
        witnesses.extend(checked)
        observed.append({'source_id': ident, 'date': value, 'role': 'declared_writing_date'})
    earliest = []
    if not missing:
        first = min(row['date'] for row in observed)
        earliest = [row['source_id'] for row in observed if row['date'] == first]
    return {'writing_dates': observed, 'earliest_sources': earliest,
            'citations': witnesses, 'missing': missing}


def inspect(root, question, profile, operation, source_ids, max_passages, max_chars):
    """Read current native sources and return source-scoped observations only."""
    if (operation not in _LENGTHS or not isinstance(source_ids, (tuple, list))
            or len(source_ids) != _LENGTHS[operation] or any(
                not isinstance(ident, str) or not _SOURCE_ID.fullmatch(ident) for ident in source_ids)
            or len(set(source_ids)) != len(source_ids)):
        raise ValueError('Select distinct exact ledger source IDs for this inspection')
    report = {'operation': operation, 'selected_sources': list(source_ids),
              'citations': [], 'answer_supported': False, 'event_identity_verified': False,
              'historical_priority_verified': False, 'content_truth_verified': False}
    try:
        index = PassageIndex(root, question, profile)
        records = {r.id: r for r in index.records if r.id in source_ids}
        if operation == 'wording':
            results = _wording(records, source_ids, max_passages, max_chars)
        elif operation == 'writing_dates':
            results = _writing_dates(index, records, source_ids, max_passages, max_chars)
        else:
            results = _chain(records, source_ids, max_passages, max_chars)
        if not index.unchanged() or results.get('status') == 'source_changed':
            return dict(report, status='source_changed', missing=['current eligible source evidence'])
    except ReaderError as exc:
        return dict(report, status=exc.code, missing=['current eligible source evidence'])
    report.update(results)
    report.setdefault('missing', [])
    report['status'] = ('complete' if not report['missing'] else
                        'partial' if report['citations'] else 'unresolved')
    return report
