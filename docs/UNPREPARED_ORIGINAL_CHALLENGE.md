# Unprepared original-record reconstruction challenge

Last reviewed: 2026-11-16.

This challenge measures rather than presumes historical reconstruction. The
[dated baseline inventory](../evaluation/unprepared-originals/2026-11-16/BASELINE.md)
pins default-branch commit `614b18cc34f5270d4cb7dfbbf8239391a9f83b31` before behavior
changes. The versioned results directory preserves originals, rights/provenance,
questions, incomplete source-linked reference drafts, frozen rules, output,
failures, measurements and blank human review packets.

The authentic arm uses five independently published source editions/transcriptions:
Darwin correspondence, Jefferson's rough draft, the final Declaration, an archival
Sumter telegram presentation, and NASA's original Apollo 13 report OCR. This is a
purposive development corpus. Modern editorial framing, OCR errors and digital
edition limitations are retained. It is not a representative archive sample or a
collection of autograph manuscript images. Originals are byte-pinned; no Event-ID,
Related, Corrects or gold answers are added to their source bodies.

The separate synthetic arm uses 24 randomized finite-contract controls across 12
fictional rare-topic domains. Runtime workers receive source facts and questions
but not expected outcomes or private seed files. The developer authored the
generator and sees the source facts. This is execution-payload separation, not
independently blinded human evaluation. Synthetic outcomes never enter authentic
historical metrics or reference sets.

Independent human question authorship, semantic review and adjudication are
**NOT RUN**. Developer questions are explicitly not independently unseen. Two
real separate reviewers can supply judgments using the packets; this software
cannot authenticate people or certify independence from submitted IDs.

## Frozen conditions and measurement versions

`freeze.json` records original source/question/protocol/reference digests, baseline
native modules, acquisition/importer and evaluator code. `freeze-v2.json` binds the
same inputs/rules to a versioned measurement correction. The profiled pilot is
preserved: its first authentic question exceeded 180 seconds; allocation tracing
added measurement overhead and completed native phases were not checkpointed.
No semantic conclusion follows from that timeout. Primary v2 runs disable Python
allocation tracing, retain fresh-worker OS peak RSS and checkpoint completed
phases before a possible later timeout. Corpus, questions, scoring rules, native
baseline and the 180-second wall limit remain unchanged. The pilot's source and
outputs remain in `measurement-pilot-v1` and `baseline-profiled-pilot`.

Each real worker uses the existing fail-closed Linux bubblewrap command, read-only
native code and input ledger, network isolation, cleared environment, resource
limits and private scratch. Audit mappings, draft answers and private seeds remain
outside its mounts. The host/custodian/kernel remain trusted. This is not a
cryptographic attestation that the human operator has never seen the answers.

Costs include native engine CPU/wall time, whole-worker CPU, parent wall including
launch, fresh-worker peak process RSS, import cost, repeated source HTML bytes/read
calls, native records and distinct original documents examined. RSS includes
imports. Source read counts are instrumented logical UTF-8 HTML reads, not physical
disk I/O. Python allocation peaks are unknown in v2. Host load/concurrent runs and
cache effects limit efficiency comparisons. No model calls are made; API charge
zero does not mean computation is free. Monetary compute prices and human effort
stay unknown unless actually supplied.

## Bounded implementation change

The baseline expert understands explicit documentary headers. An opt-in
`investigate(..., prose_candidates=True)` now exposes ordinary eligible prose
contexts using the existing passage index and source-state rechecks. It labels
raw date mentions with unresolved roles and correction/correspondence words as
inspection cues. It does not infer event identities, normalize event dates,
assert causal edges, apply corrections or modify source authority. Every context
has its exact source hash, offsets, quotation and false answer/truth flags.

The unchanged normal expert path remains the default. Historical interpretation
still requires review. More retrieved quotations are an evidence-discovery result,
not automatically improved historical reconstruction precision or recall.

## Reproduction

Run commands from the repository root with Linux, bubblewrap and namespace
permission available. Clone/check out the pinned baseline into a separate path;
do not run a supposed baseline from the modified working directory.

```sh
STUDY=evaluation/unprepared-originals/2026-11-16
python -m tools.unprepared_sources verify "$STUDY"
python -m tools.unprepared_sources acquire "$STUDY" --output /tmp/refetched-originals
python -m tools.unprepared_challenge run "$STUDY" --implementation /path/to/baseline \
  --mode baseline --commit 614b18cc34f5270d4cb7dfbbf8239391a9f83b31 \
  --seal freeze-v2.json --output /tmp/new-baseline-run
python -m tools.unprepared_challenge run "$STUDY" --implementation /path/to/modified \
  --mode updated --commit MODIFIED_COMMIT --seal freeze-v2.json --output /tmp/new-updated-run
python -m tools.unprepared_challenge run "$STUDY" --implementation /path/to/baseline \
  --mode bm25 --commit 614b18cc34f5270d4cb7dfbbf8239391a9f83b31 \
  --seal freeze-v2.json --output /tmp/new-bm25-run
python -m tools.unprepared_challenge run "$STUDY" --implementation /path/to/baseline \
  --mode keyword --commit 614b18cc34f5270d4cb7dfbbf8239391a9f83b31 \
  --seal freeze-v2.json --output /tmp/new-keyword-run
python -m tools.unprepared_challenge compare "$STUDY" /tmp/new-baseline-run \
  /tmp/new-updated-run /tmp/new-bm25-run /tmp/new-keyword-run --output /tmp/new-comparison.json
python -m tools.unprepared_challenge packets "$STUDY" /tmp/new-baseline-run \
  /tmp/new-updated-run --output /tmp/new-review-packets
```

Reacquisition fails on changed publisher bytes; preserve the frozen bytes instead
of silently updating them. Outputs refuse overwrite. Comparisons reject different
corpora, rules, questions, import receipts or case coverage. Old harness snapshots
must be restored into an isolated checkout to replay their frozen measurement
version; never overwrite the published old results with a new-code replay.

For future genuinely unseen questions:

```sh
python -m tools.unprepared_sources prepare-study "$STUDY" --output /tmp/external-study
python -m tools.historical_study seal /tmp/external-study /private/independent-questions.json
python -m tools.historical_study run /tmp/external-study --sandboxed
```

The preparation emits an empty template. An independently recruited question
author must supply actual questions; no software-generated set is called unseen.
Keep keys and participant information outside public Git history until authorized
release. The existing salted seal and independent submission protocol is reused.

## Assessment and interpretation

Machine checks validate frozen inputs, source-quote offsets/pins and evidence-span
coverage against the incomplete developer draft. The latter is retrieval coverage,
not semantic event or relationship recall. Published summaries retain per-case
refusals, conflicts, candidates, errors, costs and unassessed semantic fields.

Reviewers judge event/chronology/citation/correction/relationship accuracy, false
causality, missing evidence, refusal/uncertainty and completeness. They provide
source citations, delimited reference scope, TP/FP/FN, explicit outcomes and any
actual effort measurements. Success, partial success, failure and unassessed are
all legitimate outcomes. Contradictory success labels are rejected. Incomplete
reference sets do not yield complete recall; undefined precision stays null.
Disagreements require bound, explicit human adjudication rather than averaging.
Reviewer IDs/attestations and self-reported times remain unauthenticated.

```sh
python -m tools.unprepared_challenge score /tmp/new-review-packets \
  /private/reviewer-a.json /private/reviewer-b.json --output /tmp/new-review-score.json
# On disagreement, supply --adjudication /private/adjudication.json.
```

The keyword/BM25 arms are actual gated retrieval executions, not full human source-
governed workflows. General AI comparison and an independent human conventional
workflow are NOT RUN. No private third-party implementation is represented as
evaluated. See the dated report for actual results and remaining uncertainty.


## Retained execution report

See the [complete dated report](../evaluation/unprepared-originals/2026-11-16/REPORT.md), [conversion diagnosis](SOURCE_MAPPING_REPAIR.md), and `tools/audit_original_mappings.py`. The report includes all primary outputs, preserved failed measurement pilots, costs, missing draft evidence and blank independent-review packets. Run the same frozen harness for baseline and update; native hash pins in each receipt identify the measured implementation. Source fidelity and historical semantic correctness are separate results.
