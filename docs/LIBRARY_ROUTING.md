# Explicit library routing

The library layer implements the BOOT navigation contract over registered MPLPB
corpora: broad requests show a sub-index; a selected book passes the complete
question to the supported reader; uncertain scope asks for clarification. It
never blends books or treats a route label as answer evidence.

This is a deterministic reference library, not model training. Open licensing,
local storage, hashes and repeatable decisions do not certify source truth.

## Use it

In ordinary Chat or Serious mode, choose **Library index**, or type:

```
browse library
library browse shelf-logic
library ask: What is the kettle color?
library choose shelf-logic
library ask in shelf-logic: What is Dungeons and Dragons?
```

The kettle example is a question syntax example, not a claim that a bundled book
contains its answer. An unscoped question with multiple book scopes asks you to
choose. `library choose ID` reruns the pending question with fresh source checks.
An intervening unrelated request clears the pending library question. Saved chat
can resume a clarification; saved answers are never substitutes for fresh checks.

The default index lists registered bundled and saved collections. Browsing it
reads their route metadata, not every page body. Groups show up to 20 choices per
page; the displayed next-page command preserves a pending question when needed.
IDs are exact addresses. Human-readable titles and aliases must be unique to
resolve automatically; a shared alias produces choices. There is no fuzzy
best-score winner and no automatic natural-language domain classifier.

Off-the-record free chat explicitly asks you to leave that mode before accessing
ledger collections. Library operations never trigger automatic Wikipedia lookup,
even when the general automatic-lookup setting is enabled. Explicit search is a
separate operation.

## Define a hierarchy

Pass a JSON manifest to the desktop UI:

```sh
python tools/ledger_ui.py --library-manifest examples/library-routing/catalog.json
```

The example supplies Main Index → sub-index → book routes for existing bundled
collections. A manifest has `version: 1`, a root ID, and nodes with `id`, `title`,
`parent`, optional `aliases`, and optional `corpus`. A `corpus` is an already
registered key, never an arbitrary path embedded in a route. A book leaf cannot
have child nodes. Duplicate IDs, duplicate corpus registrations, missing parents,
cycles and unknown corpus keys are rejected. Limits are 10,000 total nodes and
64 levels. Configuration is metadata, not evidence.

The packaged standard-library CLI also accepts explicit local book roots:

```sh
python -m mplpb_answers.library \
  --manifest examples/library-routing/catalog.json \
  --corpus studio=examples/studio \
  --corpus logic=examples/chat-logic \
  --corpus system=examples/system \
  --shelf logic --question 'What is Dungeons and Dragons?'
```

Installed distributions expose the same command as `mplpb-library`. Arbitrary
PDFs or ebooks must first become validated MPLPB pages; this layer does not
silently convert or ingest books. Browser mode uses its registered local corpus
catalog; the custom manifest flag is currently a desktop/CLI/API capability.

## Answer and audit contract

1. Resolve an exact route to one book. With multiple descendant books, ask for a
   narrower scope instead of opening every book or ranking competing scopes.
2. Recheck the selected corpus through `supported_answer`: current revisions,
   lineage, delivery profile, scope eligibility and supported body statements.
   Metadata alone never supplies a factual answer. Multiple supporting pages or
   conflicts cause clarification. Unsupported grammar abstains.
3. Return the supported excerpt with its source ID, path and hash. Return up to
   three other eligible pages in the same book as **navigation only**, ordered
   deterministically by path and ID. These are not extra answer evidence or a
   semantic relevance ranking. If none exists, invent none.
4. Include the selected path, reverse path back to Main Index, catalog hash,
   selected page, support checks and rule tag (`LIBRARY-BROAD`,
   `LIBRARY-SPECIFIC`, or `LIBRARY-NARROW`) under `library_route` in the response.
   The UI exposes this under **Evidence and decision rules**.
5. Before a chat answer is released, reconstruct the route and answer and compare
   the result. A newly introduced conflict, changed catalog, changed page or
   altered response text invalidates the answer. Existing source-pin checks also
   apply. Context may supply the question and selected shelf, never its answer.

Pointer targets outside the registered leaf are not silently relabelled as that
leaf's sources; register the destination as a separate book. A library request
explicitly selects from the registered library; it does not silently change the
session's loaded Serious-mode collections.

## Scale measurements and limits

A synthetic benchmark (`python -m tools.benchmark_library_routes`) holds the
selected book at **one page** and grows the metadata catalog. The other book
paths are deliberately unopened. Five repeated answers use a preselected shelf.
An observed local run produced:

| Shelves | Catalog build, ms | Peak catalog allocation, bytes | Median answer, ms | Distinct books opened |
| --- | ---: | ---: | ---: | ---: |
| 10 | 2.008 | 23,611 | 1.786 | 1 |
| 100 | 6.406 | 207,817 | 2.315 | 1 |
| 1,000 | 79.870 | 2,128,709 | 1.494 | 1 |
| 5,000 | 521.468 | 10,789,325 | 2.473 | 1 |

Timing depends on host and workload. Catalog construction was measured with
tracemalloc enabled; query timing excludes construction. The chat adapter
currently constructs a catalog per request and again during final validation.
These numbers are not end-to-end chat latency or full-library performance.

Route metadata is in memory and grows with shelf count. The existing reader
rebuilds a ledger and scans the selected book; this layer does not make a
million-page book constant-time or eliminate disk I/O. Full-book conflict checks
are retained deliberately. A future persistent page index must prove equivalent
eligibility, revision, negative-statement and conflict decisions before replacing
those scans. Real-library routing coverage, source truth, broad procedural
understanding, and cross-book synthesis have not been established by this test.

## Regression coverage

`tests/test_library_routing.py` covers scope collisions, nested navigation,
pagination, no unselected-book reads, body-vs-metadata support, negation, wrong
entities, conflicting pages, delivery restrictions, revisions, stale proofs,
changed catalogs, replay, saved clarifications, both source-reading chat modes,
network isolation and the free-chat boundary. WebAssembly checks exercise the
same ambiguity → choose → supported answer flow in the embedded Python runtime.

Validation for this implementation: all 601 Python tests passed in 275.526
seconds. All 30 focused library/self-knowledge/structured-request tests passed.
Actual Pyodide WebAssembly routing checks, UI script checks, browser transport,
crawler fixtures, and the packaged CLI smoke check passed. These are local
validation results; the newly deployed public site was not rechecked here.
