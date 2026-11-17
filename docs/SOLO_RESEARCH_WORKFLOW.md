# Solo research workflow and bounded local checks

Last reviewed: 2026-11-17.

Package role: [how this part fits Combined MPLPB](PACKAGE_GUIDE.md#documentary-research). This guide covers documentary inspection; source assertions, candidate relations and historical truth remain distinct.

These improvements work without other reviewers, paid services or a local model.
They do not manufacture independent historical judgment.

## Inspect each question part

```sh
python -m mplpb_answers reconstruct CORPUS 'Who appointed Mira Vale, and who appointed Lena Grey?' --format text
```

The new text view shows original question parts, their existing check statuses,
numbered evidence, exact quotations, source IDs/hashes, canonical offsets,
alternatives, missing evidence and candidate-graph count. It is a snapshot:
rerun the command to recheck current eligibility. JSON remains the default and
retains the full reversible map. Existing browser documentary answers now show
question parts and canonical offsets as well.

`documentary_support.obligations` adds `evidence_proof_sha256`, zero-based
`evidence_claim_indices` and `undisplayed_evidence_count`. These fields link
existing checker output to displayed claims; they do not establish additional
support or fill missing obligations. Hidden evidence never receives a displayed
claim index. Plans, reported instructions, ambiguous identities, conditions,
conflicts and missing links retain their existing verification status.

## Check an actual locally stored artifact

A native host can place an artifact beneath its existing private work directory's
`artifacts/` folder and call the existing host operation:

```python
receipt = store.record_external_receipt(
    host, receipt=execution_receipt_id, kind='STORE', artifact='Execution output',
    local_artifact='result.bin', expected_artifact_sha256=raw_sha256,
    expected_head=store.head(host)['hash'])
current = store.verify_storage_receipt(host, receipt_id=receipt['id'])
```

The host supplies the expected raw SHA-256. Software reads the actual regular
file, hashes at most8MiB, and rejects mismatches, traversal, symlinks, special files
and detected in-place changes. Each path component is opened relative to a
no-follow directory descriptor. These checks require native POSIX support;
unsupported runtimes fail closed. No arbitrary external path or network is read.
The observation records only byte pins, size and relative path, not artifact
contents. A read-only recheck returns intact, changed or unavailable and appends
no event. It remains host-only through the existing API.

This is a local byte check, not independent authentication of the host, proof of
persistent storage, external delivery, human reading, task completion or historical
truth. The file can change immediately after inspection; rerun the recheck when
needed. Existing predecessor checks, task acceptance and false source-support/
external-world-truth flags remain intact. Legacy host declarations still work.

## Reduce parsing without caching authority

`mplpb_combined.record` caches only immutable parse results keyed by the complete
source text, including unhashed status and the declared hash. At most8 inputs of
2,000,000 characters each enter the LRU; larger pages bypass it. Each call returns
fresh mutable Record fields/problems and preserves path-dependent record kind.
Every file is still reread; same-size, same-mtime edits cannot evade content keys.
Current source eligibility, restrictions, correction state and final rechecks
remain uncached. Input/derived strings consume bounded extra memory; actual costs
must be measured on the relevant corpus rather than presumed faster.

Run focused checks with:

```sh
python -m unittest tests.test_solo_research tests.test_record tests.test_answer_boundaries tests.test_documentary_assertions -q
```

Use the existing [original-record protocol](UNPREPARED_ORIGINAL_CHALLENGE.md) and
[ZIP-first release checks](ZIP_FIRST_RELEASE_TESTING.md) for broader measurements.
Historical semantic precision/recall and human-review times stay null unless
actually assessed. Solo use does not require recruiting reviewers; the software
simply makes no claim of independent validation.

## Complete recorded-arrangement answers

The independent documentary kernel can close a finite compound question asking
who arranged for a named recipient to receive a named writer's item and which
dated letter records it. It re-derives the instruction from original wording,
binds possessive `my` to the printed writer and `you` to the printed recipient,
checks the exact requested item, and retains the heading date's actual role.
Ambiguous local surnames, missing ownership/date, a different item, extra delivery
questions, negated/planned/quoted instructions and insufficient budgets cannot
close the question.

Three source anchors are required: the printed heading, the complete instruction,
and the complete local letter (at most4,000 canonical characters). Local cancellation/
withdrawal wording stops completion. This is complete only as a source-reported
arrangement request and printed date; it does not establish actual arrangement,
instruction receipt/acceptance, execution, dispatch or delivery. Those flags remain
false. No event identities are merged and no corpus-wide absence of later
correction is claimed. The historical source remains eligible only under existing
gate and final source-state checks.

The record cache uses standard-library `functools`; the core's explicit permitted
standard-library import list includes it. Network/model imports remain prohibited.

The [dated milestone report](../evaluation/solo-milestone/2026-11-17/RESULTS.md)
separates the measured arrangement completion and blinded AI assessment from
cache speed, evidence inspection and local storage support work.
