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
from .source_attribution import unqualified_span

_PERSON = r'[^,;:!?“”"\n]{2,120}?'
_OBJECT = r'the [\w -]{2,180}?'


def request(question):
    q = kernel.source_question(question)
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
    active = re.fullmatch(r'(.{2,120}?) (reported|stated|reports|states|said|says|did not report|did not state|did not say|would report|would not report) that (.+)', clean)
    quote = re.fullmatch(r'(.{2,120}?) (?:reported|stated|said|says|reports|states),? [“"](.+)[”"]', clean)
    according = re.fullmatch(r'According to (.{2,120}?), (.+)', clean)
    postposed = re.fullmatch(r'[“"](.+?)[”"],? (.{2,120}?) (?:reported|stated|said)\.', clean)
    passive = re.fullmatch(r'The statement that (.+?) (was reported|would be reported|would not be reported) by (.{2,120}?)\.', clean)
    if active:
        reporter, verb, payload = active.groups()
        outer_negative = verb.startswith(('did not ','would not '))
        hypothetical = verb.startswith('would ')
    elif quote:
        reporter, payload = quote.groups()
    elif according:
        reporter, payload = according.groups()
    elif postposed:
        payload, reporter = postposed.groups()
        payload = payload.rstrip(',') + '.'
    elif passive:
        payload, verb, reporter = passive.groups(); payload += '.'
        outer_negative = verb.startswith('would not ')
        hypothetical = verb.startswith('would ')
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
            'outer_negative': outer_negative, 'content_asserted_by_reporter': asserted,
            'outer_polarity': 'conditional_unestablished' if conditions else 'negative' if outer_negative else 'affirmative',
            'inner_polarity': ('negative' if content.negative else 'affirmative') if asserted else 'unasserted',
            'conditional_content_negative': content.negative if conditions else None,
            'conditions': conditions, 'actual_authorship_established': False}


def _writer(body):
    """Printed body label only; never authenticate a writer or resolve initials."""
    patterns = [r'^From: (?P<writer>[^\n]+)(?=\n|$)',
                r'^(?P<writer>[^\n]{2,100}?) TO [^\n]{2,120}?\. [^\n]+',
                r'^(?:Report\.\n)?Written by (?P<writer>[^.\n]+)\.?',
                r'^Meeting minutes\.\s*(?:Recorder:|Recorded by) (?P<writer>[^.\n]+)\.?']
    for pattern in patterns:
        match = re.match(pattern, body)
        if match and kernel.named_actor(match['writer']):
            return match['writer'], match.span()
    return None, None


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


def _proof(record, body, start, end, roles, goal):
    if (record.kind != 'page' or record.derived_from or record.fields.get('corrects-field')
            or not unqualified_span(record, body, start, end)):
        return None
    # A separate governing paragraph cannot disappear at a sentence boundary.
    prior = body[:start]
    if re.search(r'\b(?:If|Unless)\b[^.!?]{0,180}[.:]\s*$', prior):
        return None
    if bool(roles['conditions']) != goal['conditional']:
        return None
    writer, writer_span = _writer(body)
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
    proofs, unresolved = [], False
    # The checker rederives clauses from every eligible reread record. Proposals,
    # retrieval ranks, source titles and published scoring keys do not authorize it.
    records = {r.path:r for r, *_ in checked['contexts']}
    for record in records.values():
        body = kernel.body_text(record.body_html)
        for start, end, statement in kernel.units(body):
            roles = report_roles(statement)
            relevant = (kernel.normalized(goal['reporter']) in kernel.normalized(statement)
                        and kernel.normalized(goal['object']) in kernel.normalized(statement)
                        and re.search(r'\b(?:report\w*|said|says|stated|states|according)\b', statement, re.I))
            if not roles:
                unresolved |= bool(relevant)
                continue
            if (kernel.normalized(roles['reporter']) != kernel.normalized(goal['reporter'])
                    or kernel.normalized(roles['object']) != kernel.normalized(goal['object'])
                    or (goal.get('author') and kernel.normalized(roles['author']) != kernel.normalized(goal['author']))):
                continue
            proof = _proof(record, body, start, end, roles, goal)
            if proof is None:
                unresolved = True
            else:
                proofs.append(proof)
    if unresolved or not proofs or len(proofs) > 2:
        return None
    if len(proofs) == 2:
        identity = lambda p: tuple(str(p['proposition'][k]) for k in
                                   ('reporter','author','object','inner_negative','outer_negative','conditions','conditional_content_negative'))
        if identity(proofs[0]) == identity(proofs[1]):
            return None
        kind, code = 'conflict', 'conflicting_reported_content'
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
            'examined_units':checked['examined_units'],'limits':checked['limits'],'record_limit':8}}
