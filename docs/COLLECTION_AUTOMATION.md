# From a raw dump to a checked collection

Last reviewed: 2026-11-20.

Use the native tools from the repository checkout or install the Python wheel. Work in a new source folder and keep the original files. The sorter accepts bounded UTF-8 text and Markdown. Documents can contain prose, inconsistent titles and repeated references. A known record ID and literal field labels help the automatic path. The sorter can propose a generated ID for weaker input, which leaves a record for review.

## Build and inspect

1. Put the source files in `RAW`. A card with an explicit source `Record-ID` or `Document-ID` and separate lines such as `Ingredients: 20 g sorrel` and `Preparation: No cook` is eligible for automatic acceptance when it has no classing blockers. Existing source IDs and literal fields travel with the classed copy. A sentence in a serving note remains source prose.
2. Run the sorter in compare mode to see the source occurrences, literal observations and candidate links. Its output gives you source positions and tells you when a budget stopped discovery. A candidate can prompt a review of the originals.
3. Run classing propose with `--auto-accept-clean` and inspect status. Clean, uniquely identified drafts can proceed automatically. Pending or blocked drafts need a decision. Inspect conflicting IDs, corrections and proposed references against the originals. Follow the documented review fields for any deliberate source-backed edits.
4. Build a new ledger. The builder rereads the raw dump, checks the reviewed extraction, stages sealed pages and validates them before publishing. A truncated extraction or changed source stops the build. To ingest a large dump, use bounded batches with nonoverlapping source IDs. Propose each later batch against the same ledger and build it with `--append`.
5. Validate the published ledger. Machine-classed pages carry provenance and usually use the internal profile. Ratification, when needed, is a separately authorized human action.

```sh
python -m mplpb_work.sorter_v2 sort RAW --mode compare --output graph.json
python -m mplpb_work.classing propose RAW --auto-accept-clean --output review.json
python -m mplpb_work.classing status review.json
python -m mplpb_work.classing build review.json --dump RAW --ledger LEDGER --receipt receipt.json
python -m mplpb_work.classing propose NEXT_RAW --ledger LEDGER --auto-accept-clean --output next-review.json
python -m mplpb_work.classing build next-review.json --dump NEXT_RAW --ledger LEDGER --append --receipt next-receipt.json
python -m mplpb_answers validate LEDGER --strict
```

The sorter works in bounded batches. An automatic decision is intentionally limited to evidence it can classify cleanly. When input is prose without stable identifiers or when sources disagree, an inspectable draft can be the result. Fully automated classing of arbitrary prose or arbitrary binary documents remains outside this workflow.

## Ask and investigate

```sh
python -m mplpb_answers ask LEDGER \
  "Which records where Ingredients contains sorrel and Occasion is picnic and Preparation is no cook?" --json
python -m mplpb_answers ask LEDGER "Which recipes use no water?" --max-passages 64 --json
python -m mplpb_answers investigate LEDGER "Trace declared related records" \
  --source SRC-0001 --adaptive-search
```

Strict collection predicates support one to four literal field conditions joined with `and`. Use `Field is value` for a declared scalar, `Field contains item` for a comma-separated list of items, or `Field is explicitly absent` for a declaration such as `None` or `0 ml`. The preparation modifier groups the explicit declarations `No cook`, `No-cook` and `No cooking`. It preserves cooking instructions as different values. Conditions must be satisfied on the same eligible record. Missing, qualified, conflicting or stacked fields can leave that record unresolved. Limited natural-language forms for recipe ingredients, no-water recipes, no-cook occasions, and spell school plus level select the same rules.

The reader checks the eligible collection under the original question and checks its source state again before returning. Scope-only profiles can refuse this body-reading operation. A scan can evaluate up to 4,096 eligible pages and 16 million projected characters. The regular passage and character limits still govern the claims that can be displayed. Use `collection_filter` in JSON for evaluated, verified-match and unresolved counts. Only a complete supported list sets `answer_supported:true`. A count of verified matches in a partial result describes verified records, with the diagnostic explaining the remaining limits.

Investigation builds an in-memory index of declared document identities for the selected eligible ledger. The index covers ingestion batches, subject to the explicit discovery limits. It keeps competing declarations visible and independently verifies visited declarations and endpoints against the current snapshot. A link can remain unavailable or ambiguous. Negated and conditional text does not authorize a hop. Separate ledgers stay separate.

## What the test automation checks

The ordinary Python regression suite includes predicate and investigation controls. It covers exact conjunction, explicit absence, no-cook versus stovetop preparation, missing fields, conflicts, policy, source changes, cross-boundary identity lookup and provenance that could be mistaken for a link. For releases, GitHub Actions tests the exact extracted source archive and the browser build. The Pages workflow checks the deployed browser separately.

[Classing review and receipts](CLASSING.md) · [Investigation and budgets](HISTORICAL_EXPERT_PATH.md) · [ZIP-first release checks](ZIP_FIRST_RELEASE_TESTING.md)
