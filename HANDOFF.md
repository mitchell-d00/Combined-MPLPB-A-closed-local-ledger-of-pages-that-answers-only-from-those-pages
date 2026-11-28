# Repository handoff

Last reviewed: 2026-11-28.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `241bee0f2301e69331db862f3cfd1ab49e59924a` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `9d3ad83cef0a37ea62919a5927c4633835a838d831ba81443fdd1de23f9609c5`.

## Betty report for Al

Run the Betty implementation step first, then the Al review step in a separate chat. Both inspect the repository and the public API manifest, confirm their step, then read the last Betty report on the newest PR by creation time. A specific PR link selects that PR. The maintainer pastes Al’s response and direction to Betty, who tests and updates that PR. Resume from the last applied state after a pause.

### Latest user update instructions

Betty, start ARIADNE-01 — FRUS subject-line identification. Acknowledge Al note 0014 at dcdcfd93fc4a3017f44b0d976ae7de2aad9f6986. Recheck main against verified #135 at 241bee0f2301e69331db862f3cfd1ab49e59924a. Use a separate reader PR or reconcile an existing sprint branch. You can begin the baseline readback and packet freeze while Al publishes note 0015. Acknowledge its exact commit when supplied. Use DIRECT-02 as consumed evidence. Under the original question and profile, verify the complete subject reference against exactly one eligible original memorandum, binding named writer, date, addressee, and topic to exact witnesses. Leave submission, receipt, agreement, and execution unresolved. Keep ranking unchanged. Freeze the baseline, grammar, source pins, independently worded development and separate held fresh cases, citation spans, scorer, budgets, and expected stopping stages before edits.

### Implemented scope

- ARIADNE-01 frozen rule and unchanged baseline. Read note 0014 at dcdcfd93 and note 0015 at 265f1f7e on PR #128.

### Validation recorded

- Against released reader 241bee0f, all 21 frozen arms stopped at interpretation. Zero complete answers, claims or execution failures. The controls did not reach their required proof stages.

### Limitations and blocked checks

- Same-operator preparation and scoring. Evaluator keys, the held operator packet and reconstructible parameters are private. Independent historical accuracy and human assessment remain NOT_RUN.

### Next steps

- Implement the frozen native subject-reference rule, replay development and protection, pin a qualifying candidate before held evaluation, and verify remote evidence, exact-head checks and release. Keep ranking, DIRECT-03, two-link, UI, Chronos and production dispatch on separate tracks.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
