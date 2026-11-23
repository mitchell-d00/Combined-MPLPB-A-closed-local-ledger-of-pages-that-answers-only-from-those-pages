# Repository handoff

Last reviewed: 2026-11-23.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `2b70ad791e37a08cf29701e2908d7b2cff847ad1` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `9a3031698ea5f81e46189d718bc568900c5cec08e464fca01af3b95549571924`.

## Latest user update instructions

Make this explicit but not the raiting Combined MPLPB as a research methodology demonstrated through working software

## Implemented scope

- State the methodology-through-working-software framing near the top of the README.
- Explain how constraints, implemented evidence checks, and retained experiments inform each other.

## Validation recorded

- Passed the documentation audit and checked the linked package guide, Test Index, and retained D% failure evidence.

## Limitations and blocked checks

- This documentation update draws on retained experiments. It includes no new benchmark or live deployment result. Full local ZIP extraction exceeds the available disk space.

## Next steps

- Use the ZIP-first CI workflow on the exact candidate revision before any release.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
