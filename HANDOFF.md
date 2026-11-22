# Repository handoff

Last reviewed: 2026-11-22.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `78535734029de32762adecf5fa55080635f2418f` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `f65f640f9a7854d33fe58d1e9abfacddecd1a669a527bec8939244fc9301ba0e`.

## Latest user update instructions

Explain this in Readme too

The strongest thing you’ve built is a way to improve a deterministic reader without losing track of what it used to get right.

One of the strongest things I built many strong things

## Implemented scope

- Describe preserving existing behavior during rule improvements as one of the project’s strengths, with D20 and Dice Bag as measured examples.

## Validation recorded

- Checked the quoted counts and their scopes against the frozen D20 and Dice Bag reports and checked README navigation.

## Limitations and blocked checks

- This update explains existing evidence. It records no new reader behavior or independent validation.

## Next steps

- Use independently authored questions to measure transfer beyond the frozen cases.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
