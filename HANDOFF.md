# Repository handoff

Last reviewed: 2026-11-26.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `8e5402a2ecf3fff73586e0d7f64a74f3ca0f6238` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `5f9890d2f75770b3a80c2f3ea6109d5fe25aea9e8a64160cf170b73b9b7bd31f`.

## Betty report for Al

Run the Betty implementation step first, then the Al review step in a separate chat. Both inspect the repository and the public API manifest, confirm their step, then read the last Betty report on the newest PR by creation time. A specific PR link selects that PR. The maintainer pastes Al’s response and direction to Betty, who tests and updates that PR. Resume from the last applied state after a pause.

### Latest user update instructions

Close and preserve Bunyip C3, then complete the bounded Wampus Cat sprint in the existing Cryptid series.

### Implemented scope

- Closed Bunyip Round 2 as a narrow measured result and completed the bounded Wampus Cat sprint. Implemented a shared literal named-field check and one bounded compound composition path. No consolidation claim.

### Validation recorded

- Scope and both case sets froze at d5848641b. Wampus code 1ca8a1a0be648de660c928da879c8c86788c10a0, scoped runtime ZIP SHA-256 9ff59768cacfcdfe1498c210b93f7de74c4918b60a25bda7e5e239e56aed308f. Fresh opened at 8e5402a2e after candidate pin. Three-way development: 4/6 versus both earlier 0/6. Three-way fresh: 3/5 versus both earlier 0/5; one useful contrast partial, no unsupported claims or execution failures.
- All three C3 routing gains retained. Consumed Bunyip 50 completes: released 1, C3 4, Wampus 7 plus 3 checked partials. Wampus retained the 832 public contracts, BB 900 exact positives and eligible citations with 200 withholds, and 28 focused tests. Artifacts and exact hashes in the Wampus result.

### Limitations and blocked checks

- Terminal-period imperative questions still miss. Same-operator keys remain separate; no independent blinding. Original 17 private and 100 held cases unchanged. Retired recovery closed, Git-history incident open, no release, merge or deployment. All independent and human NOT_RUN labels retained.

### Next steps

- Bounded sprint closed. Next executable diagnostic is the terminal-period whole-question contrast under the existing guards. If the first fresh outcomes inform a repair, classify that packet as consumed development and freeze fresh transfer again. Keep custody/history remediation separate from the language evidence.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
