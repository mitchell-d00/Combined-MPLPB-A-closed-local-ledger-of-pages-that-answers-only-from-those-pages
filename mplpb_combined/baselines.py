"""Deterministic lexical retrieval baselines; standard library only.

BM25 uses k1=1.2 and b=0.75. TF-IDF uses smoothed IDF and cosine
similarity. Both return top one, break ties by key, and refuse zero overlap.
They share the reader's tokenization so the comparison isolates ranking.
"""
import math
import re
from collections import Counter

from .reader import STOPWORDS, stem


def counts(text):
    words = re.findall(r'[a-z0-9]+', re.sub(r"['\u2019]s\b", '', text.lower()))
    return Counter(stem(w) for w in words if w not in STOPWORDS)


class LexicalIndex:
    def __init__(self, pages):
        self.docs = {key: counts(text) for key, text in sorted(pages.items())}
        self.n = len(self.docs)
        self.df = Counter(t for doc in self.docs.values() for t in doc)
        self.avg_length = sum(sum(doc.values()) for doc in self.docs.values()) / max(1, self.n)

    def rank(self, question, method):
        if method not in ('bm25', 'tfidf'):
            raise ValueError('unknown lexical method: ' + method)
        query = counts(question)
        scores = []
        def idf(t):
            return math.log((1 + self.n) / (1 + self.df.get(t, 0))) + 1
        qnorm = math.sqrt(sum((tf * idf(t)) ** 2 for t, tf in query.items()))
        for key, doc in self.docs.items():
            shared = query.keys() & doc.keys()
            if method == 'bm25':
                length = sum(doc.values())
                score = sum(math.log(1 + (self.n - self.df[t] + .5) / (self.df[t] + .5))
                            * doc[t] * 2.2 / (doc[t] + 1.2 * (.25 + .75 * length / self.avg_length))
                            for t in shared) if self.avg_length else 0
            else:
                dnorm = math.sqrt(sum((tf * idf(t)) ** 2 for t, tf in doc.items()))
                dot = sum(query[t] * doc[t] * idf(t) ** 2 for t in shared)
                score = dot / (qnorm * dnorm) if qnorm and dnorm else 0
            scores.append((key, score))
        return sorted(scores, key=lambda pair: (-pair[1], pair[0]))

    def top(self, question, method):
        ranked = self.rank(question, method)
        return ranked[0][0] if ranked and ranked[0][1] > 0 else None
