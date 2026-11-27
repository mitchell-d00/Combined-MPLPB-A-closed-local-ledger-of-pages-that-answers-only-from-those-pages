# Repository handoff

Last reviewed: 2026-11-27.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `a01369392071bd6781be379a4b580d9a9d0bc460` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `d4d13967f8fb3af28edb108a36957809500ca7fa5b9211548ece74bbe0b15726`.

## Betty report for Al

Run the Betty implementation step first, then the Al review step in a separate chat. Both inspect the repository and the public API manifest, confirm their step, then read the last Betty report on the newest PR by creation time. A specific PR link selects that PR. The maintainer pastes Al’s response and direction to Betty, who tests and updates that PR. Resume from the last applied state after a pause.

### Latest user update instructions

Archive the published From Workflow Decisions to Git Effects PDF unchanged. Freeze and measure restart duplication first. If needed, freeze a separate durable lab candidate. Retain the original results, preserve a recoverable checkpoint, and merge only after applicable checks pass.

### Implemented scope

- Archive the exact PDF with its digest, paper index entry and separate dated PR #111 note. Freeze the baseline fixtures, expected outcomes and scoring against released a0136939.

### Validation recorded

- The PDF copy matches the supplied attachment byte for byte. Verified the frozen baseline input digests.

### Limitations and blocked checks

- No restart measurements were run before this freeze. The study is lab-only.

### Next steps

- Execute the frozen baseline using two fresh Node processes per scenario. Preserve the first results and Git readback.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
