# Round 4 attribution interpretation and proof

Last reviewed: 2026-11-27.

Released baseline `39df3d14ebf4bb01c056e8b04b8da65c7303fa61`.
The [diagnostic](SCOPE.md) was frozen at `717be4e0cdc53a68fc70e102bf1b7b388174e9aa`.
The [fresh policy and cases](REPAIR.md) were frozen at
`84b13f0a3f9e83da04de414488ccd78f73ca9ce3`, before reader edits.
Native candidate `568b44c5fcba9fa65bb29e045a1e1080cfebb709`, scoped ZIP SHA-256
`f7aa5541e1114722fac62b09ba0323a1400b0d3af2eb7de61d33f17ae3a283b7`.

## Diagnosis and first results

Round 3 D03-A found both source witnesses. [Its first score](../round3/first-score.json)
is unchanged. The native reporting-object pattern expected punctuation
immediately after “wrote.” The terminal generic source adjunct left that
request without an attribution operation. Source selection was sufficient
to find the passages. Attribution proof and final admission were never
reached on that answer.

The unchanged diagnostic ran eight cases across seven distinct questions.
It kept bare attribution and a bare wrong-reporter proof rejection, and
separately found one cited conflict. The generic and named positives missed
after discovery. Both generic negative questions withheld before proof.

The [first diagnostic score](evidence/diagnostic-score.json) flagged two
unsupported cases because the key stated byte offsets against fixture HTML
while the native citations pointed into admitted HTML. The native ledger
prepends a title heading. The [coordinate recheck](evidence/diagnostic-coordinate-recheck.json)
applies that exact transformation to the unchanged byte spans and verifies
the admitted body hash and exact offsets. It scored one complete answer,
one cited conflict, four withholds and two misses from the original raw
executions. It did not change semantic expectations or reader output. Both
scores and the [first raw run](evidence/diagnostic-baseline.zip) are retained.

## Fresh comparison

| Outcome | Released | Candidate |
|---|---:|---:|
| Complete answers / 3 | 1 | 2 |
| Checked partials | 0 | 0 |
| Cited conflict / 1 | 1 | 1 |
| Correct withholds / 4 | 4 | 4 |
| Misses | 2 | 1 |
| Cases reaching native attribution proof | 3 | 6 |
| Unsupported claim cases | 0 | 0 |
| Lost valid outcomes | — | 0 |
| Execution errors | 0 | 0 |

Eight cases and seven distinct questions ran once per reader. Across the
diagnostic and paired fresh comparison there were 16 registered cases,
14 distinct question strings and 24 executions. Preparation and scoring
were same-operator. Fresh structure repeats the same obligations with a
different open request, source wording, names and objects. The worker received
no key or scorer. The candidate was committed and hashed before the fresh run.
The first fresh score was retained before any release work. There was no
further reader repair.

The recovered F02 uses “Which document did … say … wrote, according to this
source.” It cites the printed writer and the separate source-reported
speaker’s clause. F03 (wrong reporter) and F07 (competing eligible objects)
now reach the specialized checker and return `reported_object_unresolved`
with zero claims. Bare wrong-reporter rejection and the two-citation
conflict held. F05 still misses despite locating both witnesses. It asks
for a name-constrained source selection, which this reader rule does
not establish. The wrong named-source control also still stops before
that proof and supplies no positive evidence about a named selector.
[First paired raw results](evidence/fresh-comparison.zip).

The one-line interpretation extension admits only a terminal comma and
“according to the/this record/source” in the existing reporting-object
request. The original question remains the authority throughout the
pipeline. No source-selection, proof, budget or admission rule changed.
This is one measured wording gain. No logic consolidation was made.

## Preservation

- **Focused suites:** 30 reported-content and ordinary-question tests passed.
- **Public contracts:** 832/832 exact, with zero execution failures. New raw
  responses and their comparison are retained. The original reference
  remains at its published SHA-256 and was used unchanged.
- **BB:** 900/900 positive values, 900 exact eligible citations and
  200/200 expected withholds.
- **Bunyip/Wampus/Thoth:** all 96 consumed contracts executed. The original
  strict result stayed at 87/96, and all nine differences matched the
  already recorded released normalized refusal fingerprints. The reused
  Round 3 comparator labels its own wrapper “Byte-identical released reader
  replay.” This Round 4 execution used the new candidate stated in the
  raw comparison metadata. The policy was neither changed nor extended.
- **Release:** unchanged exact-head and deployment gates apply. Their final
  receipts are in the live PR.

The effect-controller lab is unchanged. The original 17 checks remain
incomplete, 100 transfers remain NOT_RUN, recovery stays INTERRUPTED /
UNRECOVERED, and the publication-history incident stays open. Independent
historical accuracy, external scoring, independent semantic adjudication,
native OOCC and human evaluations remain NOT_RUN.

## Reproduce

From repository root with `PYTHONPATH=.`, use `packet.py diagnostic --key
<private-file>` and `freeze_fresh.py --key <private-file>` on a new source
copy without the two materialized study directories. Compare the generated
packets and private key hashes against their corresponding freeze files.
The evaluator key is reconstructible and stays outside the worker.

The branch-scoped study workflow runs the unchanged Cryptid worker.
Extract the appropriate comparison ZIP and pass each arm directory
to `score.py diagnostic` (original first scorer) or to
`score_v2.py diagnostic` / `score_v2.py fresh`, with `--key`, `--run`
and an unused `--output` path. Use `sha256sum -c SHA256SUMS` for the
retained package and scoring inventory.
