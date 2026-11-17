# Scoped header/occurrence correction — 2026-11-17

Baseline: `ccbb5804eb47f78c2338d57c142ad087b47be710`.
Status: implementation and focused checks complete; frozen-archive checks pending.
This is a developer reproduction of a supplied probe and targeted software fix,
not an independently validated historical-reconstruction benchmark.

## Reproduction and exact cause

Two regression tests were added **before changing sorter.py**. Running:

```bash
python -m unittest tests.test_sorter.SorterTests.test_fenced_example_is_observation_not_primary_identity_member tests.test_sorter.SorterTests.test_embedded_header_does_not_partition_real_record_occurrences -v
```

exited1 with2 failures: the cluster contained `03-example.md`, and a concatenated
file had3 source occurrences rather than2. See `before-regressions.log`. The existing
pre-edit sorter suite passed27 tests in0.891s.

At the baseline revision:

- `HEADER` (line29) is a physical-line recognizer without container context. It matches bare header lines inside fences.
- `_fence_ranges` and `_scope` (lines171-188) detect formatting/quotation, but the result only annotates statements later in extraction.
- `extract` (lines220-228) collects **all** header matches and selects Message-ID/Document-ID/Record-ID markers before scope is applied. Embedded headers therefore partition occurrences.
- Header emission (lines270-277) produces ordinary `header_identifier` nodes with paragraph scope warnings, but no distinct declaration role.
- `compare` (lines331-354) indexes every header_identifier and groups occurrences by its value/namespace without consulting the warning.
- The same undifferentiated index also supplies reference targets. Embedded Status/date headers can contaminate outer document annotations.

The baseline evidence trace in `minimal-before.json` identifies the exact cluster
edge, member occurrence nodes and header evidence nodes, including source IDs,
SHA-256 hashes, offsets and excerpts. The example header already carried a quoted
scope warning; the failure was that declaration consumers ignored that distinction.
The full supplied native probe produced the same contamination as its original
transcribed-core/stub experiment. Its original files and script remain unchanged.
The supplied ZIP SHA-256 is
`ef1c0e7064d88a88617ee4a639cd1fa3d8c8fa57990ece22c13f55f543d8f3b1`.

## Correction

The correction is in extraction/occurrence classification, not only edge filtering:

1. Derive coalesced structural embedded ranges before selecting occurrence markers. Fence closing now respects marker family, length and trailing-text rules. Explicit nested forward frames, BOM, CRLF and blockquote prefixes retain their positions.
2. Assign each header a `header_context`, `header_role` and `primary_identity_eligible`. Embedded headers remain original-span observations; top-level declaration candidates remain eligible even when body prose in the same paragraph is quoted.
3. Partition only on primary identifier-header candidates. Mark occurrences as `declared_record_candidate` or `textual_appearance_only`. Restrict outer status/date roles to primary headers.
4. Reuse the primary-header index for candidate cluster membership and reference resolution. Retain embedded lexical matches as separately labeled `embedded_identifier_review` annotations. Embedded-only, missing and ambiguous targets never become resolved primary links.

No external dependency, source rewrite, new answer engine or authority rule was
introduced. Native authorization, serving, correction and retirement code is unchanged.
`source_occurrence` still represents a source appearance: an example file remains
a node, with textual-only identity role, rather than being erased or asserted to
be a genuine communication. Existing implementation-hash replay fails closed on
old classifications; retained prior assessments are not silently overwritten.

## Before and after

| Fixture | Before | After |
|---|---|---|
| Requested3-file MAIL-001 cluster |3 members, including the fenced example |2 primary members; the example is retained as an embedded observation |
| Supplied8-file MAIL-001 cluster |4 members, including07-quoted-header.md |3 primary members; changed-body appearance retained |
| Real + fenced sample + real in one file |3 occurrence partitions |2 real declaration partitions, with embedded evidence attached to its containing occurrence |
| Supplied source/node observations |8 sources;159 nodes;253 raw edges |8 sources;159 nodes;253 raw edges |
| Supplied compare edges |312 |313, including a separate embedded-header review annotation |

The extra edge is not a success metric. The targeted improvement is removal of a
wrong primary role while preserving legitimate members, reference ambiguity,
changed-body warnings and all original evidence. No historical identity, independent
communication event or answer support is established in either version.

## Verification observed so far

```bash
python -m unittest tests.test_sorter -q
python -m unittest tests.test_sorter tests.test_answer_boundaries tests.test_scoped_extensions tests.test_source_mapping tests.test_supersession_policy -q
```

The sorter command exited0:42 tests passed in1.005s. The final focused/native
command exited0:99 tests passed in1.989s. Logs are retained as `sorter.log` and
`focused.log`. Fresh Python invocations performed these checks; they do not depend
on the preceding AI session's private state.

Coverage includes the12 requested classes: legitimate repeated IDs; fenced examples;
quoted/forwarded copies; shared subject/different IDs; changed bodies; identical
bodies/different IDs; quoted correction; actual unique correction; missing/ambiguous
references; CRLF/BOM/Unicode spans; backticks/tildes; concatenated real records.
Additional controls cover nested/unclosed forwards and fences, marker-like non-closers,
embedded date/status pollution, legitimate headers with quoted body prose,
forged eligibility metadata, bounded comparison and deterministic replay.

All covered scenarios preserve source byte/character round trips, identical modes'
sources/nodes/assessments, raw-edge prefix equality and false support/truth flags.
The existing reader-withholding, corrupted-source, export/retirement and native
boundary tests remain in the passing suites.

The unchanged supplied `reproduce_upstream.py` exits0 before the fix. Afterward it
exits1 at its last assertion because it expressly requires
`quoted_header_in_unverified_cluster=true`; the corrected value is false. Every
other reported invariant remains true. Both logs are retained. That expected
failure is not relabeled as a passing script or hidden by editing the supplied probe.

## Remaining ambiguity and continuity

Finite structural cues do not resolve arbitrary unmarked copied headers, misleading
example labels, broken/OCR quotation syntax or genuine historical identity. Explicit
unclosed frames conservatively retain review scope; embedded historical communications
remain inspectable and lexically associated but are not primary cluster members.
This does not establish general candidate precision/recall or historical accuracy.

`checkpoint.json` preserves source/probe/fixture hashes, the task status, exact
commands, observed exit codes, expected failure of the original bug-presence probe,
remaining ambiguity and non-negotiable verification rules. A replacement worker can
read AGENTS.md, HANDOFF.md, this report and the checkpoint, then rerun verification.
No model identity, private conversation memory or previous model runtime is needed
for that deterministic process. A fresh AI-instance resumption experiment and the
minimum model context needed are **NOT RUN / unknown**, not inferred from software
replay. Work-state continuity remains separate from historical truth and source authority.
