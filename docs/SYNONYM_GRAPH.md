# SQLite synonym graph

Last reviewed: 2026-11-22.

The graph is an opt-in index for suggesting record IDs and field labels. It
uses the standard Python SQLite driver and stores collections, phrases,
selectors, direct matches, and directed phrase links in separate tables. The
database can be reopened read-only for lookup. It is a separate SQLite file
from the WorkStore.

## Build and query

The native wheel installs `mplpb-synonym-graph`. Use `query` for JSON or
`suggest` for a readable preview that preserves the original question.
From a source checkout, the `python -m test_tools.graph_synonym_index` entry
point continues to work.

```sh
mplpb-synonym-graph build \
  --catalog evaluation/persona-corpus-transfer/synonyms.json --db /tmp/synonyms.sqlite
mplpb-synonym-graph suggest --db /tmp/synonyms.sqlite \
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

## Triage communication issues

Export questions as a JSON array with `id` and `question` per case, or pass a
Dice Bag operator packet. The report is written to standard output and runs
locally against a read-only graph.

```sh
mplpb-synonym-graph review --db /tmp/synonyms.sqlite \
  --collection coelacanth --questions questions.json > review.json
```

Use the report to group unmatched fields or records, competing selectors,
and traversal limits. A unique pair is marked `review_full_question` so a
reviewer can check every condition before using the pair. Add or revise an
edge in a separate reviewed catalog and rerun the same questions before
promoting the change. In a Dice Bag source checkout, pass `--graph-db PATH`
to the existing `run` command to retain graph lookup and strict-reader
results in the same report. A new held-out batch tests whether the change
transfers beyond the replay.

## Verification

On the unchanged 72-question Dice Bag packet, the SQLite graph using the
original lexicon reproduced every flat-index lookup, including 36 unique
candidate pairs, 12 ambiguous lookups, and 24 incomplete lookups. The graph
added path explanations. Separate authored controls cover multi-hop links,
direction, cycles, competing selectors, collection isolation and incomplete
traversal. The parity run measured preservation of existing lookup behavior
with the same vocabulary. Broader vocabulary coverage requires new reviewed
links and a new evaluation.

With the graph as the selected Dice Bag backend, the 72-case full score
file was byte-identical to the original. The communication review grouped
24 questions with unmatched fields, 12 with competing records, and 36
unique pairs needing whole-question review. The 36 strict negative
controls all withheld support. [Replay receipt](../evaluation/dice-bag/sqlite-graph-replay.json)

[Dice Bag evaluation](../evaluation/dice-bag/README.md) ·
[Regression tests](../tests/test_graph_synonym_index.py)
