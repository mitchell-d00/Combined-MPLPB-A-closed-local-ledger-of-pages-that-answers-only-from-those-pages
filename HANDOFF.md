# Repository handoff

Last reviewed: 2026-11-26.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `d1363642cdf40b8b02ce2687886c2a8e54a9bf3c` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `f21c0db43d7d31fe48f66424c25d79e37f80c46f7922c2b8aa28bfa05e709bd1`.

## Betty report for Al

Run the Betty implementation step first, then the Al review step in a separate chat. Both inspect the repository and the public API manifest, confirm their step, then read the last Betty report on the newest PR by creation time. A specific PR link selects that PR. The maintainer pastes Al’s response and direction to Betty, who tests and updates that PR. Resume from the last applied state after a pause.

### Latest user update instructions

Devise and run Thoth, a bounded ordinary-question interpretation sprint. Group retained misses by stage, freeze before implementation, compare released/C3/Wampus/Thoth, preserve earlier gains and close with a pushed checkpoint.

### Implemented scope

- Bind one terminal mark and ordinary direct/indirect location forms to the existing named-field admission, preserving the original question for eligibility. Existing compound proof and cited partial composition are reused.

### Validation recorded

- 28 existing Bunyip/compound tests passed. Matched parser controls cover negation, attribution, conditions and terminal punctuation.
- BB replay on Thoth retains 900 positive contracts and exact eligible citation checks plus 200 withholds. Start the existing public-only 832 replay.
- First hosted development execution completed, but incorrect upload path retained only the old public runtime directory. The original artifact and console receipt are retained separately as an unscored infrastructure failure.
- Fresh inputs opened after the pinned candidate ZIP; their bytes match the pre-implementation registry and seal. The development transport retry and fresh once-only comparison use unchanged reader code. The two keys stay in separate custody.

### Limitations and blocked checks

- Terminal-period imperative questions still miss. Same-operator keys remain separate; no independent blinding. Original 17 private and 100 held cases unchanged. Retired recovery closed, Git-history incident open, no release, merge or deployment. All independent and human NOT_RUN labels retained.

### Next steps

- Verify hosted development retry, fresh first results, and public preservation. Close the bounded sprint without repairing from the fresh results.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
