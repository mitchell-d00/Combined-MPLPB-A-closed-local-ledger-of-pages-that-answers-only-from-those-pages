# Repository handoff

Last reviewed: 2026-11-23.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `262e64bf7769cfb504bed6caf946db40d812f0a4` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `ec9208d7946b09c52e4e3465ee0dd1a8303a07a8080f52ddd3fbc255cc72dc76`.

## Latest user update instructions

Make a note about this in b tests and mplpb distinctive, independently developed approach to making AI research inspectable and reproducible. The strongest evidence for that description is the record you leave when a test fails.

## Implemented scope

- Add a README research note explaining why retained failures make the work inspectable and reproducible.
- Use the existing D% worker failure and hosted replay as the example.

## Validation recorded

- Checked the README against the retained D% launch failure record and the hosted 75-case replay.

## Limitations and blocked checks

- The referenced replay measures isolated worker completion and scored case outcomes on its frozen inputs.

## Next steps

- Keep the original failure, patch, and replay linked when reporting later evaluations.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
