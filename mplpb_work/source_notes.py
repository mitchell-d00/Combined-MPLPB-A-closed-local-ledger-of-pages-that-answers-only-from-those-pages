"""Rank source-pinned WorkStore notes for discovery under the live serving policy."""
from collections import Counter
from pathlib import Path

from mplpb_answers.body_text import body_text
from mplpb_answers.evidence_contract import ReaderError
from mplpb_answers.passages import PassageIndex
from mplpb_combined.ledger import Ledger
from mplpb_combined.reader import terms

from .errors import WorkError
from .store import digest

VERSION = 'work-source-notes-discovery-v1'


def pin(root, evidence, start):
    records = [r for r in Ledger(root).servable()
               if r.id == evidence['source_id'] and r.hash_actual == evidence['source_hash']]
    if len(records) != 1:
        return False
    return _matches(records[0], evidence, start)


def _matches(record, evidence, start):
    quote = evidence['quote']
    return body_text(record.body_html)[start:start + len(quote)] == quote


def rank(root: Path, question, profile, pairs, max_passages, max_chars):
    query = terms(question)
    pins, ranked = [], []
    for note, evidence in pairs:
        payload = note['payload']
        keywords = set().union(*(terms(word) for word in payload['keywords']))
        score = len(query & keywords)
        if score:
            pins.append((note['id'], note['revision'], digest(payload), evidence['id'],
                         evidence['revision'], digest(evidence['payload'])))
            ranked.append((score, note, evidence))
    result = {'schema': VERSION, 'status': 'ok', 'question_sha256': digest(question),
              'note_snapshot': digest(sorted(pins)), 'corpus_snapshot': None,
              'policy_sha256': None, 'candidates': [], 'rule_order': [],
              'answer_supported': False, 'truth_verified': False}
    if not ranked:
        return result
    try:
        index = PassageIndex(root, question, profile)
    except ReaderError as error:
        if error.code == 'source_changed':
            result['status'] = 'source_changed'
            return result
        raise WorkError(str(error)) from error
    records = {}
    for record in index.records:
        records.setdefault((record.id, record.hash_actual), []).append(record)
    selected, seen, used = [], set(), 0
    for score, note, evidence_record in sorted(ranked, key=lambda row: (-row[0], row[1]['id'])):
        if len(selected) == max_passages:
            break
        note_data = note['payload']
        evidence = evidence_record['payload']
        matches = records.get((evidence['source_id'], evidence['source_hash']), ())
        start = note_data['body_start']
        quote = evidence['quote']
        if len(matches) != 1 or used + len(quote) > max_chars:
            continue
        record = matches[0]
        identity = (record.path, record.hash_actual, start, len(quote))
        if identity in seen or not _matches(record, evidence, start):
            continue
        selected.append({'note_id': note['id'], 'note_revision': note['revision'],
                         'evidence_id': evidence_record['id'], 'evidence_revision': evidence_record['revision'],
                         'source_id': record.id, 'source_hash': record.hash_actual, 'path': record.path,
                         'body_start': start, 'body_end': start + len(quote), 'quote': quote,
                         'rule': note_data['rule'], 'weight': score, 'answer_supported': False})
        seen.add(identity)
        used += len(quote)
    if not index.unchanged():
        result['status'] = 'source_changed'
        return result
    # The same evidence span gets at most one vote. Different notes on the same
    # passage cannot manufacture stronger support or take additional slots.
    rules = Counter()
    for row in selected:
        rules[row['rule']] += row['weight']
    result.update(candidates=selected, corpus_snapshot=index.gate.corpus_snapshot,
                  policy_sha256=digest(index.gate.policy),
                  rule_order=[{'rule': rule, 'weight': rules[rule]}
                              for rule in sorted(rules, key=lambda name: (-rules[name], name))])
    return result
