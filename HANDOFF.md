# Repository handoff

Last reviewed: 2026-11-22.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `3b6dcaf1f4e8b1b25209f63a5c46acb3c649eef2` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `735ed157f2c4b46db007b2a21936fb42f7b35fa0ddab1bc135df3aa03274cf62`.

## Latest user update instructions

Continue

can we get more out of it by building new people and corpa like sewage treatment, cat care, fish care , plant care and mystical creatures and alien/exocreatures like Bigfoot and selacamph

We need a synonym index

Build one let’s test the idea

## Implemented scope

- Add a collection-scoped experimental synonym catalog and lookup command that retains every competing record or field selector.
- Compare lookup with native proof on existing and alternative persona questions. Preserve lookup-only results for additional unresolved time conditions.

## Validation recorded

- The direct reader missed all 16 study questions. After reviewed selector handoff, the native reader returned 16 exact cited answers. Eight qualified questions stayed lookup-only.
- Two study runs were byte-identical, and nine synonym, persona and D20 tests passed.

## Limitations and blocked checks

- This study uses authored catalog expressions and questions. No blind semantic or domain validation is claimed.
- The index is an opt-in selector suggestion tool. The strict default pipeline is unchanged.

## Next steps

- Test an independent catalog and questions whose phrasing, qualifiers and colliding aliases were chosen by a separate custodian. Require explicit review before supplying record and field pins.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
