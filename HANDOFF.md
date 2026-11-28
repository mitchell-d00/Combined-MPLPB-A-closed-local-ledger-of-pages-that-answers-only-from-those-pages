# Repository handoff

Last reviewed: 2026-11-28.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `e90226354e509a7f1f3e73ce3845621d11aaf7c4` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `fe1df6d91472a9a21a21d140ca3adea691ff7514f8909acf2fb35b5793945c1e`.

## Betty report for Al

Run the Betty implementation step first, then the Al review step in a separate chat. Both inspect the repository and the public API manifest, confirm their step, then read the last Betty report on the newest PR by creation time. A specific PR link selects that PR. The maintainer pastes Al’s response and direction to Betty, who tests and updates that PR. Resume from the last applied state after a pause.

### Latest user update instructions

Acknowledge note 0011 at 8df0aeeae765fc21eea4bc0020539ab79f20c74c. Recheck main and use 26621affeb487fb096a08acfc5bcdeb335760ad7 as the proposed baseline for a separate reader PR. Keep Git effects disconnected. Freeze independently worded development and fresh packets before changing the reader. Stop at the native result.

### Implemented scope

- Native source-attributed instruction and explicit same-directive date composition. Frozen 15 development and 15 first-fresh cases.

### Validation recorded

- 5/15 baseline, 15/15 candidate development and first fresh. Each candidate draw yielded three complete answers, six checked partials, six expected withholds, and a successful withdrawal reread. All 114 focused preservation tests passed.

### Limitations and blocked checks

- Closed date grammar, same-operator synthetic evaluation, no authenticated event or execution. Original PR #130 fresh and Git effects stay NOT_RUN. External private custody is unverified.

### Next steps

- Verify exact-head archive/software/browser checks and remote bytes. Verify deployment after a qualifying merge. A future Git-effects study requires its own freeze.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
