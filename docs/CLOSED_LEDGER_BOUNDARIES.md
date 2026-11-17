# Closed-ledger diagnostics and operational observations

Last reviewed: 2026-11-17.

`answer-contract-v1` now adds `diagnostic.category` while preserving existing detailed
codes, legacy return kinds and proof requirements. The categories distinguish
unsupported question grammar, absent eligible source, known source conflict,
insufficient evidence, index exhaustion, clarification, source-state change and
reader failure. A model-reported conflict has its own unverified category.
Ambiguous ownership does not certify a body contradiction. Exhaustion describes
the configured execution budget, never exhaustion of the world's historical record.
An exact route without eligible pages is distinguished from a present record
without the requested field. `corpus_answerability` remains `not_established`.

Every result adds `source_assurance`. It requires outside-world confirmation,
including when source support passes. The count of declared evidence roots is
computed from fresh eligible output sources and pinned ancestry. An unavailable
count is null. One root is thin provenance; several roots do not establish
independent testimony. Neither count detects a lie. CLI and both answer renderers
show the same notice. The diagnostic and assurance fields do not alter serving policy or award source
support. The later [arrangement completion rule](SOLO_RESEARCH_WORKFLOW.md#complete-recorded-arrangement-answers)
is independently checked and retains all external-execution exclusions.
External reviewers can use the existing question, claims, exact citations and
source pins as a review packet. No external service is contacted, and no external
truth verdict is manufactured.

`WorkStore.record_external_receipt` extends the existing host-only operation with
explicit STORE → DISPATCH → DELIVERY → READ → ACK → COMPLETION observations.
Each linked transition requires its own artifact, an existing execution receipt,
and a predecessor of the immediately required kind from the same execution.
The stored artifact digest commits the supplied observation. All stages remain
host-declared: a checked ordering is not independently authenticated delivery,
reading, completion or historical truth. Observations cannot support claims or
satisfy task acceptance; existing execution and task-revision checks still apply.
Legacy standalone READ/ACK calls remain compatible, have `transition_checked:false`,
and cannot serve as predecessors for checked transitions. Missing intermediate
receipts stop the chain. Current head fencing applies to every append.

Existing source occurrences, field/time-scoped corrections, candidate-only paths,
and exact-field zero/one/multiple matching remain in place; see
[scoped extensions](SCOPED_EVIDENCE_EXTENSIONS.md). The new tests reuse their
regression controls rather than replacing their verification mechanisms.

## Reproduce a committed source archive

```sh
python -m tools.reproduce_boundaries --revision FULL_COMMIT --output /tmp/mplpb-new-check
```

Use a fresh output directory. The runner creates a tracked source ZIP, verifies
CRC, extracts it, removes inherited PYTHONPATH, and executes focused boundaries,
full unittest discovery, and the public capability suite from that extraction.
It retains failed and timed-out commands and logs, archive hash, exact revision,
environment, CPU and wall time, and process-lifetime maximum child RSS. The latter
is not summed process-tree memory. `--suite boundary` runs only the focused set.
Do not apply current tests retroactively to a revision without those tests.
JavaScript, WebAssembly and Chromium release checks remain separate required
commands in [ZIP-first testing](ZIP_FIRST_RELEASE_TESTING.md).

Human labeling time, source bytes read, coverage and false-bridge accuracy remain
null when unmeasured. Software checks do not establish independent historical
accuracy. This runner does not certify an exact legacy 887-test experiment:
that experiment's revision, fixtures and scoring must first be identified.
The current test count must be reported from actual discovery, not renamed 887.
No Gelhaus or Beyond Guarded Retrieval text was found in the inspected Markdown
or plaintext documentation; this change therefore addresses the supplied critique
without claiming to reproduce or validate those authors' experiments.
