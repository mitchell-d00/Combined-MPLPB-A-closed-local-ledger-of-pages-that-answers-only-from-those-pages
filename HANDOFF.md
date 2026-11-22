# Repository handoff

Last reviewed: 2026-11-22.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `5b0fa559d511b925af3595c52d083cac1cdceb43` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `263e4d2ad70afa1966e1342e09963e4b0f43af41ac1ca39d7c4a3ab6943638f9`.

## Latest user update instructions

Test it vs synonym graph.

Add corona history of cv 66 America and mt airy history

Add Corona as a third topic

Mt airy nc

And see if it helps historic

Test historic 22 on graph too

## Implemented scope

- Compare baseline and SQLite synonym graph-guided passage discovery on the frozen original historical 22 and the 40 historical follow-up questions.
- Add attributed starter history records and twelve questions on USS America CV-66, Mount Airy in North Carolina, and Corona in California.

## Validation recorded

- On the original 22 the graph suggested eligible records for 18/22 and raised complete reference-anchor visibility from 4/21 to 5/21. H09 and H13 gained anchors and no case lost any.
- On the 40 follow-ups the graph suggested all reference records for 27/40. One direct or paraphrased question gained an anchor, and fully surfaced cases stayed 14/20. All 12 new starter cases found the intended record.
- All 13 scope controls across the follow-ups and new topics withheld full support. Ten focused graph and historical tests passed.

## Limitations and blocked checks

- The graph-guided comparison is a passage inspection probe. Strict proof uses its existing unmodified source path. Curated aliases and prepared source summaries do not establish blind transfer or historical answer accuracy.
- Corona was interpreted as the California city. The new corpora use attributed short factual summaries rather than complete copied originals.

## Next steps

- Measure source-bound proof rules for documentary date roles and attribution separately from graph-guided discovery.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
