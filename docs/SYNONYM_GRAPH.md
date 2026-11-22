# SQLite synonym graph

Last reviewed: 2026-11-22.

The graph is an opt-in index for suggesting record IDs and field labels. It
uses the standard Python SQLite driver and stores collections, phrases,
selectors, direct matches, and directed phrase links in separate tables. The
database can be reopened read-only for lookup. It is a separate SQLite file
from the WorkStore.

## Build and query

```sh
python -m test_tools.graph_synonym_index build \
  --catalog evaluation/persona-corpus-transfer/synonyms.json --db /tmp/synonyms.sqlite
python -m test_tools.graph_synonym_index query --db /tmp/synonyms.sqlite \
  --collection coelacanth 'What catalogue number belongs to the coelacanth display specimen?'
```

A catalog uses the existing `mplpb-synonym-index-v1` schema and may include
an optional `links` object inside each collection. In this example, “inventory
code” reaches the field through two explicitly listed phrase links.

```json
{
  "schema": "mplpb-synonym-index-v1",
  "collections": {
    "museum": {
      "records": {"ITEM-4": ["display fish"]},
      "fields": {"Catalog Number": ["catalogue number"]},
      "links": {
        "fields": {
          "inventory code": ["catalog identifier"],
          "catalog identifier": ["catalogue number"]
        }
      }
    }
  }
}
```

Traversal stays within the selected collection and within the record or field
facet. Links are directional. A shared alias can reach competing selectors,
which are all shown. Lookups include a phrase path for each reached selector
and starting phrase. The graph handles cycles and returns `limited` with no
suggestions if it cannot finish within its traversal budget. A unique match
remains a candidate that carries no proof about the question's qualifiers,
source eligibility, or content. The strict reader remains responsible for
checking the evidence. Rebuild into a new file when the catalog changes.

## Verification

On the unchanged 72-question Dice Bag packet, the SQLite graph using the
original lexicon reproduced every flat-index lookup, including 36 unique
candidate pairs, 12 ambiguous lookups, and 24 incomplete lookups. The graph
added path explanations. Separate authored controls cover multi-hop links,
direction, cycles, competing selectors, collection isolation and incomplete
traversal. The parity run measured preservation of existing lookup behavior
with the same vocabulary. Broader vocabulary coverage requires new reviewed
links and a new evaluation.

[Dice Bag evaluation](../evaluation/dice-bag/README.md) ·
[Regression tests](../tests/test_graph_synonym_index.py)
