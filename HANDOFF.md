# Repository handoff

Last reviewed: 2026-11-27.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `e7680e6ee379456f1bc11b8b36ed68c20c4a7271` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `aa72e95fa0a18e98e66677a0904a8b2736afabd248dde71078e71c2a9a3fbdda`.

## Betty report for Al

Run the Betty implementation step first, then the Al review step in a separate chat. Both inspect the repository and the public API manifest, confirm their step, then read the last Betty report on the newest PR by creation time. A specific PR link selects that PR. The maintainer pastes Al’s response and direction to Betty, who tests and updates that PR. Resume from the last applied state after a pause.

### Latest user update instructions

Add a dated current-status note above PR #106’s historical reports. Correct live documents where needed and preserve original checks and the incident status. Keep these changes separate from the tested restart candidate. Finish PR #106 by reconciling useful publishable material on a clean branch. Merge the checked reconciliation, then close #106 unmerged as superseded. Retire the interrupted study and keep the incident open.

### Implemented scope

- Reconcile the current status page, Test Index, results registry and Thoth clean-release guide on a separate documentation branch.
- Inventory 253 original and historical-only paths, carry forward 34 selected public items with exact publication authority, and retain the original primary and replacement scoring records.

### Validation recorded

- PR #106 is open and unmerged. Its historical description body was preserved byte for byte under the dated note. Verified merges and successful Pages receipts for PRs #109, #110 and #111. PR #112 merged separately after all 11 checks.
- Six historical 444-case primary output sets matched original strict per-case grades. Both replacement comparison score objects matched exactly using verified original keys in evaluator custody. No reader executions were added.

### Limitations and blocked checks

- Original 17 checks incomplete, original 100 transfers NOT_RUN, workspace recovery INTERRUPTED / UNRECOVERED and historical exposure OPEN.
- Original 128 exposed case keys remain unavailable for independent regrading. The historical 17 private checks and 100 held transfers retain their incomplete and NOT_RUN statuses. The incident remains separately linked and open.

### Next steps

- Verify the promoted exact-head checks and remote readback, merge the clean reconciliation, verify any Pages deployment, then close the original PR unmerged. Leave branch and custody evidence intact.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
