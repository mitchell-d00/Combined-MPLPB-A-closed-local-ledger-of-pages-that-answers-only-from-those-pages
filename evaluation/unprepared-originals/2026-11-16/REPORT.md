# Unprepared original-record reconstruction study — 2026-11-16

Engineering outcome: **partial success**. Source preservation and reversible evidence mapping work in the executed cases. Useful historical reconstruction accuracy remains **UNASSESSED**. Independent human review and independently authored unseen questions are **NOT RUN**. No favorable scientific conclusion is presumed.

## Exact implementations and frozen conditions

- Unchanged baseline: `614b18cc34f5270d4cb7dfbbf8239391a9f83b31`.
- Initial candidate-context implementation: `057863715ee0a24849430bd96b516f6fc55a4783`.
- Conversion repair: `81ec51367010582d72223f8c02fc4823ec8f7eb3` (the run receipt uses its unambiguous abbreviation `81ec513`).
- [freeze-v2.json](freeze-v2.json) pins the same five authentic source editions, 14 developer-authored questions, incomplete draft references and rules. Every primary run uses the same checkpoint/RSS harness and 180-second per-question budget. Native module hashes are retained in each output and receipt.
- [BASELINE.md](BASELINE.md) and [pre-behavior-receipt.json](pre-behavior-receipt.json) predate behavior changes. No originals, questions, scoring criteria or prior results were rewritten.
- The original allocation-tracing pilot and timeout remain in `baseline-profiled-pilot/`; [measurement-revision.json](measurement-revision.json) documents the measurement-only revision. Pilot timing is not compared as software efficiency.

## Corpus and precise failure stages

[The manifest](corpus-manifest.json) preserves exact acquired bytes, original URLs, hashes, retrieval dates, rights/access basis and provenance records. Sources are the published Darwin correspondence edition, Jefferson draft, Declaration transcript, Sumter telegram page and Apollo 13 mission-report OCR. These are published transcriptions/editions and archival presentations, not authenticated autograph inspection. No private or restricted archive was acquired. Retrieval failures remain in [acquisition-failures.json](acquisition-failures.json).

Five originals reproducibly import into seven native pages without answer-bearing relationship fields. All 23 draft spans survive the existing normalized body projection; original bytes remain unchanged. [The stage audit](conversion-stage-audit-v2.json) records every question and every wrapper field. A preserved [count correction](audit-count-correction.json) corrects an initial prose tally from six to five retrieved draft spans without changing per-case outputs.

The native index contains 1,529 passages. Six draft spans cross individual passage boundaries. The baseline expert skips large pages at its character budget and recognizes declared headers rather than ordinary prose. Strict answering often stops at `interpretation_unsupported` before answer retrieval; three questions return `retrieval_ambiguous`. Actual separate BM25 retrieval locates 5/23 complete draft spans. These are indexing/context, retrieval and interpretation limits, not evidence of failed import. Negative controls require semantic assessment of refusal appropriateness.

## Authentic-source executions

| Execution | Completed | Native supported | Draft spans retrieved | Exact quote checks | CPU seconds | Worker wall seconds | Peak RSS MiB | Logical HTML read GB |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| baseline | 14/14 | 0/14 | 0/23 | 0/0 | 758.99 | 759.82 | 37.43 | 9.172 |
| updated | 14/14 | 0/14 | 5/23 | 168/168 | 901.68 | 902.52 | 40.65 | 9.373 |
| conversion-repair | 14/14 | 0/14 | 10/23 | 96/96 | 869.15 | 870.11 | 40.60 | 9.413 |
| bm25 | 14/14 | 0/14 | 5/23 | 168/168 | 17.25 | 17.28 | 32.12 | 0.040 |
| keyword | 14/14 | 0/14 | 0/23 | 0/0 | 11.73 | 11.75 | 30.38 | 0.040 |

The source-search comparators return passages, not answers, so their zero native-supported count is inapplicable as answer accuracy. Draft-span coverage is retrieval against incomplete developer references, not independently validated recall of events or relationships. Exact quote checks establish canonical citation fidelity, not interpretation correctness. Search remains incomplete.

Every correct/incorrect classification, omitted semantic relationship, false causal relationship, correction-detection judgment and refusal-appropriateness judgment remains unassessed until review. [research-summary.json](research-summary.json) links every answer, candidate, conflict, refusal, missed draft span and cost for every question; no unfavorable case is removed. Native supported coverage remains zero, rather than being forced upward.

## Repair and round-trip evidence

Existing gated passage retrieval now recovers bounded neighboring canonical source text across layout boundaries. The native investigation path derives separate statement, entity, date, event, correction, disagreement and related-context candidates with exact quotations, coordinates, source hashes, operation, ambiguity and fidelity/semantic statuses. Antecedent search uses shared lexical evidence, excludes overlapping self-context, leaves predecessor and date roles unresolved and never applies supersession or creates a verified causal edge. No optional model was used.

[The mapping audit](conversion-repair-mapping-audit.json) checked **865/865** mapping objects, including **126** unique canonical/raw supporting passages. A representative mapping per question was reconstructed through a fresh eligibility/state check; all objects received separate automated coordinate/quote/hash checks. These objects are not 865 verified historical facts.

[All 23 draft reference passages](roundtrip-draft-reference-audit.json) also round-tripped to exact original byte slices. This is a separate post-run fidelity audit using draft references, not question-time reconstruction or independent historical scoring. Raw excerpts retain markup/layout separately from normalized canonical quotes. Original/cached source changes, withdrawals, policy changes, corrupted hashes and forged anchors fail closed in targeted tests.

## Synthetic controls — separate corpus

The 24 prepared randomized fictional rare-topic controls passed **24/24** for baseline, initial update and repair. They exercise finite-contract color, conflicts and absent causality. Initial keys were withheld from worker execution payloads and released after the initial paired runs. Repair runs are public-key regression controls, not a new blinded trial. The developer authored the generator, and these are not independently blinded human evaluations. [Synthetic outputs, scoring and seed commitment/release](synthetic-controls/) remain separate and are never pooled with authentic-source scores.

## Regression and independent review

- Baseline targeted authority regressions: **137 passed**; [receipt](baseline-regressions.json) and [log](baseline-regressions.log).
- Initial candidate-context full suite: **988 passed**; [receipt](initial-full-regression.json) and [log](initial-full-regression.log).
- Repaired full suite and extracted-source checks: see [repair-regressions.json](repair-regressions.json).
- Public prepared evidence suite: **52/52**; [retained output](public-52-after-repair.json).
- Fresh-process integration imports the authentic Sumter page into a native collection, reopens it, asks a question, inspects candidates and reconstructs original byte excerpts; negative controls invalidate changed/corrupted sources. Existing tests are unchanged.
- [Initial review packets](review-packets/) and [repair review packets](conversion-repair-review-packets/) include full source-linked outputs, draft reference status and blank submissions. Two genuine human reviewers and explicit adjudication are required. No reviewers, signatures, human durations or historical conclusions have been invented.

## Costs, limitations and reproduction

Worker CPU, wall time, peak Linux RSS, repeated logical source HTML reads and distinct original/native documents are actually measured. Parent launch time and import costs are in run receipts. Logical reads include repeated safety checks and are not physical disk I/O. Concurrent local testing can affect wall times. No efficiency improvement is claimed. Benchmark model calls/API charges are zero; compute price, acquisition/network charges, engineering model costs and human labeling/correction/review/adjudication times are unknown or not measured. Zero API charges do not mean zero computation.

The draft-reference and mapping audits record their separate CPU/wall/RSS costs. Historical event/relationship/correction precision and recall, false-positive rates and semantic completeness remain null because defensible independently adjudicated references are unavailable. Wider semantic understanding, arbitrary event identity, chronology and partial correction reconstruction have not been demonstrated by lexical mappings. Source OCR/layout limitations, incomplete retrieval, unresolved ambiguity and reading-cost amplification remain material constraints.

Exact commands are in [the operational evaluation guide](../../../docs/UNPREPARED_ORIGINAL_CHALLENGE.md) and [mapping repair guide](../../../docs/SOURCE_MAPPING_REPAIR.md). To rerun a primary arm, use `python -m tools.unprepared_challenge run evaluation/unprepared-originals/2026-11-16 --implementation CHECKOUT --mode baseline` (or `updated`) `--commit EXACT_SHA --seal freeze-v2.json --output NEW_DIRECTORY`. Use the baseline commit checkout for `baseline`; use the repair commit checkout for repaired `updated`. Existing result directories refuse overwrite. The latest harness/importer must match freeze-v2 hashes. Source and question access are identical across paired runs. Ordinary BM25 and conjunctive keyword search were executed; no general-purpose AI or complete human source-governed workflow was executed or claimed.
