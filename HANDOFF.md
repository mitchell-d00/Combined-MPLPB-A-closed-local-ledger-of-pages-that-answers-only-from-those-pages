# Repository handoff

Last reviewed: 2026-11-27.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `23b77d305f4f696ef64c02f4aad7b0a1711eb643` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `6a3a0988fb6c8ee6cc4b2ab6f72100f9f151850084576731e0b03f38cbd8e06e`.

## Betty report for Al

Run the Betty implementation step first, then the Al review step in a separate chat. Both inspect the repository and the public API manifest, confirm their step, then read the last Betty report on the newest PR by creation time. A specific PR link selects that PR. The maintainer pastes Al’s response and direction to Betty, who tests and updates that PR. Resume from the last applied state after a pause.

### Latest user update instructions

Just give me a Betty prompt this time and note it in Al notes

Have her run a sprint too if we need a newest let’s do Greek gods

When she finishes and it’s all good push and merge

### Implemented scope

- Publish Al note 0004 with a focused Betty prompt reviewing the two Heka-01 withdrawal diagnostic differences.
- Preserve all native implementation, packet/key/scorer bytes and first scores; advice does not authorize silent acceptance-policy changes.
- Keep the Heka-01 implementation and its working state on parent PR 120; this advisory branch targets that branch, not an independent release to main.
- Add the newly authorized Athena/Hermes/Hephaestus sprint to the advice, keeping new packets and scores separate from Heka.

### Validation recorded

- Read PR 120 at 4d5f4a4f, frozen CONTRACT.md, grade.py and the retained development score. The only scored differences are D-04 proof and D-07 recheck codes.
- No reader or effect experiment was executed. This update does not relabel a failing exact grade or activate production dispatch.

### Limitations and blocked checks

- Original baseline 10/11, development 12/14 and first fresh 13/13 remain their recorded exact grades.
- The report is Al advice. Betty must verify the exact merge requirements, distinguish expectation discrepancy from implementation defect, and record her own disposition.
- Keys/generator are private workspace material with no remote backup attested in the reviewed report; prompt requires approved private custody and retrieval verification.

### Next steps

- Betty reads note 0004 at its published commit, acknowledges it, and applies/defer/rejects the prompt under the maintainer's existing scope.
- Publish diagnostic disposition and recoverable evidence; merge lab-only work only under actual applicable gates, preserving all historical failures and production boundaries.
- Betty freezes and runs the new Greek three-set sprint; push recoverable checkpoints and merge qualifying lab work after applicable checks under Mitchell's explicit authorization without another confirmation.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
