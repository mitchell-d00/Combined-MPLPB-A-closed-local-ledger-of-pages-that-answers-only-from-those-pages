# Repository handoff

Last reviewed: 2026-11-28.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `0b83ebe91426af4a0104a82b8ce8a72d6622565f` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `3cdedb57243b1bd80ac4c1134e11014dd163355701b0a898d40357adbb402c79`.

## Betty report for Al

Run the Betty implementation step first, then the Al review step in a separate chat. Both inspect the repository and the public API manifest, confirm their step, then read the last Betty report on the newest PR by creation time. A specific PR link selects that PR. The maintainer pastes Al’s response and direction to Betty, who tests and updates that PR. Resume from the last applied state after a pause.

### Latest user update instructions

Publish your findings and recommendation in the next numbered Al Note under the established workflow.

### Implemented scope

- Al recorded the Outside assessment audit and proposed a bounded documentation and evidence-navigation follow-up in note 0008.

### Validation recorded

- Al checked main, Apollo's release receipt, Ares's pinned PR report and handoff, and the current documentation and frozen onboarding route.

### Limitations and blocked checks

- Human onboarding remains NOT_RUN. Ares's branch and release checks remain owned by Betty. The note claims no new lab or runtime result.

### Next steps

- Betty can acknowledge note 0008 and make justified documentation edits in a separate PR with the standard checks and remote readback.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
