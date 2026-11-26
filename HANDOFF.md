# Repository handoff

Last reviewed: 2026-11-26.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `491e0e15086b23546407d361344f28698a32c53c` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `ce899a6829c644860a91756f18942d3216c9bc8c57e5156270ee5b1cc30d1199`.

## Betty report for Al

Run the Betty implementation step first, then the Al review step in a separate chat. Both inspect the repository and the public API manifest, confirm their step, then read the last Betty report on the newest PR by creation time. A specific PR link selects that PR. The maintainer pastes Al’s response and direction to Betty, who tests and updates that PR. Resume from the last applied state after a pause.

### Latest user update instructions

Run the bounded C3 comparison within existing Cryptid → Bunyip → Round 2. Freeze the five C3-REPL-P replacement pairs before execution, then freeze paired fresh C3-REPL-R and X packets and run both pinned readers once without reader repairs. Report useful comparisons and keep replacement, formatting, and incident status separate. Preserve the old incomplete checks.

### Implemented scope

- Completed the bounded Round 2 comparison on the unchanged released and C3 pins. Registered the frozen P/R/X packets, source and formatting judgments, raw archives and question-level receipts in the Test Index and Round 2 report.

### Validation recorded

- Dev freeze dcbf222 and fresh freeze 491e0e1 preceded separate isolated runs. Released 2622813 runtime ZIP SHA-256 62231d49f21df9c61bc58d48e5038202158893001214fc197c4b9f4fb0b3d634; C3 3bf9657 runtime ZIP SHA-256 73b96b79eed8a116df54dd4f48cce2a116553d4f056204694e1913c5428f38e0.
- Both readers executed 50 cases each with zero execution failures. Development: one overlapping target, four joint misses, five of five controls on both. Fresh: three C3-only routing gains, zero released-only, seventeen joint misses, 16/20 keyed contrasts on both. The four missed contrasts expected checked partials. Zero unsupported completions or claims. The two emitted yes/no answers meet the separate format check.
- Retained raw archives: development SHA-256 1420fc5a9c68ea48a27f8df2082ed7b5c01896aeefbde6202edf5ee5383c6a48; fresh SHA-256 f0e6da998f224b8f0e58ab99bd2c0b8dd52aca6fe4f9a75ca4f858b856949e68. Existing 832 and BB preservation carry forward on unchanged reader bytes.

### Limitations and blocked checks

- Narrow coverage to the three fresh routing questions. Same-operator preparation and scoring. Original 17 private checks incomplete and 100 original held cases NOT_RUN. Retired recovery closed. Git-history incident open. Independent measurements, native OOCC and human onboarding remain NOT_RUN. C3 unmerged and undeployed.

### Next steps

- Hold C3. If reader work continues, trace C3-REPL-X07-B from discovery to compound obligation admission using the retained output. If it informs a repair, retain the original fresh score as consumed development and rerun affected preservation on the changed reader.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
