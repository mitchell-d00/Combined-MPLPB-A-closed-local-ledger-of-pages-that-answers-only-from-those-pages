# Repository handoff

Last reviewed: 2026-11-22.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `65fc5eb13c7ff19302502b245f64e52ddaa8c719` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `178604c0125d231b18f6b94ae2d3cfdf8c435444b76f81994240cf1c620f4eed`.

## Latest user update instructions

Push it as such but make it an active rout to fixing other issues it may fix my communication experience-packaging

Do the 72

## Implemented scope

- Package the opt-in SQLite synonym graph as a native-wheel command, with readable suggestions and a local report that groups communication issues for review.
- Allow the sealed Dice Bag runner to select a SQLite database and preserve the resulting 72-case replay receipt. Add a release check for the installed command.

## Validation recorded

- The frozen 72-case full score was byte-identical to the original and all 36 strict negative controls withheld. The communication report grouped 24 unmatched fields, 12 competing record matches, and 36 unique pairs that require whole-question review.
- Thirteen focused graph, flat index, Dice Bag and persona transfer tests passed.

## Limitations and blocked checks

- This route suggests selectors and keeps the original wording. It does not supply selectors automatically to the strict reader or expand the catalog by itself.
- The replay kept the same vocabulary. It checks parity rather than measuring independent language transfer.

## Next steps

- Use the review groups to design scoped candidate changes and test against a separate held-out collection before promoting expansions.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
