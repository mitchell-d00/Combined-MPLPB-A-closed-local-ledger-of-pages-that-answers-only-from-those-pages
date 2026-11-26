# Repository handoff

Last reviewed: 2026-11-26.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `d3d34c4e95e79f38e9da524af60c4ae95600d485` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `4943e7f83c5c9969441236ea85d01de583aa396fd8d7ad3fcae3e6891f53a8c6`.

## Betty report for Al

Run the Betty implementation step first, then the Al review step in a separate chat. Both inspect the repository and the public API manifest, confirm their step, then read the last Betty report on the newest PR by creation time. A specific PR link selects that PR. The maintainer pastes Al’s response and direction to Betty, who tests and updates that PR. Resume from the last applied state after a pause.

### Latest user update instructions

Close and preserve Bunyip C3, then complete the bounded Wampus Cat sprint in the existing Cryptid series.

### Implemented scope

- Close Bunyip with unchanged retained evidence. Freeze Wampus Cat, 12 development and 10 fresh synthetic cases, before implementation.

### Validation recorded

- Frozen registry and key hashes prepared before implementation. Fresh materials remain outside public artifacts.

### Limitations and blocked checks

- Original private checks incomplete, original held transfers NOT_RUN, publication incident open. C3 unmerged.

### Next steps

- Implement the shared named-field compound admission and compare the released reader, C3 and Wampus Cat on the same frozen cases.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
