# Repository handoff

Last reviewed: 2026-11-24.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `c8762c3f72528dc4b08f0652d702be8175cdbd28` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `fe2d6311c748ed19242c361c679715bd77a12bdeacba402a73fcdd8dadc43aa8`.

## Latest user update instructions

New test using what we found named J/Opass.     The Observer records what happened. Which parts of the question were understood? Which passages were found? What did Strict Ask verify? What stayed open? The Observer also records where the chain stopped. “The search missed a passage” and “the question had no proof rule” call for different warnings.
* The Judge decides what the reader needs to see. It applies deterministic presentation rules to the Observer’s record. If a claim is verified but easy to overread, it adds a short boundary beside that claim. If a required link is missing, it tells the presenter to show the verified parts and mark the rest unresolved. The Judge cannot promote a candidate into proof. Then test the model

## Implemented scope

- Add J/Opass with a read-only Observer, a deterministic presentation Judge, and two local model layout arms.

## Validation recorded

- Replayed six native cases and verified byte-identical native output.
- Ran 16 local SmolLM2 CPU calls. All preserved the presentation contents and strict proof decision. JSON enum accepted 8/8 layouts and free text accepted 0/8.
- Passed 53 focused tests with loopback available.

## Limitations and blocked checks

- This is an evaluation harness. The model selects layout only, and the run uses one small model.
- The full repository ZIP exceeds available local extraction space.

## Next steps

- Reuse the retained J/Opass inputs when evaluating a production presentation integration.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
