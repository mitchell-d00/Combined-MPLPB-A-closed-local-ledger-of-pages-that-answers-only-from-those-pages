# Repository handoff

Last reviewed: 2026-11-19.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `c7dd333f06b4f0af739d36672b2f98727be5a5b9` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `1d151251b62ae1c594dd3fb573d4c8ad5f5fe7565f5fdd0935828c3260d823e8`.

## Latest user update instructions

K rn a d100 test on it local and then merge if it passes this repo has the tests im talking about https://github.com/mitchell-d00/B-Tests

## Implemented scope

- Inspect and pin the linked B-Tests d100 protocol;run its unmodified local100-case test against clean MPLPBc7dd333.
- Check the new exploration view separately on all100 unchanged packets,without passing the scoring key to runtime.
- Preserve seed,inputs,rolls,receipts and results;push a reviewable branch,require exact-head release CI,then merge to main if passed.

## Validation recorded

- B-Tests64b646ee89ea819f59f39f0eecced71ee7ef24c8 harness:123 unit tests passed.
- Fresh seed13814892761879707678 native100/100 cases,25/25 users,100 workspace replays passed;exit0.
- Exploration companion100/100 cases,25/25 users passed;source/node/label identity,native isolation,profile restrictions,budgets and unchanged ledgers/packets verified;exit0.
- Existing final implementationf856205 full1379 tests and52 public controls retained;d100 executionc7dd333 is evidence/docs-only descendant with identical runtime.

## Limitations and blocked checks

- D100 uses fictional source records with real topic metadata;not historical accuracy or model-quality measurement.Model calls0.
- Native d100 and companion runtime costs differ;upstream native CPU/wall unmeasured,null.
- Exact final-head CI,main merge and postdeployment validation pending;local success alone is not publication.

## Next steps

- Push tested feature branch and open a main PR with concrete d100 evidence.
- Wait for successful archived-source,regression and handoff checks on exact final head;investigate failures before merging.
- Merge with expected head SHA once gates pass,then verify main/deployment and record publication receipt.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
