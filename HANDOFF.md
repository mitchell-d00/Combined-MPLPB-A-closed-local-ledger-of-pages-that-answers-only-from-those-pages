# Repository handoff

Last reviewed: 2026-11-22.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `d497b0009eb079b475259ffef04f9d2da4277284` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `2cd3a00ac071e3da4840e58a1ac88d69e888bc9a93667bbfe4652541ff932dd9`.

## Latest user update instructions

Explain how all my tests etc “train” my system and build that synthetic call it D20

Not how I use tests to train in notes too so Ai and human understand how I train a deterministic Ai

Do that for all tests I run all test types call it test index for both ai and humans to use

Run a D20 large enough to find grouping of misses and classes so we don’t wack a mole

And explain that too in test index

My spectrum rules vs wack a mole

## Implemented scope

- Explain deterministic training in the README, and add the human and AI Test Index for choosing suites, reading evidence, and distinguishing bounded rule classes from individual patches.
- Add D20 generation, native replay, scoring and a grouped study command. Retain a frozen seed, native outputs and large study counts with replay receipts.

## Validation recorded

- Native seed 20 produced one supported result in five expected positives and withheld all 15 single-owner controls. Two native executions produced identical JSON.
- The 64-seed study ran 1,280 primary cases and 320 diagnostic replays. It withheld all 960 single-owner controls and identified three candidate rule classes.
- Four D20 regression tests, the documentation audit covering 48 evaluation families, and the repository infrastructure check passed.

## Limitations and blocked checks

- The public generator uses five authored structures. Seeds change identifiers and owners within those structures. Blind and historical transfer still require independently authored evaluations.
- The raw sorter path measures candidate preprocessing only. The study changes no production rule and is not an application deployment.

## Next steps

- Trace and test narrow owner-question grammar, explicit record-alias binding and field-boundary rules independently. Keep all original D20 decisions and add independent negative controls before changing runtime behavior.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
