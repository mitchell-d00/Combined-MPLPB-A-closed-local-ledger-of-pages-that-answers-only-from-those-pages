# Repository handoff

Last reviewed: 2026-11-23.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `a609706b90f953d666059fbdd34c3090295e4c86` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `3537664f17d86cb5b03a7b7e92686e173fd7f8ac207cf68c86931b6ee9627854`.

## Latest user update instructions

Test D10 and mplpb on % suit then mega push if it works how I’m picturing
Enhance MPLPB if possible push evolve enhance never harm
Fix the workers in % and note failure and patch if you have not already

## Implemented scope

- Add the D10 suite index, live/local capture, exact-anchor paired questions, and independently checked citation scoring.
- Report D% worker setup failures accurately and replay all 75 executable classes on the hosted isolation lane.

## Validation recorded

- Ten synthetic D10 source pairs and two mixed-capture pairs passed; supported citations were checked and every altered quote withheld.
- The focused D10 and D% suites passed 32 tests. On this host bubblewrap failed while setting up the UID map for all 75 attempts. The patched driver returned nonzero and reported zero completions.
- No native answer or sorter implementation changed.
- The first hosted PR lane rejected stray workflow command arguments before any worker ran. The retry uses Bash arrays for worker arguments and keeps the same isolation.
- The next hosted attempt reached all 75 launch calls and all failed. The workflow now uses the same temporary-directory location as the isolation probe and reports the first worker failure and stderr if any launch fails.

## Limitations and blocked checks

- Other D% classes are indexed for planning. A live, topic-aligned ten-source D10 batch and independent semantic validation are still unmeasured.

## Next steps

- Require successful isolated worker completion on the exact PR head before merging.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
