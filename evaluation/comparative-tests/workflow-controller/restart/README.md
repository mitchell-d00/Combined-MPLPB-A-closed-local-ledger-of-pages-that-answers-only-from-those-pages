# Lab restart and duplicate protection

Last reviewed: 2026-11-27.

The released base is `a01369392071bd6781be379a4b580d9a9d0bc460`. The
[paper archive](../../../../papers/2026-11-27-workflow-git-effects-archive-note.md)
covers the preceding work from PR #111. The restart study is a separate lab
record. Original 40-case and competing-writer results remain unchanged.

## Baseline

[Policy and scoring](BASELINE.md) and [fixtures](baseline.json) were frozen
at `164232883959299bdbbd9d23b065fd4b0a3ec737` before measurement. Both
requests used the same revision and proposal in different Node processes.
The observed canary ref was carried across restart without a reset.
All three scenarios matched the freeze.

| First request | Restart admission | Restart writer attempts | Additional writes and ref readback |
|---|---|---:|---|
| CAS completed | Allow, Git failed | 1 | 0, intended commit remains |
| CAS failed against competing writer | Allow, Git failed | 1 | 0, competing commit remains |
| CAS completed, host carries the used key | Withhold duplicate | 0 | 0, intended commit remains |

Git prevented both unretained duplicate effects. Only the host-retained
key control stopped the duplicate before dispatch.
[First raw results](results/baseline-first.json)

## Separate store candidate

The [reservation and recovery policy](STORE.md) and [fixed cases](candidate.json)
were frozen at `8b7fb962b8fe771dba7a37478db606849f6b9fa2`. The tests ran from
the [extracted lab archive](results/tested-lab.zip) of
`0aba797739ec4787cd677397036bc1d27581c529`, with SHA-256
`f40a6330587dc62177e082170ce2ae45580af2fbc1ec29b8447379d35a58d577`.

| Scenario | Store, execution and independent Git observation |
|---|---|
| Successful first update and restart | Verified completion. Duplicate withheld with zero writer attempts. |
| Competing writer and restart | First Git CAS failed. Competing commit preserved. Restart duplicate withheld before Git. |
| Two processes contend | One exclusive claim, one Git writer attempt and intended update. The other process withheld after losing the claim. |
| Process exits after claim | Zero Git attempts. Restart reports indeterminate, and the ref stays initial. |
| Reservation path is unavailable | Missing evidence, zero writer attempts, and initial ref remains. |
| Process exits after Git | The intended ref is visible. There is no completed worker receipt. Restart reports indeterminate with zero additional attempts. |

All six scenarios matched across 11 fresh worker invocations, including
the two expected abrupt exits. Git provides old-value protection for the
actual ref. The exclusive store protects duplicate dispatch across tested
restarts and contention, including after known failure or interruption.
No automatic retry or inferred completion occurs. [Candidate raw results](results/candidate-first.json)

The original 42 cases passed again, as did the three restart baseline
replays, 14 pinned B-Tests checks and 63 existing governance, continuity,
and handoff checks. Neither the original controller nor reader, browser,
or production workflows changed. Same-operator testing, one local filesystem,
one Git namespace and trusted host processes bound the result. Authentication,
receipt provenance, power-loss recovery, distributed locking, manual
reconciliation and production dispatch remain outside scope.

## Recovery and reproduction

The [checksum inventory](results/SHA256SUMS) covers the exact tested lab
archive, summaries and [raw evidence ZIP](results/raw-evidence.zip).
The raw ZIP preserves the first baseline and first candidate process results,
logs, outcome records and recoverable disposable Git bundles. Candidate
D04 and D06 retain consumed directories without terminal outcome receipts.
The original source PDF is retained with its separate SHA-256 receipt.
All experiment data is public synthetic material. The harness supplies
fixture environments containing no credentials. The fixture builder uses
fixed marker contents, local author data and commit timestamps.

Use Node 20 or newer and Git. In a fresh directory, download the upstream
module, extract the tested lab ZIP, and run the following from
`evaluation/comparative-tests/workflow-controller` in the extraction.
Use new output directories for each invocation. The checked archive
already contains the earlier 42-case fixture files.

```sh
scratch="$(mktemp -d)"
curl -fsSL https://raw.githubusercontent.com/mitchell-d00/B-Tests/c8f5b90a3560a0c0a916955719cef76074abebf8/gate-js/index.mjs -o "$scratch/gate.mjs"
sha256sum -c INPUTS.sha256
sha256sum -c COMPETING_WRITER.sha256
sha256sum -c restart/BASELINE.sha256
(cd restart && sha256sum -c CANDIDATE.sha256)
for suite in shadow development canary held competing-writer; do
  node replay.mjs "$scratch/gate.mjs" "$suite" "$scratch/$suite.json"
done
node restart/baseline-run.mjs "$scratch/gate.mjs" "$scratch/baseline"
node restart/durable-run.mjs "$scratch/gate.mjs" "$scratch/candidate"
```

The controller verifies the upstream module's pinned bytes before loading it.
Fresh process IDs and race winner order may differ. The scorer requires
the same outcomes and verifies the final commit and marker regardless
of which process wins.
