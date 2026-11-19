# Repository handoff

Last reviewed: 2026-11-19.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `c10a81bcc519a0208ddcc5762edda8e79ea6f9b8` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `31f0c71332d49e021ddce402647c71527c2e2d17c4e6c10957a08d46e2b9a766`.

## Latest user update instructions

Agreed

## Implemented scope

- User agreed to structured article dossiers that display competing accounts while withholding an unsupported resolution.
- Add bounded read-only article assembly over existing reconstruction reports; retain complete original questions, native checker results and candidate graphs.
- Expose known shared declared ancestry across sections without counting independent witnesses; missing ancestry never proves independence.
- Add CLI, general positive/negative/source-mutation controls, unchanged-original preservation study and usage documentation.
- Prior PR #54 was merged to main as 3a79603e1865f1ef0a1cd1dc72bb656ba5542d8c after all seven reported checks passed. This feature branch starts from its identical PR-head source tree c10a81b.

## Validation recorded

- Baseline focused reconstruction/assertion suites:52 tests passed before implementation.
- New article suite:15 fictional development tests passed, including native contract equality, conflicts, shared ancestry, missing links, restrictions and source invalidation.
- Initial absent-module test failed as expected before implementation; this establishes missing functionality, not a newly discovered native proof defect.
- Full Python suite,52 public controls and unchanged22-original preservation study started; results pending.

## Limitations and blocked checks

- No new historical proof rule, automatic cross-document relationship or historical answer-coverage gain is claimed.
- Independent historical semantics, witness independence, undeclared copying and historical truth remain unestablished.
- Article exports are optimistic inspection snapshots, not atomic filesystem snapshots or permanently eligible evidence.
- This is a native CLI/library addition; browser/deployment integration is not implemented.

## Next steps

- Complete and retain all test/study results, freeze a source candidate and test its extracted archive.
- Record exact outcomes and resource costs; update README/docs/result index and regenerate handoff.
- Publish findings on a feature PR if available; do not merge without a new instruction.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
