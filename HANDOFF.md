# Repository handoff

Last reviewed: 2026-11-20.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `9b5ff0c220780875359a74918b3ad4dd50bf4d89` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `9ecc6b0747d9a7f1ba158da51ad170dff52794ee8bb7c456fba3475d79d8028d`.

## Latest user update instructions

M6 sorry 8 meant it’s not shared or anything be explicit the package don’t include i5

## Implemented scope

- General whole-question literal field-request syntax in the existing exact parser; additive inspectable normalization; no core authority changes.
- Unchanged public reproduction preserved with baseline at published bbf6690 and pre-change 3483b1a; new tests and exact CSV scoring.
- Separate follow-up branch feature/field-question-normalization based on unmerged PR56; no merge performed.
- Additional instruction: write a response paper to the 19 November public evaluation after tests complete, citing the original paper/package members and reproducible source tests.
- Implement optional expanded D% generator/scorer around existing isolated worker;48 semantic families;1000cases frozen; all dice/keys hash-pinned in separate custody.
- User supplied another parser-only verification account; distinguish that from our completed full engine replay. Do not manufacture independent semantic review.
- Inspect B-Tests per preceding instruction; record exact software/test/harness attribution, distinguishing unsupported M6/OOCC claims.
- Address general additional record-context and labelled-imperative question structures exposed by frozen stress batch, not individual fixtures.
- Harden post-run field scorer against matching text without citations; source packets/keys/dice unchanged, initial/hardened scores identical.
- Completed B-Tests inspection at7771497 and explicit attribution section in response paper; no undocumented B-Tests/M6/OOCC execution claimed.
- User attachment is byte-identical to the downloaded public ZIP:60 files; no M6 implementation supplied. Paper explicitly states M6 was not shared in that package or available for inspection/execution.
- Rendered response paper by Mitchell D. McPhetridge in Markdown, TXT and8-page PDF with hash manifest, citing the publication package, all members via inventory, own code/tests and remaining gaps.

## Validation recorded

- Completed archive044ac27:1477 Python tests and52 public controls passed. Public unchanged1100 probes:900 supported exact field-value matches,200 refusals.
- Original frozen1240D%:200/600 matched completes,640/640 expected refusals,no execution failures.
- Original22historical replay retains3 complete,2 partial,3 conflicts,14 abstentions.
- Expanded1000baseline:156/420 matched complete,264 over-refusals,580/580 refusals,zero failed executions or unscored supported.
- Scorer missing-citation mutation failed before hardening; all5 generator/scorer tests pass afterward;1000 real scores unchanged.
- Two more syntax classes: four independent-vocabulary subcases failed before repair; all47 focused tests passed after repair.
- Follow-up full2aca624 suite interrupted by environment unavailability; no final exit code, no pass inferred. Retained partial logs and source ZIP.
- Final frozen9b5ff0c:1482 full Python tests,52 public controls and boundary subset passed, all exit0. Native packages/tools/tests unchanged since final freeze.
- Final unchanged public replay900/900 supported with exact field values;200/200 negative refusals;900 citations independently reread for exact source anchors and current default-profile eligibility.
- Final expanded1000 replay:168/420 key-matched complete,252 over-refusals,580/580 refusals,no failed/unscored executions. Twelve gains,no lost complete or new false support; identical packet/key/dice seals.
- Final22 original contracts identical except code hashes; source/question seals preserved. Outcomes3 complete,2 partial,3 conflict,14 abstain.
- Final UI script, JS API, transport and crawler checks each exit0; CLI accepted literal form exit0 and refused time-qualified/external variants exit3 as expected.
- PDF read back successfully:8 pages, correct title/author, M6-not-supplied statement present. Paper-only software tests not added.

## Limitations and blocked checks

- 252 expanded developer-key answerable cases remain incomplete:12 families of21 each, including aliases/compound requests and historical-prose composition.
- No independent semantic/human review, unseen evaluation, M6 implementation inspection or live-model run. Historical semantic accuracy remains null.
- Actual browser/WASM/deployed-site checks not rerun locally. Final native tests apply to9b5ff0c; subsequent edits are evidence/docs and an executed read-only citation audit script.
- This feature branch depends on unmergedPR56. No new merge or deployment authorized/performed.

## Next steps

- Audit final documentation/handoff and verify native source/test parity with9b5ff0c; commit findings/paper.
- Publish reviewable follow-up PR against PR56 feature branch with full failures/results and exact source pins. Do not merge.
- Future proof work should target general remaining families, preserve frozen inputs/negative controls, and report both missed answers and false support. Independent review remains NOT RUN.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
