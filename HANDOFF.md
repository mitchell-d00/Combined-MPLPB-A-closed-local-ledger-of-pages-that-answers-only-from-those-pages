# Repository handoff

Last reviewed: 2026-11-28.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `5082c5d975ca41a2478ccb25576f3cfdf65b77f0` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `8b10dd981b3e5d01532adec50f6e39c429815c91a86d03d9a1af4a40c3a7394d`.

## Betty report for Al

Run the Betty implementation step first, then the Al review step in a separate chat. Both inspect the repository and the public API manifest, confirm their step, then read the last Betty report on the newest PR by creation time. A specific PR link selects that PR. The maintainer pastes Al’s response and direction to Betty, who tests and updates that PR. Resume from the last applied state after a pause.

### Latest user update instructions

Publish the design and recommendation in the next numbered Al Note.

### Implemented scope

- Al proposed a bounded source-attributed instruction-to-Git trial in note 0010, using the existing Heka effect boundary and distinct native support and synthetic truth scoring.

### Validation recorded

- Al inspected Ares main and verified publication, Betty's newcomer PR checkpoint, the graph and historical review contracts, and the Heka, Apollo, Ares and reservation boundaries.

### Limitations and blocked checks

- Design advice only. Native coverage for the exact proposed mandatory role and date combinations must be established on the frozen baseline. No new lab result or production effect.

### Next steps

- Betty acknowledges note 0010, rechecks main and freezes the separate lab branch inputs, expectations and acceptance criteria before execution.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
