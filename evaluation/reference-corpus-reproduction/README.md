# How the 73/73 result was obtained

Last reviewed: 2026-11-02. See [current status and result-to-test index](../../docs/CURRENT_STATUS_2026-11-02.md). Dates and numeric results in historical validation sections retain their original scope; this review is not a rerun or independent certification.

This is the permanent, inspectable evidence bundle for the **73 authored positive reference questions**, plus **20 missing-information controls**. It includes every generated ledger page and per-question result from all four stages. The original test code and frozen inputs were already on main; this bundle makes the generated evidence available without an expiring Actions artifact.

## What 73/73 means

The same strict reader is used at every stage. The collection grows from 0 to 23 to 48 to 73 narrowly scoped fact pages. That produces 0/73 → 23/73 → 48/73 → 73/73 supported positive returns. It is **source collection growth, not the reader learning 73 answers or a measured improvement in general English understanding**.

Every stage asks the same 93 questions. A counted positive must return the expected record ID **and the complete expected quotation**, with an intact record, machine origin, depth 2 and supported evidence status. The builder also checks source-record lineage and seals. All 20 missing-information controls must refuse. The observed stage results, all positive/negative cases, exact source hashes and refusal→support transitions are in the linked reports and CSV.

These questions and declarations were authored for the finite description grammar. They are development acceptance cases, **not an independent human holdout**. Upstream publisher bytes are not included or authenticated: the SRC pages are local machine-built attribution records. A local seal and a correctly returned authored quotation do not certify real-world truth. All facts remain machine-derived, unratified, external=no, and available only through the existing experimental `lab` profile. Nothing here loads these facts into the hosted app's default collections or changes its authority boundaries.

## Everything needed to inspect the result

- [Builder and evaluator](../../tools/build_reference_corpus.py): admission checks, sealed snapshot construction, exact answer scoring and stage deltas.
- [Regression tests](../../tests/test_reference_corpus.py): growth, seals/lineage, restricted profiles, invalid declarations, source tampering, competing owners and revision history.
- [Catalog of all 73 declarations](../../reference_corpus/catalog.v1.json).
- [All 93 frozen questions and expectations](../../reference_corpus/probes.v1.json).
- [Original pre-amendment expectations](../../reference_corpus/probes.v1.pre-amendment.json) and [amendment log](../../reference_corpus/PROBE_AMENDMENTS.md). Nine grammar quotations and the climate-interval quotation were narrowed before release acceptance; their original bytes are retained. No label is rewritten by this reproduction.
- [Combined staged audit](releases/release-audit.json).
- [v0.0.0 audit](releases/v0.0.0/audit.json), [v0.1.0 audit](releases/v0.1.0/audit.json), [v0.2.0 audit](releases/v0.2.0/audit.json), [v0.3.0 audit](releases/v0.3.0/audit.json).
- Each stage's `ledger/` contains the actual sealed HTML pages, source-citation records, index and ledger event chain. Citation records do not count toward the 73 fact pages.
- [All 372 stage/question rows as CSV](results.csv), [run metadata and input pins](run.json), [snapshot/report file checksums](files.sha256.json), and [test output](tests.txt).

The original audit metric `unnecessary_refusals` counts missing returns against all 73 final positives even before their source pages exist. Those early-stage refusals are appropriate under the smaller collection; do not reinterpret that column as a semantic error count. `results.csv` keeps both the final answerable label and the expected outcome for the available stage.

## Reproduce offline

From the repository root, with Python 3.8+ and no application dependencies:

```sh
python -m unittest tests.test_reference_corpus -v
python -m tools.verify_reference_evidence
python -m tools.build_reference_corpus --output /tmp/mplpb-reference-new-run
python -m mplpb_answers ask /tmp/mplpb-reference-new-run/v0.3.0/ledger 'What is noun?' --profile lab --json
```

Use a fresh output directory for each build. The builder refuses to overwrite a prior release. Compare new per-case outcomes and source quotes with the stored evidence; publish a separate report if the engine changes. The verifier checks frozen input hashes and every committed snapshot/report file before replaying all 372 rows. It compares answers and citations, while allowing later diagnostic wording to improve. Recorded engine hashes identify this run; a changed engine is reported rather than disguised as the old version.

The existing PR and ZIP workflows run the reference tests, regenerate fresh stages, and retain the generated releases. They also replay this committed evidence bundle. GitHub status is established by those actual runs, not by prose in this README.
