# Bastet document selection and reporter attribution

Recorded 2026-11-27. [PR #117](https://github.com/mitchell-d00/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages/pull/117)

[Released baseline](baseline.json) · [First baseline results](RESULTS.md) ·
[Candidate pin and source ZIP](candidate-dispatch.json) ·
[Checksums](IMPLEMENTATION-SHA256SUMS)

## First results on the frozen packets

| Contract | Released development baseline | Candidate development | First fresh candidate |
|---|---:|---:|---:|
| Completed executions | 12/12 | 12/12 | 12/12 |
| Distinct question strings | 4 | 4 | 4 |
| Verified document selections | 0/8 | 8/8 | 8/8 |
| Verified reporter attributions and complete answers | 0/6 | 6/6 | 6/6 |
| Correct selections with the requested attribution withheld | 0/2 | 2/2 | 2/2 |
| Claim-free controls | 6/6 | 6/6 | 6/6 |
| Exact abstention contracts | 5/6 | 6/6 | 6/6 |
| Checked partial answers | 0 | 0 | 0 |
| Unsupported claims | 0 | 0 | 0 |
| Execution failures | 0 | 0 | 0 |

The fresh column is the first run on the frozen fresh packet. It has no
released-reader arm. Both draws use synthetic records with same-operator
preparation and scoring. The isolated worker received the source inputs and
questions, with the key and scorer held outside its sandbox.

The released development reader returned a claim-free retrieval conflict on
`CRYPT-BASTET-D-0006`. The requirement was an exact ambiguity abstention.
Candidate cases D-0006 and F-0006 meet it with
`named_report_source_unresolved` and `multiple_eligible_documents`.
The original baseline score, raw result and key retain their original values.

## Rule

For the two tested named-document request forms, resolve a printed writer
from an exact, unqualified leading declaration in the original. Check the
canonical body and the original HTML layout. A quoted label, a conflicting
declaration, or an ineligible record cannot establish a unique selection.
Select only when exactly one eligible original has the required declaration.
Return an ambiguity abstention if two or more eligible originals qualify.

Run reporter proof independently on that selected original. A verified
selection may accompany a reporter refusal. A complete answer must also
verify the requested reporter, reported text and eligible citation with the
existing native proof route. The writer identity alone supplies no reporter
proof.

## Preservation and first failures

- All 41 focused tests passed.
- [Public contracts](implementation-evidence/public-832-comparison.json)
  matched 832/832 with zero changed contracts and zero execution failures.
  The [first attempt](implementation-evidence/public-832-first-failure-receipt.json)
  stopped at a frozen harness checksum because new tests had been added to
  a pinned test file. Restoring that file and placing the new tests in
  their own file allowed the retry to score. The pinned native bytes, raw
  first fresh answers and expectations stayed identical.
- [BB](implementation-evidence/bb-receipt.json) matched 900 answers,
  900 exact eligible citations and 200 withholds.
- [Retained 96](implementation-evidence/retained-96-receipt.json) reproduced
  87 exact matches and the nine already authorized diagnostic-only
  fingerprints. The original exact failure stands. The compatibility
  rule and its scope stayed unchanged.
- The [run receipt](implementation-evidence/fresh-run-receipt.json) links
  the first fresh run, the preservation retry and the verified archive
  digests. The retained compressed preservation archive keeps every raw
  member byte, with a [member checksum list](implementation-evidence/public-832-archive-members.json).
  The baseline archive, input registries and frozen seals remain under
  their original paths.

## Reproduce and delimit

Use the [original runner and scoring instructions](README.md#reproduce)
with the candidate pin in `candidate-dispatch.json`. Recreate the scoped
source with `git archive --format=zip -0 <candidate> mplpb_answers mplpb_combined mplpb_work`.
The [study workflow](../../../.github/workflows/egyptian-bastet-selection.yml)
records the isolation, resource bounds and preservation commands. Fresh
replays now reproduce an exposed first score.

Independent historical accuracy, outside scoring, independent semantic
adjudication, native OOCC and human evaluation remain NOT_RUN. The original
17 private checks remain incomplete, the 100 held transfers remain
NOT_RUN, and the historical publication incident remains open.
