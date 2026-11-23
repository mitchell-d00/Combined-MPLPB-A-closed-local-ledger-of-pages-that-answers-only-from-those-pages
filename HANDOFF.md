# Repository handoff

Last reviewed: 2026-11-23.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `c80e546ef6d04296a1c136e9fc4933057d79d071` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `9b359fad6c1ba8155249b95faf642b23f890549f1c2b2d80175f940c720de970`.

## Latest user update instructions

Do it

## Implemented scope

- Run a D12 solo post-freeze pilot on six randomly drawn linked FRUS source pairs and 24 natural questions.
- Retain the engine pin, source and key seals, original XML fragments, raw mode outputs, and scripts for replay.
- Index the run and keep passage discovery, source labels, and strict proof results distinct.

## Validation recorded

- Verified 12 exact source fragments against the pinned volume downloads and sealed the key before native execution.
- Replayed the same engine and packet. Scores, strict contracts, passage results, and sorter graphs matched exactly. Only WorkStore receipt IDs differed.
- Passed the documentation inventory audit, artifact digest checks, and 21 focused D12, Advanced, source-notes, and historical-seam tests.

## Limitations and blocked checks

- This is a post-freeze solo evaluation with one operator and no independent human review.
- The sample consists of paired English diplomatic records. No WorkStore notes or configured local model were loaded into the evaluation.
- The full repository ZIP is too large to extract locally with the available disk space.

## Next steps

- Keep this first result fixed. Compare notes on and off for passage discovery, then trace matched passages to proof admission.
- Use another post-freeze draw to measure transfer after any change, and seek cold reviews of one packet at a time.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
