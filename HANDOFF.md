# Repository handoff

Last reviewed: 2026-11-20.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `100805f0f4e96ac95c52150340cd7cf9da4febf7` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `98fc75cdcdf0574d900fe2ebc365b31c58d047503f9e171fadfe6386a5f19a1c`.

## Latest user update instructions

Merge it all once it’s fixed

## Implemented scope

- Latest engineering assignment: inspect and pin all distinct baselines; classify252 misses; begin one general source-grounded field-synonym improvement, preserve original questions and all frozen inputs.
- New branch feature/source-field-aliases based on be6a556; small finite label rules, eligible-body discovery in field-scoped serving views, ambiguity refusal and fresh dependency revalidation; native core unchanged.
- Prepare a new sealed240-case development holdout and a self-contained external replay package with synthetic keys/seals. No independent/human validation fabricated.
- User authorizes merging PR56,PR57 and this iteration after required native/release checks pass. No merge yet.

## Validation recorded

- Before native edits: runtime equal9b5ff0c;46 baseline focused tests passed.
- All252 expanded misses diagnosed by code/output, not assumed retrieval failures.
- New holdout baseline16/64 complete,176/176 refusals; sources/questions/key/dice sealed before implementation.
- New11-test alias suite failed7 subcases before implementation.
- First exact-spelling-priority collision rule rejected by failing control; reconstructed replay ZIP/log retained honestly.
- 62 focused tests passed after ambiguity repair; original unit question current state intentionally moves from unsupported-language assertion to licensed-positive assertion; no frozen label changes.
- PR56 andPR57 exact-head GitHub release checks already successful; do not merge until new iteration evaluation also completes.
- Candidate100805f passed1501 tests/52 public controls and benchmark replays, but rejected after3 later semantic modifier-inversion counterexamples. Full evidence retained; no benchmark pass treated as semantic certification.
- Typed-role v2 requires an approved documentary noun head, not arbitrary adjective/name inversion;66 focused controls pass.

## Limitations and blocked checks

- Native alias discovery adds fresh reads; caps inspected records/text/declarations, not total authority I/O.
- Finite lexical rules only, no arbitrary synonym inference; temporal roles and geographic state remain distinct.
- Independent blind/human evaluation NOT RUN. New holdout is developer-authored, not context-blind.
- Full candidate regressions,900/1240/1000/22 replays and updated240 holdout pending.
- Final v2 native/evaluation/release checks pending;100805f intermediate gains are not yet accepted final results.

## Next steps

- Freeze candidate and run complete archive tests plus all unchanged evaluations. Preserve every failed/partial result.
- After actual results, finish report and public synthetic replay bundle, update docs/README/handoff, push PR.
- Merge dependent PRs in order only after exact-head required CI succeeds, then verify deployed live checks.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
