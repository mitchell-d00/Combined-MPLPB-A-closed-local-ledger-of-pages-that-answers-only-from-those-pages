"""Classing assistant: raw data dump -> reviewed, strict-readable MPLPB ledger.

``propose`` reads a dump with sorter v2 and writes a *review file*: one page
draft per source occurrence plus the decisions a person must make. ``build``
writes only accepted drafts into a new (or explicitly appended) ledger through
the native ``mplpb_combined.ledger`` writer, then validates it.

Rules this module never relaxes
  * Literal only. Field values are copied byte-for-byte from the source; the
    build re-reads the source and refuses any value it cannot find verbatim.
  * Machine origin. Drafts are ``origin=machine`` (depth 1): served by the
    ``internal`` and ``lab`` profiles, withheld by ``external`` until a named
    person ratifies them (``--ratify-by``, per draft ``"ratify": true``).
  * No silent serving changes. Supersession, field-scoped corrections, duplicate
    ids and declared "retired" status are decisions with explicit options. An
    unanswered decision applies nothing; a blocking one stops its drafts.
  * The dump is pinned. The review stores the sorter graph hash; the build
    refuses if the dump changed.
  * Nothing is written to an existing ledger without ``--append``, and every
    write is rehearsed on a copy and validated first.
Automation: ``--auto-accept-clean`` accepts drafts with a declared unique id
and no open decision. Everything else waits for a person.
"""
import argparse
import copy
import html
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path

from . import sorter_v2

SCHEMA = 'mplpb-classing-review-v1'
SAFE_ID = re.compile(r'[A-Za-z0-9][A-Za-z0-9._-]{0,79}')
FIELD_LABEL = re.compile(r'[A-Za-z][A-Za-z0-9 _-]{0,79}')
PROVENANCE_LABELS = ('Classing source file', 'Classing source SHA-256', 'Classing source bytes')
RELATION_ACTIONS = ('ignore', 'supersede', 'field_correction')
STATUS_ACTIONS = ('ignore', 'withdraw_after_write')
DUPLICATE_ACTIONS = ('keep_both', 'second_supersedes_first', 'reject_second')


class ClassingError(ValueError):
    pass


def _sha(data):
    return 'sha256:' + hashlib.sha256(data).hexdigest()


def _digest(value):
    return _sha(json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode('utf-8'))


def _source(root, name):
    relative=Path(name)
    if relative.is_absolute() or '..' in relative.parts or any(ord(c)<32 for c in str(name)):
        raise ClassingError('Unsafe source path')
    root=Path(root).resolve();path=root/relative
    try:path.resolve().relative_to(root)
    except ValueError as exc:raise ClassingError('Source path escapes dump') from exc
    if any((root/Path(*relative.parts[:i])).is_symlink() for i in range(1,len(relative.parts)+1)):
        raise ClassingError('Source symlinks are not accepted')
    if not path.is_file() or path.stat().st_size>sorter_v2.DEFAULT_LIMITS['file_bytes']:
        raise ClassingError('Source is missing or exceeds the byte budget')
    return path


def _existing_ids(ledger):
    if not ledger or not Path(ledger).is_dir():
        return set()
    from mplpb_combined.ledger import Ledger
    return set(Ledger(Path(ledger), serving=False).by_id)


# Labels are at most four words, so "A diary entry: the porter said ..." is prose.
HEADER_LINE = re.compile(r'[ \t]*([A-Za-z][A-Za-z0-9_-]{0,40}(?: [A-Za-z0-9_-]{1,40}){0,3}):[ \t]+(\S[^\r\n]*?)[ \t]*(?=\r?$)')


def _header_block_fields(text, start, end, notes):
    """Every "Label: value" line of the leading header block, copied literally.

    The sorter recognizes a fixed header list; dumps carry arbitrary fields
    (Cargo:, Invoice total:, Ward:). A block counts only if it is unbroken and
    either ends at a blank line before more text or has two or more fields, so
    a lone prose sentence with a colon never becomes a field. A numbered
    designation line ("Letter No. 41") may sit inside the block.
    """
    fields, pos = [], start
    while pos < end:
        newline = text.find('\n', pos, end)
        line_end = newline if newline != -1 else end
        line = text[pos:line_end].rstrip('\r')
        if not line.strip():
            break
        if sorter_v2.NUMBERED_HEADER.fullmatch(line):
            pos = line_end + 1
            continue
        m = HEADER_LINE.fullmatch(line)
        if not m:
            if fields:
                notes.append(f'Header block ends at a non-field line: {line.strip()[:60]!r}')
            break
        label = m[1].strip()
        if label.casefold() in {x.casefold() for x in PROVENANCE_LABELS}:
            notes.append(f'Header {label!r} skipped: reserved for provenance.')
        else:
            fields.append({'label': label, 'value': m[2], 'from': 'header',
                           'char_span': [pos + m.start(2), pos + m.end(2)]})
        pos = line_end + 1
    ends_at_blank = pos < end and not text[pos:text.find('\n', pos, end) if text.find('\n', pos, end) != -1 else end].strip() \
        and text[pos:end].strip() != ''
    if not fields or (len(fields) < 2 and not ends_at_blank):
        return [], start
    return fields, pos


def _occurrence_drafts(graph, dump_root, prefix, taken):
    nodes = graph['nodes']
    by_occ = {}
    for n in nodes:
        if n.get('occurrence'):
            by_occ.setdefault(n['occurrence'], []).append(n)
    declared_count = {}
    for n in nodes:
        if n['kind'] == 'header_identifier' and n.get('primary_identity_eligible'):
            declared_count[n['value']] = declared_count.get(n['value'], 0) + 1
    drafts, used = [], set(taken)
    for occ in [n for n in nodes if n['kind'] == 'source_occurrence']:
        items = by_occ.get(occ['id'], [])
        headers = [n for n in items if n['kind'] in {'header', 'header_identifier', 'declared_status'}
                   and n.get('header_context') == 'top_level_text']
        ids = [n for n in headers if n['kind'] == 'header_identifier' and n.get('primary_identity_eligible')]
        path = occ['span']['path']
        raw = _source(dump_root,path).read_bytes()
        if _sha(raw)!=occ['span']['source_sha256']:
            raise ClassingError('Source changed during proposal')
        text = raw.decode('utf-8')
        blockers, notes = [], []
        declared = ids[0]['value'] if ids else None
        doc_id = declared
        if declared is None:
            doc_id = f"{prefix}-{hashlib.sha256((path + ':' + str(occ['span']['char_start'])).encode()).hexdigest()[:8].upper()}"
            notes.append('No declared record id; a stable id was generated from the file path.')
        elif not SAFE_ID.fullmatch(declared):
            doc_id = f"{prefix}-{hashlib.sha256(declared.encode()).hexdigest()[:8].upper()}"
            notes.append(f'Declared id {declared!r} is not a safe ledger id; generated {doc_id}. The original stays as a field.')
        if declared and declared_count.get(declared, 0) > 1:
            blockers.append('duplicate_declared_id')
        if doc_id in used:
            suffix = 2
            while f'{doc_id}-{suffix}' in used:
                suffix += 1
            if doc_id in taken:
                blockers.append('id_taken_in_target_ledger')
            doc_id = f'{doc_id}-{suffix}'
        used.add(doc_id)
        fields, body_start = _header_block_fields(text, occ['span']['char_start'], occ['span']['char_end'], notes)
        numbered = next((h for h in headers if h.get('header_name') == 'numbered-record-id'), None)
        if numbered:
            fields.insert(0, {'label': 'Designation', 'value': numbered['designation_text'], 'from': 'header',
                              'char_span': [numbered['span']['char_start'], numbered['span']['char_end']]})
        subject = next((f['value'] for f in fields if f['label'].lower() == 'subject'), None)
        body = text[body_start:occ['span']['char_end']].strip()
        title = subject or (body.splitlines()[0][:80] if body else doc_id)
        status = next((h for h in headers if h['kind'] == 'declared_status'), None)
        drafts.append({
            'draft_id': f'D{len(drafts) + 1:03d}', 'occurrence': occ['id'], 'decision': 'pending', 'ratify': False,
            'auto_accept_eligible': bool(declared and not blockers and doc_id == declared),
            'blockers': blockers, 'notes': notes,
            'source': {'path': path, 'raw_sha256': _sha(raw), 'char_span': [occ['span']['char_start'], occ['span']['char_end']],
                       'byte_span': [occ['span']['byte_start'], occ['span']['byte_end']]},
            'page': {'doc_id': doc_id, 'title': ' '.join(title.split()), 'scope': f"{doc_id}: {' '.join(title.split())}",
                     'when_to_use': f'Questions about record {doc_id}.', 'not_for': '', 'owner': '',
                     'origin': 'machine', 'source_authorship': 'unknown', 'external': '',
                     'event_id': '', 'occurrence_id': ''},
            'fields': fields, 'reviewer_fields': [],
            'declared_status': status['value'] if status else None,
            'body': body})
    return drafts


def _decisions(graph, drafts):
    draft_of = {d['occurrence']: d['draft_id'] for d in drafts}
    quote_of = {n['id']: n['span'].get('text', '') for n in graph['nodes']}
    out = []
    def add(kind, **fields):
        out.append({'decision_id': f'X{len(out) + 1:03d}', 'kind': kind, 'choice': None, **fields})
    for e in graph['edges']:
        k = e['kind']
        if k in {'possible_correction', 'possible_partial_correction'}:
            add('correction' if k == 'possible_correction' else 'partial_correction',
                from_draft=draft_of.get(e['from']), to_draft=draft_of.get(e['to']),
                evidence_quote=(e.get('claim_scope_quote') or '').strip(), options=list(RELATION_ACTIONS),
                recommended='field_correction' if k == 'possible_partial_correction' else None,
                corrects_field=None, valid_from=None, valid_until=None, blocking=False,
                help='"supersede" retires the target page; "field_correction" needs corrects_field and keeps other fields served.')
        elif k == 'candidate_identity_cluster' and e.get('changed_bodies'):
            members = sorted(draft_of[m] for m in e['members'] if m in draft_of)  # file order
            add('duplicate_id', drafts=members, key=e['key'], options=list(DUPLICATE_ACTIONS), blocking=True,
                help='Two sources declare the same id with different text. Pick how they enter the ledger.')
        elif k in {'descriptive_reference_review', 'unresolved_reference_review'}:
            add('reference_review', from_draft=draft_of.get(e['to']) or draft_of.get(e['from']),
                reason=e.get('reason'), target_key=e.get('target_key'),
                candidates=[draft_of.get(c['occurrence']) for c in e.get('candidates', [])],
                evidence_quote=(e.get('claim_scope_quote') or quote_of.get(e['evidence_nodes'][-1], '')).strip(),
                options=['ignore', 'field_correction', 'supersede'], to_draft=None, corrects_field=None,
                valid_from=None, valid_until=None, blocking=False,
                help='Machine could not resolve this. To apply it, set to_draft and an action yourself.')
    for d in drafts:
        if d['declared_status'] and d['declared_status'].lower() in {'retired', 'superseded', 'withdrawn', 'cancelled', 'canceled'}:
            add('declared_status', draft=d['draft_id'], value=d['declared_status'], options=list(STATUS_ACTIONS), blocking=False,
                help='The source says it is no longer current. "withdraw_after_write" keeps it in the folder but not served.')
    return out


def propose(dump, ledger=None, prefix='DUMP', auto_accept_clean=False):
    if not SAFE_ID.fullmatch(prefix):
        raise ClassingError('Prefix must be a safe id')
    graph = sorter_v2.sort_directory(dump, 'compare')
    taken=_existing_ids(ledger)
    drafts = _occurrence_drafts(graph, Path(dump).resolve(), prefix, taken)
    decisions = _decisions(graph, drafts)
    touched = {d for x in decisions if x['blocking'] for d in x.get('drafts', [])}
    for d in drafts:
        decisions_for_draft=[x for x in decisions if x.get('from_draft')==d['draft_id']
                             and x['kind'] in {'correction','partial_correction'} or x.get('draft')==d['draft_id']]
        if decisions_for_draft:d['blockers'].append('serving_decision_required')
        if d['draft_id'] in touched and 'duplicate_declared_id' not in d['blockers']:
            d['blockers'].append('open_blocking_decision')
        d['auto_accept_eligible'] = d['auto_accept_eligible'] and not d['blockers'] and graph['complete']
        if auto_accept_clean and d['auto_accept_eligible']:
            d['decision'] = 'accept'
    review = {'schema': SCHEMA, 'sorter': {'schema': graph['schema'], 'graph_sha256': graph['graph_sha256'],
                                           'complete': graph['complete'], 'limits_or_exclusions': graph['limits_or_exclusions']},
              'dump_sources': [{'path': s['path'], 'raw_sha256': s['raw_sha256'], 'decoding': s.get('decoding', 'utf-8')} for s in graph['sources']],
              'target_ledger': str(ledger) if ledger else None,
              'generation':{'prefix':prefix,'taken_ids':sorted(taken),'auto_accept_clean':bool(auto_accept_clean)},
              'how_to_review': ['Set each draft "decision" to "accept" or "reject".',
                                'Optionally edit page.title/scope/when_to_use/not_for/owner/source_authorship/external/event_id/occurrence_id.',
                                'Add reviewer_fields as {"label","value","quote"}: quote must appear verbatim in the source and contain value.',
                                'For each decision set "choice" to one of its options (and corrects_field for field_correction).',
                                'Set "ratify": true only for drafts you personally stand behind, then build with --ratify-by "Your Name".'],
              'drafts': drafts, 'decisions': decisions}
    review['review_sha256'] = _digest({k: v for k, v in review.items() if k != 'review_sha256'})
    return review


def _check_literal(draft, text):
    errors = []
    for f in draft['fields']:
        a, b = f['char_span']
        if text[a:b] != f['value'] and f['label'] != 'Designation':
            errors.append(f"{draft['draft_id']}: field {f['label']!r} no longer matches source bytes")
        if f['label'] == 'Designation' and f['value'] not in text:
            errors.append(f"{draft['draft_id']}: designation not found in source")
    a,b=draft['source']['char_span'];text=text[a:b]
    for f in draft.get('reviewer_fields', []):
        if not FIELD_LABEL.fullmatch(f.get('label', '')) or f['label'].casefold() in {x.casefold() for x in PROVENANCE_LABELS}:
            errors.append(f"{draft['draft_id']}: reviewer field label {f.get('label')!r} is not allowed")
        elif not f.get('value') or f['value'] not in f.get('quote', '') or f.get('quote', '') not in text:
            errors.append(f"{draft['draft_id']}: reviewer field {f['label']!r} is not a literal quote of the source")
    if draft['body'] and draft['body'] not in text:
        errors.append(f"{draft['draft_id']}: body no longer matches source")
    return errors


def _page_body(draft):
    rows = [f"{f['label']}: {f['value']}" for f in draft['fields'] + draft.get('reviewer_fields', [])]
    src = draft['source']
    rows += [f"{PROVENANCE_LABELS[0]}: {src['path']}", f"{PROVENANCE_LABELS[1]}: {src['raw_sha256']}",
             f"{PROVENANCE_LABELS[2]}: {src['byte_span'][0]}-{src['byte_span'][1]}"]
    # One field per paragraph: the strict reader cannot split stacked fields.
    return '\n'.join('<pre>'+html.escape(value)+'</pre>' for value in rows + ([draft['body']] if draft['body'] else []))


def plan(review, dump):
    """Validate a reviewed file against the dump; return the ordered write plan."""
    if not isinstance(review,dict) or len(json.dumps(review,ensure_ascii=False).encode())>sorter_v2.DEFAULT_LIMITS['output_bytes']:
        raise ClassingError('Review exceeds its byte budget or has invalid shape')
    if review.get('schema') != SCHEMA or review.get('review_sha256') is None:
        raise ClassingError('Not a classing review file')
    graph = sorter_v2.sort_directory(dump, 'compare')
    if graph['graph_sha256'] != review['sorter']['graph_sha256']:
        raise ClassingError('The dump changed since this review was proposed; propose again')
    if not graph['complete']:raise ClassingError('Incomplete sorter extraction cannot authorize a build')
    generation=review.get('generation',{})
    baseline=_occurrence_drafts(graph,Path(dump).resolve(),generation.get('prefix','DUMP'),set(generation.get('taken_ids',[])))
    expected={d['draft_id']:d for d in baseline}
    decisions={x['decision_id']:x for x in _decisions(graph,baseline)}
    if len(review['drafts'])!=len(expected) or {d['draft_id'] for d in review['drafts']}!=set(expected):
        raise ClassingError('Draft inventory differs from source occurrences')
    if len(review['decisions'])!=len(decisions) or {x['decision_id'] for x in review['decisions']}!=set(decisions):
        raise ClassingError('Decision inventory differs from source observations')
    for d in review['drafts']:
        for key in ('occurrence','source','fields','body','declared_status'):
            if d[key]!=expected[d['draft_id']][key]:raise ClassingError('Extracted source evidence is immutable: '+key)
        if set(d['page'])!=set(expected[d['draft_id']]['page']) or d['page']['origin']!='machine':
            raise ClassingError('Invalid page metadata or origin')
    editable={'choice','to_draft','corrects_field','valid_from','valid_until'}
    for x in review['decisions']:
        old=decisions[x['decision_id']]
        if set(x)!=set(old) or any(x[k]!=v for k,v in old.items() if k not in editable):
            raise ClassingError('Decision evidence/options are immutable')
        if old.get('to_draft') is not None and x.get('to_draft')!=old['to_draft']:
            raise ClassingError('An explicit source target cannot be silently replaced')
    drafts = {d['draft_id']: copy.deepcopy(d) for d in review['drafts']}
    errors = []
    for x in review['decisions']:
        if x['choice'] is not None and x['choice'] not in x['options']:
            errors.append(f"{x['decision_id']}: choice {x['choice']!r} is not one of {x['options']}")
        if x['blocking'] and x['choice'] is None and any(drafts[d]['decision'] == 'accept' for d in x.get('drafts', [])):
            errors.append(f"{x['decision_id']}: blocking {x['kind']} decision is unanswered")
        actor=x.get('from_draft') if x['kind'] in {'correction','partial_correction'} else x.get('draft')
        if actor and drafts[actor]['decision']=='accept' and x['choice'] is None:
            errors.append(f"{x['decision_id']}: serving decision is unanswered")
    accepted = {k: d for k, d in drafts.items() if d['decision'] == 'accept'}
    for d in drafts.values():
        if d['decision'] not in {'accept', 'reject', 'pending'}:
            errors.append(f"{d['draft_id']}: decision must be accept, reject or pending")
    for d in accepted.values():
        if not SAFE_ID.fullmatch(d['page']['doc_id']):
            errors.append(f"{d['draft_id']}: unsafe doc_id")
        if not d['page']['scope'].strip():
            errors.append(f"{d['draft_id']}: scope is required")
        text = _source(dump,d['source']['path']).read_bytes()
        if _sha(text) != d['source']['raw_sha256']:
            errors.append(f"{d['draft_id']}: source file changed")
            continue
        errors += _check_literal(d, text.decode('utf-8'))
    # Duplicate decisions rewrite drafts before relations are planned.
    supersedes, field_of, withdraw = {}, {}, set()
    for x in review['decisions']:
        if x['kind'] == 'duplicate_id' and x['choice']:
            first, *rest = x['drafts']
            for other in rest:
                if x['choice'] == 'reject_second':
                    accepted.pop(other, None)
                elif x['choice'] == 'second_supersedes_first' and first in accepted and other in accepted:
                    supersedes.setdefault(other, []).append(first)
                    if accepted[other]['page']['doc_id'] == accepted[first]['page']['doc_id']:
                        accepted[other]['page']['doc_id'] += '-REV'
        elif x['kind'] in {'correction', 'partial_correction', 'reference_review'} and x['choice'] not in (None, 'ignore'):
            src, dst = x.get('from_draft'), x.get('to_draft')
            if src not in accepted or dst not in accepted:
                errors.append(f"{x['decision_id']}: both drafts must be accepted to apply {x['choice']}")
                continue
            if x['choice'] == 'field_correction':
                if not x.get('corrects_field') or not FIELD_LABEL.fullmatch(x['corrects_field']):
                    errors.append(f"{x['decision_id']}: field_correction needs corrects_field")
                    continue
                field_of[src] = (x['corrects_field'], x.get('valid_from') or '', x.get('valid_until') or '')
            supersedes.setdefault(src, []).append(dst)
        elif x['kind'] == 'declared_status' and x['choice'] == 'withdraw_after_write' and x['draft'] in accepted:
            withdraw.add(x['draft'])
    ids = [d['page']['doc_id'] for d in accepted.values()]
    if len(ids) != len(set(ids)):
        errors.append('Two accepted drafts share a doc_id; resolve the duplicate decision')
    order, state = [], {}
    def visit(k):
        if state.get(k) == 1:
            errors.append(f'{k}: supersession cycle')
            return
        if state.get(k) == 2:
            return
        state[k] = 1
        for dep in supersedes.get(k, []):
            visit(dep)
        state[k] = 2
        order.append(k)
    for k in sorted(accepted):
        visit(k)
    if errors:
        raise ClassingError('Review is not buildable:\n  ' + '\n  '.join(dict.fromkeys(errors)))
    return {'order': order, 'drafts': accepted, 'supersedes': supersedes, 'field_of': field_of, 'withdraw': withdraw}


def _apply(root, steps, ratify_by):
    """Write in dependency order. Ratification is recorded on the page as it is
    written (``ratified_by``), so the id is kept and the named person stands
    behind exactly the reviewed content. A later ``ledger.ratify`` would mint a
    new id and could not ratify a page already superseded for one field."""
    from mplpb_combined.ledger import write, withdraw, build_index
    written, ratified = [], []
    for key in steps['order']:
        d = steps['drafts'][key]
        p = d['page']
        field, start, until = steps['field_of'].get(key, ('', '', ''))
        who = ratify_by if (d.get('ratify') and ratify_by) else ''
        rec = write(root, doc_id=p['doc_id'], title=p['title'], scope=p['scope'], when_to_use=p['when_to_use'],
                    not_for=p['not_for'], owner=p['owner'], origin='machine', body_html=_page_body(d),
                    source_authorship=p['source_authorship'], external=p['external'],
                    event_id=p['event_id'], occurrence_id=p['occurrence_id'], ratified_by=who,
                    supersedes=[steps['drafts'][s]['page']['doc_id'] for s in steps['supersedes'].get(key, [])],
                    corrects_field=field, valid_from=start, valid_until=until,
                    note=f"classing {d['draft_id']} from {d['source']['path']}" + (f'; ratified by {who}' if who else ''))
        written.append({'draft_id': key, 'doc_id': rec.id, 'hash': rec.hash, 'depth': rec.depth_declared})
        if who:
            ratified.append(rec.id)
    for key in sorted(steps['withdraw']):
        withdraw(root, steps['drafts'][key]['page']['doc_id'], note='source declared it no longer current')
    build_index(root)
    return written, ratified


def _validate(root):
    from mplpb_combined.ledger import Ledger
    findings = Ledger(Path(root), serving=False).findings()
    return [str(f) for f in findings if f.level == 'error'], [str(f) for f in findings if f.level != 'error']


def _files(root):
    """Bounded local ledger snapshot, excluding only the native writer lock."""
    from mplpb_combined.ledger import LOG_DIR,LOCK_NAME
    out={};size=0
    for p in sorted(Path(root).rglob('*')):
        if p.is_symlink():raise ClassingError('Ledger symlinks cannot be staged')
        if not p.is_file() or p.relative_to(root)==Path(LOG_DIR)/LOCK_NAME:continue
        with p.open('rb') as stream:raw=stream.read(64*1024*1024-size+1)
        size+=len(raw)
        if len(out)>=4096 or size>64*1024*1024:raise ClassingError('Ledger staging budget exceeded')
        out[p.relative_to(root)]=raw
    return out


def _publish_append(target,stage,before):
    from mplpb_combined.ledger import ledger_lock,_atomic_write
    after=_files(stage);changed=[]
    with ledger_lock(target):
        if _files(target)!=before:raise ClassingError('Target ledger changed during rehearsal; propose again')
        try:
            for name,raw in after.items():
                if before.get(name)==raw:continue
                changed.append(name)
                _atomic_write(target/name,raw.decode('utf-8'),must_be_new=name not in before)
        except Exception:
            for name in reversed(changed):
                if name in before:_atomic_write(target/name,before[name].decode('utf-8'),must_be_new=False)
                else:(target/name).unlink(missing_ok=True)
            raise


def build(review, dump, ledger, append=False, ratify_by=None, reviewed_by=None):
    review=copy.deepcopy(review)
    steps = plan(review, dump)
    if not steps['drafts']:raise ClassingError('No accepted drafts')
    target = Path(ledger).resolve()
    if Path(dump).resolve() in [target, *target.parents]:
        raise ClassingError('The ledger must be outside the dump')
    if target in Path(dump).resolve().parents:raise ClassingError('The dump must be outside the ledger')
    if target.exists() and not append:
        raise ClassingError('Ledger exists; pass --append to add pages to it')
    if append and not target.is_dir():
        raise ClassingError('--append needs an existing ledger directory')
    if any(d.get('ratify') for d in steps['drafts'].values()) and not ratify_by:
        raise ClassingError('Drafts are marked ratify; pass --ratify-by "Name" (a person, not a tool)')
    reviewer=reviewed_by or ratify_by
    def active_decision(x):
        if x['choice'] is None:return False
        if x['kind']=='duplicate_id':return any(d in steps['drafts'] for d in x['drafts'])
        if x['kind']=='declared_status':return x['draft'] in steps['drafts']
        if x['kind']=='reference_review' and x['choice']=='ignore':return False
        return x.get('from_draft') in steps['drafts']
    judgment=any(active_decision(x) for x in review['decisions']) or any(
        d.get('reviewer_fields') or d['page']['source_authorship']!='unknown' or d['page']['external']
        or d['page']['event_id'] or d['page']['occurrence_id'] for d in steps['drafts'].values())
    if judgment and not reviewer:raise ClassingError('Serving decisions and reviewer fields require --reviewed-by or --ratify-by')
    for name in (reviewer,ratify_by):
        if name is not None and (not isinstance(name,str) or not name.strip() or len(name)>128
                                or any(ord(c)<32 for c in name) or name.casefold() in {'ai','codex','chatgpt','assistant','machine','tool','system'}):
            raise ClassingError('Name a person as reviewer/ratifier, not a tool')
    target.parent.mkdir(parents=True,exist_ok=True)
    before=_files(target) if append else None
    with tempfile.TemporaryDirectory(dir=target.parent, prefix='.mplpb-classing-') as tmp:
        stage = Path(tmp) / 'ledger'
        if append:
            from mplpb_combined.ledger import LOG_DIR,LOCK_NAME
            shutil.copytree(target, stage,ignore=lambda directory,names: [LOCK_NAME] if Path(directory)==target/LOG_DIR else [])
            if _files(stage)!=before:raise ClassingError('Target ledger changed during staging')
        written, ratified = _apply(stage, steps, ratify_by)
        errors, warnings = _validate(stage)
        if errors:
            raise ClassingError('Rehearsal failed validation; nothing written:\n  ' + '\n  '.join(errors))
        if sorter_v2.sort_directory(dump,'compare')['graph_sha256']!=review['sorter']['graph_sha256']:
            raise ClassingError('The dump changed during rehearsal; nothing published')
        if append:
            _publish_append(target,stage,before)
        else:
            os.replace(stage, target)
    return {'schema': 'mplpb-classing-receipt-v1', 'review_sha256': _digest(review),
            'proposal_sha256':review['review_sha256'],'reviewed_by':reviewer,
            'reviewer_identity_authenticated':False,'answer_supported':False,
            'sorter_graph_sha256': review['sorter']['graph_sha256'], 'ledger': str(target), 'appended': append,
            'pages_written': written, 'ratified': ratified, 'ratified_by': ratify_by if ratified else None,
            'withdrawn': [steps['drafts'][k]['page']['doc_id'] for k in sorted(steps['withdraw'])],
            'validation': {'errors': errors, 'warnings': warnings},
            'notice': 'Pages are machine-assembled literal copies. Source support is not truth; ratification is a person standing behind a page.'}


def status(review):
    drafts = review['drafts']
    counts = {k: sum(1 for d in drafts if d['decision'] == k) for k in ('accept', 'reject', 'pending')}
    open_blocking = [x['decision_id'] for x in review['decisions'] if x['blocking'] and x['choice'] is None]
    open_other = [x['decision_id'] for x in review['decisions'] if not x['blocking'] and x['choice'] is None]
    return {'drafts': counts, 'auto_accept_eligible': sum(d['auto_accept_eligible'] for d in drafts),
            'blocking_decisions_open': open_blocking, 'other_decisions_open': open_other,
            'ready_to_build': counts['accept'] > 0 and not open_blocking}


def _save(path, value):
    data = (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    with os.fdopen(fd, 'wb') as f:
        f.write(data)


def _load_review(path):
    from mplpb_answers.evidence_contract import loads
    with Path(path).open('rb') as stream:raw=stream.read(sorter_v2.DEFAULT_LIMITS['output_bytes']+1)
    if len(raw)>sorter_v2.DEFAULT_LIMITS['output_bytes']:raise ClassingError('Review exceeds its byte budget')
    return loads(raw.decode('utf-8'))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('propose'); p.add_argument('dump'); p.add_argument('--ledger'); p.add_argument('--prefix', default='DUMP')
    p.add_argument('--auto-accept-clean', action='store_true'); p.add_argument('--output', required=True)
    s = sub.add_parser('status'); s.add_argument('review')
    b = sub.add_parser('build'); b.add_argument('review'); b.add_argument('--dump', required=True); b.add_argument('--ledger', required=True)
    b.add_argument('--append', action='store_true'); b.add_argument('--ratify-by'); b.add_argument('--receipt')
    b.add_argument('--reviewed-by',help='declared person authorizing reviewed serving choices; not authenticated identity')
    args = parser.parse_args(argv)
    try:
        if args.command == 'propose':
            review = propose(args.dump, args.ledger, args.prefix, args.auto_accept_clean)
            _save(args.output, review)
            result = dict(status(review), output=args.output, sorter_complete=review['sorter']['complete'],
                          sorter_limits_or_exclusions=review['sorter']['limits_or_exclusions'])
        elif args.command == 'status':
            result = status(_load_review(args.review))
        else:
            review = _load_review(args.review)
            result = build(review, args.dump, args.ledger, args.append, args.ratify_by,args.reviewed_by)
            if args.receipt:
                _save(args.receipt, result)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (ClassingError, ValueError, OSError, KeyError,TypeError,IndexError) as exc:
        print(json.dumps({'status': 'refused', 'error': str(exc)}), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
