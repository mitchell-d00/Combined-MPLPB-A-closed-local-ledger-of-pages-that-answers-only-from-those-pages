# Repository handoff

Last reviewed: 2026-11-21.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `5d6300f55f0a4996d0cf8ab3b98a8dcfadadeec4` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `4452cd53207178ebde564270696cc6824cf823b471b980b812d8d6250b1e4a83`.

## Latest user update instructions

Let’s do that clean up the repo organize let’s do house keeping don’t break it

## Implemented scope

- Organize user-facing tools by task in a directory reachable from the README, documentation index, and browser help.
- Guide users from the sample to creating a collection, importing material, reviewing a source, and asking a question.
- Clarify browser and desktop storage in the help view. Preserve existing UI controls, behavior, test inputs, and archived evidence paths.

## Validation recorded

- All local tool directory paths and section links resolved. The documentation audit checked preserved documents and retained test links.
- The UI script, serialized browser transport, JavaScript API, and infrastructure synchronization checks passed locally.
- Real Chromium followed the new help path and performed collection creation, text import, source review, a supported answer, and a refusal.

## Limitations and blocked checks

- This pass changes navigation and instructions. Archived evaluation data remains at the paths used by release checks and citations.
- The tool directory links the main user-facing tools and the repository map for implementation and maintenance scripts.

## Next steps

- Run the exact-head release gates when the housekeeping candidate is submitted.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
