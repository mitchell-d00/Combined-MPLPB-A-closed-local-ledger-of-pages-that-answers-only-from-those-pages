# Repository handoff

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `1fc908bdead1eb326427a84d8a0d7175a89fb9dd` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `0970a2ef85c0d92aebd44e1d8d83214720e23d0b64c791c8623b5c5da4d19d70`.

## Latest user update instructions

Push the tests too how you got the 73/73 and include it all

Status follow-up: Report.

## Implemented scope

- Publish the complete 73-positive/20-negative authored reference evidence: existing runner/tests/frozen catalog and probes, all four generated sealed snapshots, all 372 per-case outcomes, CSV, checksums and reproduction guide.
- Preserve original questions, labels, pre-amendment expectations and amendment history; do not alter engine semantics or load unratified lab facts into default collections.
- Add an offline replay verifier, integrity tests for changed inputs/pages/CSV and omitted material, and run that verifier in normal and extracted-ZIP CI.

## Validation recorded

- Reproduced at source revision 1fc908bdead1eb326427a84d8a0d7175a89fb9dd: 0/73, 23/73, 48/73, 73/73 as fact pages are added. All 20 controls refuse in every stage; no observed wrong returns or ambiguities within this fixture.
- Seven existing reference corpus tests passed in 118.562 seconds; the committed snapshots replayed all 372 cases with matching answers, quotes, record hashes and metrics.
- Four evidence integrity tests passed; infrastructure synchronization and handoff tests passed. This is data/docs/CI tooling, with no reader-engine changes.
- Prior PR #28 is merged; its main Pages build and postdeployment browser workflow completed successfully (Actions run 41483418218). This does not verify the present unpublished update.
- Publication and the new candidate GitHub checks remain pending; the handoff records actual known results, not promised CI outcomes.

## Limitations and blocked checks

- The 73/73 result is authored finite-grammar lab-profile acceptance data, not independent human validation or general English accuracy.
- Only local source declarations, record seals and lineage are checked. Upstream publisher bytes and real-world truth are not independently verified; all facts remain machine-derived and unratified.
- The source collection grows across stages; the engine does not learn answers. Early refusals are appropriate when the source pages are absent.
- Historical snapshots and original gold amendments are preserved. Further engine changes should produce a separate comparison rather than silently overwriting this run.

## Next steps

- Read evaluation/reference-corpus-reproduction/README.md; run python -m unittest tests.test_reference_corpus -v and python -m tools.verify_reference_evidence.
- Build a fresh independent output with python -m tools.build_reference_corpus --output NEW_EMPTY_DIRECTORY; inspect all per-case quotations and lab-only eligibility.
- Wait for the present candidate archive-first/regression/handoff checks and merge it into main; do not claim deployment verification before its postdeploy workflow finishes.
- For future updates, replace this record with the latest user instruction and actual results, stage intended files and rebuild/check the repository handoff.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
