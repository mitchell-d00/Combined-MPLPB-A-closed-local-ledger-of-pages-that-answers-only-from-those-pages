"""Persistent SQLite synonym graph for reviewable record and field suggestions."""
import argparse
from collections import Counter, defaultdict, deque
from contextlib import closing, contextmanager
import json
from pathlib import Path
import re
import sqlite3
import unicodedata

APPLICATION_ID = 0x4D505347
VERSION = 1
MAX_PHRASE_WORDS = 16
MAX_LINKS = 4
MAX_STATES = 256
FACETS = ('records', 'fields')
WORDS = re.compile(r"[\w]+(?:[-'’][\w]+)*")
SCHEMA = """
CREATE TABLE collections (name TEXT PRIMARY KEY);
CREATE TABLE terms (
    collection TEXT NOT NULL REFERENCES collections(name),
    facet TEXT NOT NULL CHECK(facet IN ('records', 'fields')),
    phrase TEXT NOT NULL,
    PRIMARY KEY (collection, facet, phrase)
);
CREATE INDEX term_lookup ON terms(collection, phrase, facet);
CREATE TABLE selectors (
    collection TEXT NOT NULL REFERENCES collections(name),
    facet TEXT NOT NULL CHECK(facet IN ('records', 'fields')),
    value TEXT NOT NULL,
    PRIMARY KEY (collection, facet, value)
);
CREATE TABLE matches (
    collection TEXT NOT NULL,
    facet TEXT NOT NULL,
    phrase TEXT NOT NULL,
    value TEXT NOT NULL,
    PRIMARY KEY (collection, facet, phrase, value),
    FOREIGN KEY (collection, facet, phrase) REFERENCES terms,
    FOREIGN KEY (collection, facet, value) REFERENCES selectors
);
CREATE TABLE links (
    collection TEXT NOT NULL,
    facet TEXT NOT NULL,
    source TEXT NOT NULL,
    target TEXT NOT NULL,
    PRIMARY KEY (collection, facet, source, target),
    FOREIGN KEY (collection, facet, source) REFERENCES terms,
    FOREIGN KEY (collection, facet, target) REFERENCES terms
);
"""


def words(text):
    return tuple(WORDS.findall(unicodedata.normalize('NFC', text).casefold()))


def phrase_key(phrase):
    tokens = words(phrase)
    if not 1 <= len(tokens) <= MAX_PHRASE_WORDS:
        raise ValueError(f'An indexed phrase needs between 1 and {MAX_PHRASE_WORDS} words')
    return ' '.join(tokens)


def associations(mapping):
    if not isinstance(mapping, dict):
        raise ValueError('Expected a mapping from phrases or selectors to lists')
    for key, values in mapping.items():
        if not isinstance(key, str) or not isinstance(values, list) or not all(
                isinstance(value, str) for value in values):
            raise ValueError('Use strings as keys and lists of strings as values')
        yield key, values


def load_catalog(db, catalog):
    """Build a graph from the existing catalog format and optional directed links."""
    if catalog.get('schema') != 'mplpb-synonym-index-v1':
        raise ValueError('Unsupported synonym index schema')
    db.execute('PRAGMA foreign_keys=ON')
    db.executescript(SCHEMA)
    with db:
        db.execute(f'PRAGMA application_id={APPLICATION_ID}')
        db.execute(f'PRAGMA user_version={VERSION}')
        for name, spec in sorted(catalog['collections'].items()):
            db.execute('INSERT INTO collections VALUES (?)', (name,))
            links = spec.get('links', {})
            if links.keys() - set(FACETS):
                raise ValueError('Unknown synonym link facet')
            for facet in FACETS:
                scope = (name, facet)
                direct = {(phrase_key(phrase), value)
                          for value, aliases in associations(spec[facet]) for phrase in [value, *aliases]}
                edges = {(phrase_key(src), phrase_key(dst))
                         for src, targets in associations(links.get(facet, {})) for dst in targets}
                terms = {term for term, _ in direct} | {term for pair in edges for term in pair}
                db.executemany('INSERT INTO terms VALUES (?, ?, ?)',
                               ((*scope, term) for term in sorted(terms)))
                db.executemany('INSERT INTO selectors VALUES (?, ?, ?)',
                               ((*scope, value) for value in sorted(spec[facet])))
                db.executemany('INSERT INTO matches VALUES (?, ?, ?, ?)',
                               ((*scope, phrase, value) for phrase, value in sorted(direct)))
                db.executemany('INSERT INTO links VALUES (?, ?, ?, ?)',
                               ((*scope, src, dst) for src, dst in sorted(edges)))


class GraphSynonymIndex:
    def __init__(self, db):
        self.db = db
        if (db.execute('PRAGMA application_id').fetchone()[0] != APPLICATION_ID
                or db.execute('PRAGMA user_version').fetchone()[0] != VERSION):
            raise ValueError('Expected a supported SQLite synonym graph')

    def _seeds(self, collection, question):
        tokens = words(question)
        spans = sorted({' '.join(tokens[start:end])
                        for start in range(len(tokens))
                        for end in range(start + 1, min(start + MAX_PHRASE_WORDS, len(tokens)) + 1)})
        for offset in range(0, len(spans), 200):
            batch = spans[offset:offset + 200]
            slots = ','.join('?' for _ in batch)
            yield from self.db.execute(f"""
                SELECT facet, phrase FROM terms
                WHERE collection=? AND phrase IN ({slots})
                ORDER BY facet, phrase
            """, (collection, *batch))

    def lookup(self, collection, question):
        if len(question) > 400:
            raise ValueError('Synonym lookup question exceeds 400 characters')
        if self.db.execute('SELECT 1 FROM collections WHERE name=?', (collection,)).fetchone() is None:
            raise ValueError('Unknown synonym graph collection')
        options = {facet: defaultdict(set) for facet in FACETS}
        explanations = {facet: {} for facet in FACETS}
        result = {'collection': collection, 'status': 'limited',
                  'records': {}, 'fields': {}, 'paths': {'records': {}, 'fields': {}}}
        states = 0
        for facet, seed in sorted(self._seeds(collection, question)):
            queue = deque([(seed, (seed,))])
            visited, beyond = {seed}, set()
            while queue:
                term, path = queue.popleft()
                states += 1
                if states > MAX_STATES:
                    return result
                params = (collection, facet, term, MAX_STATES + 1)
                values = self.db.execute("""
                    SELECT value FROM matches WHERE collection=? AND facet=? AND phrase=?
                    ORDER BY value LIMIT ?
                """, params).fetchall()
                links = self.db.execute("""
                    SELECT target FROM links WHERE collection=? AND facet=? AND source=?
                    ORDER BY target LIMIT ?
                """, params).fetchall()
                if len(values) + len(links) > MAX_STATES:
                    return result
                for value, in values:
                    options[facet][value].add(seed)
                    explanations[facet].setdefault(value, []).append(
                        {'phrases': list(path), 'selector': value})
                for target, in links:
                    if target in visited:
                        continue
                    if len(path) > MAX_LINKS:
                        beyond.add(target)
                    else:
                        visited.add(target)
                        queue.append((target, (*path, target)))
            if beyond - visited:
                return result
        result['status'] = ('ambiguous' if any(len(hit) > 1 for hit in options.values())
                            else 'candidate' if all(options.values()) else 'incomplete')
        for facet in FACETS:
            result[facet] = {value: sorted(hits) for value, hits in sorted(options[facet].items())}
            result['paths'][facet] = dict(sorted(explanations[facet].items()))
        return result


def build(path, catalog):
    path.touch(exist_ok=False)
    try:
        with closing(sqlite3.connect(path)) as db:
            load_catalog(db, catalog)
    except Exception:
        path.unlink()
        raise


@contextmanager
def open_index(path):
    uri = path.resolve().as_uri() + '?mode=ro'
    with closing(sqlite3.connect(uri, uri=True)) as db:
        db.execute('PRAGMA trusted_schema=OFF')
        db.execute('BEGIN')
        yield GraphSynonymIndex(db)


def review(index, collection, cases):
    """Group local communication cases by the next decision they need."""
    if not isinstance(cases, list):
        raise ValueError('Expected a question list or an object with a cases list')
    seen, rows = set(), []
    counts = Counter()
    for case in cases:
        if not isinstance(case, dict):
            raise ValueError('Each case requires a unique string ID and a question')
        ident, question = case.get('id'), case.get('question')
        if not isinstance(ident, str) or not ident.strip() or ident in seen:
            raise ValueError('Each case requires a unique string ID')
        if not isinstance(question, str) or not question.strip():
            raise ValueError('Each case requires a question')
        seen.add(ident)
        result = index.lookup(collection, question)
        issues = []
        if result['status'] == 'limited':
            issues.append('traversal_limit')
        else:
            for facet in FACETS:
                if not result[facet]:
                    issues.append('unmatched_' + facet)
                elif len(result[facet]) > 1:
                    issues.append('competing_' + facet)
            if not issues:
                issues.append('review_full_question')
        counts.update(issues)
        rows.append({'id': ident, 'question': question, 'lookup': result, 'review': issues})
    return {'collection': collection, 'questions': len(rows), 'review_counts': dict(sorted(counts.items())),
            'cases': rows}


def suggestion(question, result):
    intro = {
        'candidate': 'Did you mean this record and field?',
        'ambiguous': 'Several records or fields match. Review the alternatives.',
        'incomplete': 'The lookup could not match both a record and a field.',
        'limited': 'The graph reached its lookup limit. No pair was selected.',
    }
    lines = [intro[result['status']], f'Question: {question}']
    for facet, label in [('records', 'Record'), ('fields', 'Field')]:
        for value, matched in result[facet].items():
            lines.append(f'{label}: {value} (matched {", ".join(matched)})')
    lines.append('Review the full question, including any conditions. These are suggestions for source checking.')
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    builder = commands.add_parser('build')
    builder.add_argument('--catalog', type=Path, required=True)
    query = commands.add_parser('query')
    suggest = commands.add_parser('suggest')
    review_command = commands.add_parser('review')
    for command in (query, suggest, review_command):
        command.add_argument('--collection', required=True)
    for command in (query, suggest):
        command.add_argument('question')
    review_command.add_argument('--questions', type=Path, required=True)
    for command in (builder, query, suggest, review_command):
        command.add_argument('--db', type=Path, required=True)
    args = parser.parse_args()
    if args.command == 'build':
        build(args.db, json.loads(args.catalog.read_bytes()))
        return
    with open_index(args.db) as index:
        if args.command == 'review':
            packet = json.loads(args.questions.read_bytes())
            cases = packet.get('cases') if isinstance(packet, dict) else packet
            result = review(index, args.collection, cases)
        else:
            result = index.lookup(args.collection, args.question)
    if args.command == 'suggest':
        print(suggestion(args.question, result))
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
