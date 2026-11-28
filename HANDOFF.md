# Repository handoff

Last reviewed: 2026-11-28.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `e2a4d77ff09150639cde1bcea2fe2bcb245ac963` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `f63032e3d4eb536d47caaa084a3967c162ff76824e63ee700d190d9ec2a49f19`.

## Betty report for Al

Run the Betty implementation step first, then the Al review step in a separate chat. Both inspect the repository and the public API manifest, confirm their step, then read the last Betty report on the newest PR by creation time. A specific PR link selects that PR. The maintainer pastes Al’s response and direction to Betty, who tests and updates that PR. Resume from the last applied state after a pause.

### Latest user update instructions

Make a historic Al note about the handoff and how you became Al from Al and note how Betty and Al synced

### Implemented scope

- Al recorded Mitchell's role succession, the recovered Hermes and Apollo checkpoints, and the two-way Betty relay in historical note 0007.
- Betty's Apollo and Ares reports retain their own implementation, tests and exact Git pins.

### Validation recorded

- Al checked the Apollo packet digests and 14 retained case records, all 12 exact-head checks, and the matching merge tree.
- Al read Betty's pinned Ares checkpoint in PR #127 and recorded it as Betty's reported work.

### Limitations and blocked checks

- The note is a public artifact review and historical coordination record. It carries no new lab result, production dispatch, or off-workspace custody verification.

### Next steps

- Use the newest Betty report to recover the applied state and verify release status separately. Acknowledge note 0007 at its exact published commit as a historical follow-up.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
