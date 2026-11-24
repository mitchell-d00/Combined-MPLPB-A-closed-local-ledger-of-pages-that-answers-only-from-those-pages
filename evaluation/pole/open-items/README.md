# Pole follow-up · named tests for reconstruction gaps

Last reviewed: 2026-11-24.

The study preserves the original Pole replay. Its priority is partial corrections
and multi-document proof. The baseline was the original Pole implementation at
`b9d581b09aae94aeb76439ac750f85595af12665`. The runner reported the
authentic baseline before replaying it against the candidate.

## Seven tests

| Test | Evidence and outcome |
|---|---|
| **Herodotus** | Replayed all 24 Scout questions against the frozen authentic FRUS originals. All 24 retained their kind, diagnostic, and support flag. The separate historical 22 replay also matched every archived strict row. |
| **Ida B. Wells** | Replayed the 12 original focus misses and 20 new seeded cases. All 28 answerable cases remained unresolved and all four controls withheld in both runs. The added named-source correction set proved six positives and withheld on six contrasting controls. |
| **Ada Lovelace** | Eight repetitions from one occurrence previously filled every witness slot. The repair preserved 2 occurrences in the crowded two-record case and 8 in the crowded many-record case, with at most 8 spans per phrase. The single-occurrence control kept its 8 spans and produced zero cross-record review links. |
| **Zora Neale Hurston** | Across 24 fresh synthetic cases, complete results stayed at 6/12 and expected withholds at 12/12. A separate named three-source dispatch-chain set proved six positives and withheld on six contrasting controls. |
| **Anna Komnene** | Prepared 22 paired anonymous outputs with source originals, citation checks, and blank review forms. Independent semantic review remains **NOT RUN**. |
| **Al-Biruni** | Rehearsed the matched-budget protocol on 24 authentic FRUS questions with a separate local key. Native discovery covered all reference anchors on 14/18 answerable cases, versus 13/18 for word overlap. All six missing-evidence controls withheld. Outside custody and independent adjudication remain **NOT RUN**. |
| **Sima Qian** | Ran identical literal and direct questions over 2, 24, 31 and 34 eligible pages, reaching approximately 1.56 MB of canonical ledger HTML. The literal check was complete at 2 and 24 pages and partial at 31 and 34. The direct question withheld at all sizes. Larger authentic corpus accuracy and capacity remain open. |

The pinned first-Pole chain still reports `repeated_phrase_group_budget`.
The patch preserves a representative span from each distinct occurrence
when another occurrence has redundant spans. It leaves both numerical caps
at their original values. Repeated phrases are review observations. [Before
regression](ada-independent-before.log) · [Seven detailed reports](seven-tests.json)

## Scoped native repair

Strict Ask now verifies two named-source operations across currently eligible
originals. Partial corrections require a literal target, a changed field
with the earlier value and replacement, and a separate field whose identical
retained value is explicit in both sources. Request–dispatch–receipt comparisons
require exact source references and matching sender, object, and destination.
The final receipt remains attributed to the person reporting it. Both forms
retain the complete question, exact citations, original budgets, and source
state rechecks. The existing opt-in chain inspection uses the same checker.

The matched 24-case synthetic proof replay moved from **0/12 to 12/12**
complete assertions. Both runs withheld on all **12/12** negative controls.
There were no new false-support cases, execution failures, or lost correct
outcomes. The independent wording tests also cover an incorrect target,
changed or absent retention, qualifiers, a restricted source, quoted content,
insufficient witness room, and a source withdrawal during verification.
[Baseline failures](named-proof-independent-before.log) ·
[Matched proof replay](named-proof-comparison.json) ·
[Historical 22](historical-22-replay.json)

## Authentic development draw

Acquisition captured ten GovInfo originals and two source files pinned to
B-Tests commit `e3a544b2e8ac37f5a23323025b264c18a15678f7`. The duplicate-copy
control uses a separate source path and ID with the same original SHA-256.
The operator packet preserves original bytes and records media type, encoding,
publisher URL, staged path and SHA-256. The custody key records explicit byte
and character anchor ranges in those originals. Native citation readback
also checks the eligible ledger path, hash and exact canonical character span.

The authentic baseline and candidate each produced **1/10** complete answers
with all required anchors, **0/6** complete relational answers, **5/5** expected
withholds, and zero unsupported full responses on controls. Discovery surfaced
all required anchors on **8/10** answerable cases. The one completion was a
literal lookup in the B-Tests erratum. The federal publications cover a venue
change, a corrected filing deadline, amended instructions, and a correction
to an earlier correction. The erratum supports its own statement about the
superseded attribution and the preserved benchmark record. The archived
version 1.2 Markdown is retained as a separate appearance. These results
measure a local authored reference and exact witness coverage.
[Authentic baseline](authentic-baseline.json) · [Comparison](authentic-comparison.json) ·
[Venue correction](https://www.govinfo.gov/content/pkg/FR-2008-12-05/html/E8-28884.htm) ·
[Deadline correction](https://www.govinfo.gov/content/pkg/FR-2020-11-04/html/2020-24461.htm) ·
[FEC correction](https://www.govinfo.gov/content/pkg/FR-2024-01-29/html/2024-01676.htm) ·
[DHS correction](https://www.govinfo.gov/content/pkg/FR-2025-01-14/html/2025-00553.htm) ·
[B-Tests erratum](https://github.com/mitchell-d00/B-Tests/blob/e3a544b2e8ac37f5a23323025b264c18a15678f7/docs/paper/TESTING_OOCC_ERRATA.md)

## Reproduction and custody

Verify `sha256sum -c evaluation/pole/open-items/evidence.sha256` from the
repository root. Extract the operator packet in a new directory. The local
development key and its case definition live outside the implementation and
operator packet. The runner receives no custody path. These replays record
`os_isolated: false`. The local Bubblewrap probe could not create a UID map.
Use a separate operator account or isolated mounts for outside custody.

```sh
python -I -B tools/pole_authentic.py run --packet PACKET --implementation CHECKOUT --output NEW_RECEIPT.json
python -m tools.pole_authentic score --packet PACKET --custody CUSTODY --receipt NEW_RECEIPT.json --output NEW_SCORE.json
python -m tools.pole_authentic compare --before BASELINE_SCORE.json --after CANDIDATE_SCORE.json --output NEW_COMPARISON.json
python -m tools.pole_open_items run ada-lovelace --public LADDER_PACKET --custody LADDER_CUSTODY --out NEW_RUN
python -m tools.pole run --packets NAMED_PROOF_PACKET --implementation CHECKOUT --out NEW_POLE_RUN
```

Freeze any independent study inputs separately. The outside custodian should
choose fresh public originals, author and seal a concealed reference key,
and issue only sources, questions and budgets to the operator. Score source
attribution, relationships, distinct event identities, unsupported links and
abstentions from two blinded reviews with disagreements retained for
adjudication. The anonymous review packet includes compatible forms and
instructions for the existing scorer. [Operator packets](public-packets.tar.gz) ·
[Anonymous review packet](anna-komnene-review-packet.tar.gz) ·
[Native readbacks](native-readbacks.tar.gz)

## Tacitus, Douglass, Babbage, and Komnene-Outside

The prose cycle moved Tacitus from **0/6 to 3/6** complete bridges and Douglass
from **0/12 to 6/12** on authentic transfer questions. Both preserved all
five controls. Babbage retained two records at the eight-slot cap and
withheld on both eligibility controls. Komnene-Outside has a verified
transport package for 22 pairs. Independent scoring remains **NOT RUN**.
[Four result tables and rule](prose/README.md)

## Herodotus-DHS, Polybius, Lovelace-Limit, and Komnene-Ship

Herodotus-DHS moved from **0/3 to 2/3** complete with all four controls
withheld. Polybius stayed at **0/6** complete with all six controls withheld.
Lovelace-Limit traced the large-corpus literal drop to character and unit
caps. Komnene-Ship verifies 22 paired questions, 44 arms, the separately
held mapping, and a byte-identical delivery archive. [Four result tables](remaining/README.md)

## BT-Erratum, Polybius-Prose, Scan-Phrase, and Komnene-Hold

BT-Erratum moved from **0/1 to 1/1** complete with unchanged discovery
coverage and **5/5** expected withholds. Expanded Polybius-Prose stayed at
**0/10** complete with 7/10 native anchor coverage, one partial, nine
answerable misses, and 10/10 expected withholds. Both suites observed zero
false-supported bridges. Scan-Phrase retained two eligible records while
reproducing the literal and phrase cap diagnostics. Komnene-Hold verified
22/22 concealed mappings across 44 anonymous arms. Outside scoring remains
**NOT_RUN**. [Four result tables and rule](erratum/README.md)

## Focus-12, Polybius-Extend, Cap-Diagnosis, and Komnene-Status

Focus-12 stayed at **0/12 complete**, with two partials, ten abstentions
on positive cases, and **20/20** original controls preserved. Native
discovery on the fresh FRUS set moved from **0/4 to 4/4** after folding
publisher layout whitespace. Strict Ask stayed at **0/4 complete** with
**4/4** controls withheld and zero false-supported bridges. The fixed cap
diagnostics and Komnene's 22/22 concealed mapping checks reproduced.
[Four result tables, case diagnostics, and projection rule](focus-extend/README.md)

## FRUS-Boundary

For the same four FRUS comparisons, both anchors were found in **4/4 → 4/4**,
Strict Ask completed **0/4 → 0/4**, and partials stayed at **0 → 0**.
All four existing controls withheld with zero false-supported bridges.
The native checker admitted no proposition-level proof for the comparisons.
[Four case decisions and withhold rule](frus-boundary/README.md)

## FRUS-Proposition

On the same four comparisons, discovery stayed at **4/4**, Strict Ask
stayed at **0/4 complete**, and partials stayed at **0**. The four
existing controls correctly withheld. The native checker rejected all
**16** exact-unit action or relationship proposals with no scan cap
reached and no false-supported bridges.
[Case decisions and withhold condition](frus-proposition/README.md)

## Open items

- All 12 original focus cases remain open, including date roles, reported
  statements, partial corrections, wording changes, and less explicit chains.
- General historical reconstruction and ordinary-prose linking across unfamiliar
  originals remain open. The four fresh FRUS cases have both anchors available
  after projection. FRUS-Boundary traced the remaining blocker to native
  proposition and attribution admission. FRUS-Proposition found that
  directly supplying the exact source units still produced no certificates. The earlier ten cases stay
  frozen. The scoped repository erratum and both tested DHS
  relations now have complete development proofs.
- Phrase-token and repeated phrase-group limits and loss of complete literal
  lookup at the larger Sima Qian stages remain open. The scan caps remain
  200,000 characters and 1,000 units. The USDA venue lookup also returned
  a partial when two verified spans from the same eligible source answered
  the source-location question.
- Arbitrary natural wording, more complex compound requests, and larger
  mixed authentic collections require further held-out measurements.
- Independent historical accuracy, outside-custodian scoring, independent
  semantic adjudication, and native OOCC remain **NOT_RUN**.

The extracted candidate completed the full Python suite with two skips,
passed all 52 public evidence controls, passed the Pyodide and Chromium
checks, and preserved all scored outcomes in the inherited catalog.
[Validation](validation.json) · [Inherited catalog replay](inherited-catalog-comparison.json)
