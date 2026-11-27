# Repository handoff

Last reviewed: 2026-11-27.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `5e30c9b8844d03257cab81de34ab15bb00b5f950` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `019dba9ecec49f88b7a8eceed08a711c9737556a6e56044dea9d72c11e033e00`.

## Betty report for Al

Run the Betty implementation step first, then the Al review step in a separate chat. Both inspect the repository and the public API manifest, confirm their step, then read the last Betty report on the newest PR by creation time. A specific PR link selects that PR. The maintainer pastes Al’s response and direction to Betty, who tests and updates that PR. Resume from the last applied state after a pause.

### Latest user update instructions

Build a bounded deterministic workflow controller from MPLPB’s retained evidence. Start from current released main. Freeze the policy, schemas, development cases, and held evaluation before implementation. Run shadow tests and one disposable local Git canary. Push a reproducible checkpoint and leave Al a report. Stop at the frozen scope.

### Implemented scope

- Freeze the lab policy and separate development, retained shadow, held and canary packets.
- Integrate the verified B-Tests evaluator as a lab-only dependency. Add a disposable Git compare-and-swap canary and a shadow runner.

### Validation recorded

- Verified released main at a7d572067dbf68077ea306584b067e457bd7a3a4. Inspected TeamBuilding, WorkStore controls, and pinned B-Tests action gate. Verified the input hashes.
- First working-tree shadow and development runs matched 7/7 and 15/15 expected outcomes. Two historical withholding labels were refined to missing evidence. The pinned upstream tests passed 14/14 after staging the upstream fixture.

### Limitations and blocked checks

- Held cases are same-operator and accessible to the implementer. Production dispatch is excluded.
- Two local canary initialization attempts hit Node subprocess capture EPERM. Neither reached any case or ref write. File-descriptor output capture was substituted in the harness.

### Next steps

- Run the candidate archive with the frozen canary and held suites and preserve the first results.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
