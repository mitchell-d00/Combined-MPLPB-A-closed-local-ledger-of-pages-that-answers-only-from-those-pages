# Repository handoff

Last reviewed: 2026-11-27.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `0aba797739ec4787cd677397036bc1d27581c529` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `664f3c8fe087bef5c754e251a6ef7ca06fba8e098c669bff4985a783ed410355`.

## Betty report for Al

Run the Betty implementation step first, then the Al review step in a separate chat. Both inspect the repository and the public API manifest, confirm their step, then read the last Betty report on the newest PR by creation time. A specific PR link selects that PR. The maintainer pastes Al’s response and direction to Betty, who tests and updates that PR. Resume from the last applied state after a pause.

### Latest user update instructions

Archive the published From Workflow Decisions to Git Effects PDF unchanged. Freeze and measure restart duplication first. If needed, freeze a separate durable lab candidate. Retain the original results, preserve a recoverable checkpoint, and merge only after applicable checks pass.

### Implemented scope

- Archive the exact PDF with its digest, paper index entry and separate dated PR #111 note. Freeze the baseline fixtures, expected outcomes and scoring against released a0136939.
- Keep the restart baseline and store experiment separate. Freeze the exclusive reservation, outcome readback, interruption, and no-retry policy before implementation.
- Add a lab-only fsynced exclusive directory reservation wrapper with separate Git execution and readback receipts. Leave the original controller and release paths unchanged.
- Preserve exact source and result archives, raw subprocess logs and outcome records, independent ref readbacks and disposable Git bundles. Add the study to the Test Index and paper archive.

### Validation recorded

- The PDF copy matches the supplied attachment byte for byte. Verified the frozen baseline input digests.
- Baseline matched all three frozen scenarios. Both unretained duplicates reached Git after restart with zero successful writes. The host-retained key blocked the duplicate with zero Git attempts.
- The archive from 0aba797739ec4787cd677397036bc1d27581c529 passed all 42 original controls, three baseline scenarios and six frozen candidate scenarios. The candidate withheld known and pending duplicates before Git, selected one writer in the local contention test, and retained uncertainty on both abrupt exits. 63 existing checks and 14 pinned upstream tests passed.

### Limitations and blocked checks

- No restart measurements were run before this freeze. The study is lab-only.
- The store assumes a trusted host and local filesystem with atomic create and directory sync. Power loss, distributed authority and storage, authentication, manual reconciliation and production dispatch are outside the tested scope. Public lab fixtures and bundles contain no restricted inputs or credentials.

### Next steps

- Download and compare the pushed paper and lab archive bytes. Verify exact-head CI and merge only after its checks pass under the maintainer’s existing authorization.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
