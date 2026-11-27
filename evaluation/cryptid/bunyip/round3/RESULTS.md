# Bunyip Round 3 first comparison

Last reviewed: 2026-11-27.

The frozen diagnostic ran once on each of four unchanged readers. The
[hosted run](evidence/hosted-receipt.json), [scope](SCOPE.md), [reader pins](readers.json),
[first score](first-score.json) and [checksums](SHA256SUMS) identify the
case set and all executions. The deterministically authored synthetic
packet has 12 cases and nine distinct question strings. Preparation
and scoring were same-operator. The realized key stayed outside the
worker, which ran with network isolation. The freeze was pushed at
`62a6ed78832522f1038e2dea4ccfe48b29586cb0` and all 29 changed files
matched independent remote readback.

| Reader | Executions | Complete / 6 | Checked partial / 1 | Correct withhold / 5 | Misses | Unsupported claim cases | Execution errors |
|---|---:|---:|---:|---:|---:|---:|---:|
| C3 | 12 | 0 | 0 | 5 | 7 | 0 | 0 |
| Wampus | 12 | 0 | 0 | 5 | 7 | 0 | 0 |
| Thoth | 12 | 3 | 1 | 5 | 3 | 0 | 0 |
| Released main | 12 | 5 | 1 | 5 | 1 | 0 | 0 |

Released main gained five complete answers and one checked partial
over C3 and Wampus. Those six outcomes use five distinct question
strings. Released main retained all observed valid Thoth outcomes
and added two complete answers on two questions. No earlier supported
answer, checked partial or correct withholding was lost on this packet.
The four historical comparisons did not modify any reader. No rule
consolidation is claimed.

## By language family

| Pair | C3 | Wampus | Thoth | Released main |
|---|---|---|---|---|
| D01 imperative and terminal punctuation | Miss / withhold | Miss / withhold | Complete / withhold | Complete / withhold |
| D02 named compound and missing location | Miss / miss | Miss / miss | Complete / partial | Complete / partial |
| D03 reported authorship with source adjunct | Miss / withhold | Miss / withhold | Miss / withhold | Miss / withhold |
| D04 embedded versus outer negation | Miss / withhold | Miss / withhold | Miss / withhold | Complete / withhold |
| D05 conditional instruction versus completed action | Miss / withhold | Miss / withhold | Miss / withhold | Complete / withhold |
| D06 irrelevant owner versus relevant unresolved value | Miss / withhold | Miss / withhold | Complete / withhold | Complete / withhold |

All four readers found the expected passages on all seven
claim-bearing cases. The remaining D03-A miss contains the exact
report and recorder witnesses. The released reader returned
`interpretation_unsupported` with no documentary plan or finite
frame. The report-object request grammar does not recognize the
terminal source adjunct in this question. The matched wrong-reporter
control also stopped at interpretation. It therefore shows withholding
on this input without establishing a proof-stage speaker rejection
for adjunct-bearing forms.

No repair is proposed on this packet. The one remaining miss isolates
a phrasing gap but supplies no evidence for which source adjuncts can
safely share a rule. A bounded follow-up would contrast a generic source
adjunct with a named-record constraint and a wrong reporter, checking
role rejection after recognition. This assessment closes at its frozen
diagnostic boundary. Publication carries evidence and its lab workflow;
the released reader, browser and production workflows have unchanged bytes.

## Consumed preservation

- **832 public contracts:** 832/832 exact and zero execution failures.
  All 1,664 baseline and new raw contract hashes match their receipt.
  [Replay comparison](evidence/public-832-comparison.json).
- **BB:** 900/900 exact positives, all 900 accepted eligible citations
  reread, and 200/200 original withholds. [Replay receipt](evidence/bb-receipt.json).
- **96 Bunyip, Wampus and Thoth contracts:** all 96 executed. The original
  strict comparator again returned 87/96. The nine changed cases matched
  the normalized released fingerprints for the original approved
  diagnostic-only changes. The PR #110 approval stays attached to
  its exact action and pins. [Replay readback](evidence/retained-96-readback.json).
- **Current acceptance:** the unchanged release workflows run on the
  evidence PR. The first evidence head failed repository checks because Round 3
  was initially indexed as a top-level family. The index now registers it under
  Cryptid. Hosted isolation setup also encountered a transient Microsoft feed
  HTTP 403 at that head, before any isolation test. The release workflow and
  frozen study remain unchanged. [First evidence-head run](https://github.com/mitchell-d00/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages/commit/246a1bdcb9cf80c5561bc7b761cb3fd58bed21bc/checks).

The original 17 private checks remain incomplete. The original 100
held transfers remain NOT_RUN and unopened. Recovery stays
INTERRUPTED / UNRECOVERED and the publication-history incident stays
open. Independent historical accuracy, semantic adjudication,
outside scoring, native OOCC and human onboarding remain NOT_RUN.

## Reproduce

Check `sha256sum -c SHA256SUMS` here. The four hosted ZIPs contain the attempted
runs, citations, execution receipts and runtime archives or published
preservation comparisons. Run the scorer from repository root with
`PYTHONPATH=. python evaluation/cryptid/bunyip/round3/score.py --run
<extracted-diagnostic-directory> --key <evaluator-key> --output <new-file>`.
To regenerate the key, use `make_packet.py --root <new-source-copy> --key
<new-private-file>` from the frozen environment with the existing harness
and no preexisting diagnostic directory. The generated key and registry
digests must match the original freeze. Keep the key in evaluator custody.
