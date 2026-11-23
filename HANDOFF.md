# Repository handoff

Last reviewed: 2026-11-23.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `0cedff517fcd96e039729df990268c244b3feade` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `4e26e0153a404394ec855ff91725b9d2c777bfe69424a2c498faa96aa4c6c991`.

## Latest user update instructions

Run it note it test it then push it all to main and merge

## Implemented scope

- Run and document a deterministic proposal, approval, WorkStore dispatch, and report readback experiment.
- Carry the previously committed documentary-language rule and installed-wheel demo in the same pull request.

## Validation recorded

- The local governance demo wrote a cited report and returned its matching receipt and artifact hash.
- The governance controls and related local regressions passed all 64 tests.
- The earlier two-wheel comparison reproduced both wheel hashes and all 40 case responses per revision.
- The extracted candidate source subset passed all 10 governance controls and reproduced the cited report and matching receipt.

## Limitations and blocked checks

- The governance experiment uses scripted proposals, one local adapter, and a trusted host with in-memory approval. It has no external effects or independent isolation validation.

## Next steps

- Evaluate another operation with a separately reviewed policy and independently verifiable effect.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
