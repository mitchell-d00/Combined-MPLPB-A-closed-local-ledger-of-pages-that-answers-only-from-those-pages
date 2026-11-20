# Repository handoff

Last reviewed: 2026-11-20.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `9c9212e5b9789e3b3e1b28e0426b2bdc7c9ee79c` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `05e984b85f8bac5641062ba07cf539f4406be73f476a8e71faa781b726319ae9`.

## Latest user update instructions

Push it to main as documentation I may publish it later

## Implemented scope

- Add The McPhetridge Method for Evidence-Gated Software Engineering under Mitchell D. McPhetridge's byline as a dated documentation case study.
- Link the manuscript from the documentation index and retain a compact, attributed record of the cited baseline and replay measurements.

## Validation recorded

- The manuscript retains the requested design standard verbatim.
- GitHub PR 62, its exact merge tree and its live Chromium deployment run corroborate the historical release facts. The author-supplied timer stays distinct from GitHub's record.
- The documentation inventory audit and repository infrastructure checker passed on the staged documentation. The evidence record reuses saved runs.

## Limitations and blocked checks

- This documents a specific engineering cycle and authored controls. It does not establish independent accuracy or general natural-language coverage.
- The snapshot retains selected measurements. It does not contain complete corpora or external publication assets.

## Next steps

- Run the exact-head PR release checks and merge the documentation to main when they pass.
- Keep any later publication decision with the author.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
