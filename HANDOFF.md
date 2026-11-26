# Repository handoff

Last reviewed: 2026-11-26.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `43eca170d8bcd903f6c2f92e74fd7950540a7f81` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `022eca016e6b69b26491637e87e4383ece623923b66db8ca527c905e2e829d48`.

## Betty report for Al

Run the Betty implementation step first, then the Al review step in a separate chat. Both inspect the repository and the public API manifest, confirm their step, then read the last Betty report on the newest PR by creation time. A specific PR link selects that PR. The maintainer pastes Al’s response and direction to Betty, who tests and updates that PR. Resume from the last applied state after a pause.

### Latest user update instructions

Devise and run Thoth, a bounded ordinary-question interpretation sprint. Group retained misses by stage, freeze before implementation, compare released/C3/Wampus/Thoth, preserve earlier gains and close with a pushed checkpoint.

### Implemented scope

- Bind one terminal mark and ordinary direct/indirect location forms to the existing named-field admission, preserving the original question for eligibility. Existing compound proof and cited partial composition are reused.

### Validation recorded

- 28 existing Bunyip/compound tests passed. Matched parser controls cover negation, attribution, conditions and terminal punctuation.
- BB replay on Thoth retains 900 positive contracts and exact eligible citation checks plus 200 withholds. Start the existing public-only 832 replay.

### Limitations and blocked checks

- Terminal-period imperative questions still miss. Same-operator keys remain separate; no independent blinding. Original 17 private and 100 held cases unchanged. Retired recovery closed, Git-history incident open, no release, merge or deployment. All independent and human NOT_RUN labels retained.

### Next steps

- Pin the candidate runtime and compare the four readers on frozen development. Recheck consumed Wampus and Bunyip.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
