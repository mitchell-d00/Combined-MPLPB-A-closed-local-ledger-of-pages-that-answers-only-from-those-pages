# Apollo-01 first receipt provenance results

Last reviewed: 2026-11-28.

I read [Al note 0006](../../../handoff/al-notes/0006-greek-trust-and-recovery-sprint.md)
at `20885e500faf75b88fa80548aabadd1f991fe76b`. Apollo-01 applies the first
set only. Ares-01 and Hestia-01 remain deferred. The released bridge had no
producer-signature input. Apollo adds a lab adapter and retains the original
reader, binding seam, controller, and reservation code byte-for-byte.

The [contract](CONTRACT.md) and [freeze](freeze.json) pin the public trust
snapshot, exact inputs and held key seals. The [candidate pin](candidate.json)
precedes the first fresh run. Signature validity, producer trust, native proof,
binding scope, host authority, writer attempts and independently observed
effect are distinct fields in the retained traces.

| Draw | Exact fixtures | Writer attempts | Intended writes | Durable completions |
|---|---:|---:|---:|---:|
| Development | 7/7 | 1 | 1 | 1 |
| First fresh | 7/7 | 1 | 1 | 1 |

The active producer's correct receipt performed the fixed disposable Git
write in each draw. Changing the signed payload invalidated the signature.
Retired and unaccepted lab producers had valid signatures and were withheld
by the frozen trust table. An authentic wrong namespace or wrong Git revision
failed the existing Heka comparison. The properly signed unsupported report
failed at native proof. A properly signed supported report without a host
grant failed at authority. The six negatives per draw made zero writer
attempts and left the ref, marker and reservation state unchanged.

The preserved networked component uses Ed25519 for page-serving attestations.
Apollo uses Node's standard verifier with a distinct receipt scope. The first
unchanged networked suite run recorded one socket-permission error and a
reference experiment score of 0.875 for `after_hub_loss_answered`. All 61
tests passed on retry with local networking enabled. Hermes-02 preservation
matched 9/9 and 9/9. The controller replay matched 42/42 current grades, and
restart matched 3/3 and 6/6. The first preservation attempt ran out of space
during fixture creation and is retained separately. Heka and prior Greek
results remain in their original scope.

One operator prepared and scored the packets. Fresh changes wording,
entities, ordering and the wrong-scope field. It repeats the same causal
structures. A local producer process receives only its own fixture key.
Private Ed25519 keys and grading keys were read back from private workspace
preservation. An off-workspace private backup remains unverified. These test
keys and outcomes confer no real-world identity or production authorization.

## Reproduction

Use Node 24, Python and Git. The [controller guide](../../comparative-tests/workflow-controller/restart/README.md)
identifies the pinned gate. To reproduce exact signatures, recover the sealed
private lab producer keys separately from the public input packet. Reusing
the deterministic generator reproduces the operator packets, while generating
new keypairs creates a different trust snapshot.

From the repository root set `lab=evaluation/greek-gods/apollo-01` and run
`node "$lab/run.mjs" "$lab/D-inputs.json" "$gate" "$private_producer_key_dir" "$out"`.
Grade separately with
`python "$lab/score.py" "$lab/D-inputs.json" "$held_grading_key" "$out" "$out-score.json"`.
Use the corresponding exposed fresh packet and key for preservation.

[Development grade](evidence/development-score.json) ·
[First fresh grade](evidence/fresh-score.json) · [Raw evidence](evidence/raw.tar.gz) ·
[Member inventory](evidence/archive-inventory.json) · [Checksums](SHA256SUMS)
