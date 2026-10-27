"""Provenance-gated, one-owner page retrieval. Never a supported-answer fallback."""
from . import reader as R
from .ledger import Ledger
from .provenance_gate import gather

VERSION = 'gated-page-retrieval-v1'


def retrieve(root, question, profile=None):
    if not isinstance(question, str) or not question.strip() or len(question) > 4000:
        raise ValueError('Enter a question of 1–4000 characters')
    if any(ord(c) < 32 and c not in '\n\t\r' for c in question):
        raise ValueError('Control characters are not valid query text')
    profile = profile or R.PROFILES[R.DEFAULT_PROFILE]
    # Gather checks root escapes, intact seals, unique IDs, explicit origins,
    # pinned lineage, current dependencies, exclusions and delivery policy.
    gate = gather(root, question, profile)
    ledger = Ledger(root)
    if any(rec.kind == 'pointer' for rec in ledger.servable()):
        selected = R.Answer(R.NOT_IN_CORPUS, question, profile, str(ledger.root),
                            reason='Page retrieval requires a directly selected corpus; no pointer is followed.')
    else:
        selected = R.answer(root, question, profile)
    decision = selected.to_dict()
    decision.update(mode='page_retrieval', answer_supported=False,
                    answer_support={'status': 'not_evaluated', 'spans': []})
    source = None
    if selected.kind == R.RETURN:
        matches = [s for s in gate.sources if selected.record and
                   s['id'] == selected.record.id and s['path'] == selected.record.path and
                   s['hash'] == selected.record.hash_actual and s['text'] == selected.record.text]
        if len(matches) == 1:
            source = matches[0]
        else:
            # Do not search for a different owner after the gate rejects the
            # selected one. Preserve diagnostics, withhold its text/citation.
            decision.update(kind=R.NOT_IN_CORPUS, id=None, path=None, hash=None,
                            text='', reason='Selected owner failed the provenance gate; no replacement owner chosen.')
    decision['citation'] = selected.citation() if source else ''
    if not source:
        decision['text'] = ''
    return {'version': VERSION,
            'kind': 'retrieved' if source else decision['kind'],
            'reply': source['text'] if source else '',
            'decision': decision,
            'citation': decision['citation'],
            'source': source,
            'gate': gate.to_dict(),
            'answer_supported': False,
            'authority': 'source_page_retrieval',
            'notice': ('Retrieved page text only. No answer to the question, permission, '
                       'semantic entailment, factual truth or cross-surface claim is certified.')}
