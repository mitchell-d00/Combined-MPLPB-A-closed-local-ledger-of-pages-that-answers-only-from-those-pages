# Heka-01 evidence-to-Git I/O

Last reviewed: 2026-11-27.

[Al note 0003](https://github.com/mitchell-d00/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages/blob/a36cc00a52d28588e22a1e0faa5e6451451976fa/handoff/al-notes/0003-next-phase-evidence-to-git-effects.md)
was read at `a36cc00a52d28588e22a1e0faa5e6451451976fa`. This lab applies its
bounded bridge experiment to released main
`4ac1e9ac1e1b6ea17a4e40244112242656772ec6`. The
[Bastet reader](../bastet/SELECTION_RESULTS.md),
[controller](../../comparative-tests/workflow-controller/README.md) and
[reservation store](../../comparative-tests/workflow-controller/restart/README.md)
remain byte-identical to that revision.

## Pins and results

The first frozen contract and scorer were committed at `161d9100d`. The first
runner stopped before scoring because this managed environment returned EPERM
while Node tore down a Python capture pipe. [Preflight log](evidence/baseline-preflight.log)
preserves the failure. File-backed capture at `f823d7b9c` allowed the baseline to
run. Packet bytes and expectations remained unchanged. The bridge candidate
`9a4d2c09e9e31529867252779a2d15a7d998f985` was pinned before the fresh packet
was opened. Scoped candidate ZIP SHA-256
`28e947a30cb211e8a5f561dc81fc7db804142c9cba6f9c08bd40dae39e740576`.

| Packet | Scenarios | Exact phases | Intended writes observed | Durable completions | Failed CAS | Indeterminate after Git |
|---|---:|---:|---:|---:|---:|---:|
| Disconnected development baseline | 11 | 10/11 | 0 | 0 | 0 | 0 |
| Candidate development | 11 | 12/14 | 3 | 2 | 1 | 1 |
| Candidate first fresh | 10 | 13/13 | 3 | 2 | 1 | 1 |

The two development mismatches were the withdrawn-source diagnostic for D-04
and the withdrawal-at-reread diagnostic for D-07. The frozen key expected
`named_report_source_unresolved` and the unchanged reader returned
`restricted_or_unavailable`. Both withheld and made zero writer attempts.
D-04 also differed on the disconnected baseline. These are recorded exact grades.
Neither the key nor the reader was changed.

Each candidate packet had four writer attempts. One failed CAS preserved the
competing ref and marker. One deliberate interruption produced an intended
ref update with a pending reservation and no completion receipt. The repeat was
withheld as indeterminate. Known completed and failed reservations blocked
their repeats before Git. All evidence and authority controls made zero writer
attempts, including correct named selection with a wrong reporter, stale
source state, missing or revoked authority, and an advice-only report.

The existing controller replay matched 7 shadow, 15 development, 8 canary,
10 held and 2 competing-writer cases. The original shadow label differences
S04 and S06 remain recorded. Restart matched the 3 baseline and 6 durable
candidate cases. Heka changes no production dispatch or release policy.
Host identity, receipt provenance and cross-resource atomicity remain
outside the demonstrated boundary.

## Reproduce and verify

Use Node 20+, Python 3 and Git. Obtain the pinned upstream B-Tests module
through the [original reproduction instructions](../../comparative-tests/workflow-controller/restart/README.md#reproduce).
The bridge and controller both check its digest.

From the repository root, set `lab=evaluation/egyptian-gods/heka-01`,
`gate` to the pinned module, and `output` to a new scratch directory path.
Run:

```sh
node "$lab/study.mjs" baseline "$lab/D-inputs.json" "$gate" "$output"
node "$lab/study.mjs" candidate "$lab/D-inputs.json" "$gate" "${output}-candidate"
node "$lab/study.mjs" candidate "$lab/F-inputs.json" "$gate" "${output}-fresh"
python "$lab/grade.py" "$lab/F-inputs.json" "$held_fresh_key" "${output}-fresh" "${output}-grade.json"
```

The same operator authored and scored both packets. The runner did not receive
the keys. Authoring code and keys are held in the private workspace; no remote
backup of the held keys is attested. Both exact public operator packets and the
sealed key digests are available. Public phase reports and the
[raw archive](evidence/first-runs-and-replay.tar.gz) preserve the real reader
outputs, ledger bytes, local Git bundles, reservations, logs and replay receipts.
The [archive inventory](evidence/archive-inventory.json) hashes the raw members.
The [baseline](evidence/baseline-score.json),
[development](evidence/development-score.json) and
[first fresh](evidence/fresh-score.json) grades remain separately recorded.
Check the tracked public package with `sha256sum -c PUBLIC-SHA256SUMS` from this
directory. The original observation path and Git readback are recorded for
every phase. Subsequent replays reproduce exposed packets.

Heka stays a lab candidate. Its two frozen development diagnostic discrepancies
remain open. The parent reader's 87/96 historical result and scoped exceptions,
17 incomplete checks, 100 NOT_RUN transfers, custody limits and incident retain
their original status.
