# Repository handoff

Last reviewed: 2026-11-27.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `9910fec157124ab66803e0263ae61420fbb24c48` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `91c393f091fe4e162b03dfefec6722625d16c51f453d303bcd36956aa7b43567`.

## Betty report for Al

Run the Betty implementation step first, then the Al review step in a separate chat. Both inspect the repository and the public API manifest, confirm their step, then read the last Betty report on the newest PR by creation time. A specific PR link selects that PR. The maintainer pastes Al’s response and direction to Betty, who tests and updates that PR. Resume from the last applied state after a pause.

### Latest user update instructions

Add a dated current-status note above PR #106’s historical reports. Correct live documents where needed and preserve original checks and the incident status. Keep these changes separate from the tested restart candidate.

### Implemented scope

- Reconcile the current status page, Test Index, results registry and Thoth clean-release guide on a separate documentation branch.

### Validation recorded

- PR #106 is open and unmerged. Its historical description body was preserved byte for byte under the dated note. Verified merges and successful Pages receipts for PRs #109, #110 and #111. PR #112 merged separately after all 11 checks.

### Limitations and blocked checks

- Original 17 checks incomplete, original 100 transfers NOT_RUN, workspace recovery INTERRUPTED / UNRECOVERED and historical exposure OPEN.

### Next steps

- Review the documentation-only PR and applicable checks. Keep the historical incident and lab-only controller boundary in scope.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
