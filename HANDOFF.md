# Repository handoff

Last reviewed: 2026-11-28.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `49c2ab856c45b6f826e55ef4495b730b644e8ffe` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `403299227b53134752dffe30dbf071ef32d448951790a419675015ed999fc83e`.

## Betty report for Al

Run the Betty implementation step first, then the Al review step in a separate chat. Both inspect the repository and the public API manifest, confirm their step, then read the last Betty report on the newest PR by creation time. A specific PR link selects that PR. The maintainer pastes Al’s response and direction to Betty, who tests and updates that PR. Resume from the last applied state after a pause.

### Latest user update instructions

Finish the FRUS page mappings and freeze the source and extraction records. Verify harmless GitHub sandbox preflight, then run the frozen development smoke on the unchanged released reader. Audit unresolved and NOT_RUN entries against the Test Index and results inventory; reconcile Gremlin and retain earlier study boundaries. Keep evaluator material in private custody.

### Implemented scope

- Audit active and deferred work in a dated register linked through Gremlin to authoritative results. Public seven-record FRUS diagnostic and prepared review/onboarding packages.

### Validation recorded

- Verified main cb7ed70a. Frozen 17 printed pages from seven publisher TEI fragments. Hosted isolation passed four preflight tests. Three-case smoke executed, followed by 77 diagnostic cases with zero execution failures.
- Location 27/42, controls 15/15. Direct 0/4 and two-link 0/2 with five safe controls. Documentary 0/4 with five controls. Exact 27 citations. Recovered public raw archive and verified initial 30 paths. Read back held local seals separately.

### Limitations and blocked checks

- Same-operator evaluation. Local Bubblewrap failed prior to reader execution. Older, fresh, independent semantic review and human routes NOT_RUN. External private recovery unverified. Exact Gelhaus externally blocked and low priority. Production dispatch inactive.

### Next steps

- Verify final public readback and exact-head checks. Recruit reviewers and first-time participants with exposure and permission records. See dated open work for other triggers.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
