# Repository handoff

Last reviewed: 2026-11-22.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `3931b675acd214f8ff6203cd4928e4c5d43517b4` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `d0b773a63648d7a565de16d9955f0b9691522ca568610e82181e5b249db5a7bf`.

## Latest user update instructions

Build a graph synonym index like my SQLite

## Implemented scope

- Build and query a separate SQLite graph from the existing synonym catalog format, with optional reviewed directed links and selector explanations.

## Validation recorded

- Ten focused graph, flat synonym index, and Dice Bag unit tests passed. The persisted graph reopened read-only with SQLite integrity checks passing and reproduced all 72 frozen Dice Bag lookup results.

## Limitations and blocked checks

- Lookup gives suggestions for review, and the default reader still checks evidence through the existing path. The Dice Bag parity run kept the original vocabulary and measures no improvement in unfamiliar wording.

## Next steps

- Use a separately authored held-out catalog to evaluate added graph edges, ambiguity, and qualifier retention.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
