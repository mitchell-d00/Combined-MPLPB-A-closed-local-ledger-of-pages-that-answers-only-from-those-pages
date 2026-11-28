# Repository handoff

Last reviewed: 2026-11-28.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `fdf32d2b6e2b80d63be2128ec7b24dc4cf93ebe3` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `7e4996aa78c062e267edf3a4e9c5514b6071a9c0adf40a10f8e30a4074ea9776`.

## Betty report for Al

Run the Betty implementation step first, then the Al review step in a separate chat. Both inspect the repository and the public API manifest, confirm their step, then read the last Betty report on the newest PR by creation time. A specific PR link selects that PR. The maintainer pastes Al’s response and direction to Betty, who tests and updates that PR. Resume from the last applied state after a pause.

### Latest user update instructions

Finish the FRUS page mappings and freeze the source and extraction records. Verify harmless GitHub sandbox preflight, then run the frozen development smoke on the unchanged released reader. Audit unresolved and NOT_RUN entries against the Test Index and results inventory; reconcile Gremlin and retain earlier study boundaries. Keep evaluator material in private custody.

### Implemented scope

- Frozen seven-record FRUS diagnostic and optionally repeated native sandbox study. Runtime and production dispatch unchanged.

### Validation recorded

- Main verified at cb7ed70a. Seventeen distinct printed pages mapped to publisher XML fragments. Local Bubblewrap preflight failed before reader execution.

### Limitations and blocked checks

- Baseline NOT_RUN pending hosted isolation and smoke. Same-operator author and scorer; human and independent results NOT_RUN. Gelhaus exact replication externally blocked pending authorized access.

### Next steps

- Check hosted isolation receipts and score public packets after smoke. Reconcile open records and prepare external review and current-route onboarding.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
