# Source conversion and reversible prose mapping

Last reviewed: 2026-11-17.

Package role: [how this part fits Combined MPLPB](PACKAGE_GUIDE.md#documentary-research). This guide covers documentary inspection; source assertions, candidate relations and historical truth remain distinct.

The frozen experiment is retained in [the dated results directory](../evaluation/unprepared-originals/2026-11-16). Its baseline is `614b18cc34f5270d4cb7dfbbf8239391a9f83b31`; the first candidate-context implementation is `057863715ee0a24849430bd96b516f6fc55a4783`. Neither is rewritten by this repair. Independent historical judgments remain **NOT RUN**.

## Diagnosed stages

The [stage audit](../evaluation/unprepared-originals/2026-11-16/conversion-stage-audit-v2.json) traces every historical question. Five immutable originals import reproducibly into seven valid native pages. All 23 unreviewed draft reference spans survive the existing canonical text projection. The projection intentionally normalizes whitespace and omits HTML headings; original bytes remain separately preserved. This is not byte-identical HTML conversion.

The actual gated passage index contains 1,529 passages. Six draft reference spans cross individual passage boundaries. Separate BM25 execution retrieves 5/23 complete draft spans. The original expert path skips large pages at its character budget and recognizes declared documentary headers rather than arbitrary historical prose. The answer pipeline often returns `interpretation_unsupported` with answer retrieval `not_run`; three questions return `retrieval_ambiguous`. These are different constraints. A zero supported-answer count does not demonstrate failed acquisition or import, and a negative control is not automatically a semantic failure.

## Implemented repair

The existing opt-in `investigate(..., prose_candidates=True)` path now expands retrieved passages into bounded, exact neighboring canonical contexts, within the existing 12,000-character budget. Expansion crosses layout boundaries, merges contained selections, preserves qualifications, and explicitly leaves search incomplete. Existing source eligibility, source hashes, permissions, origin/depth checks, supersession, specialist receipts and final source-state rechecks still govern.

`mplpb_work/source_mapping.py` derives statement appearances, possible proper-name appearances, date mentions with unresolved roles, event-verb cues, reconsideration/correction cues, disagreement language and potential related contexts. An antecedent lookup searches other non-overlapping eligible passages for shared query vocabulary. The result remains unresolved: it does not assign chronology, resolve a predecessor, apply a correction, establish event identity or infer causality. These deterministic lexical cues are limited candidate analysis, not unrestricted semantic understanding.

Every mapping carries source identity, native revision hash, exact canonical coordinates, full evidence quote, operation, qualification cues, unresolved issues, conflict-search limits and distinct fidelity/semantic statuses. Native-to-original import receipts link the native revision to acquired original identity, URL and byte hash. `reconstruct` reloads current eligibility, policy, source state and exact source text; stale, withdrawn, corrupted or forged anchors are rejected. A mapping digest detects edits, but is not authentication and cannot verify an interpretation.

`tools/source_roundtrip.py` maps canonical coordinates back to exact original character and byte slices, preserving raw layout and HTML markup. It returns the raw excerpt separately from the normalized canonical quote. A successful round trip proves source fidelity; it does not verify the historical relationship. Changed original bytes fail the frozen manifest gate. No historical originals receive added Event-ID, Related, Corrects or answer fields.

## Reproduce

From a checkout containing the frozen results:

```sh
python -m tools.unprepared_sources verify evaluation/unprepared-originals/2026-11-16
python -m tools.unprepared_sources import evaluation/unprepared-originals/2026-11-16 --output /tmp/my-original-ledger
python -m tools.reconstruct_original map --ledger /tmp/my-original-ledger --question "Sumter telegram surrender April Anderson" --output /tmp/my-map.json
```

Choose an actual `mapping_id` from `candidate_analysis.information_map.mappings` and reconstruct in a fresh process:

```sh
python -m tools.reconstruct_original reconstruct --ledger /tmp/my-original-ledger --report /tmp/my-map.json --mapping-id MAPPING_ID --corpus evaluation/unprepared-originals/2026-11-16 --import-receipt /tmp/my-original-ledger/import-receipt.json --output /tmp/my-original-passage.json
python -m unittest tests.test_source_mapping tests.test_unprepared_prose tests.test_unprepared_challenge -q
```

Output files and imported collections must be new paths. Native answers use the existing answer contract; candidate maps remain `answer_supported=false` and `content_truth_verified=false`, even when their quotes match exactly. The command-line inspection does not execute an operator or contact a model.

The same frozen v2 harness evaluates each implementation, including the repair, with the unchanged 180-second per-question budget. Use the [evaluation guide](UNPREPARED_ORIGINAL_CHALLENGE.md) and measured revisions in run receipts. The separate round-trip audit records its own processing costs. Never present its post-run use of draft references as question-time discovery.


## Executed comparison

The [dated research report](../evaluation/unprepared-originals/2026-11-16/REPORT.md) retains all prior runs and complete costs. All 14 repaired historical cases completed: draft-span coverage is 10/23, compared with 0/23 in the original expert report and 5/23 in the first candidate path and actual BM25 comparator. Native supported coverage remains 0/14. All 96 returned citations match the pinned projection; 865 candidate mappings and 126 unique raw supporting passages pass the post-run fidelity audit. These are mechanical fidelity/retrieval measures, not semantic historical accuracy. The full repaired suite passed 994 tests; prepared public evidence passed 52/52 and separate randomized controls passed 24/24. Independent historical review is NOT RUN.
