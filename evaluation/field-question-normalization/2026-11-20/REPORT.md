# Literal field question normalization experiment

Last reviewed: 2026-11-20.

The exact-field parser recognized one canonical request structure. Other questions
containing the same identifier entered exact routing but had no parsed field,
ending at `exact_field_missing`. This was admission failure, not absent source data.

Before changes, the new general-vocabulary regression failed on eight request
forms (exit 1). Two subsequent test-harness failures used an uppercase filename
and then a relative record path incorrectly; both errors are retained. The final
nine new tests pass (exit 0), including real withdrawal/corruption, final readback,
question-specific restrictions, conflict/budget and explicit-selector mismatches.

The bounded class fix extends `relation_graph.exact_request` with whole-question
imperative, record-first, possessive and interrogative structures. Fields remain
literal: no synonym table, model, ranking or benchmark IDs/values authorize support.
The unchanged source checker still establishes support. Original question policy
is preserved and normalization appears separately in the contract. No core
`mplpb_combined` changes. Existing frozen sources, keys and reports are preserved.

## Measured public reproduction

Source package: https://drive.google.com/drive/folders/1i_n34wkDoHEky-5p7-pmu4Xs2IPblli0

Downloaded ZIP SHA-256: `f4d1c8263dbb8dcf9f7ddbc9fc85be5d005864db4c74fce1a93cda1bb4865718`.
All 59 checksum-listed members verified. The ZIP is retained unchanged.

| Outcome | Published pin bbf6690 | Before change 3483b1a | Updated working candidate |
|---|---:|---:|---:|
| Canonical support | 150/150 | 150/150 | 150/150 |
| Paraphrase support | 0/750 | 0/750 | 750/750 |
| Nonexistent record refusal | 50/50 | 50/50 | 50/50 |
| Missing field refusal | 50/50 | 50/50 | 50/50 |
| External machine-source refusal | 50/50 | 50/50 | 50/50 |
| Unsupported identity refusal | 50/50 | 50/50 | 50/50 |

Each unchanged reproduction script run exited 0. No positive query exceptions.
The 900-query CSV contains positives; the script separately generates 200 negative
controls. This reconciles the 900 versus 1,100 totals. Support counts are not a
historical accuracy measure. Additional CSV scoring checks exact returned field
and value against the public synthetic keys, outside engine execution.

## Validation status

Full frozen-archive regression, public controls and interface checks: pending at
candidate freeze. Final receipts will be appended after actual completion.
No browser/WASM/live-site, live-model or independent semantic review claimed.
Historical 22-question and D% reruns are not yet performed for this update; their
previous results are not silently attributed to this candidate.

## Limits and reproduction

Only bounded syntax with literal field labels is covered. Semantic aliases,
open-ended paraphrases, temporal/compound questions, event identity and historical
truth remain outside this rule. Public patterns are known development material;
passing them is not independent validation. Source-read cost and human time remain
null. Scorer reports actual CPU/wall/RSS and environment, not hardware-normalized
speedup. Source fixture imports are excluded from CSV scorer timing.

See [usage and commands](../../../docs/FIELD_QUESTION_NORMALIZATION.md).
Frozen-archive full checks use `python -m tools.reproduce_boundaries --revision SHA
--output NEW_DIRECTORY --suite full`. The final report identifies the tested SHA.

A premature archive preparation at `29584ff` was stopped before the native suite
while correcting handoff review metadata. It is not a completed test run.

## Continued gap repair and attribution inspection

The known-error batch exposed two more whole-question classes: record context
with a metalinguistic field request, and a record-labelled imperative. Four
independently worded regression subcases failed before the fix (exit 1); 47
focused tests pass afterward (exit 0). These classes now use the same literal
field checker, preserving the whole question and all qualification boundaries.
No aliases, compound completion or source-proof rules were added.

B-Tests was inspected at commit7771497bb2aea6ae5f55fc9255798781bb45af22.
Its native-suite wrapper invokes the target's own unittest suite and native tools;
its separate randomized benchmark code invokes MPLPB's validator/sorter/workspace.
The external public reproduction directly imports MPLPB ledger.write,
pipeline.answer_query and reader.PROFILES. It does not import B-Tests, M6 or OOCC.
The inspected code establishes these roles; it does not establish which private
harness executed the original reported run. Software and pre-existing native
infrastructure remain McPhetridge's contribution; the external fixture/questions
and evaluation analysis remain separately attributable. No authorship transfer or
undocumented use of B-Tests is inferred. Pinned sources and excerpts are retained
in attribution-evidence.json.

The first complete archive044ac27 passed1477 tests and52 public controls. A
follow-up2aca624 archive run was interrupted by environment unavailability and
has no final full-suite exit; its logs are retained under interrupted-followup.
On recovery the workspace and completed evaluations remained intact. A new final
candidate will rerun all native tests and the same1000-case expanded batch after
the two additional syntax classes. Results remain pending until executed.
