# Repository handoff

Last reviewed: 2026-11-28.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `08e2d72d53c73d3dfde94f07424f718dd9d35d2b` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `d4347fadc291e2ed2e69d141420fb259d50e75d5cc80cea9b8850d2d4228b5aa`.

## Betty report for Al

Run the Betty implementation step first, then the Al review step in a separate chat. Both inspect the repository and the public API manifest, confirm their step, then read the last Betty report on the newest PR by creation time. A specific PR link selects that PR. The maintainer pastes Al’s response and direction to Betty, who tests and updates that PR. Resume from the last applied state after a pause.

### Latest user update instructions

Al; prioritize MPLPB’s demonstrated weaknesses and give Betty one bounded next sprint.

### Implemented scope

- Al recorded one native subject-line identification sprint, with first-use, external assessment and Chronos on separate tracks.

### Validation recorded

- Reviewed current main and postmerge Pages, the FRUS first scores and both diagnostic trace archives, the native response rule, browser startup and recruitment protocols.

### Limitations and blocked checks

- Design and source review only. No new reader, browser or participant run. Production dispatch remains inactive.

### Next steps

- Betty acknowledges note 0014 and freezes a separate FRUS reader repair. Preserve original scores and #135's tested response and withdrawn-target outcomes.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
