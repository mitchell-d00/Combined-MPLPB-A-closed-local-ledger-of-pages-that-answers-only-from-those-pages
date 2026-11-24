# Repository handoff

Last reviewed: 2026-11-24.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `0c33369c70ea58593d8e0620fc46554915414022` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `66eb04614c3b24a3b2bd39ca56e70ead557a463349dfbd973153febfce6b404a`.

## Latest user update instructions

Go from that and do test name test 4score20

## Implemented scope

- Implement 4score20 in the order understand the question, find the relevant words, and check what they prove in context.
- Retain the native plan, passage coverage, strict outputs with and without source-location hints, and exact-quote controls for three frozen D12 cases.

## Validation recorded

- Ran 4score20 twice with byte-identical output. Wide search found all four telegram anchors, while the original question still lacked a documentary plan. The exact quote crossing a statement boundary withheld while both fragments passed.
- Passed 49 focused tests and the documentation inventory audit.

## Limitations and blocked checks

- The replay diagnoses three previously seen cases. It changes no native answer rule and does not exercise verification of a valid telegram relationship plan.
- The full repository ZIP exceeds the available local extraction space.

## Next steps

- Use the retained trace to measure each proposed repair against the original questions and the final-wording refusal control.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
