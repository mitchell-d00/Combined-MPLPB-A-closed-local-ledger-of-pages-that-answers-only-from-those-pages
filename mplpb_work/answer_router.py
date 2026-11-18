"""Strict-first answering that fails gracefully.

Order of work for one question:

1. **Official** – ``mplpb_answers.pipeline.answer_query`` on the ledger. Only its
   ``supported_answer`` is ever labelled official.
2. **Explained failure** – the strict diagnostic is translated into a plain
   reason plus what the ledger actually holds (e.g. which fields a record has).
3. **Rewrites** – the router proposes questions in a grammar MPLPB supports
   (``What is the <field> for record <ID>?``) and runs them strictly. A hit is
   reported as *official for the reformulated question*, never for the original.
4. **Unofficial answer** – best passages from eligible ledger pages and the raw
   dump, clearly labelled UNOFFICIAL with citations and scope warnings. An
   optional ``reader`` callable may compose prose from those passages only.
5. **Classing help** – concrete steps that would let strict MPLPB answer next
   time, pointing at ``mplpb_work.classing``.

Nothing here writes to a ledger or promotes a candidate. ``answer_supported`` is
true only inside the ``official`` block and only when the strict pipeline said so.
"""
import argparse
import json
import re
import sys
from pathlib import Path

from mplpb_answers.body_text import body_text
from mplpb_answers.pipeline import answer_query
from mplpb_combined.baselines import LexicalIndex, counts
from mplpb_combined.ledger import Ledger
from mplpb_combined import provenance_gate
from mplpb_combined.reader import PROFILES, DEFAULT_PROFILE

from . import sorter_v2

SCHEMA = 'mplpb-answer-router-v1'
UNOFFICIAL_LABEL = 'UNOFFICIAL — not supported by MPLPB. Read the cited passages before relying on it.'
FIELD_LINE = re.compile(r'^([A-Z][A-Za-z0-9 _-]{0,79}):[ \t]+(\S.*)$')
RECORD_REF = re.compile(sorter_v2.ID_ALT)

# Question wording that points at a field label. Used only to *propose*
# rewrites; the strict pipeline decides whether the rewrite is supported.
FIELD_HINTS = {
    'sender': ('who sent', 'sent by', 'from whom', 'sender', 'author', 'who wrote', 'from'),
    'from': ('who sent', 'sent by', 'from whom', 'from'),
    'recipient': ('to whom', 'who received', 'recipient', 'sent to', 'addressed to', 'received'),
    'to': ('to whom', 'who received', 'sent to', 'addressed to'),
    'date': ('when', 'what date', 'what day', 'what year', 'date'),
    'subject': ('about', 'subject', 'topic', 'regarding'),
    'cargo': ('how many', 'how much', 'cargo', 'carried', 'shipped', 'load'),
    'count': ('how many', 'number of', 'count', 'quantity'),
    'location': ('where', 'location', 'place'),
    'destination': ('where', 'destination', 'bound for', 'sent to'),
    'status': ('status', 'current', 'still'),
    'owner': ('who owns', 'owner', 'belongs'),
}

REASONS = {
    'absent_eligible_source': 'No page in the ledger is eligible to answer this under the selected profile.',
    'unsupported_question_grammar': 'MPLPB only answers a fixed set of question forms, and this question is not one of them.',
    'insufficient_evidence': 'Eligible pages exist, but none states the answer in a form the strict reader can certify.',
    'known_source_conflict': 'Two or more eligible pages disagree or both claim the subject, so MPLPB will not pick one.',
    'clarification_required': 'The question matches more than one record or needs a field, date or subject named.',
    'index_exhaustion': 'The evidence needed does not fit the strict passage budget.',
    'source_state_changed': 'The ledger changed while the question was being answered.',
    'reader_unavailable_or_failed': 'An optional model reader was requested but is not available.',
}

SUPPORTED_FORMS = [
    'What is the <field> for record <ID>?   (page has a paragraph "<Field>: <value>")',
    'When did <name> open?                  (page says "<name> opened in <year>")',
    'Who owns <name>?                       (page says "<owner> owns <name>")',
    'What is <name>?                        (page says "<name> is ...")',
    'Under what conditions can <thing> be <verb>?  (policy sentences)',
    'What happens if <condition>?           (page says "If <condition>, <outcome>")',
    'Show procedure <ID> / Show step <n> of procedure <ID>',
]


STACKED_LABEL = re.compile(r'(?:^|\s)([A-Z][A-Za-z0-9_-]{0,40}(?: [A-Za-z0-9_-]{1,40}){0,3}):[ \t]+(?=\S)')


def page_fields(text):
    """Return (readable, stacked) field labels of one page's served text.

    The ledger joins the lines of a paragraph with spaces, so a header block
    arrives as one line "Sender: A Recipient: B". Every label in such a line is
    stacked: the strict reader refuses it (stacked_field_paragraph).
    """
    readable, stacked = {}, {}
    for line in re.split(r'\n', text):
        line = line.strip()
        if not FIELD_LINE.match(line):
            continue
        labels = list(STACKED_LABEL.finditer(line))
        if len(labels) == 1:
            readable.setdefault(labels[0][1], line[labels[0].end():].strip())
            continue
        for i, m in enumerate(labels):
            end = labels[i + 1].start() if i + 1 < len(labels) else len(line)
            stacked.setdefault(m[1], line[m.end():end].strip())
    return readable, stacked


def _profile(name):
    return PROFILES[name or DEFAULT_PROFILE]


def _gate(ledger, question, profile):
    from mplpb_answers.relation_graph import exact_request
    from mplpb_combined.ledger import serving_view
    request=exact_request(question)
    with serving_view(None,request['field']):
        return provenance_gate.gather(ledger,question,profile)


def _pages(ledger, profile, question):
    """Use the full native question/profile gate, never a depth-only surrogate."""
    if not ledger or not Path(ledger).is_dir():
        return {}
    pages = {}
    allowed={(s['id'],s['path'],s['hash']) for s in _gate(ledger,question,profile).sources}
    for record in Ledger(Path(ledger)).servable():
        if record.kind == 'index':
            continue
        depth = record.depth_declared
        if (record.id,record.path,record.hash_actual) not in allowed:
            continue
        pages[record.id] = {'id': record.id, 'hash': record.hash_actual, 'path': record.path,
                            'title': record.title, 'text': body_text(record.body_html), 'depth': depth}
    return pages


def _catalog(ledger):
    """Every record, served or not: status, successors and classing source.

    Used only to explain refusals and label passages; never as evidence.
    """
    if not ledger or not Path(ledger).is_dir():
        return {}
    native = Ledger(Path(ledger), serving=False)
    out = {}
    for record in native.records:
        if record.kind == 'index':
            continue
        readable, _ = page_fields(body_text(record.body_html))
        out[record.id] = {'status': record.status, 'hash': record.hash_actual,
                          'successors': [{'id': s.id, 'corrects_field': s.fields.get('corrects-field', '')}
                                         for s in native.superseded_by.get(record.id, [])],
                          'source_file': readable.get('Classing source file'),
                          'source_sha256': readable.get('Classing source SHA-256'),
                          'fields': sorted(readable)}
    return out


def _strict(ledger, question, profile):
    result = answer_query(ledger, question, profile)
    return result.contract


def _official(contract, question, via=None):
    return {'question_answered': question, 'reformulated_from': via, 'kind': contract['kind'],
            'text': contract['text'], 'answer_supported': True,
            'sources': [{'id': s['id'], 'hash': s['hash']} for s in contract['sources']],
            'claims':contract['claims'], 'verification':contract['verification'],
            'notice': contract.get('source_assurance', {}).get('notice', '')}


def _asked_field(question):
    m = re.match(r'(?i)what is (?:the )?([A-Za-z][A-Za-z0-9 _-]{0,79}) (?:for|of) (?:record|event|occurrence) ', question.strip())
    return m[1].lower() if m else None


def _gate_exclusions(ledger, question, profile):
    """The provenance gate's own reasons for withholding pages (id -> reason)."""
    if not ledger or not Path(ledger).is_dir():
        return {}
    gate = _gate(ledger,question,profile)
    return {e['id']: e['reason'] for e in gate.excluded}


def explain(contract, question, pages, catalog=None, excluded=None):
    """Plain-language reason for a strict refusal, with ledger facts."""
    catalog = catalog or {}
    excluded = excluded or {}
    diagnostic = contract.get('diagnostic', {})
    category = diagnostic.get('category', 'insufficient_evidence')
    lines = [REASONS.get(category, 'MPLPB could not establish an answer.')]
    details = []
    ids = [_canonical(m[0]) for m in RECORD_REF.finditer(question)]
    asked = _asked_field(question)
    for rid in ids:
        page = pages.get(rid)
        entry = catalog.get(rid)
        if rid in excluded:
            details.append(f"{rid} is withheld for this question under the '{contract.get('profile', 'selected')}' profile: {excluded[rid]}.")
            if 'authorship' in excluded[rid]:
                details.append('A reviewer can declare source authorship (classing page.source_authorship) and ratify the page '
                               'if they stand behind it; MPLPB will not guess authorship.')
        if rid in excluded and excluded[rid]!='retired':
            continue
        for s in (entry or {}).get('successors', []):
            if s['corrects_field']:
                details.append(f"{rid} has a field-scoped correction: {s['id']} corrects its '{s['corrects_field']}' field"
                               + (' (the field you asked about).' if asked and s['corrects_field'].lower() == asked else '.')
                               + f" {rid} is still served for its other fields.")
            else:
                details.append(f"{rid} was superseded by {s['id']}; ask about {s['id']}.")
        if not page:
            if entry and entry['status'] == 'retired' and not entry['successors']:
                details.append(f'{rid} is in the ledger but withdrawn, so it is not served.')
            elif entry and entry['successors'] and all(s['corrects_field'] for s in entry['successors']):
                pass
            elif entry:
                details.append(f"{rid} is in the ledger but not served under the '{contract.get('profile', 'selected')}' profile "
                               '(its depth or status is outside what the profile serves).')
            else:
                details.append(f'No page in the ledger has the id {rid}.')
            continue
        readable, stacked = page_fields(page['text'])
        if readable:
            details.append(f'{rid} has readable fields: {", ".join(sorted(readable))}.')
        if stacked:
            details.append(f'{rid} has field lines the strict reader cannot use because they are stacked '
                           f'in one paragraph: {", ".join(sorted(stacked))}. Re-class the page with one field per paragraph.')
    if category == 'unsupported_question_grammar' or not ids:
        details.append('Question forms MPLPB can certify: ' + ' | '.join(f.split('  ')[0] for f in SUPPORTED_FORMS))
    if not pages:
        details.append('The ledger has no eligible pages for this profile (empty, missing, or every page is deeper than allowed).')
    return {'code': diagnostic.get('code'), 'category': category, 'reason': lines[0],
            'details': details, 'mplpb_next_steps': diagnostic.get('next_steps', []),
            'note': 'A refusal is not evidence that the answer is absent.'}


def _canonical(value):
    return sorter_v2._canonical(value)


def rewrites(question, pages, limit=5, catalog=None):
    """Propose strict-grammar questions. Pure proposal; the caller runs them."""
    catalog = catalog or {}
    q = question.lower()
    words = set(counts(question))
    ids = [_canonical(m[0]) for m in RECORD_REF.finditer(question)]
    if not ids and pages:
        index = LexicalIndex({pid: p['title'] + '\n' + p['text'] for pid, p in pages.items()})
        ids = [pid for pid, score in index.rank(question, 'bm25')[:3] if score > 0]
    asked = _asked_field(question)

    def field_score(label):
        """How strongly the question's own wording points at this label."""
        key = label.lower()
        if asked is not None:
            return 10 if key == asked else 0
        score = len(set(counts(label)) & words) * 2
        for hint_key, hints in FIELD_HINTS.items():
            if hint_key in key and any(h in q for h in hints):
                score += 3
        return score

    scored = []
    for rid in ids:
        entry = catalog.get(rid, {})
        corrected = {s['corrects_field'].lower(): s for s in entry.get('successors', []) if s['corrects_field']}
        for s in entry.get('successors', []):
            if not s['corrects_field'] and s['id'] in pages:
                ids.append(s['id'])  # full replacement: ask the successor instead
        page = pages.get(rid)
        if page is not None:
            readable, _ = page_fields(page['text'])
        elif entry and (entry['status'] != 'retired' or (corrected and len(corrected) == len(entry['successors']))):
            readable = {f: '' for f in entry['fields']}  # field-scoped: still served for other fields
        else:
            readable = {}
        labels = set(readable) | {s['corrects_field'] for s in corrected.values()}
        for label in labels:
            score = field_score(label)
            if not score:
                continue
            successor = corrected.get(label.lower())
            if successor:
                # A field-scoped successor owns the corrected field: ask it directly.
                scored.append((-score, f"What is the {label.lower()} for record {successor['id']}?", successor['id'], label,
                               f"{successor['id']} corrects the {label.lower()} of {rid}"))
            elif label in readable:
                scored.append((-score, f'What is the {label.lower()} for record {rid}?', rid, label, None))
    seen, out = set(), []
    for _, question_text, record, label, why in sorted(scored):
        if question_text not in seen:
            seen.add(question_text)
            out.append({'question': question_text, 'record': record, 'field': label, 'why': why})
    return out[:limit]


QUALIFIED_FOR_ANSWERS = {'quoted_or_format_scope_unresolved', 'conditional_or_uncertain', 'reported_speech_scope',
                         'negation_scope_unresolved', 'negated_correction_mention'}


def _dump_graph(dump):
    return sorter_v2.sort_directory(dump, 'compare') if dump else None


def _dump_corrections(graph):
    """Record id -> correction candidates aimed at it (sorter v2 review edges)."""
    if not graph:
        return {}
    by_id = {n['id']: n for n in graph['nodes']}
    declared = {}
    for n in graph['nodes']:
        if n['kind'] == 'header_identifier' and n.get('primary_identity_eligible'):
            declared.setdefault(n['occurrence'], set()).add(n['value'])
    out = {}
    for e in graph['edges']:
        if e['kind'] not in {'possible_correction', 'possible_partial_correction'}:
            continue
        quote = e.get('claim_scope_quote') or ''
        for record in declared.get(e['to'], ()):
            out.setdefault(record, []).append({'kind': e['kind'], 'from_path': by_id[e['from']]['span']['path'],
                                               'quote': quote.strip(), 'review_only': True})
    return out


def _dump_passages(graph):
    """Statements of the raw dump with the record ids they declare or mention."""
    if not graph:
        return []
    flagged, mentioned, declared = {}, {}, {}
    for n in graph['nodes']:
        local = n.get('local_scope')
        if n.get('statement') and local in QUALIFIED_FOR_ANSWERS:
            flagged.setdefault(n['statement'], set()).add(local)
        if n['kind'] in {'identifier', 'header_identifier'} and n.get('statement'):
            mentioned.setdefault(n['statement'], set()).add(n['value'])
        if n['kind'] == 'header_identifier' and n.get('primary_identity_eligible'):
            declared.setdefault(n['occurrence'], set()).add(n['value'])
    out = []
    for n in graph['nodes']:
        if n['kind'] != 'statement':
            continue
        out.append({'origin': 'dump', 'text': n['span']['text'], 'path': n['span']['path'],
                    'source_sha256': n['span']['source_sha256'],
                    'bytes': [n['span']['byte_start'], n['span']['byte_end']],
                    'records': sorted(mentioned.get(n['id'], set()) | declared.get(n['occurrence'], set())),
                    'warnings': sorted(flagged.get(n['id'], set()))})
    return out


def _ledger_passages(pages):
    """One passage per served paragraph (the ledger serves one per line)."""
    out = []
    for page in pages.values():
        for paragraph in page['text'].split('\n'):
            if paragraph.strip():
                out.append({'origin': 'ledger', 'text': paragraph.strip(), 'page': page['id'],
                            'hash': page['hash'], 'records': [page['id']], 'warnings': []})
    return out


def _segments(text):
    """Sentences, and for a stacked field line its separate "Label: value" parts."""
    labels = list(STACKED_LABEL.finditer(text))
    if len(labels) > 1 and FIELD_LINE.match(text):
        return [text[m.start():(labels[i + 1].start() if i + 1 < len(labels) else len(text))].strip()
                for i, m in enumerate(labels)]
    return [s for s in re.split(r'(?<=[.!?])\s+|\n', text) if s.strip()]


def _label_against_ledger(passages, pages, catalog, excluded=None):
    """Mark dump passages already classed into the ledger; drop exact duplicates
    of served pages; warn when the ledger withdrew that source."""
    by_sha = {}
    for rid, entry in catalog.items():
        if entry.get('source_sha256'):
            by_sha.setdefault(entry['source_sha256'], []).append(rid)
    served_text = {(p['page'], p['text']) for p in passages if p['origin'] == 'ledger'}
    out = []
    for p in passages:
        if p['origin'] == 'dump':
            rids = by_sha.get(p['source_sha256'], [])
            if any(r in (excluded or {}) and excluded[r]!='retired' for r in rids):
                continue  # A supplied dump cannot bypass known delivery exclusions.
            p = dict(p, in_ledger_as=rids)
            if any((rid, p['text'].strip()) in served_text for rid in rids):
                continue
            withdrawn = [r for r in rids if catalog[r]['status'] == 'retired' and not catalog[r]['successors']]
            if withdrawn:
                p['warnings'] = sorted(set(p['warnings']) | {'withdrawn_in_ledger'})
        out.append(p)
    return out


def unofficial(question, pages, dump, reader=None, top=3, catalog=None, excluded=None):
    """Best passages, labelled UNOFFICIAL. Never an MPLPB answer.

    If the question names records, only passages tied to them are used.
    Ledger passages rank ahead of dump passages of similar strength, and
    qualified passages (quoted, conditional, reported, negated, withdrawn)
    rank last. Correction candidates aimed at the same records are shown.
    """
    catalog = catalog or {}
    graph = _dump_graph(dump)
    corrections = _dump_corrections(graph)
    passages = _label_against_ledger(_ledger_passages(pages) + _dump_passages(graph), pages, catalog, excluded)
    ids = {_canonical(m[0]) for m in RECORD_REF.finditer(question)}
    if ids:
        passages = [p for p in passages if ids & set(p['records'])]
    if not passages:
        return None
    query = re.sub(sorter_v2.ID_ALT, ' ', question)
    index = LexicalIndex({str(i): p['text'] for i, p in enumerate(passages)})
    scored = [(passages[int(k)], s) for k, s in index.rank(query, 'bm25')]
    if not ids:
        scored = [(p, s) for p, s in scored if s > 0]
    if not scored:
        return None
    best_score = max(s for _, s in scored) or 1.0
    def order(item):
        # Qualified passages are halved, not hidden: a withdrawn or quoted
        # source can still be the only relevant text, and is shown flagged.
        p, s = item
        adjusted = s * (0.5 if p['warnings'] else 1.0) * (1.25 if p['origin'] == 'ledger' else 1.0)
        return (-adjusted, p.get('path', p.get('page', '')))
    ranked = sorted(scored, key=order)[:top]
    best = ranked[0][0]
    q = set(counts(query))
    words = set(re.findall(r'[a-z]+', query.lower()))
    def fit(segment):
        label = FIELD_LINE.match(segment)
        hinted = bool(label) and any(h in label[1].lower() and any(x in query.lower() for x in hints)
                                     for h, hints in FIELD_HINTS.items())
        return (hinted, len(set(counts(segment)) & q), len(set(re.findall(r'[a-z]+', segment.lower())) & words), -len(segment))
    sentence = max(_segments(best['text']), key=fit)
    composed, method = sentence.strip(), 'extractive_best_sentence'
    if reader is not None:
        proposal=reader(question, [dict(p) for p, _ in ranked])
        if isinstance(proposal,str) and len(proposal)<=8000 and proposal in {p['text'] for p,_ in ranked}:
            composed,method=proposal,'checked_verbatim_reader_selection'
    if graph:
        sorter_v2.verify_graph(graph,dump)  # A reader hook cannot keep stale dump evidence.
    records = set().union(*(set(p['records']) for p, _ in ranked))
    related = [dict(c, record=r) for r in sorted(records) for c in corrections.get(r, [])]
    return {'label': UNOFFICIAL_LABEL, 'answer_supported': False, 'text': composed, 'method': method,
            'based_on': {'origin': best['origin'], 'warnings': best['warnings']},
            'passages': [dict(p, score=round(s, 3)) for p, s in ranked],
            'possible_corrections': related,
            'search_limits':{'sorter_complete':graph['complete'] if graph else None,
                             'limits_or_exclusions':graph['limits_or_exclusions'] if graph else [],
                             'displayed_passages':len(ranked),'matching_passages':len(scored)},
            'not_in_ledger': sorted({p['path'] for p, _ in ranked if p['origin'] == 'dump' and not p.get('in_ledger_as')} |
                                    {c['from_path'] for c in related
                                     if not any(e.get('source_file') == c['from_path'] for e in catalog.values())})}


def classing_help(question, explanation, unofficial_answer, ledger, dump):
    steps = []
    if unofficial_answer and unofficial_answer['not_in_ledger']:
        files = ', '.join(unofficial_answer['not_in_ledger'])
        steps.append({'why': f'The best evidence is in dump file(s) not in the ledger: {files}.',
                      'do': f'python -m mplpb_work.classing propose {dump or "DUMP"} --ledger {ledger or "LEDGER"} --output review.json',
                      'then': 'Review review.json (accept/reject drafts and decisions), then: '
                              f'python -m mplpb_work.classing build review.json --dump {dump or "DUMP"} --ledger NEW_LEDGER'})
    if any('stacked' in d for d in explanation['details']):
        steps.append({'why': 'Some fields share one paragraph, so the strict reader cannot tell where each value ends.',
                      'do': 'Re-class those pages: classing writes one "<Field>: <value>" paragraph per header field, copied literally.'})
    if explanation['category'] == 'unsupported_question_grammar':
        steps.append({'why': 'The question form is outside the strict grammar.',
                      'do': 'Ask one of the supported forms, or record the fact as a field paragraph so the field form applies.'})
    if explanation['category'] == 'known_source_conflict':
        steps.append({'why': 'Pages conflict.',
                      'do': 'Resolve by a pinned revision (supersedes) or a field-scoped correction; classing lists these as decisions.'})
    return steps


def route(question, ledger=None, dump=None, profile=None, try_rewrites=True, reader=None):
    profile_obj = _profile(profile)
    out = {'schema': SCHEMA, 'question': question, 'profile': profile_obj.name, 'status': 'no_answer',
           'official': None, 'explanation': None, 'rewrites_tried': [], 'unofficial': None, 'classing_help': []}
    contract = None
    if ledger and Path(ledger).is_dir():
        contract = _strict(ledger, question, profile_obj)
        if contract['kind'] == 'supported_answer' and contract['answer_supported'] is True:
            out.update(status='official', official=_official(contract, question))
            return out
    pages = _pages(ledger, profile_obj, question)
    initial_gate=_gate(ledger,question,profile_obj).to_dict() if ledger and Path(ledger).is_dir() else None
    catalog = _catalog(ledger)
    if contract is None:
        out['explanation'] = {'code': None, 'category': 'absent_eligible_source',
                              'reason': 'No ledger was given (or it does not exist), so MPLPB cannot answer officially.',
                              'details': ['Only an unofficial answer from the dump is possible until material is classed into a ledger.'],
                              'mplpb_next_steps': [], 'note': 'A refusal is not evidence that the answer is absent.'}
    else:
        out['explanation'] = explain(dict(contract, profile=profile_obj.name),
                                     question, pages, catalog, _gate_exclusions(ledger, question, profile_obj))
    if try_rewrites and pages:
        for proposal in rewrites(question, pages, catalog=catalog):
            excluded=_gate_exclusions(ledger,question,profile_obj)
            if proposal['record'] in excluded and excluded[proposal['record']] not in {
                    'retired','correction scope unclear','field-scoped source requires a field selector'}:
                continue
            attempt = _strict(ledger, proposal['question'], profile_obj)
            out['rewrites_tried'].append({'question': proposal['question'], 'kind': attempt['kind'],
                                          'code': attempt['diagnostic'].get('code'), 'why': proposal.get('why')})
            if attempt['kind'] == 'supported_answer' and attempt['answer_supported'] is True:
                out.update(status='official_via_rewrite', official=_official(attempt, proposal['question'], via=question))
                out['official']['caution'] = ('MPLPB certified the reformulated question, not your wording. '
                                              'Check that it asks what you meant.')
                return out
    # Raw files have no sealed external-delivery declaration. External inspection
    # must first class/review them; depth-0 ratification alone is insufficient.
    allowed_dump = dump if profile_obj.name!='external' else None
    out['unofficial'] = unofficial(question, pages, allowed_dump, reader, catalog=catalog,
                                   excluded=_gate_exclusions(ledger,question,profile_obj))
    if initial_gate is not None:
        if _gate(ledger,question,profile_obj).to_dict()!=initial_gate:
            raise ValueError('Ledger source or delivery state changed during exploration; ask again')
    if out['unofficial']:
        out['status'] = 'unofficial'
    out['classing_help'] = classing_help(question, out['explanation'], out['unofficial'], ledger, dump)
    return out


def render(result):
    lines = [f"Q: {result['question']}", '']
    if result['official']:
        o = result['official']
        head = 'OFFICIAL (MPLPB strict)' if result['status'] == 'official' else 'OFFICIAL for a reformulated question'
        lines += [head + ':', '  ' + o['text'].replace('\n', '\n  '),
                  '  sources: ' + ', '.join(f"{s['id']}@{s['hash'][:19]}" for s in o['sources'])]
        if o.get('reformulated_from'):
            lines += [f"  asked as: {o['question_answered']}", '  ' + o['caution']]
        return '\n'.join(lines)
    e = result['explanation']
    lines += ['MPLPB could not answer strictly.', '  why: ' + e['reason']] + ['  - ' + d for d in e['details']]
    if result['rewrites_tried']:
        lines += ['  tried supported forms:'] + [f"    {r['question']} -> {r['kind']} ({r['code']})" for r in result['rewrites_tried']]
    u = result['unofficial']
    if u:
        lines += ['', u['label'], '  ' + u['text']]
        if u['based_on']['warnings']:
            lines.append('  caution, the passage it comes from is qualified: ' + ', '.join(u['based_on']['warnings']))
        for p in u['passages']:
            where = (f"ledger page {p['page']} (eligible, not certified for this question)" if p['origin'] == 'ledger'
                     else f"dump {p['path']} bytes {p['bytes'][0]}-{p['bytes'][1]}, "
                          + (f"classed into the ledger as {', '.join(p['in_ledger_as'])}" if p.get('in_ledger_as') else 'not in ledger'))
            flag = f" [{', '.join(p['warnings'])}]" if p['warnings'] else ''
            lines.append(f"  - {where}{flag}: {p['text'][:140]!r}")
        for c in u['possible_corrections']:
            lines.append(f"  ! {c['record']} may be corrected by {c['from_path']} (review only, not applied): {c['quote'][:120]!r}")
    else:
        lines += ['', 'No unofficial passage was surfaced within the inspected material and budgets.']
    lines.append(e['note'])
    for step in result['classing_help']:
        lines += ['', 'To make this answerable: ' + step['why'], '  ' + step['do']] + (['  ' + step['then']] if step.get('then') else [])
    return '\n'.join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    sub = parser.add_subparsers(dest='command', required=True)
    ask = sub.add_parser('ask')
    ask.add_argument('question')
    ask.add_argument('--ledger')
    ask.add_argument('--dump', help='raw text folder used only for unofficial answers and classing help')
    ask.add_argument('--profile', choices=sorted(PROFILES), default=DEFAULT_PROFILE)
    ask.add_argument('--no-rewrites', action='store_true')
    ask.add_argument('--json', action='store_true')
    args = parser.parse_args(argv)
    try:
        result = route(args.question, args.ledger, args.dump, args.profile, not args.no_rewrites)
    except (ValueError, OSError) as exc:
        print(json.dumps({'status': 'refused', 'error': str(exc)}), file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2) if args.json else render(result))
    return 0 if result['status'] in {'official', 'official_via_rewrite'} else 1


if __name__ == '__main__':
    sys.exit(main())
