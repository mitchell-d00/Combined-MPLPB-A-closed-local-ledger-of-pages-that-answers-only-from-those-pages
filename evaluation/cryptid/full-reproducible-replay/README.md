# Full reproducible Cryptid replay

Last reviewed: 2026-11-27.

This is the replay of the authorized material available now. The [frozen
coverage manifest](coverage-manifest-v1.json) binds input and key hashes,
runners, scorers, original source states and budgets to released main
`a442c8f0c9629b65a3af38ba57319aa9c2af8dbe` and PR #110 reader
`426791113348b259797223316f6ca2d6e6b7ccb8`. Its scope includes 55 registries
across Cryptid, Wampus Cat, Thoth and the later protected Egyptian batch.
The 941 registry memberships include 940 distinct exact input equivalents
with case ID omitted and 383 exact question strings. The same question with
a changed source state or budget remains a different input. This counting
method differs from older reports' source-text-only overlap calculations.

| Cohort | Classification | Memberships per reader |
|---|---|---:|
| 55 native registries, including all three Round 2 replacements | Replayable unchanged | 941 |
| Bunyip D% development and consumed fresh | Replayable unchanged | 140 + 108 |
| First D% preparation repeat | Identical development alias | 140 memberships represented by that earlier draw |
| BB | Replayable unchanged with original retained fixture bytes | 900 positives + 200 controls |
| Public 832 preservation | Replayable unchanged; includes overlap with native registries | 832 comparisons |
| Round 2 original exposed primary | Replayable unchanged with reconstructed original key | 444 |
| Round 2 other original exposed development | Verified inputs and historical receipts, no original key | 128 historical memberships |
| Round 2 original private preservation | Unavailable and retired | 17 original checks incomplete |
| Round 2 original held transfer | Unavailable and retired | 100 NOT_RUN |

The D% development and consumed fresh generator reproduced the original
seals, including public inputs, key, dice, worker and pairing hashes.
The old first preparation repeat maps to development and remains retained.
The separately recoverable Bunyip replacement, Wampus and Egyptian keys
are kept in evaluator custody. Registry jobs collect original immutable
outputs through the existing Cryptid runner. Both reader lanes are sequential
per cohort, with at most two hosted cohort jobs in parallel. Separate artifacts
retain each cohort's raw results and logs. BB uses the already retained
fixture bytes and original scoring. Historical software selectors and human
onboarding preparation are inventoried separately from reader question packets.

## Original packet rebuild and retirement

The [supplemental freeze](round2-primary-rebuild-freeze-v1.json) adds the
Round 2 primary packet to the frozen inventory. The original generator fully
enumerates this packet. Its Dice Bag record has a null seed and no rolls, like
the two earlier D% draws. All 962 public files including the seal match the
retained public archive. The original evaluator key, dice, pairing, worker,
runner and scorer hash checks also match. The [public-only ZIP](round2-primary-sealed-public-v1.zip)
preserves the same packet members. The exact evaluator key is regenerated
in separate custody using `tools/bunyip_round2_packets.py` from
`961be47602c5e3ccb94459c106b3fa28754549bf`. Copy the exact generator
bytes with `git show`, verify its SHA-256 against the supplemental freeze,
then run it on the evaluator host with `--out <empty-public-dir>` and
`--custody <empty-private-dir>`. Use the pinned runner and worker hashes in
the freeze. Verify the public seal, key, dice and pairing before replay.
Mount only the sealed case inputs in the worker. Apply the original scorer
to the saved outputs in separate evaluator custody.

The other 128 exposed development inputs match their public seals: 54 routing,
18 polarity, 44 guards, four mixed-binding and eight irrelevance. No matching
original keys were recovered. They retain their original scores and historical
failure records. No scoring recipe was inferred from the original results.
The 17 original private checks remain incomplete, with one original startup
failure and 16 unrun. The 36 original held routing and 64 held cross-family
cases remain unopened and NOT_RUN. No exact generation recipes with the
full original custody inputs and hashes were recovered for those cohorts.
They are retired from active recovery. The interrupted workspace recovery
remains INTERRUPTED / UNRECOVERED.

## Matched replay results

The [verified receipt](replay-receipt-v1.json) records the original scores,
normalization and raw-artifact digests. Both readers completed 941 registry
memberships. There are 899 exact contracts, 18 new original-key passes
(nine Egyptian development and nine Egyptian fresh), and 24 diagnostic-only
changes on unsupported, zero-claim abstentions. All 419 claim-bearing
released contracts match. No earlier registry key pass was lost and no new
registry false-support flag was recorded.

Both readers matched all 832 public preservation contracts and all 900 BB
positives with their citations, plus 200 BB withholds. The BB raw results
are retained in the [public replay ZIP](bb-replay-raw-v1.zip). The 64 original
software controls passed per reader after the retained Nessie fixture
staging failure.

The separate isolated [D% raw artifact](https://github.com/mitchell-d00/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages/actions/runs/45998421140/artifacts/15196778865) contains the
original worker outputs. The frozen original evaluator scored them outside
the worker.

| Cohort | Cases per reader | Complete answers, released → candidate | Expected withholds, released → candidate | False alarms, released → candidate | Execution failures, released → candidate |
|---|---:|---:|---:|---:|---:|
| D% development | 140 | 28/32 → 28/32 | 108/108 → 108/108 | 0 → 0 | 0 → 0 |
| D% consumed fresh | 108 | 24/24 → 24/24 | 84/84 → 84/84 | 0 → 0 | 0 → 0 |
| Restored Round 2 primary | 444 | 72/78 → 72/78 | 366/366 → 366/366 | 0 → 0 | 0 → 0 |

All 692 normalized D% contracts matched. The restored primary retained six
strict literal-field mismatches on both readers. Each includes a Yes/No
prefix that the strict matcher retains. The original source/format assessor
accounts for the prefix and verifies the underlying source claims and
citations. It scored 444/444 source decisions and 12/12 prospective polarity
checks on both readers. The receipt retains both scores and the six IDs.
The three earlier hosted prelaunch failures ran zero readers and are retained
in the receipt.

Both readers completed all 3,565 replay memberships. It includes
569 repeated memberships between public preservation and the registries.
The additional 64 software selectors are counted separately. These are
synthetic development and preservation comparisons.

## Release boundary

The reproducible release proposal requires completed eligible replays,
original semantic scoring, preserved prior source support, zero new
unsupported claims and no silent eligibility or budget change. Changed
diagnostics and intentional gains require their own records. The [nine-case
diagnostic proposal](../../egyptian-gods/attribution-scope/DIAGNOSTIC_COMPATIBILITY_PROPOSAL.md)
is inactive. The original 87/96 result remains failed. Prospective approval,
applicable exact-head software checks and deployment verification are separate
gates. The publication-history incident remains separately open. Independent
and human evaluations remain NOT_RUN.
