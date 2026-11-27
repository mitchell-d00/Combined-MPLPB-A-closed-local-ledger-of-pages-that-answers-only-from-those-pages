# Repository handoff

Last reviewed: 2026-11-27.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `df45d400d9d5a65e0019464f7893267cc4cc22b7` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `a7b748149b8dfb29ff89f739ef6441b4a80d0cc983c290f2d603b7bd2b1db675`.

## Betty report for Al

Run the Betty implementation step first, then the Al review step in a separate chat. Both inspect the repository and the public API manifest, confirm their step, then read the last Betty report on the newest PR by creation time. A specific PR link selects that PR. The maintainer pastes Al’s response and direction to Betty, who tests and updates that PR. Resume from the last applied state after a pause.

### Latest user update instructions

Expand the current assignment into one bounded three-set Egyptian-gods batch. Preserve any Seshat work already completed. Freeze Seshat attribution, Anubis negation and scope, and Horus conditions and modality together. Compare the released and pinned candidate readers and close after the frozen evaluation; release only if the recorded gates pass.

### Implemented scope

- Freeze six development and six fresh cases per set, each with three supported targets and three contrasts. Use the unchanged Cryptid v5 isolation runner.

### Validation recorded

- Remote main is a442c8f0. No Seshat branch or worktree was found. The initial stage diagnosis and all six freezes precede changes to the reader.

### Limitations and blocked checks

- Fresh packets and scoring keys stay in separate local custody. Preparation and scoring are same-operator. Independent/human measures NOT_RUN. Original 17 checks incomplete, 100 held cases NOT_RUN and historical publication incident separately OPEN.

### Next steps

- Run the released development baseline, then Seshat, Anubis and Horus in order. Pin the cumulative candidate before releasing fresh operator inputs.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
