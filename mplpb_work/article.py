"""Read-only assembly of existing research reports, never a new proof engine.

Each question retains its own native checker, policy and candidate report.
No cross-section relationship, event merge, witness independence or historical
truth is inferred. Known ledger ancestry is structural provenance only.
"""
import copy

from mplpb_answers.evidence_contract import pin, ReaderError
from mplpb_combined import provenance_gate as G
from mplpb_combined.reader import PROFILES, DEFAULT_PROFILE
from .prose_evidence import reconstruct_report, render_reconstruction

VERSION = 'documentary-article-v1'
MAX_SECTIONS = 8
MAX_SOURCES_PER_SECTION = 256


def validate_plan(plan):
    if not isinstance(plan, dict) or set(plan) != {'title', 'questions'}:
        raise ValueError('Article plan requires only title and questions; no supplied answers or prose')
    title, questions = plan['title'], plan['questions']
    if not isinstance(title, str) or not title.strip() or len(title) > 240 or '\n' in title or '\r' in title:
        raise ValueError('Article title must be a single line of 1–240 characters')
    if not isinstance(questions, list) or not 1 <= len(questions) <= MAX_SECTIONS:
        raise ValueError('Article plan requires 1–8 questions')
    if any(not isinstance(q, str) or not q.strip() or len(q) > 4000 for q in questions):
        raise ValueError('Each original question must contain 1–4000 characters')
    if len(set(questions)) != len(questions):
        raise ValueError('Duplicate questions do not create additional evidence')
    return copy.deepcopy(plan)


def _state(gate):
    return pin({'question': gate.question, 'profile': gate.profile,
                'policy': gate.policy, 'corpus_snapshot': gate.corpus_snapshot})


def _identity(source):
    # Deliberately exclude titles and page text: metadata is not article evidence.
    return {key: copy.deepcopy(source[key]) for key in
            ('id', 'path', 'hash', 'derived_from', 'supersedes', 'origin_depth', 'status')}


def _provenance(gates):
    sources, roots = {}, {}
    for gate in gates:
        for source in gate.sources:
            key = (source['id'], source['hash'], source['path'])
            sources[key] = dict(_identity(source), ancestry=[_identity(p) for p in source['ancestry']])
            # Same structural grouping as the provenance gate, across the union
            # of question-specific source bundles. No historical dependence is
            # inferred from similar wording or an absence of declared ancestry.
            for node in [source] + source['ancestry']:
                if not node['derived_from'] and not node['supersedes']:
                    root = (node['id'], node['hash'])
                    roots.setdefault(root, set()).add(key)
    groups = []
    for (identifier, digest), members in sorted(roots.items()):
        if len(members) > 1:
            groups.append({'root_id': identifier, 'root_hash': digest,
                           'source_ids': sorted({key[0] for key in members}),
                           'notice': 'Shared declared ancestry; not independent corroboration.'})
    return {'sources': [sources[key] for key in sorted(sources)],
            'shared_declared_roots': groups, 'independent_witness_count': None,
            'independence_verified': False,
            'scope': 'Union of question-eligible source metadata, not a set of supporting witnesses.',
            'notice': 'Declared ancestry is not authenticated historical transmission. Missing ancestry does not establish independence.'}


def assemble(root, plan, profile=None, *, max_passages=12, max_chars=12000):
    """Assemble a bounded research snapshot without authoring new assertions.

    Full original questions reach the existing checker and eligibility gate.
    Check all question-specific source states again after the last section;
    discard the whole assembly if any changed. This is an optimistic snapshot,
    not a filesystem transaction or a promise of future source eligibility.
    """
    plan = validate_plan(plan)
    profile = PROFILES[profile] if isinstance(profile, str) else profile or PROFILES[DEFAULT_PROFILE]
    if profile.name not in PROFILES or profile != PROFILES[profile.name]:
        raise ValueError('Choose a known delivery profile')
    if type(max_passages) is not int or not 1 <= max_passages <= 64:
        raise ValueError('Passage budget must be 1–64 per section')
    if type(max_chars) is not int or not 1000 <= max_chars <= 64000:
        raise ValueError('Context budget must be 1000–64000 characters per section')
    result = {'schema': VERSION, 'plan': plan, 'profile': profile.name,
              'status': 'article_snapshot', 'sections': [],
              'coverage': {'complete_sections': 0, 'unresolved_sections': len(plan['questions'])},
              'provenance': _provenance([]), 'source_state_pins': [],
              'cross_section_relationships': [], 'answer_supported': False,
              'source_support_established': False, 'historical_truth_independently_verified': False,
              'budgets': {'max_sections': MAX_SECTIONS, 'max_passages_per_section': max_passages,
                          'max_context_chars_per_section': max_chars,
                          'max_eligible_sources_per_section': MAX_SOURCES_PER_SECTION},
              'search_complete': False,
              'notice': 'Research assembly only. Section answers retain their own support scope. No article-level historical conclusion, event identity or independent corroboration is established.'}

    def stop(status):
        # All-or-nothing assembly on a source-state failure: no stale earlier
        # section, candidate graph, source quote or provenance list survives.
        result.update(status=status, sections=[], provenance=_provenance([]), source_state_pins=[])
        result['coverage'] = {'complete_sections': 0, 'unresolved_sections': len(plan['questions'])}
        return result

    try:
        gates = [G.gather(root, q, profile) for q in plan['questions']]
        if any(len(g.sources) > MAX_SOURCES_PER_SECTION for g in gates):
            return stop('source_budget_exceeded')
        for question, gate in zip(plan['questions'], gates):
            report = reconstruct_report(root, question, profile, max_passages=max_passages, max_chars=max_chars)
            if report['status'] != 'research_report':
                return stop('source_changed')
            result['sections'].append({'question': question,
                'eligible_source_refs': [{'id': s['id'], 'path': s['path'], 'hash': s['hash']} for s in gate.sources],
                'report': report})
        if any(_state(G.gather(root, q, profile)) != _state(g)
               for q, g in zip(plan['questions'], gates)):
            return stop('source_changed')
    except (OSError, ReaderError):
        return stop('source_unavailable')
    result['source_state_pins'] = [_state(g) for g in gates]
    result['provenance'] = _provenance(gates)
    complete = sum(s['report']['native_answer']['kind'] == 'supported_answer'
                   and s['report']['native_answer']['answer_supported'] is True for s in result['sections'])
    result['coverage'] = {'complete_sections': complete, 'unresolved_sections': len(plan['questions'])-complete}
    result['snapshot_pin'] = pin(result)
    return result


def render(article):
    """Render an inspection snapshot as plain text, without generated bridges.

    A saved/exported report is not active evidence; rerun assemble to recheck it.
    This renderer makes no authority decision and must not be used as a verifier.
    """
    lines = ['DOCUMENTARY ARTICLE — RESEARCH DOSSIER', 'Topic label: '+article['plan']['title'],
             'Snapshot only; rerun article to recheck current source eligibility.', article['notice'],
             'Independent witnesses: NOT ESTABLISHED']
    if article['status'] != 'article_snapshot':
        return '\n'.join(lines + ['Assembly withheld: '+article['status']])
    for group in article['provenance']['shared_declared_roots']:
        lines.append('Shared declared root '+group['root_id']+'@'+group['root_hash']+': '+', '.join(group['source_ids']))
    for number, section in enumerate(article['sections'], 1):
        lines += ['', 'SECTION '+str(number), render_reconstruction(section['report'])]
    lines += ['', 'Cross-section connections: none established by assembly.',
              'Search completeness: not established.']
    return '\n'.join(lines)
