# Herodotus-DHS, Polybius, Lovelace-Limit, and Komnene-Ship

Last reviewed: 2026-11-24.

The baseline is `53408cdb452cda5aadf10cc42a4d9e50a388c4e2`. The prior
Tacitus, Douglass, Babbage, and Komnene results remain frozen. Each new
operator set was sealed before scoring. The Herodotus typed readback was
committed to separately before the candidate run. The local worker had
no key path and was non-isolated. These are local development tests.

## Herodotus-DHS

| Case or measure | Baseline | Candidate |
|---|---|---|
| FR-10, scope of the August DHS error | Withheld; all discovery anchors found | Complete, attributed to the January notice; all anchors found by discovery |
| FR-11, reaffirmed applicability date | Withheld; incomplete discovery | Complete from direct source verification; discovery anchors still incomplete |
| BT-01, B-Tests attribution and score retention | Withheld; all discovery anchors found | Withheld; `interpretation_unsupported` |
| All discovery anchors on answerable questions | 2/3 | 2/3 |
| Complete / partial / missed answerable cases | 0 / 0 / 3 | 2 / 0 / 1 |
| Negative controls correctly withheld | 4/4 | 4/4 |
| False-supported bridges observed | 0 | 0 |

The January notice attributes the replacement of the whole of paragraph
(a) to a typographical error and says only its introductory text was
intended to change. The second proof keeps August 28, 2024 applicability
separate from the correcting amendment's January 14, 2025 effective date.
It does not establish application to an individual or remove exceptions.
The four controls cover an actual individual outcome, an unverified M6
execution, an incorrect source month, and an unsupported universal claim.

BT-01 remains an over-refusal on the question as asked. The erratum reports
the attribution withdrawal and preservation of benchmark scores. The
earlier document contains the disputed words in a statement that the
available package did not establish the claim. The Federal Register
grammar has no report-attributed erratum operation. A bridge that turns
that earlier statement into a positive attribution was refused. The
three previously complete Tacitus claims reproduced exactly.
[Baseline](herodotus-before.json) · [Candidate](herodotus-after.json) ·
[Retained unsuccessful trial](herodotus-trial.json)

## Polybius

The sample is the six relational and six missing-evidence questions from
the authentic Scout packets. These questions use ordinary prose and do not
supply a publication citation. A local custody scorer compares exact
anchor coverage separately from Strict Ask completion.

| Measure | Baseline | Candidate |
|---|---:|---:|
| All required anchors, native discovery | 3/6 | 3/6 |
| All required anchors, word overlap | 2/6 | 2/6 |
| Strict complete / partial / withheld, answerable cases | 0 / 1 / 5 | 0 / 1 / 5 |
| Missing-evidence controls withheld | 6/6 | 6/6 |
| False-supported bridges observed | 0 | 0 |

The five abstentions on answerable cases report unsupported interpretation.
The existing partial did not complete the relationship. Dates, topic or
actor overlap, and sequence alone did not establish a bridge. The sample
does not classify the five misses as correct abstentions.
[Baseline](polybius-before-score.json) · [Candidate](polybius-after-score.json)

## Lovelace-Limit

| Eligible pages in the same staged corpus | Baseline | Candidate | Limits reached by the literal witness scan |
|---|---|---|---|
| 2, 24 | Complete | Complete | None |
| 31, 34, 38 | Partial | Partial | 200,000 source characters and 1,000 source units |
| 42 | Partial | Partial | 200,000 source characters |

At 42 pages the scan examined 456 source units. Importing the last
publications changed which text fell inside the bounded scan. The unit cap
therefore stopped firing even though the character cap still prevented
unique-source completion. The witness was present in each of these partial
answers. In controlled 40-page runs, short records completed, long records
hit only the character cap and became partial, and many short units hit
only the unit cap and became partial. Either cap was sufficient for the
drop with page count held fixed.

The sorter again retained two distinct records in eight slots and the
separate repeated-phrase-group limit fired on the frozen chain. Both
records supported the Babbage proof only when eligible and within budget.
Phrase-token and phrase-group limits concern sorter inspection. The
literal lookup drop was traced to the independent documentary scan.
[Baseline](lovelace-limit-before.json) · [Candidate](lovelace-limit-after.json)

## Komnene-Ship

| Check | Existing package | Delivery package |
|---|---:|---:|
| Anonymous paired questions | 22 | 22 |
| Anonymous arms | 44 | 44 |
| Question packet hashes matching concealed mapping | 22 | 22 |
| Keys or crosswalks inside the archive | 0 | 0 |
| Independent scoring | NOT_RUN | NOT_RUN |

The delivery archive is byte-identical to the prior package. Its SHA-256 is
`af4f3c37b8f02c4f7a9cbe94db158e6a85b429d7d01202dfbceb90d7476076b1`.
It is ready for delivery. The concealed mapping stays separate.
[Delivery verification](komnene-ship.json)

## Rule added

> For the bounded successive-correction question forms, uniquely resolve
> the follow-up's publication reference to the earlier correction and that
> correction's publication reference to the original rule. Require three
> eligible originals in chronological order under the same declared agency.
> Permit a terminal acronym to vary in the heading only when the follow-up
> explicitly declares that acronym. For reported scope, keep the change
> and intention attributed to the follow-up and verify their shared
> instruction and paragraph. For applicability, require explicit agreement
> between the original and earlier correction dates and the follow-up's
> reaffirmation. Keep the follow-up's own effective date separate. Require
> exact citations and the existing source-state and budget checks. Withhold
> on a missing, ambiguous, conflicting, or out-of-scope witness.

No implied-link rule was added. No literal or sorter cap was raised.
[Implementation](../../../../mplpb_answers/publication_corrections.py) ·
[Independent baseline regression](pole-successive-baseline.log)

## Open items

- Add a checked report-attributed erratum path for BT-01. Keep its withdrawal
  statement and the earlier verification-limited wording distinct.
- Resolve ordinary-prose relationships on Polybius and the 12 original
  synthetic misses with new frozen negative controls.
- Investigate literal location under bounded corpus scans. Retain separate
  sorter phrase-token and phrase-group failures.
- Obtain outside judgments for Komnene-Ship. Independent historical accuracy
  and native OOCC remain **NOT_RUN**.

## Replay

Verify the bundles with `sha256sum -c evaluation/pole/open-items/remaining/evidence.sha256`.
After extracting the operator packet, use a new output path for each replay.
The Herodotus and Polybius scoring keys remain in their separate custodies.

```sh
python -I -B tools/pole_authentic.py run --packet HERODOTUS_PACKET --implementation CHECKOUT --output HERODOTUS_NATIVE.json
python -m tools.pole_authentic score --packet HERODOTUS_PACKET --custody HERODOTUS_CUSTODY --receipt HERODOTUS_NATIVE.json --output HERODOTUS_SCORE.json
python -m tools.pole_remaining polybius --packet POLYBIUS_PACKET --output POLYBIUS_NATIVE.json
python -m tools.pole_remaining score-polybius --packet POLYBIUS_PACKET --custody POLYBIUS_CUSTODY --receipt POLYBIUS_NATIVE.json --output POLYBIUS_SCORE.json
python -m tools.pole_remaining lovelace-limit --packet LOVELACE_PACKET --output LOVELACE_TELEMETRY.json
```

[Sealed operator cases](frozen-operator-packets.tar.gz) ·
[Raw readbacks](native-readbacks.tar.gz) · [Matched summary](matched-summary.json)
