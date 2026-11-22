# Repository handoff

Last reviewed: 2026-11-22.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `ef288782109f33b578f188d9d4d4cbca145fda9b` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `5a5fbe7257eec0f368df70827d81872929ece82882504998da28325cca2c0261`.

## Latest user update instructions

Write the live experiment with D12 folder and note planed run proposed human pilot

## Implemented scope

- Document the proposed D12 live experiment and human pilot with eight frozen historical cases.
- Provide a reviewer worksheet that separates initial source judgments, native-output review, and adjudication.
- Link the plan in the D12 guide and Test Index. Document the pending live Dice Bag transfer run.

## Validation recorded

- Verified the eight proposed IDs and question wording against the frozen historical 22 inputs and confirmed their 3 discovery, 3 proof, 1 conflict and 1 control strata in the retained D12 traces.

## Limitations and blocked checks

- The procedure is a proposal. Reviewers, run dates, independent historical verification, and live transfer results are pending.

## Next steps

- Freeze the pilot baseline, distribute the source-only packets to two independent reviewers, and assign a third reviewer to adjudicate.
- Use the pilot findings to choose a repeated failure mechanism and run held-out historical prose and fresh Dice Bag transfer checks against any candidate repair.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
