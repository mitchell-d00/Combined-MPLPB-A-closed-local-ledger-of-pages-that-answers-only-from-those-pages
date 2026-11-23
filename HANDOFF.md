# Repository handoff

Last reviewed: 2026-11-23.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `d60c6cd209287059244fd64d0723d280b38bde5e` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `f17feaaf19692ce53932e4d33b528b704647091af4b4adad0005505458bd915e`.

## Latest user update instructions

Push to main make Readme explicit push all open tree to main merge and we will call it a morning

## Implemented scope

- Compare Strict Ask, unconfigured Assisted Ask, candidate lookup, investigation, and article assembly on the frozen historical questions.
- Index the graph, historical follow-up, public 52, D20, Primary Book, and Dice Bag replays with separate scoring criteria.
- Add the Advanced MPLPB guided CLI and strict-first Python entry point.
- Use one command to freeze training inputs, group baseline misses, and test one authored candidate or registered repair.
- Make Advanced MPLPB routing, local model opt-in, rule training, and the archived benchmark outcomes explicit in the root README.

## Validation recorded

- The standalone historical replay returned four full answers, three partials, three conflicts, and twelve abstentions. Article assembly preserved all 22 contracts.
- The Wallace-Darwin letter question returned a strict documentary answer and an unconfigured-assisted abstention.
- Public evidence passed 52 cases. The frozen D20, book, and Dice Bag replays completed, and 56 focused mode and governance controls passed.
- The archived historical replay reproduced every case. Unconfigured Assisted Ask abstained on all 22. Expert investigation produced 22 reports with zero verified observations or traversed links.
- Advanced MPLPB and adjacent training, governance, evidence, and investigation suites passed 70 focused checks.
- The archived Advanced MPLPB replay preserved all 22 strict contracts, launched 12 lookups and three investigations, and stopped after Strict Ask on seven cases.
- The elapsed-days repair recovered two development cases and one holdout with zero regressions. The inclusive-days variant failed a protected holdout and stayed at review_needed. The clean wheel ran both CLI commands.
- The full Python suite ran 1666 tests with two skips and zero failures. Fifteen focused checks also passed from the extracted source archive.

## Limitations and blocked checks

- The historical questions and drafted source anchors are development fixtures. Live model inference and independent historical accuracy were not assessed.

## Next steps

- Run the exact-head archive and regression checks before merging the complete branch into main.
- Run separately adjudicated historical assisted inference when a pinned local model is available.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
