# Repository handoff

Last reviewed: 2026-11-21.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `cf2f9cb91eceef7bae7666dc3c615eeafe3967ec` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `5db4b28d89827a0ec8e10a0d642baffaf37736d56201c779bb8c2d73d6463d88`.

## Latest user update instructions

Push it merge to main

## Implemented scope

- Publish the original Executable Gates comparative package and the verified dispatch enforcement follow-up.
- Retain the follow-up ZIP, checksum, harness, raw and preliminary observations, and regression log in both repositories.
- Index the follow-up with the original evidence and report its tested operational boundary.

## Validation recorded

- The original seven paired probes and both disposable local Git fixtures reproduced.
- All 28 follow-up controls passed from the extracted experiment ZIP and replayed successfully in both publication checkouts. The specialist-continuity suite passed 48 tests.
- The B-Tests suite passed all 130 tests. The MPLPB handoff, documentation and infrastructure checks apply to the publication candidate.

## Limitations and blocked checks

- The follow-up tests supported execution surfaces and a cooperative local fixture adapter at MPLPB 6ba371c.
- A source change after reservation produced no adapter effect and retained an indeterminate outcome with two events.
- Complete mediation under adversarial conditions remains unestablished.

## Next steps

- Run both repositories' checks for the submitted revisions before merging.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
