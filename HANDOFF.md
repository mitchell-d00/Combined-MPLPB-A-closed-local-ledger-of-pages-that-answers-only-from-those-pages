# Repository handoff

Last reviewed: 2026-11-28.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `c4c5dc696c349e397b6677b98085f0755eded91d` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `85141b78a7b199e2ee302fa2dc946df11b8decd1fedfcef67146a4ef031c43ff`.

## Betty report for Al

Run the Betty implementation step first, then the Al review step in a separate chat. Both inspect the repository and the public API manifest, confirm their step, then read the last Betty report on the newest PR by creation time. A specific PR link selects that PR. The maintainer pastes Al’s response and direction to Betty, who tests and updates that PR. Resume from the last applied state after a pause.

### Latest user update instructions

Run the new note

### Implemented scope

- Applied Al note 0005 at 4ec98541f6961a320af4453f6d0425aa80575000 from PR #123. Lab-only namespace regression through the original reader, binding check and fixed Git writer.

### Validation recorded

- Hermes development 9/9 and first fresh 9/9, each with two authorized attempts and durable completions. Seven blocked phases per draw made no attempt.
- Consumed Greek 15/15 and 16/16, controller 42/42 and restart 3/3 plus 6/6. Original Heka and production bytes unchanged.
- Reproduced both packets and verified original sealed keys in a separate private workspace archive.

### Limitations and blocked checks

- Shared operator and workspace custody. Host identity, malicious host resistance and production dispatch are outside the tested boundary. Off-workspace backup remains unverified.

### Next steps

- Verify exact-head CI, public readback, and merge/publication. Future evaluation of these packets is consumed preservation.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
