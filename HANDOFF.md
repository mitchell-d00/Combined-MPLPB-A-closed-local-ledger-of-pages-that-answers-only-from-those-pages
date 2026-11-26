# Repository handoff

Last reviewed: 2026-11-26.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `d5848641bcaf46410576e7dd04202a506b7dab94` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `881d5d9559b5f59ecd87db567b6e85eae08af55eb0cdb474aab79809c739ba12`.

## Betty report for Al

Run the Betty implementation step first, then the Al review step in a separate chat. Both inspect the repository and the public API manifest, confirm their step, then read the last Betty report on the newest PR by creation time. A specific PR link selects that PR. The maintainer pastes Al’s response and direction to Betty, who tests and updates that PR. Resume from the last applied state after a pause.

### Latest user update instructions

Close and preserve Bunyip C3, then complete the bounded Wampus Cat sprint in the existing Cryptid series.

### Implemented scope

- Implement shared named-field checking and combine independently checked opening time and location with one source identity and the original eligibility gate. Add a scoped hosted invocation of the existing isolated Cryptid runner.

### Validation recorded

- 28 focused compound-field and Bunyip regressions passed. Candidate commit and runtime ZIP will be pinned before the fresh packet opens.

### Limitations and blocked checks

- Original private checks incomplete, original held transfers NOT_RUN, publication incident open. C3 unmerged.

### Next steps

- Run Wampus development on all three readers and replay consumed Bunyip with the candidate.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
