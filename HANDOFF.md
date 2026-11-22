# Repository handoff

Last reviewed: 2026-11-22.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `fa2647c85f5d001983d3326e18f8255bd66aff71` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `eaff824e0e320a0501dc71621527267e6f209ca92170aa3d81dda5e6eaec1976`.

## Latest user update instructions

Directions for an AI to inspect the full Combined MPLPB package

And make it explicit it is important that an Ai understands full MPLPB on read

## Implemented scope

- Add AI inspection directions to the README with the requested reading order, source entry points, supporting material and verification boundaries.
- Link the directions from the opening of the README and the public AI discovery file.

## Validation recorded

- Verified the navigation anchors and requested reading order, and checked the referenced paths.
- The documentation audit, infrastructure check, and 108 focused tests passed.

## Limitations and blocked checks

- The directions explain how to inspect and reproduce claims at a named commit. The edit records no new historical accuracy measurement.

## Next steps

- Keep the inspection directions synchronized with package entry points and evidence boundaries.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
