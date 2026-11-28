# Repository handoff

Last reviewed: 2026-11-28.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `ca19e987a21756739bb4f1ef9633e110e3e7d83e` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `74bf434f13fa1459c757cdb818cc0547fc64bfd249f581dc503faec21b1f0b7f`.

## Betty report for Al

Run the Betty implementation step first, then the Al review step in a separate chat. Both inspect the repository and the public API manifest, confirm their step, then read the last Betty report on the newest PR by creation time. A specific PR link selects that PR. The maintainer pastes Al’s response and direction to Betty, who tests and updates that PR. Resume from the last applied state after a pause.

### Latest user update instructions

Read Al note 0006 at 20885e50. Acknowledge the revision, begin Apollo-01, preserve first results and existing evidence, then push and merge qualifying lab work under Mitchell’s existing authorization.

### Implemented scope

- Applied Al note 0006 at 20885e500faf75b88fa80548aabadd1f991fe76b. Apollo-01 is lab-only. Ares and Hestia deferred.

### Validation recorded

- First development and first fresh each 7/7. Each made one authorized and durably recorded Git update. All six blocked controls per draw made zero writer attempts.
- Hermes 9/9 and 9/9, controller 42/42 and restart 3/3 plus 6/6, with original bridge, policy and store bytes unchanged.
- Preserved the networked first-run failures and 61/61 local-networking retry. Preserved the first preservation space error and successful unstaged retry.

### Limitations and blocked checks

- One operator, synthetic trust snapshot, and private keys in one workspace failure domain. No production authorization or dispatch.

### Next steps

- Verify the exact-head checks, merge and Pages publication. Keep first-run material at its original grade and use it as consumed preservation.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
