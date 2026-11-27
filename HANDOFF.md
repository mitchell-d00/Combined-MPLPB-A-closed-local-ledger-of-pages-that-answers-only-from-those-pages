# Repository handoff

Last reviewed: 2026-11-27.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `6ff09a241b722321dfa5af2397fb7b5342b4b20b` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `5a36215f52cffc97270a1cbe9b4565542eacc295813b0d30ec9fa58ff7a00a41`.

## Betty report for Al

Run the Betty implementation step first, then the Al review step in a separate chat. Both inspect the repository and the public API manifest, confirm their step, then read the last Betty report on the newest PR by creation time. A specific PR link selects that PR. The maintainer pastes Al’s response and direction to Betty, who tests and updates that PR. Resume from the last applied state after a pause.

### Latest user update instructions

Finish PR #111’s verification with one bounded competing-writer test. Retry the failed isolation job unchanged. Freeze the matched ref scenarios first, retain the original evidence and keep the controller lab-only. Merge verified lab work when requirements pass.

### Implemented scope

- Freeze the lab policy and separate development, retained shadow, held and canary packets.
- Integrate the verified B-Tests evaluator as a lab-only dependency. Add a disposable Git compare-and-swap canary and a shadow runner.
- Retain raw first candidate results, measured historical label differences, and the artifact and fixture digests.
- Freeze two matched disposable Git ref scenarios, including beforeWrite hook location, independent ref and marker readback, CAS failure and duplicate reservation expectations.
- Add the matched competing-writer scenario to the lab harness using the existing beforeWrite hook. Keep the workflow and controller policy unchanged.

### Validation recorded

- Verified released main at a7d572067dbf68077ea306584b067e457bd7a3a4. Inspected TeamBuilding, WorkStore controls, and pinned B-Tests action gate. Verified the input hashes.
- First working-tree shadow and development runs matched 7/7 and 15/15 expected outcomes. Two historical withholding labels were refined to missing evidence. The pinned upstream tests passed 14/14 after staging the upstream fixture.
- The extracted candidate ZIP at 5111ebba9f6bab653b93d1f61dd73965eeb43583 matched 40/40 frozen cases. Eight admissions and 32 protective results. Zero false admissions, false denials or case execution failures. One mediated ref update, and the seven canary controls left its observed marker unchanged.
- The pinned B-Tests action suite passed 14/14 and the existing governance, specialist continuity and handoff tests passed 63/63 on retry. Documentation audit passed. No reader, browser runtime or production release workflow bytes changed.
- Retained the first study-sandbox failure from run 46020305274 attempt 1. The Microsoft Ubuntu package repository returned HTTP 403 before isolation tests. Requested an unchanged retry.
- The unchanged study-sandbox retry passed at the original PR head. The first package setup failure remains separate and was retained.

### Limitations and blocked checks

- Held cases are same-operator and accessible to the implementer. Production dispatch is excluded.
- Two local canary initialization attempts hit Node subprocess capture EPERM. Neither reached any case or ref write. File-descriptor output capture was substituted in the harness.
- Six development/shadow pairs overlap. The held suite is same-operator, with no exact input/state overlap. Cross-process isolation and durable revocation remain outside the lab. Direct Git and external operations can bypass this harness.

### Next steps

- Run the candidate archive with all 40 earlier cases and the two frozen competing-writer cases. Retain raw readback and first logs.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
