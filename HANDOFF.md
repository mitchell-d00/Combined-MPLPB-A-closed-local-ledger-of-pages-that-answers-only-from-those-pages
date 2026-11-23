# Repository handoff

Last reviewed: 2026-11-23.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `fa13b0eb038dbb4079e5f630cb91a090cbd00bc6` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `ed24fd299e730398b3249be8ec83275ec2ba00eeea5982801f9b73ff72842259`.

## Latest user update instructions

Test on historic 22 and other benches so we can document each mode

## Implemented scope

- Compare Strict Ask, unconfigured Assisted Ask, candidate lookup, investigation, and article assembly on the frozen historical questions.
- Index the graph, historical follow-up, public 52, D20, Primary Book, and Dice Bag replays with separate scoring criteria.

## Validation recorded

- The standalone historical replay returned four full answers, three partials, three conflicts, and twelve abstentions. Article assembly preserved all 22 contracts.
- The Wallace-Darwin letter question returned a strict documentary answer and an unconfigured-assisted abstention.
- Public evidence passed 52 cases. The frozen D20, book, and Dice Bag replays completed, and 56 focused mode and governance controls passed.

## Limitations and blocked checks

- The historical questions and drafted source anchors are development fixtures. Live model inference and independent historical accuracy were not assessed.

## Next steps

- Record the complete matched results and confirm the replay from an extracted archive.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
