"""Experimental collection-scoped synonym index. Results are selector candidates."""
import argparse
import json
from pathlib import Path
import re
import unicodedata

WORDS = re.compile(r"[\w]+(?:[-'’][\w]+)*")
CATALOG = Path(__file__).resolve().parents[1] / 'evaluation/persona-corpus-transfer/synonyms.json'


def words(text):
    return tuple(WORDS.findall(unicodedata.normalize('NFC', text).casefold()))


class SynonymIndex:
    """Look up literal whole phrases and retain all competing candidates."""

    def __init__(self, catalog):
        if catalog.get('schema') != 'mplpb-synonym-index-v1':
            raise ValueError('Unsupported synonym index schema')
        self.collections = {}
        for collection, facets in catalog['collections'].items():
            tables = {}
            for facet in ('records', 'fields'):
                table = {}
                for canonical, aliases in facets[facet].items():
                    for phrase in [canonical, *aliases]:
                        tokens = words(phrase)
                        if not tokens:
                            raise ValueError('An indexed expression must contain words')
                        table.setdefault(tokens, set()).add(canonical)
                tables[facet] = table
            self.collections[collection] = tables

    def lookup(self, collection, question):
        if len(question) > 400:
            raise ValueError('Synonym lookup question exceeds 400 characters')
        tokens = words(question)
        options = {}
        for facet, table in self.collections[collection].items():
            hits = {}
            max_phrase = max(map(len, table), default=0)
            for offset in range(len(tokens)):
                for size in range(1, min(len(tokens) - offset, max_phrase) + 1):
                    span = tokens[offset:offset + size]
                    for candidate in table.get(span, ()):
                        hits.setdefault(candidate, set()).add(' '.join(span))
            options[facet] = {candidate: sorted(matches)
                              for candidate, matches in sorted(hits.items())}
        lengths = [len(table) for table in options.values()]
        status = 'ambiguous' if any(n > 1 for n in lengths) else 'candidate' if all(lengths) else 'incomplete'
        return {'collection': collection, 'status': status, **options}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--catalog', type=Path, default=CATALOG)
    parser.add_argument('--collection', required=True)
    parser.add_argument('question')
    args = parser.parse_args()
    index = SynonymIndex(json.loads(args.catalog.read_bytes()))
    if args.collection not in index.collections:
        parser.error('Unknown collection')
    print(json.dumps(index.lookup(args.collection, args.question), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
