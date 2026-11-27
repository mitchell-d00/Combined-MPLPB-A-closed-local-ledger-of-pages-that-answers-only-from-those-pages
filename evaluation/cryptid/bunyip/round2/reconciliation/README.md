# Clean reconciliation of PR #106

Last reviewed: 2026-11-27.

Clean base `9910fec157124ab66803e0263ae61420fbb24c48`. Original PR #106
head `961be47602c5e3ccb94459c106b3fa28754549bf` stays a historical pin.
This reconciliation retires the unrecoverable original study as
**INTERRUPTED / UNRECOVERED**. The 17 private preservation checks remain
incomplete. The 36 routing plus 64 cross-family original transfers remain
**NOT_RUN**. Recovered public work and separately frozen replacement studies
retain their own identities. Independent and human measures remain NOT_RUN.

## Inventory and custody

The [path inventory](inventory.csv) compares 251 changed paths with the
clean PR #109 and #110 merge trees and with main. It also records two
intermediate-only restricted paths. Of 253 entries, 170 are already
incorporated, 34 are uniquely worth preserving, 37 were superseded, and
12 are restricted from re-publication. Superseded public states retain
their original PR #106 pin. The active reader, browser, tools and
production workflows come from clean main. [Inventory summary](inventory-summary.json)

The [selection manifest](selected-public-files.json) binds the exact
copied bytes to original publication authority, verified byte lengths
and SHA-256. The development and routing archives also matched every
entry of their public member manifests. The V2 interrupted preservation
archive has the descriptor-filtered scope recorded by the original custody
manifest. The approved archive contains public members only. The original
mixed-custody containers, held packets, key files and uncertain logs are
outside the selection. Safe historical reports and working-state receipts
retain their original bytes in [history](history/).

The publication-history incident remains **OPEN**. The separately maintained
incident record lists affected objects, protection of original evidence, and
the authorized cleanup prerequisites. The source branch, Git objects and
caches are independent of the PR's review status.
[Publication-history incident](../../../../../docs/recovery/THOTH_CLEAN_RELEASE.md#separate-publication-incident)

## Grades retained against their original contracts

The [readback receipt](original-grade-receipt.json) regraded six existing
444-case primary output sets using the exact rebuilt primary development key
and original base and expanded scorers. Per-case outcomes matched the
original grades on all six. No reader was executed for this readback.
The local staged C1/C2/C3 attempts share the same checkout revision marker.
Their runtime manifests and run hashes distinguish their actual bytes.

| Retained primary attempt | Strict complete | Correct withholds | Other outcomes |
|---|---:|---:|---|
| Historical baseline, `2622813aba9ee1f1880693eeb71ae015cb3da999` | 21/78 | 360/366 | 57 misses, six false alarms |
| Rejected local C1, exact runtime manifest in receipt | 72/78 | 366/366 | Six strict literal-field mismatches |
| Rejected local C2, exact runtime manifest in receipt | 72/78 | 366/366 | Six strict literal-field mismatches |
| Interrupted local C3, exact runtime manifest in receipt | 14/78 | 61/366 | 369 execution failures |
| Remote baseline, `2622813aba9ee1f1880693eeb71ae015cb3da999` | 21/78 | 360/366 | 57 misses, six false alarms |
| Completed remote C3, `483f35a97a32be4cadb4eb224e976e045124901d` | 72/78 | 366/366 | Six strict literal-field mismatches |

C1 has two unsupported reported-field guard completions. C2 has four
unsupported mixed-binding completions. Both candidate source archives
are preserved as rejected. The original staged C3 interruption stays
separate from the completed remote replay. The remote source-support
assessment for the full 572 exposed development memberships retains
57/128 → 128/128 positives, 71 gains across 34 distinct questions,
12 corrected unsupported cases, zero previously valid answers lost
and the original 22 strict-key mismatches. That source-support
assessment is distinct from the strict literal grading above. The
other 128 exposed development cases retain their original published
scores. Their original evaluator keys remain unavailable for regrading.
[Remote receipt](../remote-development-v1.json) · [Public raw files](../public-evidence-v1.tar.xz)

The original replacement scorer reproduced both complete comparison
records with the original three sealed replacement keys in evaluator
custody. On the 40-case draw, three fresh routing targets recovered,
17 targets missed on both readers and the separately keyed partial
obligations missed. Both readers withheld on all 16 expected-withhold
controls and emitted zero unsupported claims. The 10-case development
draw retained one shared supported target and four target misses on both
readers. Pins are released `2622813aba9ee1f1880693eeb71ae015cb3da999`
and C3 `3bf9657c7b956623f07ed4b94765e0edd5cd3f02`.
[Replacement freeze and scores](../replacement/RESULTS.md)

The completed exact public preservation run on `3bf9657c` matched all
832 contracts. Its first attempt produced an interrupted public subset
with the original failure metadata. BB retains 900 exact positive values,
900 verified eligible citations and 200 withholds as consumed regression.
[Public preservation and BB receipt](../public-replay-rerun-receipt.json)

## Applicable gates

The original PR #106 private preservation and held transfer gates are
incomplete in their original record. A separate prospective acceptance for
the clean release used the 832 public contracts, BB, protected prior gains
and frozen Thoth evidence. PR #110 has its own exact checks and separately
authorized nine-case diagnostic compatibility. This reconciliation carries
no reader or workflow changes. Its applicable gate runs are the unchanged
exact-head software and archive checks. The original 17 checks and 100 held
transfers are outside those prospective release scopes. No substitute
check is needed to close the interrupted original study. Any future
decision to claim those original results requires the original authorized
materials or a separately frozen, explicitly authorized prospective policy.
[Clean release boundary](../../../../../docs/recovery/THOTH_CLEAN_RELEASE.md) · [PR #110 verification](https://github.com/mitchell-d00/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages/pull/110#issuecomment-7219742999)

## Reproduce the available original grade

Use the [original generator, assessment and replacement scorer](reproduction/)
and the current repository's pinned D% scorer. The generator is fully
enumerated and reports the original null seed. Generate its public packet
and separate private custody directory from a clean working copy. Compare
the public seal and evaluator key digests with [the original freeze](../freeze.json).
Use the original replacement keys from their designated custody and check
their exact sealed digests. Keep that evaluation outside worker mounts and
public packaging. The [readback driver](reproduction/grade-original-evidence.py)
takes two paths: a fresh scratch root with a `public-review/` directory
containing the nine approved archives and `freeze.json`, and the primary
rebuild directory containing `public/` and `custody/`. It expects replacement
keys in `keys/` beside the primary rebuild directory, and a clean checkout
for the public replacement tree. Run with `PYTHONPATH=.` from that checkout.
The resulting custody directory contains actual grades and is outside Git.
