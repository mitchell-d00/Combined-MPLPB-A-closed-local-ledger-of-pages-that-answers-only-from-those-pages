# Bastet printed-writer source selection

Last reviewed: 2026-11-27.

**A printed writer may select an eligible document. The embedded reporter
determines attribution of its statement.** The selected document must
come from a unique eligible path and hash. The original question retains
the two roles even when they name the same person.

[Released baseline and archive digest](baseline.json) ·
[Development freeze](development/freeze.json) · [Fresh freeze](fresh/freeze.json)

Round 4 F05 is a consumed development lead. It found both passages and
did not reach named-source selection. Its first score remains untouched.
[Original named-source miss](../../cryptid/bunyip/round4/RESULTS.md#fresh-comparison)

Each Bastet draw includes six positive and six contrasting cases.

| Pair | Required boundary |
|---|---|
| 1 | One eligible printed writer suffices. Missing printed writer withholds. |
| 2 | A different embedded reporter remains the reporter. Selecting the writer does not convert the embedded statement into the writer's statement. |
| 3 | A withdrawn second match supplies no support. Two eligible matches require withholding. |
| 4 | A quoted label alone cannot select a document. A real byline remains usable with an unrelated quoted label. |
| 5 | Two conflicting genuine printed declarations cannot be resolved by choosing the first line. |
| 6 | A unique correct document with no matching reporter yields a proof-stage refusal and a selected-source receipt. |

The development questions select a writer in a leading report phrase.
The fresh questions select a source in an ending document clause and use a
different printed label form and new people and objects. The base reader,
contrast purposes and expected propositions are frozen before any test.
No candidate or repair is part of this freeze.

The end-to-end scorer uses the original Cryptid semantic check, then checks
the answer kind, exact body and admitted HTML witness spans, missing fields
and diagnostics. It records document selection and attribution separately.
A proof failure after successful selection requires the verified path and
hash from the native reader. Refusal before interpretation completes
establishes safe withholding only.

## Reproduce

From a clean source copy without materialized study inputs, use
`PYTHONPATH=. python evaluation/egyptian-gods/bastet/prepare.py --custodian
<existing-private-directory>`. Compare new seals to the original.
The helper generates both deterministic packets using the existing Cryptid
case-registry format. Share only the operator inputs with the isolated worker.

Run the existing `tools.cryptid_trial_v5` module on the released scoped
runtime at the commit and digest in the freeze. Keep the output directory
new. Score it with `tools.cryptid_claim_score_v5` and then the
[paired I/O check](io_score.py) with the phase registry, private key,
raw output and prior score. Preserve execution failures with their logs.
Only the development roster runs in the first hosted job. The fresh
roster remains reserved for a committed candidate.
