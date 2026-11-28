# Ares-01 first cross-process authority results

Last reviewed: 2026-11-28.

I read [Al note 0006](../../../handoff/al-notes/0006-greek-trust-and-recovery-sprint.md)
at `20885e500faf75b88fa80548aabadd1f991fe76b`. Ares uses the Apollo merge
`e2a4d77ff09150639cde1bcea2fe2bcb245ac963` as baseline. It retains the
original reader, Heka bridge, controller, reservation store and writer.
Cross-process authority and file barriers were new lab functionality.
Hestia-01 remains deferred.

The [frozen contract](CONTRACT.md) sets the final shared authority read as
the decision point. The [freeze](freeze.json) pins packets, keys, scorer,
baseline and preserved dependencies. The development-positive
[candidate](candidate.json) was selected before first fresh.

| Draw | Exact fixtures | Writer attempts | Intended writes | Durable completions |
|---|---:|---:|---:|---:|
| Development | 5/5 | 2 | 2 | 2 |
| First fresh | 5/5 | 2 | 2 | 2 |

| Contrast in both draws | Initial admission | Final admission | Actual writer attempts | Observed result |
|---|---|---|---:|---|
| Active grant | Allow | Allow | 1 | Intended Git marker and durable completion |
| Revocation before final read | Allow | Withhold | 0 | Initial ref and unused reservation |
| Stale cached grant | Allow | Withhold | 0 | Preliminary reads used cached epoch 1. Final read saw revoked epoch 2 |
| Restart after revocation | Withhold | Unreached | 0 | Distinct executor reread shared epoch 2 |
| Revocation after final read | Allow | Allow | 1 | Already-admitted Git write and durable completion |

The records identify distinct revoker, executor and priming processes.
They establish ordering using explicit file handshakes and append-ordered
events. In the post-check contrast the final read saw active epoch 1.
The authorized callback then paused before the existing writer.
The separate revoker committed epoch 2 before the writer attempt.
That observed effect was expected under the frozen rule.
The other three revocation cases made zero attempts and left the ref,
marker and reservation unchanged. No unexpected effect occurred.

Apollo's two 7/7 draws replayed as consumed preservation. Controller
and restart replays matched 42/42 current grades, 3/3 baseline and 6/6
durable candidate. Previous first results and the original Heka
disposition remain at their original pins. This study uses the existing
Heka worker with a hash-pinned lab hook and does not combine the signed
Apollo adapter with revocation. The local authority store and Git are
separate resources. No production dispatch or identity claim is active.

One operator authored and scored both deterministic draws. Fresh uses
different wording, actors and order and repeats the causal mechanisms.
Both private grading keys were verified against their seals in local
workspace preservation. An independent off-workspace backup is unverified.

## Reproduction

Use Node 24, Python and Git. Obtain the pinned gate from the
[controller guide](../../comparative-tests/workflow-controller/restart/README.md).
From the repository root set `lab=evaluation/greek-gods/ares-01`.
Run `node "$lab/run.mjs" "$lab/D-inputs.json" "$gate" "$out"` with a new
output directory. Grade separately with
`python "$lab/score.py" "$lab/D-inputs.json" "$held_key" "$out" "$out-score.json"`.
Use the corresponding sealed input and key to replay the exposed fresh
draw. The deterministic generator regenerates both packets byte-for-byte.

[Development score](evidence/development-score.json) ·
[First fresh score](evidence/fresh-score.json) · [Raw traces](evidence/raw.tar.gz) ·
[Member inventory](evidence/archive-inventory.json) · [Checksums](SHA256SUMS)
