# Repository handoff

Last reviewed: 2026-11-28.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `8357a0ec3f67e398cbed552bf4f627489fa3eaaa` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `b77339a889cb50226ed7334f5f4c5686dc8ab36cc12d4e8e975b501151f3021b`.

## Betty report for Al

Run the Betty implementation step first, then the Al review step in a separate chat. Both inspect the repository and the public API manifest, confirm their step, then read the last Betty report on the newest PR by creation time. A specific PR link selects that PR. The maintainer pastes Al’s response and direction to Betty, who tests and updates that PR. Resume from the last applied state after a pause.

### Latest user update instructions

Run it

### Implemented scope

- Applied Al note 0004 at 5cd0b2c042a6c6edeec564f55392a614b0b5a8fb. Heka disposition retains original grades. Athena, Hermes and Hephaestus form a separate lab checkpoint.

### Validation recorded

- Greek freeze 4a327ee771e8288e28aff05436229891e9c7cfe3; unchanged candidate selection 8357a0ec3f67e398cbed552bf4f627489fa3eaaa, before the first fresh run. Development 15/15, fresh 16/16 exact phases.
- Each draw observed three intended updates, two durably recorded completions, one failed CAS preserving the competitor, and one indeterminate interruption. Hermes and the blocked cases made no writer attempts.
- Regenerated both public operator packets byte-for-byte and verified both key seals and private archive readback.

### Limitations and blocked checks

- Shared operator and workspace custody. Authenticated host identity, external receipt provenance and production dispatch are outside the test. Prior evidence stays pinned to original bytes.

### Next steps

- Verify the exact lab evidence head and publication. Reuse the exposed draws only as consumed preservation.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
