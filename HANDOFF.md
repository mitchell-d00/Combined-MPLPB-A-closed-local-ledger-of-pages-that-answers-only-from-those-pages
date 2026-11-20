# Repository handoff

Last reviewed: 2026-11-20.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `2aca6243e49e5b81b2cc3b948d21e373b8f16ea2` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `805d603a0189efb9e43ab20960fe755a1910d2e43542cc03330a1851a9e04f43`.

## Latest user update instructions

And address the gaps you find n MPLPB as you find them

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

## Validation recorded

- Completed archive044ac27:1477 Python tests and52 public controls passed. Public unchanged1100 probes:900 supported exact field-value matches,200 refusals.
- Original frozen1240D%:200/600 matched completes,640/640 expected refusals,no execution failures.
- Original22historical replay retains3 complete,2 partial,3 conflicts,14 abstentions.
- Expanded1000baseline:156/420 matched complete,264 over-refusals,580/580 refusals,zero failed executions or unscored supported.
- Scorer missing-citation mutation failed before hardening; all5 generator/scorer tests pass afterward;1000 real scores unchanged.
- Two more syntax classes: four independent-vocabulary subcases failed before repair; all47 focused tests passed after repair.
- Follow-up full2aca624 suite interrupted by environment unavailability; no final exit code, no pass inferred. Retained partial logs and source ZIP.

## Limitations and blocked checks

- Literal field aliases and compound requests remain unsupported; expanded developer-key labels are not independent historical judgments.
- Independent semantic/human evaluation NOT RUN; no documented M6 or OOCC runtime execution in public reproducer.
- Final full suite and1000-case replay after latest syntax changes pending; first full pass applies to044ac27 only.
- Browser/WASM/deployed-site checks not performed for this candidate; no merge or deployment.

## Next steps

- Freeze current engine/scorer and run complete archive tests plus unchanged expanded1000 cases. Preserve all failures.
- Finalize response paper in MD/TXT/PDF only after actual native results; include attribution section and public package member inventory.
- Update README/results/docs/handoff, commit complete evidence. Do not merge without authorization and exact-head release gates.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
