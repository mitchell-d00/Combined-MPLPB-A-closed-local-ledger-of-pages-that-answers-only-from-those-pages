# Repository handoff

Last reviewed: 2026-11-28.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `5092094203a2064db7cdacb21627b4a002ee9270` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `5fa9c95695f2a227052abde8a1a85d5833d6c51e0899b92ddb7f11ccc60899b1`.

## Betty report for Al

Run the Betty implementation step first, then the Al review step in a separate chat. Both inspect the repository and the public API manifest, confirm their step, then read the last Betty report on the newest PR by creation time. A specific PR link selects that PR. The maintainer pastes Al’s response and direction to Betty, who tests and updates that PR. Resume from the last applied state after a pause.

### Latest user update instructions

Al; design Chronos as Gremlin’s cooperating timeline and relationship companion, then give Betty a bounded implementation sprint.

### Implemented scope

- Al recorded the proposed Chronos timelines, stable references, read interfaces, evidence rules and frozen acceptance grid in note 0013.

### Validation recorded

- Reviewed current main, PR #134, Gremlin and result authority, FRUS evidence and existing chronology, source verification and investigation entry points.

### Limitations and blocked checks

- Design only. No Chronos implementation or acceptance test ran. Original experiment results and production dispatch boundaries retain their scope.

### Next steps

- Betty acknowledges note 0013 and freezes Chronos in a separate lab PR, preserving the FRUS diagnostic branch and historical notes.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
