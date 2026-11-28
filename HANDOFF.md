# Repository handoff

Last reviewed: 2026-11-28.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `dcdcfd93fc4a3017f44b0d976ae7de2aad9f6986` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `3f080777aa99c50ce756630dde7927488a782d9276dd1ae3773288562b9871f3`.

## Betty report for Al

Run the Betty implementation step first, then the Al review step in a separate chat. Both inspect the repository and the public API manifest, confirm their step, then read the last Betty report on the newest PR by creation time. A specific PR link selects that PR. The maintainer pastes Al’s response and direction to Betty, who tests and updates that PR. Resume from the last applied state after a pause.

### Latest user update instructions

Al; formalize Ariadne’s Thread and use its first application for Betty’s FRUS subject-line identification sprint.

### Implemented scope

- Al documented Ariadne's Thread and indexed ARIADNE-01 as planned reader work in Gremlin.

### Validation recorded

- Verified main, active drafts, HANDOFF, the prior note, Gremlin and the current FRUS evidence pins.

### Limitations and blocked checks

- Design and coordination only. No ARIADNE-01 implementation or experiment result has been recorded in this note.

### Next steps

- Betty acknowledges notes 0014 and 0015, reconciles her working branch, and applies the frozen development, preservation and fresh gates.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
