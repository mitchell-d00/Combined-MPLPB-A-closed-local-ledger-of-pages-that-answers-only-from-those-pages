"""An offline, discovery-only WordNet graph and independent Moby reference."""
import argparse
from contextlib import closing
from hashlib import sha256
from io import TextIOWrapper
import json
import os
from pathlib import Path
import re
import sqlite3
import tarfile
from tempfile import TemporaryDirectory

VERSION = 'local-thesaurus-discovery-v1'
_WORDNET_FILES = ('noun', 'verb', 'adj', 'adv')
_RELATIONS = {
    '@': 'broader', '@i': 'broader_instance',
    '~': 'narrower', '~i': 'narrower_instance',
    '#m': 'member_of', '#s': 'substance_of', '#p': 'part_of',
    '%m': 'has_member', '%s': 'has_substance', '%p': 'has_part',
}


def _normalized(value):
    return ' '.join(value.replace('_', ' ').casefold().split())


def _hash(path):
    digest = sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def _sense(pos, offset):
    return ('a' if pos == 's' else pos) + ':' + offset


def _member(archive, path):
    member = archive.getmember('WordNet-3.0/' + path)
    if not member.isfile() or member.size > 32 * 1024 * 1024:
        raise ValueError('Expected a bounded regular WordNet input file')
    return TextIOWrapper(archive.extractfile(member), encoding='ascii')


def _import_wordnet(db, path):
    with tarfile.open(path, 'r:gz') as archive:
        with _member(archive, 'LICENSE') as license_file:
            license_text = license_file.read()
        for domain in _WORDNET_FILES:
            senses, lemmas, links = [], [], []
            with _member(archive, 'dict/data.' + domain) as stream:
                for line in stream:
                    if not re.match(r'^[0-9]{8} ', line):
                        continue
                    fields = line.split('|', 1)[0].split()
                    ident = _sense(fields[2], fields[0])
                    end = 4 + 2 * int(fields[3], 16)
                    words = {_normalized(re.sub(r'\((?:p|a|ip)\)$', '', word))
                             for word in fields[4:end:2]}
                    senses.append((ident, fields[2]))
                    lemmas.extend((word, ident) for word in sorted(words))
                    for i in range(end + 1, end + 1 + 4 * int(fields[end]), 4):
                        symbol, offset, part, position = fields[i:i + 4]
                        if position == '0000' and symbol in _RELATIONS:
                            links.append((ident, _sense(part, offset), _RELATIONS[symbol]))
            db.executemany('INSERT INTO senses VALUES (?, ?)', senses)
            db.executemany('INSERT INTO lemmas VALUES (?, ?)', lemmas)
            db.executemany('INSERT OR IGNORE INTO relations VALUES (?, ?, ?)', links)
    invalid = db.execute('SELECT 1 FROM relations r LEFT JOIN senses s ON s.id=r.target '
                         'WHERE s.id IS NULL LIMIT 1').fetchone()
    if invalid:
        raise ValueError('WordNet relations link to absent senses')
    return license_text


def _import_reference(db, path):
    with path.open(encoding='latin-1') as stream:
        for line in stream:
            root, *entries = line.rstrip('\r\n').split(',')
            root = _normalized(root)
            if root and entries:
                words = list(dict.fromkeys(_normalized(word) for word in entries if word.strip()))
                db.execute('INSERT INTO reference VALUES (?, ?) ON CONFLICT(word) DO UPDATE SET '
                           'words=excluded.words', (root, json.dumps(words, ensure_ascii=False)))


def build(database, wordnet, reference=None):
    """Build a complete separate index. A failed import leaves no published database."""
    database, wordnet = Path(database), Path(wordnet)
    reference = Path(reference) if reference is not None else None
    if database.exists():
        raise FileExistsError(database)
    with TemporaryDirectory(prefix='thesaurus-build-', dir=database.parent) as folder:
        candidate = Path(folder) / 'lexicon.sqlite'
        with closing(sqlite3.connect(candidate)) as db, db:
            db.executescript('''
                CREATE TABLE metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL);
                CREATE TABLE senses (id TEXT PRIMARY KEY, pos TEXT NOT NULL);
                CREATE TABLE lemmas (word TEXT NOT NULL, sense TEXT NOT NULL, PRIMARY KEY(word, sense));
                CREATE INDEX lemmas_per_sense ON lemmas(sense, word);
                CREATE TABLE relations (source TEXT, target TEXT, kind TEXT, PRIMARY KEY(source, target, kind));
                CREATE TABLE reference (word TEXT PRIMARY KEY, words TEXT NOT NULL);
            ''')
            pins = {'schema': VERSION, 'wordnet_sha256': _hash(wordnet),
                    'moby_sha256': _hash(reference) if reference is not None else None}
            license_text = _import_wordnet(db, wordnet)
            if reference is not None:
                _import_reference(db, reference)
            if (_hash(wordnet) != pins['wordnet_sha256']
                    or (reference is not None and _hash(reference) != pins['moby_sha256'])):
                raise ValueError('The lexical inputs changed during import')
            db.executemany('INSERT INTO metadata VALUES (?, ?)', (
                ('pins', json.dumps(pins)), ('wordnet_license', license_text),
            ))
            counts = {name: db.execute(f'SELECT count(*) FROM {name}').fetchone()[0]
                      for name in ('senses', 'lemmas', 'relations', 'reference')}
        os.link(candidate, database)
    return {'sources': pins, 'counts': counts}


def lookup(database, word, *, sense=None, limit=16):
    if not isinstance(word, str) or not 1 <= len(word.strip()) <= 120 or type(limit) is not int or not 1 <= limit <= 64:
        raise ValueError('Use a short lexical term and an explicit 1–64 result limit')
    word = _normalized(word)
    if not word:
        raise ValueError('Expected a lexical term')
    uri = Path(database).resolve().as_uri() + '?mode=ro'
    with closing(sqlite3.connect(uri, uri=True)) as db:
        pins = json.loads(db.execute("SELECT value FROM metadata WHERE key='pins'").fetchone()[0])
        if pins['schema'] != VERSION:
            raise ValueError('Unsupported thesaurus schema')
        active = db.execute('SELECT s.id, s.pos FROM lemmas l JOIN senses s ON s.id=l.sense '
                            'WHERE l.word=? AND (? IS NULL OR s.id=?) ORDER BY s.id LIMIT ?',
                            (word, sense, sense, limit)).fetchall()
        if sense is not None and not active:
            raise ValueError('Chosen sense does not contain this term')

        def words(ident):
            return [row[0] for row in db.execute('SELECT word FROM lemmas WHERE sense=? ORDER BY word',
                                                 (ident,))]

        senses = []
        for ident, pos in active:
            neighbors = db.execute('SELECT kind, target FROM relations WHERE source=? '
                                   'ORDER BY kind, target LIMIT ?', (ident, limit))
            senses.append({'sense': ident, 'part_of_speech': pos,
                           'synonyms': [term for term in words(ident) if term != word][:limit],
                           'relations': [{'kind': kind, 'sense': target, 'words': words(target)[:limit]}
                                         for kind, target in neighbors]})
        row = db.execute('SELECT words FROM reference WHERE word=?', (word,)).fetchone()
    return {'schema': VERSION, 'term': word, 'senses': senses,
            'reference_associations': json.loads(row[0])[:limit] if row else [],
            'sources': pins, 'answer_supported': False, 'truth_verified': False}



def _edge_spans(index, words, max_passages, max_chars):
    patterns = [(word, re.compile(r'(?<!\w)' + r'\s+'.join(map(re.escape, word.split()))
                                  + r'(?!\w)', re.I)) for word in words]
    ranked = []
    for passage in index.passages:
        if index.exact_status and passage['path'] not in index.exact_paths:
            continue
        matched = [word for word, pattern in patterns if pattern.search(passage['text'])]
        if matched:
            ranked.append((passage, matched))
    ranked.sort(key=lambda row: (-len(row[1]), row[0]['path'], row[0]['body_start']))
    selected, used = [], 0
    for passage, matched in ranked:
        if len(selected) == max_passages:
            break
        size = len(passage['text'])
        if used + size <= max_chars:
            selected.append(dict(passage, matched_terms=matched, answer_supported=False))
            used += size
    return selected


def probe(database, ledger, question, term, sense, *, relation='synonym', profile=None,
          max_passages=12, max_chars=8000):
    """Compare passage discovery after one explicit sense and edge-type selection."""
    from mplpb_answers.passages import PassageIndex

    if sense is None:
        raise ValueError('An explicit sense is required for search expansion')
    view = lookup(database, term, sense=sense)
    chosen = view['senses'][0]
    if relation == 'synonym':
        expanded = chosen['synonyms'][:3]
    elif relation in _RELATIONS.values():
        expanded = list(dict.fromkeys(word for link in chosen['relations'] if link['kind'] == relation
                                      for word in link['words']))[:3]
    else:
        raise ValueError('Choose a supported relation')
    index = PassageIndex(ledger, question, profile)
    baseline = index.retrieve([question], max_passages, max_chars)
    expanded_probe = index.retrieve([question, *expanded], max_passages, max_chars)
    edge_hits = _edge_spans(index, expanded, max_passages, max_chars)
    current = index.unchanged()
    return {'schema': VERSION, 'status': 'ok' if current else 'source_changed',
            'source_pins': view['sources'], 'sense': sense, 'relation': relation,
            'expansion': expanded if current else [], 'answer_supported': False,
            'corpus_snapshot': index.gate.corpus_snapshot if current else None,
            'edge_hits': edge_hits if current else [],
            'baseline': baseline if current else None, 'expanded': expanded_probe if current else None}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    builder = commands.add_parser('build')
    builder.add_argument('database')
    builder.add_argument('wordnet_archive')
    builder.add_argument('--moby')
    query = commands.add_parser('lookup')
    query.add_argument('database')
    query.add_argument('term')
    query.add_argument('--sense')
    discovery = commands.add_parser('probe')
    discovery.add_argument('database')
    discovery.add_argument('ledger', type=Path)
    discovery.add_argument('question')
    discovery.add_argument('term')
    discovery.add_argument('--sense', required=True)
    discovery.add_argument('--relation', default='synonym')
    args = parser.parse_args()
    if args.command == 'build':
        output = build(args.database, args.wordnet_archive, args.moby)
    elif args.command == 'lookup':
        output = lookup(args.database, args.term, sense=args.sense)
    else:
        output = probe(args.database, args.ledger, args.question, args.term, args.sense, relation=args.relation)
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
