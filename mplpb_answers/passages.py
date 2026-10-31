"""Query-independent passage preparation and bounded BM25 retrieval after gating."""
from collections import Counter
import math
import re
from mplpb_combined import provenance_gate as G
from mplpb_combined.ledger import Ledger
from mplpb_combined.reader import PROFILES, DEFAULT_PROFILE, terms
from .body_text import body_text, VERSION as BODY_VERSION
from .evidence_contract import pin, ReaderError


class PassageIndex:
    def __init__(self, root, question, profile=None):
        self.root, self.question = root, question
        self.profile = profile or PROFILES[DEFAULT_PROFILE]
        self.gate = G.gather(root, question, self.profile)
        if self.gate.policy.get('gate_version') != 2 or not self.gate.query_terms:
            raise ReaderError('unsupported_question', 'A content-bearing question and a known gate policy are required')
        ledger = Ledger(root)
        current_snapshot = G._digest([{'path': r.path, 'id': r.id, 'hash': r.hash_actual, 'status': ledger.effective_status(r)}
                                      for r in ledger.records if r.kind != 'index'])
        if current_snapshot != self.gate.corpus_snapshot:
            raise ReaderError('source_changed', 'Corpus changed while preparing the eligible passage index')
        if any(r.kind == 'pointer' for r in ledger.servable()):
            raise ReaderError('unresolved_corpus', 'Choose a directly resolved evidence corpus')
        excluded = {row['path'] for row in self.gate.excluded}
        lexical = {row['path'] for row in self.gate.sources}
        # gather evaluates structural/profile/not-for eligibility for every page,
        # including pages with no matching words. Its exclusions are authoritative.
        # prose=False profiles retain the original scope-only retrieval boundary.
        records = [r for r in ledger.servable() if r.kind not in {'pointer', 'index'}
                   and r.path not in excluded and (self.profile.prose or r.path in lexical)]
        self.sources, self.passages = [], []
        for rec in records:
            body = body_text(rec.body_html)
            if not body:
                continue
            source = {'id': rec.id, 'path': rec.path, 'hash': rec.hash_actual, 'title': rec.title,
                      'origin': rec.origin, 'origin_depth': ledger.depth(rec), 'scope': rec.scope, 'not_for': rec.not_for,
                      'derived_from': [str(r) for r in rec.derived_from], 'supersedes': [str(r) for r in rec.supersedes]}
            stack, visited, roots = [rec], set(), set()
            while stack:
                node = stack.pop()
                if node.path in visited:
                    continue
                visited.add(node.path)
                parents = list(node.derived_from)+list(node.supersedes)
                if not parents:
                    roots.add(node.id+'@'+node.hash_actual)
                for ref in parents:
                    stack.append(ledger.by_id[ref.id][0])
            source['evidence_roots'] = sorted(roots)
            self.sources.append(source)
            offset = 0
            for paragraph in body.splitlines():
                # Preserve full paragraphs. Very long blocks use overlapping
                # windows and carry a truncation label, rather than hiding it.
                for start in range(0, len(paragraph), 3500):
                    chunk = paragraph[max(0, start-250):start+4000]
                    if not chunk.strip():
                        continue
                    begin = offset+max(0, start-250)
                    identity = {'source': rec.path, 'hash': rec.hash_actual, 'start': begin, 'text': chunk}
                    self.passages.append({'id': pin(identity), 'source_id': rec.id, 'path': rec.path,
                        'hash': rec.hash_actual, 'body_start': begin, 'text': chunk,
                        'body_projection': BODY_VERSION, 'context_truncated': len(paragraph) > 4000})
                    if start+4000 >= len(paragraph):
                        break
                offset += len(paragraph)+1

    def retrieve(self, queries, max_passages=24, max_chars=24000):
        if not 1 <= max_passages <= 64 or not 1000 <= max_chars <= 64000:
            raise ValueError('Invalid retrieval budget')
        if not isinstance(queries, list) or len(queries) > 4 or any(not isinstance(q, str) or len(q) > 4000 for q in queries):
            raise ReaderError('invalid_reader_output', 'Invalid retrieval query list')
        counts = [Counter(t for token in re.findall(r'[^\W_]+', re.sub(r"['’]s\b", '', p['text'].casefold())) for t in terms(token)) for p in self.passages]
        # Reuse the core term normalization per token while retaining frequency.
        # This is deterministic ranking, never semantic evidence.
        n = len(counts)
        lengths = [sum(c.values()) for c in counts]
        avg = sum(lengths)/n if n else 1
        df = Counter(t for row in counts for t in row)
        query = set().union(*(terms(q) for q in queries)) if queries else set()
        ranked = []
        for i, row in enumerate(counts):
            score = sum(math.log(1+(n-df[t]+0.5)/(df[t]+0.5))*row[t]*2.2 /
                        (row[t]+1.2*(0.25+0.75*lengths[i]/max(avg, 1))) for t in query if row[t])
            ranked.append((score, i))
        ranked.sort(key=lambda pair: (-pair[0], self.passages[pair[1]]['path'], self.passages[pair[1]]['body_start']))
        # Greedy page-diversity discount keeps strong second paragraphs ahead
        # of unrelated zero-overlap pages. Zero-score fallback rotates pages.
        selected, size, page_counts = [], 0, Counter()
        remaining = list(ranked)
        while remaining and len(selected) < max_passages:
            remaining.sort(key=lambda pair: (-pair[0]/(1+page_counts[self.passages[pair[1]]['path']]),
                            page_counts[self.passages[pair[1]]['path']],
                            self.passages[pair[1]]['path'], self.passages[pair[1]]['body_start']))
            score, i = remaining.pop(0)
            p = self.passages[i]
            if size+len(p['text']) > max_chars:
                continue
            selected.append(dict(p, retrieval_score=score))
            page_counts[p['path']] += 1
            size += len(p['text'])
        paths = {p['path'] for p in selected}
        groups = {}
        for source in self.sources:
            if source['path'] in paths:
                for root in source['evidence_roots']:
                    groups.setdefault(root, []).append(source['id'])
        return {'lineage_groups': [{'root': root, 'sources': sorted(ids)} for root, ids in sorted(groups.items())],
                'independence_verified': False, 'passages': selected, 'sources': [s for s in self.sources if s['path'] in paths],
                'eligible_pages': len(self.sources), 'total_passages': len(self.passages),
                'search_complete': len(selected) == len(self.passages), 'queries': queries,
                'corpus_snapshot': self.gate.corpus_snapshot, 'ranking': 'bm25-with-page-diversity-v1'}

    def unchanged(self):
        try:
            current = G.gather(self.root, self.question, self.profile)
            return (current.corpus_snapshot == self.gate.corpus_snapshot
                    and current.policy.get('settings_hash') == self.gate.policy.get('settings_hash')
                    and current.profile == self.gate.profile)
        except (OSError, ValueError):
            return False
