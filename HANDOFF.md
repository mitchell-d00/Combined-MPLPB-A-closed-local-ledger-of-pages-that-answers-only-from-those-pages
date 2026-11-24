# Repository handoff

Last reviewed: 2026-11-24.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `9e504a9a3157618a55e25a60754fb25e0b22d20d` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `d826978b1fdd62308b259b80c7d917f647739ce2733e623ebdf1c2b369e74268`.

## Latest user update instructions

Build the missing parts they seem intuitive

## Implemented scope

- Derive shared live tags from Observer and Judge outcomes, with exact graph checks on Strict Ask and Advanced inspection presentation.
- Atomically reuse current strict versions, link each new graph version to its predecessor, expose scope history, and verify active route metadata before using candidate locators.

## Validation recorded

- Passed 72 focused native checks covering concurrent graph writes, retired routes, mismatches, history, Spot and existing answers.
- Matched all 22 historical native contracts and all 48 Scout graph passes against ordinary Strict Ask on the same frozen inputs.
- Passed the documentation inventory check.

## Limitations and blocked checks

- Live synchronization is local to an ask or inspection scope. Ledger and SQLite graph storage have separate transactions.
- Scout prose coverage remains a separate research result. Graph flags and candidates carry no proof authority.
- Full local archive extraction exceeds available storage. Use the CI archive gate for the complete release candidate.

## Next steps

- Use the retained Scout obligations to build and evaluate a bounded native recommendation comparison.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
