# Repository handoff

Last reviewed: 2026-11-28.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `97027f3f504de6e85f9e0d3e77af4fe504057ca7` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `50893195e035819c53ac579d8813ef8b40e097016fa668a4af77561a5e1a589b`.

## Betty report for Al

Run the Betty implementation step first, then the Al review step in a separate chat. Both inspect the repository and the public API manifest, confirm their step, then read the last Betty report on the newest PR by creation time. A specific PR link selects that PR. The maintainer pastes Al’s response and direction to Betty, who tests and updates that PR. Resume from the last applied state after a pause.

### Latest user update instructions

Al; reconcile three points in the Grok-reviewed handoff before Betty implements it.

### Implemented scope

- Al corrected the reported PR states, bounded the F05 and Bastet evidence, and distinguished citation validation from native reader proof in note 0009.
- Reconciled the advice branch with Ares main fe56551c752bd8df3f1728ac8b11e0cb256c5cdc. Betty's applied lab report remains in PR #127.

### Validation recorded

- Verified note 0008 at the initial PR #128 head, queried the PR states directly, and compared the original F05 identity, question and input fingerprint with both Bastet registries and retained replay archives.

### Limitations and blocked checks

- The exact F05 outcome on the later runtime is unverified. Human onboarding remains NOT_RUN. Reviewed evidence and regenerated coordination files for this note.

### Next steps

- Betty acknowledges note 0009 and audits only remaining documentation gaps in a separate branch from refreshed main. Treat the Ares Pages receipt separately from its merge.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
