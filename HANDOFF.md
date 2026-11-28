# Repository handoff

Last reviewed: 2026-11-28.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `f836d0fef98f5093f371e2b1dda7fd323895e7c7` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `8ba2e8e47c4e438ea40d2b35f80c422d75d200a10f20f47de047d961ecf0b675`.

## Betty report for Al

Run the Betty implementation step first, then the Al review step in a separate chat. Both inspect the repository and the public API manifest, confirm their step, then read the last Betty report on the newest PR by creation time. A specific PR link selects that PR. The maintainer pastes Al’s response and direction to Betty, who tests and updates that PR. Resume from the last applied state after a pause.

### Latest user update instructions

Finish Apollo-01 Pages verification. Run Ares-01 only under Al note 0006 from the Apollo merge and publish the recoverable checkpoint. Hestia stays deferred.

### Implemented scope

- Applied Al note 0006 at 20885e500faf75b88fa80548aabadd1f991fe76b. Ares baseline e2a4d77ff09150639cde1bcea2fe2bcb245ac963. Shared epoch and two-process ordering remain lab-only.

### Validation recorded

- First development and first fresh each 5/5 with two intended writes and two durable completions. Each draw had three blocked fixtures with zero writer attempts.
- Separate process traces confirm the final shared read as decision point. The post-check revocation preserved the already-admitted effect. Apollo 7/7 and 7/7, controller 42/42 and restart 3/3 plus 6/6 preserved.
- Regenerated both inputs exactly and read back both held grading keys against their frozen seals.

### Limitations and blocked checks

- Same operator and local workspace custody. Separate authority and Git resources, no production dispatch. Hestia remains deferred.

### Next steps

- Verify public byte readback and exact-head checks. Keep Apollo and Ares first results available as consumed preservation.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
