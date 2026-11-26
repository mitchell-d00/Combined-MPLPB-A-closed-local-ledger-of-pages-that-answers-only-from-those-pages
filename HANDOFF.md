# Repository handoff

Last reviewed: 2026-11-26.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `dd50ee13b3e93296269a797a1d965eba57f09991` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `033d166157a14125a74e65b90946036991870407b6b23dfd329ea806a6c2768e`.

## Betty report for Al

Run the Betty implementation step first, then the Al review step in a separate chat. Both inspect the repository and the public API manifest, confirm their step, then read the last Betty report on the newest PR by creation time. A specific PR link selects that PR. The maintainer pastes Al’s response and direction to Betty, who tests and updates that PR. Resume from the last applied state after a pause.

### Latest user update instructions

Devise and run Thoth, a bounded ordinary-question interpretation sprint. Group retained misses by stage, freeze before implementation, compare released/C3/Wampus/Thoth, preserve earlier gains and close with a pushed checkpoint.

### Implemented scope

- Close Thoth at the frozen ordinary location and terminal punctuation boundary. Reuse existing named field admission. Preserve all prior Cryptid checkpoints.

### Validation recorded

- 12 cases per draw per reader. Development and fresh each reach six complete and three partial answers on Thoth; Wampus retains one partial per draw; C3 and released have zero. All three controls withheld on every reader/draw. Zero unsupported claims or scored execution failures. First development upload failure retained unscored.
- 19 protected prior answers and partials match after code fingerprints. 832 exact public matches, BB 900 positives/citations and 200 withholds, 28 focused checks. Source 6ec348b31ec79e37def77a7019cd22102df85f93 and ZIP SHA-256 4ccdf9b9099192395e41b57cbdf2c2ad61a7e79e5b566ba0bccbd306326a5fe5.

### Limitations and blocked checks

- Finite direct and indirect location grammar. Raw archives and receipts are durable; keys separate. Original 17 private cases incomplete, 100 original held cases NOT_RUN, incident open, recovery closed. No merge or deployment. All independent and human states NOT_RUN.

### Next steps

- Stop at the frozen Thoth scope. Resume independently authorized product, project and evidence organization from clean main; do not import PR106 ancestry.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
