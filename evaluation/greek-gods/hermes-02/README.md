# Hermes-02 first namespace-bound receipt results

Last reviewed: 2026-11-28.

[Al note 0005](../../../handoff/al-notes/0005-hermes-namespace-binding.md)
was read at `4ec98541f6961a320af4453f6d0425aa80575000`. The
[contract](CONTRACT.md), [freeze](freeze.json), and [candidate pin](candidate.json)
record the baseline, seals and selection before fresh. The bridge comparison,
reader, controller and reservation implementation retain their original bytes.
The Node lab seam substitutes only the compared operand in memory. Both
fixtures run the actual reader and existing fixed local Git writer.

| Draw | Exact phases | Writer attempts | Intended writes | Durable completions |
|---|---:|---:|---:|---:|
| Development | 9/9 | 2 | 2 | 2 |
| First fresh | 9/9 | 2 | 2 | 2 |

Both targets had identical Git object IDs and ref names and shared one stable
source and proof per draw. The foreign and mutated binding differed only in
namespace. Both were rejected before controller admission. A fresh local
binding then succeeded in the receiving repository. A locally valid binding
with absent authority was denied at admission. Revocation allowed initial
admission and blocked final admission. Each restart duplicate reached the
controller's initial evaluation and was blocked by its own store before Git.
The seven blocked phases per draw made zero writer attempts and left both
refs, markers and reservation records unchanged. No unexpected effect occurred.

Fresh reverses the donor and receiving repository and changes wording, names,
layout and contrast order. The causal structures repeat. One operator authored
and scored these synthetic cases. The keys remained separate from worker inputs
and were verified against their seals in a private workspace archive. An
off-workspace backup remains unverified.

The affected Greek packets replayed 15/15 and 16/16 as consumed evidence.
The original controller suites matched 42/42 current grades and the two restart
cohorts matched 3/3 and 6/6. Heka's original grades, dispositions and policies
are retained. The host is trusted and the results apply to the tested local
namespace boundary. Production dispatch stays inactive.

## Reproduction

Use Node 24, Python and Git. Obtain the pinned gate as described in the
[controller replay guide](../../comparative-tests/workflow-controller/restart/README.md).
From the repository root set `lab=evaluation/greek-gods/hermes-02`,
`gate` to that module and `out` to a new output directory. Run
`node "$lab/run.mjs" "$lab/D-inputs.json" "$gate" "$out"`.
Grade with `python "$lab/score.py" "$lab/D-inputs.json" "$held_key" "$out" "$out-score.json"`.
Use the corresponding sealed packet and key to reproduce the exposed fresh run.
The deterministic generator regenerates both published input packets.

[Development grade](evidence/development-score.json) ·
[First fresh grade](evidence/fresh-score.json) · [Raw evidence](evidence/raw.tar.gz) ·
[Member inventory](evidence/archive-inventory.json) · [Checksums](SHA256SUMS)
