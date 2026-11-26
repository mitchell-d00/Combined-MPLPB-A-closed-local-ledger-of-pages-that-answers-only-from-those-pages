# Repository handoff

Last reviewed: 2026-11-26.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `575ce6b7b62b7ee5240654b23c638c6653eea4f7` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `e5693bbea83c63fe940195891ac5c7a9484de581abc6d85c18b64b04c64f9123`.

## Betty report for Al

Run the Betty implementation step first, then the Al review step in a separate chat. Both inspect the repository and the public API manifest, confirm their step, then read the last Betty report on the newest PR by creation time. A specific PR link selects that PR. The maintainer pastes Al’s response and direction to Betty, who tests and updates that PR. Resume from the last applied state after a pause.

### Latest user update instructions

Devise and run Thoth, a bounded ordinary-question interpretation sprint. Group retained misses by stage, freeze before implementation, compare released/C3/Wampus/Thoth, preserve earlier gains and close with a pushed checkpoint.

### Implemented scope

- Register Egyptian-gods / Thoth, freeze 12 development and 12 fresh cases, and preserve separate custody. Wampus and Bunyip evidence remain retained.

### Validation recorded

- Scope, registries and both key hashes precede implementation. Fresh inputs remain held.

### Limitations and blocked checks

- Terminal-period imperative questions still miss. Same-operator keys remain separate; no independent blinding. Original 17 private and 100 held cases unchanged. Retired recovery closed, Git-history incident open, no release, merge or deployment. All independent and human NOT_RUN labels retained.

### Next steps

- Implement only the named request interpretation and run the four pinned readers on the frozen development packet.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
