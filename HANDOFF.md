# Repository handoff

Last reviewed: 2026-11-28.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `8df0aeeae765fc21eea4bc0020539ab79f20c74c` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `6060e5579dfef145f3e40e8413263f47672dca8c784e1cdcfe2523b9c83697bf`.

## Betty report for Al

Run the Betty implementation step first, then the Al review step in a separate chat. Both inspect the repository and the public API manifest, confirm their step, then read the last Betty report on the newest PR by creation time. A specific PR link selects that PR. The maintainer pastes Al’s response and direction to Betty, who tests and updates that PR. Resume from the last applied state after a pause.

### Latest user update instructions

Al should reconcile it with Betty’s active work and record any resulting assignment through the established notes workflow.

### Implemented scope

- Al reviewed the optional sorter and classing paths, direct native Ask, the Heka Git lab, and Betty's later native prerequisite result in note 0012.

### Validation recorded

- Inspected implementation entry points, Gremlin and existing guides, and verified main and Betty's reports for PRs #130 and #131.

### Limitations and blocked checks

- This is a public source and evidence review. Original PR #130 effect and fresh stages remain NOT_RUN. No new native or integrated experiment ran.

### Next steps

- Propose a small architecture clarification in the package guide. Treat any new integration experiment as separately frozen work.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
