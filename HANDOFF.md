# Repository handoff

Last reviewed: 2026-11-28.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `7b401a4d97b31c4185ce491e096917d1c1d9dc39` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `27f560d303d5434a3638d61a6f0883ff14e3fd98d1bdcf81dad52177328cb7e1`.

## Betty report for Al

Run the Betty implementation step first, then the Al review step in a separate chat. Both inspect the repository and the public API manifest, confirm their step, then read the last Betty report on the newest PR by creation time. A specific PR link selects that PR. The maintainer pastes Al’s response and direction to Betty, who tests and updates that PR. Resume from the last applied state after a pause.

### Latest user update instructions

Run the next bounded FRUS repair and merge it if it qualifies. Recheck main and use draft PR #134 at aee8312b97cab51d6e81ca1d20fa42696c57fbd3 as the pinned diagnostic. Preserve its traces and the original 77-case baseline. Scope the repair to explicit document-to-document response identification. Pair it with the same question after d157 is withdrawn. Keep ranking unchanged. Freeze before editing. Verify Pages after merge and leave Al the freeze, candidate, tested head, merge and deployment pins.

### Implemented scope

- One original short dated memorandum response identification path. Exact current source evidence, target verification and display budget. Rankers and production dispatch unchanged.

### Validation recorded

- Freeze fb915ba3. Initial development 9/12 with retained compound-surname failure. Candidate 7b401a4d development 12/12 and first fresh 5/5. Withdrawn d157 withheld at target verification. 114 focused tests passed. Prior 77 comparison changed only DIRECT-01.

### Limitations and blocked checks

- Same-operator synthetic fresh and local private custody. Two-link, ranking changes, older-runtime comparison, independent assessment and human onboarding remain parked.

### Next steps

- Verify public remote readback and all exact-head checks before merge. Verify Pages and published native runtime after merge. Stop at this warranted narrow repair.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
