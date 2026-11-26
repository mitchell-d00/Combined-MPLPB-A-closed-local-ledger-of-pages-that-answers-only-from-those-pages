# Repository handoff

Last reviewed: 2026-11-26.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `0ce0ff8377baae641314ca919d7040b91b4c2873` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `af837e999178361a29c4f6f0c1d0035672337e4ce5ef0732bd1f0b7af3230692`.

## Betty report for Al

Run the Betty implementation step first, then the Al review step in a separate chat. Both inspect the repository and the public API manifest, confirm their step, then read the last Betty report on the newest PR by creation time. A specific PR link selects that PR. The maintainer pastes Al’s response and direction to Betty, who tests and updates that PR. Resume from the last applied state after a pause.

### Latest user update instructions

Close and preserve Bunyip C3, then complete the bounded Wampus Cat sprint in the existing Cryptid series.

### Implemented scope

- Implement shared named-field checking and combine independently checked opening time and location with one source identity and the original eligibility gate. Add a scoped hosted invocation of the existing isolated Cryptid runner.

### Validation recorded

- 28 focused compound-field and Bunyip regressions passed. Candidate commit and runtime ZIP will be pinned before the fresh packet opens.
- BB replay on Wampus retained 900 exact positive contracts, 900 eligible citation readbacks and 200 withholds. Start unchanged public 832 preservation replay for the changed runtime.
- Wampus development hits 4/6 versus both prior readers at 0/6, with zero unsupported claims and 5/6 keyed contrasts. All three C3 routing gains are retained; three consumed Bunyip cross-family complete answers and three checked partials recover. Fresh inputs match the original seal and opened after the runtime ZIP pin. Both scoring keys remain private.

### Limitations and blocked checks

- Original private checks incomplete, original held transfers NOT_RUN, publication incident open. C3 unmerged.

### Next steps

- Run the sealed fresh cases once on the pinned three readers, retain raw evidence, and close after preservation checks.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
