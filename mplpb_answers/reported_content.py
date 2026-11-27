"""Bounded native verification of report/content roles and scoped polarity.

Question parsing selects an operation. Only a fresh eligible original and its
complete governing clause can certify the source-scoped claim. Reported and
conditional content never certify independent authorship or occurrence.
"""
import hashlib
import html
import re

from . import documentary_verify as kernel
from .claim_frame import ClaimFrame
from .source_attribution import unqualified_span, printed_writer_label

_PERSON = r'[^,;:!?“”"\n]{2,120}?'
_OBJECT = r'the [\w -]{2,180}?'
_REPORT_FORMS = {
    **{word:(False,False) for word in ('reported','stated','reports','states','said','says')},
    **{prefix+word:(True,False) for prefix in ('did not ','does not ') for word in ('report','state','say')},
    'would report':(False,True), 'would not report':(True,True),
}
_REPORT_VERBS = '|'.join(re.escape(word) for word in sorted(_REPORT_FORMS,key=len,reverse=True))
_PASSIVE_FORMS = {'was reported':(False,False),'was not reported':(True,False),
                  'would be reported':(False,True),'would not be reported':(True,True)}

_REPORT_OBJECT = (
    rf'(?:What|Which document) did (?P<reporter>{_PERSON}) (?:say|state|report) '
    rf'(?:that )?(?P<author>{_PERSON}) wrote'
)
_NAMED_REPORT = (
    rf'In the report written by (?P<writer>{_PERSON}),\s+{_REPORT_OBJECT}[?.]',
    rf'{_REPORT_OBJECT},\s+in the document from (?P<writer>{_PERSON})[?.]',
)
_BYLINE = re.compile(r'^(?:Written by |Report by |From: )(?P<writer>[^\n]+?)\.?$', re.M | re.I)
_FROM_PARAGRAPH = re.compile(
    r'\s*(?:<h1>[^<>]*</h1>\s*)?<p>(From: [^<>\r\n]{1,120})</p>\s*'
    r'<p>([^<>\r\n]{1,1800})</p>', re.I
)


def _object_goal(match):
    return dict(match.groupdict(), object=None, conditional=False, form=None,
                required_outer_negative=False, required_inner_negative=False)


def request(question):
    q = kernel.source_question(question)
    for pattern in _NAMED_REPORT:
        match = re.fullmatch(pattern, q, re.I)
        if match and all(kernel.named_actor(name) for name in match.groupdict().values()):
            return _object_goal(match)
    from .ordinary_questions import request as ordinary_request
    ordinary=ordinary_request(question)
    if ordinary and ordinary['kind']=='reported':
        return {k:ordinary[k] for k in ('reporter','author','object','required_outer_negative')} | {'conditional':False,'form':None}
    patterns = [
        (rf'What does (?P<reporter>{_PERSON}) report about the writer of (?P<object>{_OBJECT}), without independently verifying the event\?', False),
        (rf'What does (?P<reporter>{_PERSON}) report about whether (?P<author>{_PERSON}) wrote (?P<object>{_OBJECT})\?', False),
        (rf'did (?P<reporter>{_PERSON}) report that (?P<author>{_PERSON}) wrote (?P<object>{_OBJECT})\?', False),
        (rf'What authorship statement does (?P<reporter>{_PERSON}) make about (?P<object>{_OBJECT}) in the minutes\?', False),
        (rf'What conditional authorship statement does (?P<reporter>{_PERSON}) report about (?P<object>{_OBJECT})\?', True),
    ]
    for pattern, conditional in patterns:
        match = re.fullmatch(pattern, q, re.I)
        if match and kernel.named_actor(match['reporter']) and (
                not match.groupdict().get('author') or kernel.named_actor(match['author'])):
            return dict(match.groupdict(), conditional=conditional,
                        form='minutes' if q.endswith(' in the minutes?') else None)
    match = re.fullmatch(
        _REPORT_OBJECT + r'(?:,\s+according to (?:the|this) (?:record|source))?[?.]', q, re.I)
    if match and all(kernel.named_actor(match[k]) for k in ('reporter', 'author')):
        return _object_goal(match)
    match = re.fullmatch(
        rf'Did (?P<reporter>{_PERSON})(?P<outer> not)? (?:say|state) that '
        rf'(?P<author>{_PERSON}) (?P<action>wrote|did not write) (?P<object>{_OBJECT})[?.]',
        q, re.I)
    if match and all(kernel.named_actor(match[k]) for k in ('reporter', 'author')):
        return {k: match[k] for k in ('reporter', 'author', 'object')} | {
            'conditional': False, 'form': None, 'required_outer_negative': bool(match['outer']),
            'required_inner_negative': match['action'].casefold() == 'did not write',
        }
    return None


def report_roles(statement):
    """Reporting shell plus the existing finite action checker for its payload.

    Active/quoted/according-to and passive reporting are equivalent shells.
    They preserve the outer reporter and the inner actor as separate arguments.
    Negation of the shell never becomes negation of the embedded action.
    """
    clean = re.sub(r'\s+', ' ', statement).strip()
    if len(clean) > 1800:
        return None
    conditions = []
    conditional = re.match(r'^(If [^,.!?;:“”"]{1,160}),\s*(.*)$', clean)
    if conditional:
        conditions, clean = [conditional[1]], conditional[2]
    reporter = payload = None
    outer_negative = hypothetical = False
    active = re.fullmatch(r'(.{2,120}?) ('+_REPORT_VERBS+r') that (.+)', clean)
    quote = re.fullmatch(r'(.{2,120}?) ('+_REPORT_VERBS+r'),? [“"](.+)[”"]', clean)
    according = re.fullmatch(r'According to (.{2,120}?), (.+)', clean)
    postposed = re.fullmatch(r'[“"](.+?)[”"],? (.{2,120}?) ('+_REPORT_VERBS+r')\.', clean)
    passive = re.fullmatch(r'The statement that (.+?) ('+'|'.join(_PASSIVE_FORMS)+r') by (.{2,120}?)\.', clean)
    if active:
        reporter, verb, payload = active.groups()
        outer_negative,hypothetical = _REPORT_FORMS[verb]
    elif quote:
        reporter, verb, payload = quote.groups()
        outer_negative,hypothetical = _REPORT_FORMS[verb]
    elif according:
        reporter, payload = according.groups()
    elif postposed:
        payload, reporter, verb = postposed.groups()
        outer_negative,hypothetical = _REPORT_FORMS[verb]
        payload = payload.rstrip(',') + '.'
    elif passive:
        payload, verb, reporter = passive.groups(); payload += '.'
        outer_negative,hypothetical = _PASSIVE_FORMS[verb]
    if not reporter or not payload or not kernel.named_actor(reporter):
        return None
    if hypothetical and not conditions:
        return None
    action = kernel.action_assertion(payload) or kernel.relationship_assertion(payload)
    if (not action or action.get('action') != 'write' or action.get('unresolved_reference')
            or action.get('temporal_qualification_text')):
        return None
    content = ClaimFrame.from_action(action)
    asserted = not outer_negative and not conditions and not hypothetical
    return {'reporter': reporter, 'author': content.actor, 'inner_action': content.action,
            'object': content.object_text, 'inner_negative': content.negative if asserted else None,
            'embedded_content_negative': content.negative,
            'outer_negative': outer_negative, 'content_asserted_by_reporter': asserted,
            'outer_polarity': 'conditional_unestablished' if conditions else 'negative' if outer_negative else 'affirmative',
            'inner_polarity': ('negative' if content.negative else 'affirmative') if asserted else 'unasserted',
            'conditional_content_negative': content.negative if conditions else None,
            'conditions': conditions, 'actual_authorship_established': False}


def _reporting_appearances_conflict(left, right):
    """Compare reporting and embedded polarity without asserting the payload.

    Different named candidates retain the existing ambiguity outcome. Distinct
    explicit conditions are not unified. Denying a report of not-C is compatible
    with reporting C; denying a report of C opposes reporting that same C.
    """
    if any(left[k] != right[k] for k in ('reporter','author','object')):
        return True
    if left['conditions'] != right['conditions']:
        return False
    same_content = left['embedded_content_negative'] == right['embedded_content_negative']
    if left['outer_negative'] != right['outer_negative']:
        return same_content
    return not left['outer_negative'] and not same_content


def _writer(body):
    """Printed body label only; never authenticate a writer or resolve initials."""
    return printed_writer_label(body, require_person=True)


def _citation(record, body, start, end):
    quote = body[start:end]
    encodings = set((html.escape(quote), html.escape(quote, quote=False), quote))
    locations = {(m.start(), m.end()) for encoded in encodings
                 for m in re.finditer(re.escape(encoded), record.body_html)}
    if len(locations) != 1:
        return None
    lo, hi = next(iter(locations))
    value = kernel.citation(record, body, start, end)
    value['original_witness'] = {'coordinate_space': 'admitted_record_body_html_utf8',
        'start_byte': len(record.body_html[:lo].encode()), 'end_byte': len(record.body_html[:hi].encode()),
        'body_html_sha256': hashlib.sha256(record.body_html.encode()).hexdigest()}
    return value


def _proof(record, body, start, end, roles, goal, *, selected_writer=None):
    ranges = selected_writer[2] if selected_writer is not None else None
    if (record.kind != 'page' or record.derived_from or record.fields.get('corrects-field')
            or not unqualified_span(record, body, start, end, ranges=ranges)):
        return None
    if (goal.get('required_inner_negative') is not None
            and roles['embedded_content_negative'] != goal['required_inner_negative']):
        return None
    if goal.get('required_outer_negative') is not None and roles['outer_negative']!=goal['required_outer_negative']:
        return None
    # A separate governing paragraph cannot disappear at a sentence boundary.
    prior = body[:start]
    governor = re.search(r'\b(?:If|Unless)\b[^.!?]{0,180}[.:]\s*$', prior, re.I)
    if governor and unqualified_span(record, body, *governor.span(), ranges=ranges):
        return None
    if bool(roles['conditions']) != goal['conditional']:
        return None
    if selected_writer is not None:
        writer, writer_citation, _ = selected_writer
        witnesses = [_citation(record, body, start, end), writer_citation]
    else:
        writer, writer_span = _writer(body)
        if not writer_span and not goal['object']:
            label = re.match(r'^Report by (?P<writer>[^.\n]+)\.', body)
            if label and kernel.named_actor(label['writer']):
                writer, writer_span = label['writer'], label.span()
        witnesses = [_citation(record, body, start, end)]
        if writer_span:
            if not unqualified_span(record, body, *writer_span):
                return None
            direct = _citation(record, body, *writer_span)
            if direct is not None:
                witnesses.append(direct)
            else:
                # Separate printed heading/byline paragraphs need separate exact
                # original witnesses, rather than an invented cross-tag substring.
                segment = body[writer_span[0]:writer_span[1]]
                lines = list(re.finditer(r'[^\n]+', segment))
                if len(lines) != 2 or lines[0][0] not in {'Report.', 'Meeting minutes.'}:return None
                for line in lines:
                    lo, hi = writer_span[0]+line.start(), writer_span[0]+line.end()
                    if not unqualified_span(record, body, lo, hi):return None
                    witnesses.append(_citation(record, body, lo, hi))
    if goal['form']:
        label = re.search(r'\bMeeting minutes\.', body)
        if not label or not unqualified_span(record, body, *label.span()):
            return None
        witnesses.append(_citation(record, body, *label.span()))
    if any(c is None for c in witnesses):
        return None
    proposition = dict(roles, relation='source_attributed_report_content', source_writer_or_unknown=writer,
        source_voice='source_reports_named_speaker', reporting_layer='source_scoped_report_content',
        writer_authentication_established=False, completion_established=False,
        historical_truth_independently_verified=False,
        reporting_chain=[{'role':'printed_document_writer_or_unknown','actor':writer},
                         {'role':'reporter_in_source','actor':roles['reporter']},
                         {'role':'asserted_content_actor' if roles['content_asserted_by_reporter'] else 'embedded_actor_unasserted',
                          'actor':roles['author']}])
    return {'text': 'The source states: ' + body[start:end], 'proposition': proposition,
            'citations': sorted(witnesses, key=lambda c:c['body_start']),
            'source_support_established': True,
            'qualifiers': ['Source-scoped reporting statement only; retain its denial and conditions. '
                           'Independent authorship, reporting occurrence and execution remain unverified.']}


def _select_writer(records, requested):
    """Resolve a unique eligible original using only unqualified printed bylines."""
    target = kernel.normalized(requested)
    matches = []
    for record in records:
        if record.kind != 'page' or record.derived_from or record.fields.get('corrects-field'):
            continue
        body = kernel.body_text(record.body_html)
        first = _BYLINE.match(body)
        if not first:
            continue
        # A physically separate From paragraph followed by complete report prose
        # is a byline in this route. Mail headers and folded fields remain guarded.
        layout = _FROM_PARAGRAPH.match(record.body_html)
        standalone_from = bool(layout and html.unescape(layout[1]) == first[0]
                               and report_roles(html.unescape(layout[2])))
        ranges = kernel.context_ranges(record, standalone_from_byline=standalone_from)
        declarations = [label for label in _BYLINE.finditer(body)
                        if unqualified_span(record, body, *label.span(), ranges=ranges)]
        if not any(kernel.normalized(label['writer']) == target for label in declarations):
            continue
        if (declarations[0].start() != 0
                or any(kernel.normalized(label['writer']) != target for label in declarations)):
            return None, None, 'conflicting_or_unscoped_byline'
        witness = _citation(record, body, *first.span())
        if witness is None or not kernel.named_actor(first['writer']):
            return None, None, 'unverified_byline'
        matches.append((record, (first['writer'], witness, ranges)))
    if len(matches) != 1:
        return None, None, 'multiple_eligible_documents' if matches else 'no_eligible_byline'
    record, writer = matches[0]
    return record, writer, None


def verify(index, max_passages, max_chars):
    goal = request(index.question)
    if goal is None:
        return None
    if len(index.records) > 8:
        return 'abstain', 'reference_scan_budget', {}
    checked = kernel.check(index, [])
    if checked['status'] != 'checked' or not index.unchanged():
        return 'abstain', 'source_changed', {}
    if not checked['scan_complete']:
        return 'abstain', 'reference_scan_budget', {}
    if goal['object']:
        matches_object = lambda text: kernel.normalized(goal['object']) == kernel.normalized(text)
        relevant_object = lambda text: kernel.normalized(goal['object']) in kernel.normalized(text)
    else:
        matches_object = lambda text: True
        relevant_object = lambda text: kernel.normalized(goal['author']) in kernel.normalized(text)
    proofs, unresolved = [], False
    # The checker rederives clauses from every eligible reread record. Proposals,
    # retrieval ranks, source titles and published scoring keys do not authorize it.
    records = {r.path:r for r, *_ in checked['contexts']}
    selected_writer = None
    selection = {}
    if 'writer' in goal:
        record, selected_writer, reason = _select_writer(records.values(), goal['writer'])
        if reason:
            return 'abstain', 'named_report_source_unresolved', {
                'documentary_support': {'named_source_selection': {'status': 'unresolved', 'reason': reason}}
            }
        records = {record.path: record}
        selection = {'named_source_selection': {
            'status': 'verified', 'source_id': record.id, 'path': record.path, 'hash': record.hash_actual
        }}
    for record in records.values():
        body = kernel.body_text(record.body_html)
        # The verified byline is its own unit even when it has no final period.
        offset = selected_writer[1]['body_end'] + 1 if selected_writer else 0
        for start, end, statement in kernel.units(body[offset:]):
            start += offset
            end += offset
            roles = report_roles(statement)
            relevant = (kernel.normalized(goal['reporter']) in kernel.normalized(statement)
                        and relevant_object(statement)
                        and re.search(r'\b(?:report\w*|said|say|says|state|stated|states|according)\b', statement, re.I))
            if not roles:
                unresolved |= bool(relevant)
                continue
            if (kernel.normalized(roles['reporter']) != kernel.normalized(goal['reporter'])
                    or not matches_object(roles['object'])
                    or (goal.get('author') and kernel.normalized(roles['author']) != kernel.normalized(goal['author']))):
                continue
            proof = _proof(record, body, start, end, roles, goal, selected_writer=selected_writer)
            if proof is None:
                unresolved = True
            else:
                proofs.append(proof)
    if not goal['object'] and (unresolved or len(proofs) != 1):
        if selection:
            if not index.unchanged():
                return 'abstain', 'source_changed', {}
            return 'abstain', 'named_report_content_unresolved', {'documentary_support': selection}
        return 'abstain', 'reported_object_unresolved', {}
    if unresolved or not proofs or len(proofs) > 2:
        if goal.get('required_inner_negative') is not None:
            return 'abstain', 'report_polarity_unresolved', {}
        return None
    if len(proofs) == 2:
        identity = lambda p: tuple(str(p['proposition'][k]) for k in
                                   ('reporter','author','object','inner_negative','outer_negative','conditions','conditional_content_negative','embedded_content_negative'))
        if identity(proofs[0]) == identity(proofs[1]):
            return None
        conflicting = _reporting_appearances_conflict(proofs[0]['proposition'], proofs[1]['proposition'])
        kind, code = ('conflict', 'conflicting_reported_content') if conflicting else ('supported_answer', 'supported')
    else:
        kind, code = 'supported_answer', 'supported'
    witnesses = [c for p in proofs for c in p['citations']]
    if len(witnesses) > max_passages or sum(len(c['quote']) for c in witnesses) > max_chars:
        return 'abstain', 'reader_budget_exceeded', {}
    if not index.unchanged():
        return 'abstain', 'source_changed', {}
    return kind, code, {'claims':proofs,'answer_supported':kind=='supported_answer',
        'text':'\n'.join(p['text'] for p in proofs),
        'missing':['The eligible reporting appearances conflict; no unqualified combined statement is established.'] if kind=='conflict' else [],
        'sources':[s for s in index.sources if s['path'] in {c['path'] for c in witnesses}],
        'verification':{'structural':True,'semantic':'bounded_source_report_content',
                        'truth_verified':False,'independence_verified':False},
        'documentary_support':{'scope':'source_attributed_report_content',
            'source_support_claims':len(proofs),'examined_characters':checked['examined_characters'],
            'examined_units':checked['examined_units'],'limits':checked['limits'],'record_limit':8, **selection}}
