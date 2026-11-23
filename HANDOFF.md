# Repository handoff

Last reviewed: 2026-11-23.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `4cd6ccc34963b134dd2b3ec8d5230dfd7f32e06c` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `0897fc049b8e6ec2d2553d78edbf3e773c7f8d6c4a6159855cdd3e7ab82e7c6e`.

## Latest user update instructions

This can also be applied to training loops test it all

## Implemented scope

- Compare Strict Ask, unconfigured Assisted Ask, candidate lookup, investigation, and article assembly on the frozen historical questions.
- Index the graph, historical follow-up, public 52, D20, Primary Book, and Dice Bag replays with separate scoring criteria.
- Add the Advanced MPLPB guided CLI and strict-first Python entry point.
- Use one command to freeze training inputs, group baseline misses, and test one authored candidate or registered repair.

## Validation recorded

- The standalone historical replay returned four full answers, three partials, three conflicts, and twelve abstentions. Article assembly preserved all 22 contracts.
- The Wallace-Darwin letter question returned a strict documentary answer and an unconfigured-assisted abstention.
- Public evidence passed 52 cases. The frozen D20, book, and Dice Bag replays completed, and 56 focused mode and governance controls passed.
- The archived historical replay reproduced every case. Unconfigured Assisted Ask abstained on all 22. Expert investigation produced 22 reports with zero verified observations or traversed links.
- Advanced MPLPB and adjacent training, governance, evidence, and investigation suites passed 70 focused checks.

## Limitations and blocked checks

- The historical questions and drafted source anchors are development fixtures. Live model inference and independent historical accuracy were not assessed.

## Next steps

- Confirm Advanced MPLPB on the archived historical 22 and finish the full regression suite.
- Run separately adjudicated historical assisted inference when a pinned local model is available.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
