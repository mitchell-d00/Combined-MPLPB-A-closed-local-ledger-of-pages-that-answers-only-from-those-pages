# Al note 0006: extend Greek; preserve the existing regression base

Last reviewed: 2026-11-28.

**\* Al advice for Betty; publication requested by Mitchell (M).**

Reviewed main: `e34d20cca4d5e96ed08e40d785c9a9e8eb707f06`.
Mitchell asked for a few experiments, what to push next, and whether the
existing sets work or Greek should be extended. I read PR #124, Hermes-02's
results, the frozen store policy, work-coordination guide and preserved
networked component guide. No experiment was run for this review.

## Recommendation

**Keep the existing sets and extend Greek with three targeted responsibilities.**
Use Bastet, Heka, Athena/Hermes/Hephaestus, Hermes-02 and original controller/
restart packets as consumed preservation at their exact pins. Their repeated
success is useful regression evidence; it is not new independent transfer.

Hermes-02 adds the recorded namespace contrast: both draws passed 9/9 phases,
with two authorized effects and two durable completions per draw. Seven blocked
phases made zero writer attempts. No comparison repair was needed. Its lab
seam, trusted host, same-operator evaluation and unchanged runtime remain the
scope. Receipt origin and cross-process revocation are still assumptions, and
the store's original contract excludes external modification and corruption.

Freeze the following three sets as a programme, then execute **Apollo first,
Ares second, Hestia third**, pinning the actual baseline at each stage. Keep
every first result. A passing unchanged baseline needs no gratuitous repair.

## Apollo-01: receipt provenance

Question: can the lab establish which accepted producer key attested the exact
receipt, while still independently requiring source proof and host permission?

Inspect Gremlin's preserved networked signing/provenance work and its original
tests before choosing reuse. Use an established signature-verification interface
and lab-only keys. Preserve the older component and distinguish its guarantees
from the new adapter; a test-only signing experiment is not production identity.
Freeze trust roots, signed fields, serialization and key-status policy before
the runs. Record key-generation randomness separately from deterministic packet
generation. The original bridge has no general public receipt-import API;
declare the lab producer/verification seam explicitly.

Pair a valid accepted-producer receipt with a changed payload, unaccepted key,
retired key under the frozen rotation policy, and authentic-but-wrong-target or
namespace receipt. Include a valid signature over an unsupported evidence claim
and a complete signed source proof without a host grant: neither may dispatch.
Require the positive control to perform its fixed disposable Git effect.

Score signature validity, producer trust, binding/freshness, actual reader proof,
host authority and effect separately. A hash alone is not producer evidence.
An accepted signature proves possession of the configured key; it does not
establish truth, real-world human identity, or authority to execute.

## Ares-01: revocation across processes

Question: does a separately running revoker affect the executor at the declared
authority decision boundary?

Use separate disposable worker processes, a host-owned shared authority source,
and explicit barriers/events. Freeze the linearization point before testing.
An active grant must permit the intended effect. A revocation committed before
the final authority check must block Git dispatch. Include a stale cached grant
and a process restart that must reread the current authority epoch/state.

Also retain a contrast where revocation happens after the declared admission
point. Grade it under the frozen rule and actual trace; do not retroactively
classify an already-authorized effect as prevented. Report process identities,
ordered state changes, authority reads, dispatch and Git readback. Wall-clock
timing alone does not establish the interleaving. This does not create atomic
revocation across the authority store and Git ref or handle a compromised host.

## Hestia-01: damaged-record recovery

Question: does the lab preserve uncertainty and avoid repeat dispatch when a
consumed reservation has a damaged or mismatched outcome record?

Alter only disposable fixtures. Test truncated JSON, missing fields, a receipt
copied from another request/namespace, and unavailable storage. A consumed marker
without a valid context-bound outcome must not become completion or an unused
request; require no automatic retry and observe the actual Git state. Pair the
negatives with a valid completed receipt and a known failure that remain
readable after process restart.

Include a valid historical completion followed by a later independent ref move.
Keep the historical event and current Git state separate; do not infer that the
earlier effect never occurred or authorize repeating it merely from today's ref.
The post-Git/no-receipt case remains indeterminate. These faults extend beyond
the original trusted-store assumption and require a separately frozen policy.
Process exits, injected corruption and local filesystem tests do not establish
real power-loss recovery or distributed-filesystem guarantees.

## Execution and publication rules

1. Recover the latest applied state and acknowledge this note's exact commit.
   For each set freeze the contract, inputs, key digests, baseline and scorer
   before implementation/execution. Distinguish existing support, missing
   functionality and a failed phase; do not fabricate an implemented baseline.
2. Run actual reader, authority/binding checks, Git effects and store readback
   where the contract calls for integration. Label isolated/dry probes separately.
   If a general mechanism defect is found, pin a separate bounded candidate and
   repair rationale before opening its new fresh packet.
3. Give new cases stable IDs and retain scope/feature denominators. Disclose
   repeated structures, same-operator preparation and key access. The first fresh
   result stays first; subsequent fresh-informed repair needs later evaluation.
4. Preserve the original Heka 10/11, 12/14 and 13/13 grades and disposition,
   consumed Greek/Hermes results and frozen policies. Replay affected old suites;
   reuse unrelated preservation only after byte-verifying its inputs/runtime.
5. Record proof, authority, admission, attempted effect, observed effect, durable
   outcome and indeterminate recovery separately. Any unexpected write or lost
   valid positive needs investigation; more refusals alone are not a gain.
6. Before long runs preserve generators and held material in approved private
   custody and verify retrieval. The remaining off-workspace backup gap is an
   operational task: identify an approved private destination and verify a
   retrieved copy, or record it as unverified. A second same-workspace copy is
   not an independent backup. Never publish private keys or restricted archives.
7. Push recoverable public evidence, checksums and reproduction steps, verify
   remote bytes, and update Gremlin, HANDOFF and the Test Index. Keep each set's
   baseline, first results, repairs and limits visible. Existing authorization
   covers qualifying lab push/merge after required exact-head checks; verify
   merged-tree and publication status. Production dispatch remains inactive.

This note assigns bounded lab experiments, not a production authentication
system or universal effect-stack guarantee. Betty records applied/deferred/
rejected instructions and her actual outcomes under Mitchell's existing scope.

## Evidence and reuse pointers

- [Hermes-02 results](../../evaluation/greek-gods/hermes-02/README.md)
- [Frozen local store scope](../../evaluation/comparative-tests/workflow-controller/restart/STORE.md)
- [Preserved networked signatures and limits](../../parts/networked/README.md)
- [Existing Work Coordination](../../docs/departments/work-coordination.md)
- [Gremlin](../../docs/gremlin/README.md)
- [Merged Hermes-02 report](https://github.com/mitchell-d00/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages/pull/124)
