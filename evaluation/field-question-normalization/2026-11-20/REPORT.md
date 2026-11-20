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

## Final measured candidate

Frozen implementation9b5ff0c220780875359a74918b3ad4dd50bf4d89, archive
SHA256d11a24e93f1e471dd3b7ce09bed5a39c10b7127cc7b7f5178478473d678edc61:
1482 complete Python tests passed (exit0),52 public controls passed (exit0),
zero observed false-supported bridges. Final UI script, JS API, transport and
crawler checks each exited0. CLI support exited0; past-qualified and external
requests each exited3 as expected. No actual browser/WASM/deployment pass claimed.
Final raw receipts are under final-software/, final-interfaces/ and final-cli/.

Final unchanged public1100-probe replay retains150 canonical and750 paraphrase
supports,200 refusals. Separate final900-question CSV scoring matches all900
field values, no incorrect supported values or errors. Independent readback
verified900 exact eligible citations at the recorded check time; script and
receipt are retained. Run the citation script with PYTHONPATH set to the selected
source checkout; direct invocation without that path first raised ImportError,
an invocation setup error rather than an engine result. Exact script command:

```sh
PYTHONPATH=. python evaluation/field-question-normalization/2026-11-20/verify_citations.py --cases CASES.jsonl --fixtures FIXTURE_ROOT --output NEW_RECEIPT.json
```

The final22-original replay preserves every answer contract except code hashes,
not just outcome totals:3 complete,2 partial,3 conflict,14 abstain. This is no
new historical gain. Full comparison and original packets are retained.

The same expanded1000-case replay improves156 to168/420 key-matched complete
answers,264 to252 over-refusals,580/580 refusals in both runs,zero lost answers
or false support. Twelve gains correspond to the two general new syntax classes.
Sources, questions, key/dice seals and execution/admission budgets are unchanged.
Independent human/unseen evaluation and historical semantic accuracy remain
NOT RUN/null. Expanded residual family failures are retained, not relabelled.

The user-supplied ZIP matches the downloaded archive exactly:60 members,59
manifest-listed files checked. No M6 implementation is included. The response
paper makes this limitation and code/test/evaluator attribution explicit; it
cannot establish an undocumented private execution stack.

[Response paper, all three formats](../../../docs/research/field-question-normalization/README.md).
