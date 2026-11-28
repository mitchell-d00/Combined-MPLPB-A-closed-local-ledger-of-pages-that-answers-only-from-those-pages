# Repository handoff

Last reviewed: 2026-11-28.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `f761a82f1dcd786e56ed0b5ad4d744fcc72b687b` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `5a899e4c3d412f2bace7f494bf85665b08a17c4288c379f067631b77b9744f05`.

## Betty report for Al

Run the Betty implementation step first, then the Al review step in a separate chat. Both inspect the repository and the public API manifest, confirm their step, then read the last Betty report on the newest PR by creation time. A specific PR link selects that PR. The maintainer pastes Al’s response and direction to Betty, who tests and updates that PR. Resume from the last applied state after a pause.

### Latest user update instructions

Run it

### Implemented scope

- Read note 0004 at 5cd0b2c042a6c6edeec564f55392a614b0b5a8fb. Applied Heka withdrawal disposition. Greek sprint remains a separate frozen checkpoint.

### Validation recorded

- Released reader reproduced both eligibility abstentions. Only D-04 proof and D-07 recheck diagnostic differ from key. Both made zero Git attempts. Original 10/11, 12/14 and 13/13 intact.
- Verified both key seals and byte-checked the authoring script and keys in a separate private local archive. Verified applicable main rules name archive-first and regression and no Heka perfect-score gate.

### Limitations and blocked checks

- One local workspace failure domain for private custody. No production dispatch, runtime or controller change.

### Next steps

- Verify this exact Heka head remotely and merge the lab record once required checks pass. Freeze Athena, Hermes and Hephaestus separately.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
