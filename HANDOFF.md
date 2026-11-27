# Repository handoff

Last reviewed: 2026-11-27.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `a7d572067dbf68077ea306584b067e457bd7a3a4` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `8c9d84b8b6740fa40c8d8abf05f7408abf3f55798e17eefbfaf222615c901a84`.

## Betty report for Al

Run the Betty implementation step first, then the Al review step in a separate chat. Both inspect the repository and the public API manifest, confirm their step, then read the last Betty report on the newest PR by creation time. A specific PR link selects that PR. The maintainer pastes Al’s response and direction to Betty, who tests and updates that PR. Resume from the last applied state after a pause.

### Latest user update instructions

Build a bounded deterministic workflow controller from MPLPB’s retained evidence. Start from current released main. Freeze the policy, schemas, development cases, and held evaluation before implementation. Run shadow tests and one disposable local Git canary. Push a reproducible checkpoint and leave Al a report. Stop at the frozen scope.

### Implemented scope

- Freeze the lab policy and separate development, retained shadow, held and canary packets.

### Validation recorded

- Verified released main at a7d572067dbf68077ea306584b067e457bd7a3a4. Inspected TeamBuilding, WorkStore controls, and pinned B-Tests action gate. Verified the input hashes.

### Limitations and blocked checks

- Held cases are same-operator and accessible to the implementer. Production dispatch is excluded.

### Next steps

- Implement the thin adapter and evaluate the development and shadow suites before opening the held run.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
