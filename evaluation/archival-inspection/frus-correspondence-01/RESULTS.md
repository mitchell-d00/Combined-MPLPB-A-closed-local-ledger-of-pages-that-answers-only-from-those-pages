# FRUS Correspondence 01 — first public baseline

Last reviewed: 2026-11-28.

Frozen study inputs and extractor commit `fdf32d2b6`. Hosted exact head
`49c2ab856c45b6f826e55ef4495b730b644e8ffe`. Released native reader and
investigation code match main `cb7ed70a57d3fab38c458f278a42ffd040108d98`.
The [source map](source-map.json) and [frozen protocol](PROTOCOL.md) retain
seven edition records across **17 distinct printed pages**. This smaller
coherent cluster is not the targeted 515-page scale.

- Publisher TEI source pin `216cdb7649a8e29504377d4f2858351dc46331a8`.
- Parent volume SHA-256
  `184b039ee0331bfac08572eebdd43001a2af047a7d46fd42262b986ded40eaf7`.
  Exact XML fragment byte ranges and edition page offsets are in the map.
  Source-map SHA-256
  `7d1a3413daf6ddc7193aad96e75dcef371158435a8a94be994ff2d589a15831d`.
- Projector SHA-256
  `598ca3fcd9f8d8f35cd494c0dc1483346bc5fa7544286484679ede5683100993`.
  Exact projected corpus SHA-256
  `d49ab3103d7dccda2264c5b21070be1641dc05c28178911f913c94290f922ad5`.

The [local preflight](local-preflight.log) failed before reaching the reader.
The isolated hosted job passed four [preflight tests](preflight.log). Each
worker returned zero with read-only mounted inputs, network isolation and
no mounted evaluator material. Three predeclared smoke executions returned
three abstentions with no execution failures. Smoke was an execution check.
The repeated smoke questions are excluded from diagnostic denominators.
[Hosted sandbox receipt and artifact](https://github.com/mitchell-d00/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages/actions/runs/46168019987)

| Track | Diagnostic cases | Complete / positive targets | Correct withholds | Missed positives | Exact target anchors found | Exact citations emitted |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Location and header | 57 | 27/42 | 15/15 | 15 | 27/42 | 27/27 |
| Direct relationship | 6 | 0/4 | 2/2 | 4 | 0/11 | 0 |
| Two-link relationship | 5 | 0/2 | 3/3 | 2 | 0/14 | 0 |
| Documentary interpretation | 9 | 0/4 | 5/5 | 4 | 0/14 | 0 |

The nine invented missing-phrase prompts withheld 9/9. The six
authentic-collection absence or unsupported-delivery prompts withheld 6/6.
No synthetic source text was imported. There were zero execution failures,
unsupported claim flags, emitted false bridges or entity merges, partials,
or conflicts in 77 diagnostic cases. These counts do not imply detection
of actual conflicting events. Nine documentary cases all abstained,
seven on interpretation and two at documentary proof. All eleven
relationship questions stopped at interpretation. Across location
questions, 27 established the quoted location, 24 ended at a documentary
diagnostic, five at unsupported interpretation, and one at unavailable
evidence. See the [first per-case scores](first-score.json) for exact
stops, citations, missing flags and uncertainty. Explicit unresolved text
appeared in 24 location and two interpretation cases. No relationship output
asserted an uncertainty-qualified partial.

The investigation visited the expected sources for every case with
required sources. Source visits do not earn passage-level credit. The
only frozen target spans it or Strict Ask surfaced were the 27 exact
literal witnesses. Consequently the recorded direct and two-link merits
are zero even though the correct documents were available. No recorded
instruction or dispatch was interpreted as performance or receipt.

Worker wall time was 70.0 seconds for location, 12.6 for relations and
10.0 for documentary interpretation, plus 3.6 for smoke. Sum of worker CPU
across diagnostics was 92.6 seconds. Maximum investigation characters
examined was 39,254. These times exclude hosted setup, authoring, reviewing
and correction effort. Human review time was unmeasured.

## Recovery, custody and remaining steps

The public [raw run archive](public-first.zip), including all four native
and investigation outputs and sandbox receipts, was recovered via the
GitHub connector after the direct artifact download returned HTTP 403.
The archive SHA-256 is
`895ef4181460bd58ec446c47818860a482ba70276d3a05487dbd0a93767a3331`.
The restored contents passed ZIP integrity, artifact allowlist, exact
input comparisons and frozen seal readback. The
[initial checkpoint](freeze-remote-readback.sha256) has a separate
30-path GitHub readback. The archive is tracked here to retain it beyond
Actions expiration.

Private custody is local workspace custody in a separate restricted
directory. Five seals, their exact source/packet hashes, salted gold,
author, scorer and rubric were verified locally. Off-workspace evaluator
recovery remains unverified. Only the fresh seal digest is public. Betty
authored the questions and reviewed and scored the public baseline after
the hosted process ran. This does not establish independent semantic
accuracy. No reviewers or human participants received packets through
this work. The [external review assignment](review/ASSIGNMENT.md) and
[participant route](../../onboarding/current-route-01/PROTOCOL.md) are ready
for recruitment and controlled assignment.

Fresh remains **NOT_RUN**, pending a separately pinned candidate. The
older comparison remains **NOT_RUN**. An exact older tree
`26621affeb487fb096a08acfc5bcdeb335760ad7` is available. Rebind only runtime
implementation pins and repeat the sealed arguments and budgets in a
separate hosted comparison. Local Bubblewrap still fails; the
first hosted run admitted only the released environment. Independent review
and human observations remain **NOT_RUN**. See [unfinished work](../../../docs/OPEN_WORK.md)
for owners, blockers and triggers. PR #130 and the Gelhaus private study
retain their separate statuses.
