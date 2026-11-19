# Repository handoff

Last reviewed: 2026-11-19.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `c9500e53bbd57e892f87c6fc4968dac0f81cb8b7` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `c7e19e3723e09c977a36861e6c63a92153d3616a3e08e830265ee60481cd14ad`.

## Latest user update instructions

Agreed

## Implemented scope

- User agreed to structured article dossiers that display competing accounts while withholding an unsupported resolution.
- Add bounded read-only article assembly over existing reconstruction reports; retain complete original questions, native checker results and candidate graphs.
- Expose known shared declared ancestry across sections without counting independent witnesses; missing ancestry never proves independence.
- Add CLI, general positive/negative/source-mutation controls, unchanged-original preservation study and usage documentation.
- Prior PR #54 was merged to main as 3a79603e1865f1ef0a1cd1dc72bb656ba5542d8c after all seven reported checks passed. This feature branch starts from its identical PR-head source tree c10a81b.

## Validation recorded

- Baseline52 focused tests passed before implementation.
- Full extracted2c173b3 source:1446 Python tests passed with no failures/skips; native boundaries and52 public controls passed, all exit0.
- 15 focused article controls, CLI example, UI script, JavaScript/native API, transport and fixture-crawler checks passed. No actual browser/WASM rerun.
- Corrected c9500e5 exported-tree original-record study:22/22 complete native contracts preserved;2 complete,2 partial,3 conflicts,15 abstentions;all provenance/immutability/non-promotion guards passed.
- Study wall160.004s,CPU159.696s,peakprocessRSS143921152bytes;source bytes and human review time null.
- First restricted full run failed:1434 tests,3 failures,11 errors,2 skips. Permission errors and sandbox-dependent workflow failures retained; complete authorized archived rerun passed1446.
- Runtime packages and tests identical to2c173b3; core ledger, grammar, checker and all old frozen corpora/evidence unchanged fromc10a81b.
- PR55 opened at https://github.com/mitchell-d00/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages/pull/55 . Final evidence/doc-only commit and exact-head CI inspection remain; no merge performed.

## Limitations and blocked checks

- No new historical proof rule, automatic cross-document relationship or historical answer-coverage gain is claimed.
- Independent historical semantics, witness independence, undeclared copying and historical truth remain unestablished.
- Article exports are optimistic inspection snapshots, not atomic filesystem snapshots or permanently eligible evidence.
- This is a native CLI/library addition; browser/deployment integration is not implemented.

## Next steps

- Push final evidence/docs-only update to PR55 and inspect exact-head CI; do not merge without a new user instruction.
- Next capability milestone: finite checked cross-document connections with exact evidence per link and copied-account/missing-link/conflict negatives; no historical score claim from assembly.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
