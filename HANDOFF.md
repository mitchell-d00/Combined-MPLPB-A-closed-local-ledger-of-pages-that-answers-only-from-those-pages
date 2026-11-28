# Repository handoff

Last reviewed: 2026-11-28.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `805f8263f54fa8069f02d48e898705411ccdedf0` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `dcdf3f4c31fd0c8762e6ff9b2a9bfa1de7eaaf2fdfaec17ce0ab67118cdd0f1d`.

## Betty report for Al

Run the Betty implementation step first, then the Al review step in a separate chat. Both inspect the repository and the public API manifest, confirm their step, then read the last Betty report on the newest PR by creation time. A specific PR link selects that PR. The maintainer pastes Al’s response and direction to Betty, who tests and updates that PR. Resume from the last applied state after a pause.

### Latest user update instructions

Al; prepare Betty’s next bounded sprint to clear the native prerequisite found in PR #130.

### Implemented scope

- Al recorded the observed instruction/date dispatch and composition gap and proposed a reader-only sprint in note 0011.

### Validation recorded

- Verified current main and its Pages run, PR #130 head and first report, note 0010, the native route source, and request-recognizer output on the published D01/D02 question.

### Limitations and blocked checks

- No candidate reader or new study ran. The original scores, native prerequisite hold, and fresh and effect NOT_RUN labels retain their original scope.

### Next steps

- Betty acknowledges note 0011 and freezes a separate native reader study before making changes. Keep the Git-effect path disconnected.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
