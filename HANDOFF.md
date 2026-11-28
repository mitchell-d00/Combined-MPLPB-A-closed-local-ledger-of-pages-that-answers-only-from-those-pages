# Repository handoff

Last reviewed: 2026-11-28.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `0e71f835f5fc053cfeb6ca97f9682476466d7c8e` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `4652377f65c0f178a6ba52ed026f17ed45523e215743433fbb5274a3af4b9a89`.

## Betty report for Al

Run the Betty implementation step first, then the Al review step in a separate chat. Both inspect the repository and the public API manifest, confirm their step, then read the last Betty report on the newest PR by creation time. A specific PR link selects that PR. The maintainer pastes Al’s response and direction to Betty, who tests and updates that PR. Resume from the last applied state after a pause.

### Latest user update instructions

Acknowledge note 0010 at 805f8263f54fa8069f02d48e898705411ccdedf0. Use verified Ares main fe56551c752bd8df3f1728ac8b11e0cb256c5cdc as the proposed baseline. Recheck main and work on a separate lab PR from newcomer PR #129. First verify the required relationship and date shapes on the unchanged native reader with Git disconnected. If a mandatory role or date case lacks native proof, retain the blocker.

### Implemented scope

- Froze two eight-case synthetic draws at 0e71f835f5fc053cfeb6ca97f9682476466d7c8e against unchanged Ares main. Read only development.

### Validation recorded

- Eight initial native probes and one withdrawal reread. Both compound dates abstained with zero claims. Four standalone claims emitted eight exact spans; frozen scorer rejects the enclosing byline span. Initial preflight and original score retained.

### Limitations and blocked checks

- Fresh, effects, independent assessment and native OOCC NOT_RUN. Private keys, scorer and oracle remain in separate verified local custody. External private recovery unverified. Production dispatch inactive.

### Next steps

- Preserve the native blocker. A separate native proof study would need to support instruction dates while retaining the proved claim when the date remains unresolved.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
