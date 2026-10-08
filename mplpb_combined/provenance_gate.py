"""Return separate local source pages with verified structural provenance.

This gate gathers lexical evidence; it does not turn co-occurrence into a
relationship or synthesize an answer. Every matching eligible page remains
visible, including multiple pages matching the same requested word.
"""
from __future__ import annotations

import re
import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from .delivery import external_restriction, authorship, clarification
from .ledger import Ledger, ORIGINS
from .reader import Profile, PROFILES, DEFAULT_PROFILE, declared_terms, page_terms, not_for_terms, terms


@dataclass
class GateResult:
    question: str
    profile: str
    query_terms: list = field(default_factory=list)
    sources: list = field(default_factory=list)
    excluded: list = field(default_factory=list)
    term_sources: dict = field(default_factory=dict)
    query_flags: list = field(default_factory=list)
    policy: dict = field(default_factory=dict)
    corpus_snapshot: str = ''
    shared_lineage: list = field(default_factory=list)

    @property
    def kind(self):
        return 'source_bundle' if self.sources else 'not_in_corpus'

    @property
    def unmatched_terms(self):
        return sorted(t for t in self.query_terms if not self.term_sources.get(t))

    @property
    def lexical_coverage(self):
        if not self.query_terms or not self.sources:
            return 'none'
        return 'partial' if self.unmatched_terms else 'complete'

    def to_dict(self):
        data = {
            'kind': self.kind, 'question': self.question, 'profile': self.profile,
            'query_terms': self.query_terms, 'sources': self.sources,
            'term_sources': self.term_sources, 'unmatched_terms': self.unmatched_terms,
            'lexical_coverage': self.lexical_coverage, 'excluded': self.excluded,
            'query_flags': self.query_flags,
            'policy': self.policy, 'corpus_snapshot': self.corpus_snapshot,
            'shared_lineage': self.shared_lineage,
            'evidence_status': 'retrieved_pages_not_truth_certification',
            'relationship_status': 'not_established_by_retrieval',
            'answer_synthesized': False, 'authorship_authenticated': False,
            'notice': ('Each source is presented separately. Complete lexical coverage means '
                       'the requested words occur across sources, not that a page answers '
                       'the question or that separate facts are related. Origin and owner '
                       'are page declarations, not authenticated identities.'),
        }
        hint = clarification(set(self.query_terms))
        if hint:
            data["clarification"] = hint
        return data


def _digest(value):
    encoded = json.dumps(value, sort_keys=True, separators=(',', ':')).encode('utf-8')
    return 'sha256:' + hashlib.sha256(encoded).hexdigest()


def _retired_dependencies(ledger, record):
    """Follow derived-from only: a retired supersedes predecessor is normal."""
    stale, seen, stack = set(), set(), [record]
    while stack:
        rec = stack.pop()
        if rec.path in seen:
            continue
        seen.add(rec.path)
        for ref in rec.derived_from:
            parent = ledger.by_id[ref.id][0]  # caller already verified the pinned graph
            if ledger.effective_status(parent) != 'current':
                stale.add(parent.id)
            stack.append(parent)
    return sorted(stale)


def _lineage(ledger, record, errors):
    """Require intact unique records and pinned, acyclic, depth-valid ancestry."""
    stack = [(record, frozenset())]
    visited = {}
    while stack:
        rec, trail = stack.pop()
        if rec.path in trail:
            return None, 'cyclic lineage'
        reason = ledger.quarantine_reason(rec)
        if reason:
            return None, rec.id + ': ' + reason
        if len(ledger.by_id.get(rec.id, [])) != 1:
            return None, rec.id + ': duplicate identifier'
        # Do not use Record.origin's legacy fallback for missing origin fields.
        if rec.fields.get('origin') not in ORIGINS:
            return None, rec.id + ': missing or invalid explicit origin'
        if rec.depth_declared is None:
            return None, rec.id + ': invalid origin depth'
        if rec.path in errors:
            return None, rec.id + ': ' + '; '.join(errors[rec.path])
        if rec.path in visited:
            continue
        visited[rec.path] = rec
        for ref in list(rec.derived_from) + list(rec.supersedes):
            parents = ledger.by_id.get(ref.id, [])
            if len(parents) != 1 or not ref.hash:
                return None, rec.id + ': lineage reference is not uniquely hash-pinned'
            parent = parents[0]
            if parent.hash_actual != ref.hash:
                return None, rec.id + ': lineage reference hash mismatch'
            stack.append((parent, trail | {rec.path}))
    for rec in visited.values():
        if rec.depth_declared != ledger.derived_depth(rec):
            return None, rec.id + ': lineage depth mismatch'
    return [visited[p] for p in sorted(visited) if p != record.path], ''


def _identity(ledger, rec):
    return {'id': rec.id, 'path': rec.path, 'title': rec.title,
            'origin': rec.fields['origin'], 'origin_depth': ledger.depth(rec),
            'owner': rec.fields.get('owner', ''), 'updated': rec.fields.get('updated', ''),
            'status': ledger.effective_status(rec), 'declared_status': rec.status,
            'hash': rec.hash, 'derived_from': [str(r) for r in rec.derived_from],
            'supersedes': [str(r) for r in rec.supersedes],
            'ratified_by': rec.ratified_by, 'location': 'local'}


def gather(root, question: str, profile: Optional[Profile] = None) -> GateResult:
    """Gather every eligible page matching at least one distinct content term.

    Scope matches are shown separately from prose-only matches. Scope and
    eligible prose are consulted together, so one subject page cannot hide a
    budget page. Page order is deterministic; there is no top-one selection.
    """
    if not isinstance(question, str):
        raise ValueError('question must be a string')
    profile = profile or PROFILES[DEFAULT_PROFILE]
    path = Path(root).resolve()
    if not path.is_dir():
        raise FileNotFoundError('not a directory: ' + str(path))
    # Check the boundary before the ledger reads any page bytes.
    for page in path.rglob('*.html'):
        if any(p.startswith('.') for p in page.relative_to(path).parts):
            continue
        if path not in page.resolve().parents:
            raise ValueError('HTML page escapes the corpus root: ' + page.relative_to(path).as_posix())
    ledger = Ledger(path)
    content = terms(question)
    result = GateResult(question, profile.name, sorted(content),
                        term_sources={t: [] for t in sorted(content)})
    settings = {'gate_version': 2, 'mode': 'separate_lexical_sources',
                'max_depth': profile.max_depth, 'prose': profile.prose, 'not_for': profile.not_for,
                'enforce_sealed_external_policy': True, 'synthesize': False, 'follow_pointers': False, 'require_current_dependencies': True}
    result.policy = dict(settings, settings_hash=_digest(settings))
    result.corpus_snapshot = _digest([
        {'path': r.path, 'id': r.id, 'hash': r.hash_actual, 'status': ledger.effective_status(r)}
        for r in ledger.records if r.kind != 'index'])
    if re.search(r'\b(?:not|no|never|without)\b', question.lower()):
        result.query_flags.append('Negation is present. Lexical evidence does not decide the premise.')
    if not content:
        return result
    errors = {}
    for finding in ledger.findings():
        if finding.level == 'error':
            errors.setdefault(finding.path, []).append(finding.message)
    for rec in ledger.records:
        if rec.kind == 'index':
            continue
        # Pointers are navigation, not source evidence. They are not followed.
        if rec.kind == 'pointer':
            result.excluded.append({'id': rec.id, 'path': rec.path, 'reason': 'pointer, not evidence'})
            continue
        ancestry, reason = _lineage(ledger, rec, errors)
        if not reason:
            reason = external_restriction(rec, profile)
        if not reason and ledger.effective_status(rec) != 'current':
            reason = 'retired'
        if not reason:
            stale = _retired_dependencies(ledger, rec)
            if stale:
                reason = 'requires recheck: retired or superseded dependency ' + ', '.join(stale)
        if not reason and profile.max_depth is not None and ledger.depth(rec) > profile.max_depth:
            reason = 'withheld by profile depth'
        excluded_terms = sorted(content & not_for_terms(rec)) if profile.not_for else []
        if not reason and excluded_terms:
            reason = 'not-for: ' + ', '.join(excluded_terms)
        if reason:
            result.excluded.append({'id': rec.id, 'path': rec.path, 'reason': reason})
            continue
        scope = content & declared_terms(rec)
        full = page_terms(rec) if profile.prose else declared_terms(rec)
        matched = content & full
        if not matched:
            continue
        source = _identity(ledger, rec)
        source.update({'scope': rec.scope, 'when_to_use': rec.when_to_use,
                       'not_for': rec.not_for, 'text': rec.text,
                       'matched_terms': sorted(matched), 'scope_terms': sorted(scope),
                       'prose_only_terms': sorted(matched - scope),
                       'unmatched_terms': sorted(content - matched),
                       'matches_every_query_term': matched == content,
                       'ancestry': [_identity(ledger, parent) for parent in ancestry],
                       'evidence_basis': {'delivery': 'verbatim_page_text',
                                          'content_truth_verified': False,
                                          'original_claim_basis': 'not_encoded_by_legacy_page_format'},
                       'recheck_conditions': ['source changes', 'dependency is superseded or retired',
                                              'serving policy changes'],
                       'verification': {'hash_intact': True, 'lineage_pinned': True,
                                        'origin_explicit': True, 'authorship_authenticated': False}})
        if authorship(rec):
            source["source_authorship"] = authorship(rec)
        result.sources.append(source)
        for term in sorted(matched):
            result.term_sources[term].append(rec.id)
    roots = {}
    for source in result.sources:
        nodes = [source] + source['ancestry']
        for node in nodes:
            if not node['derived_from'] and not node['supersedes']:
                roots.setdefault((node['id'], node['hash']), set()).add(source['id'])
    result.shared_lineage = [{'root_id': rid, 'root_hash': hash_value, 'source_ids': sorted(ids),
                              'notice': 'Shared declared ancestry; these pages are not independent corroboration.'}
                             for (rid, hash_value), ids in sorted(roots.items()) if len(ids) > 1]
    return result


def render(result: GateResult) -> str:
    data = result.to_dict()
    if not result.sources:
        lines = ['Not in corpus: no eligible source matches the content words.']
    else:
        lines = [f'{len(result.sources)} separate source page(s); '
                 f'lexical coverage: {result.lexical_coverage}.']
    lines += [data['notice']]
    lines += ['Serving policy: ' + result.policy['settings_hash'],
              'Corpus snapshot: ' + result.corpus_snapshot]
    if result.unmatched_terms:
        lines.append('No eligible source for: ' + ', '.join(result.unmatched_terms))
    lines.extend(result.query_flags)
    for shared in result.shared_lineage:
        lines.append('Shared lineage: ' + shared['root_id'] + ' → ' +
                     ', '.join(shared['source_ids']) + '. ' + shared['notice'])
    for source in result.sources:
        lines += ['', source['title'],
                  'Matches: ' + ', '.join(source['matched_terms']),
                  'Scope matches: ' + (', '.join(source['scope_terms']) or '(none)'),
                  'Prose-only matches: ' + (', '.join(source['prose_only_terms']) or '(none)'),
                  source['text'],
                  '[{id} · {path} · {status} · declared origin {origin} d{origin_depth} · '
                  'owner {owner} · {hash} · local]'.format(**source)]
        if source.get('source_authorship'):
            lines.append(source['source_authorship']['notice'])
        for parent in source['ancestry']:
            lines.append('  lineage: {id} · {origin} d{origin_depth} · {status} · {hash}'.format(**parent))
    if result.excluded:
        lines += ['', 'Excluded pages:']
        lines.extend('  {id} · {path}: {reason}'.format(**e) for e in result.excluded)
    if data.get("clarification"):
        lines += [data["clarification"]["prompt"]] + ["  - " + c for c in data["clarification"]["choices"]] + [data["clarification"]["notice"]]
    return '\n'.join(lines)
