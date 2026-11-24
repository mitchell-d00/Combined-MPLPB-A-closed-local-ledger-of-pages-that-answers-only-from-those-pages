# Tacitus, Douglass, Babbage, and Komnene-Outside

Last reviewed: 2026-11-24.

The baseline is Pole pin `5ffdca2d9e7c7bc6048b9bfb9f1a0caf36835426`. Each
operator packet and its separate key commitment were frozen before scoring.
Tacitus retains the six relational questions and five controls from the
existing authentic draw. Douglass uses two new question wordings for each
of those six authentic relations and keeps the same five controls. It is a
transfer set across the five open focus families. The original frozen
synthetic focus questions were replayed separately without changes. The
two new question variants share the original documents and the same local
authorship, so the results are a development measurement.

## Tacitus

| Measure | Before | After |
|---|---:|---:|
| All required discovery anchors, answerable cases | 4/6 | 4/6 |
| Complete typed bridges with all required exact witnesses | 0/6 | 3/6 |
| Answerable cases withheld | 6/6 | 3/6 |
| Negative controls withheld | 5/5 | 5/5 |
| Unsupported or unverified supported bridges observed | 0 | 0 |

The venue and instructions cases completed with all anchors found by
discovery. The deadline also completed. Its discovery pass missed at least
one anchor, and the bounded verifier located the needed witnesses directly
in eligible sources. The two DHS questions and the B-Tests erratum remain
unresolved. [Baseline](tacitus-before.json) · [Candidate](tacitus-after.json)

## Douglass

| Measure | Before | After |
|---|---:|---:|
| All required discovery anchors | 8/12 | 8/12 |
| Complete misses | 12 | 6 |
| Partial answers | 0 | 0 |
| Complete typed proofs | 0 | 6 |
| Negative controls withheld | 5/5 | 5/5 |
| Unsupported or unverified supported bridges observed | 0 | 0 |

The six transitions were directly from miss to complete. Original synthetic
focus outcomes stayed unchanged, including all 12 old misses. Sorter
inspection of the two authentic venue source projections retained both
occurrences and 30 phrase groups spanning both. The phrase-token and
phrase-group diagnostics still fired. Sorter output carried no proof
authority. [Baseline](douglass-before.json) · [Candidate](douglass-after.json) ·
[Sorter baseline](douglass-sorter-before.json) · [Sorter candidate](douglass-sorter-after.json) ·
[Original focus replay](original-focus-comparison.json)

## Babbage

| Measure | Before | After |
|---|---:|---:|
| Slots and distinct records in crowded pair used for proof | 8 slots / 2 records | 8 slots / 2 records |
| Slots and distinct records in many-owner control | 8 slots / 8 records | 8 slots / 8 records |
| Phrase-group cap diagnostic on retained chain | Present | Present |
| Bridge with both records eligible | Withheld | Complete |
| Bridge with earlier record denied externally or withdrawn | 0/2 | 0/2 |
| Bridge with capped proof passages or corpus scan | 0/2 | 0/2 |

The candidate distinguishes unavailable evidence, witness-budget exhaustion,
and scan-budget exhaustion. The sorter can retain both occurrences without
authorizing a bridge after a record is withheld. [Baseline](babbage-before.json) ·
[Candidate](babbage-after.json)

## Komnene-Outside

| Measure | Before | After |
|---|---:|---:|
| Anonymous paired questions | 22 | 22 |
| Anonymous arm packets | 44 | 44 |
| Matching arm crosswalk in separate custody | 1 | 1 |
| Independent scores | NOT RUN | NOT RUN |

The transport package includes original source excerpts, blank review
forms, and reviewer instructions. The concealed crosswalk matched all 22
packet hashes and stays outside the package. Outside delivery is pending
a judge or delivery destination. [Original blind packet](../anna-komnene-review-packet.tar.gz) ·
[Transport and custody receipt](matched-summary.json)

## Exact rule

> For a whole question about a supported Federal Register correction form,
> resolve each cited publication uniquely from the heading and the explicit
> reference in the source body. Match publication volume, first page,
> publication date, and published document number where provided. Verify
> the corresponding issuing agency or docket and require chronological
> order. Independently bind the changed value and any retained or reaffirmed
> value to their scoped source statements. Return only the verified
> publication assertions with exact witnesses. Withhold when a necessary
> source or value is ambiguous, unavailable, qualified, contradictory, or
> outside the scan or witness budget.

The supported shapes are venue and retained hours, a filing deadline with
a correction and later reaffirmation, and two numbered instructions with
an effective-date comparison. Subject overlap, chronology alone, candidate
edges, or a missing target cannot authorize a bridge. Broader correction of
a correction, general attribution, and applicability reasoning remain
outside this rule. [Implementation](../../../../mplpb_answers/publication_corrections.py) ·
[Independent baseline regression](independent-baseline.log)

## Remaining work

- Resolve the two DHS and one B-Tests relational cases without broadening
  the rule beyond its evidence.
- Resolve the 12 original synthetic focus misses and test independent
  question wording, additional date roles, and attributed statements.
- Diagnose the separate sorter phrase limits and the loss of complete
  literal lookup at larger corpus sizes.
- Obtain blinded outside judgments for Komnene-Outside. Independent
  historical accuracy and native OOCC remain **NOT RUN**.

The operator bundles exclude scoring keys. The local worker received no
custody path. It recorded `os_isolated: false`; the sealed comparison is
local development evidence. Verify the archives from the repository root
with `sha256sum -c evaluation/pole/open-items/prose/evidence.sha256`.
[Operator packets](frozen-operator-packets.tar.gz) ·
[Raw readbacks](native-receipts.tar.gz) · [Comparison receipt](matched-summary.json)
