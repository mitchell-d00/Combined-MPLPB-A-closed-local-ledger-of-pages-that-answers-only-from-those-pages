# Repository handoff

Last reviewed: 2026-11-02.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `6687c6b86984588d852b5195b4d3b5762a99158c` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `b6180a465d83ebfad88c76f2f674aba56cbf2ba7942f7a4be59fec6cda5e15b0`.

## Latest user update instructions

Check and make sure the repo is all up to date all results have the tests and all documentation is today except historical

## Implemented scope

- Review current documentation against main c0eb212b51c41a96e361ae0ceb680a0a5df0d55f; correct stale current-status, pottery proxy and publication claims without changing source-ledger or answer-engine semantics.
- Add explicit current/historical/vendor document inventory with byte pins for preserved material, a result-to-test/reproduction index covering every evaluation family, regression tests and CI gates for both repository and extracted-ZIP paths.
- Keep generated system descriptions and repository-owned handoffs consistent; record explicit review dates without automatically advancing them at build time.

## Validation recorded

- Baseline PR #29 published regression passed 828 Python tests in 451.954 seconds; all four PR workflows succeeded.
- Baseline main c0eb212 Pages build, deploy and postdeployment Chromium smoke succeeded in run 41495283409. This is prior-revision deployment evidence, not this update.
- Current update: 15 documentation, handoff and generated-system-guide tests passed in 8.572 seconds; infrastructure synchronization passed. Replayed all 372 reference stage/case outputs with matching answers, exact evidence and metrics (engine pins unchanged). Compared 1,264 protected baseline files byte-for-byte with no changes; documentation inventory and all 22 result/test families passed. Frozen source archive of 2649f7e passes the same 15 focused tests, documentation inventory, infrastructure and handoff checks from extracted bytes; see evaluation/documentation-audit/extracted-zip.json. At handoff freeze, final publication outcomes must be inspected in PR #30 and its exact-head Actions runs; this record certifies only the checks actually listed.
- Initial PR #30 browser build rejected an edited resource README under the existing byte verifier. Restored the exact original file, classified it as preserved vendor material, and retained the failure/correction record without relaxing integrity checks.

## Limitations and blocked checks

- Documentation review dates are not new experiment dates, independent human validation or certification of old results.
- The 73/73 reference result is authored lab-only corpus growth; pottery 12/59 is a document-identity proxy with a separate limited semantic review. Historical wiki inputs remain insufficient for scoring.
- No fresh live assisted-model quality, independent collection-builder or human-usability validation is claimed.

## Next steps

- Local focused checks, reference replay, protected-history comparison and frozen-archive checks are complete; inspect their retained outputs under evaluation/documentation-audit/.
- Publish through a PR, require archive-first/regression/handoff/infrastructure checks, then merge and inspect separate Pages deployment evidence.
- For the next update, replace this record with the latest instructions, maintain the documentation/result indexes, stage intended files and regenerate/check the handoff.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
