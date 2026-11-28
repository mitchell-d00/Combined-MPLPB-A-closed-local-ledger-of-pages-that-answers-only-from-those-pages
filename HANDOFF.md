# Repository handoff

Last reviewed: 2026-11-28.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `bb1632d4579d88dab6f9b59363c2cc8fd06fc2a6` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `76da61ccad0bf191fcf1e641c26d17b689edd61484e112913f0dcd1234ed78ee`.

## Betty report for Al

Run the Betty implementation step first, then the Al review step in a separate chat. Both inspect the repository and the public API manifest, confirm their step, then read the last Betty report on the newest PR by creation time. A specific PR link selects that PR. The maintainer pastes Al’s response and direction to Betty, who tests and updates that PR. Resume from the last applied state after a pause.

### Latest user update instructions

Betty, run the next instruction-to-Git integration study in a separate lab PR. Recheck main and use the verified PR #131 deployment at cabcd140ee438b0a63784faa2c0fc4b2a8c54e66 as the proposed baseline. Follow Al notes 0010 and 0012. Freeze eight development cases and eight separate fresh cases before implementation. Build the record from actual native output. Record where each control stops. Pin the candidate before opening fresh. Push the recoverable checkpoint, verify remote readback and applicable exact-head checks, and merge only qualifying lab work. Keep production dispatch inactive.

### Implemented scope

- Frozen native-projection, host grant, fixed Git CAS and durable receipt study limited to disposable repositories.

### Validation recorded

- Disconnected reader 8/8; candidate development and first fresh 8/8 each. Three durable intended updates and five zero-attempt controls per candidate draw. Independent payload and receipt readback matched all 16 cases. First pipe-spawn failure retained.
- Original paths replayed Apollo 7/7 and 7/7, Ares 5/5 and 5/5, competing writer 2/2, and restart/interruption 3/3 and 6/6. Two Apollo extraction setup failures retained; complete pinned replay passed.

### Limitations and blocked checks

- One operator; private evaluator custody local. No new reader coverage, production dispatch, or cross-resource atomicity. Original PR #130 grades and NOT_RUN labels stand.

### Next steps

- Verify exact-head release checks and remote byte readback before merging qualifying lab work. Retain consumed replays under their original scope.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
