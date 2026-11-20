# Repository handoff

Last reviewed: 2026-11-20.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `b2dc1da484072a1fb6ff279b5ce2edd56f9fa14b` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `cc3d621b052c94573dc9ac3fc7d0889f62b1cfc6c509aa747d2e170d1540337d`.

## Latest user update instructions

What would raise the score: a README that opens with the idea in plain words and a 30-second example, the evaluation data moved out to a release or separate repo, and a trimmed-down core package.

## Implemented scope

- Lead with a plain-language introduction and short browser and terminal examples.
- Publish a separate compact native download from the existing wheel on future Pages builds. Install from the extracted public-download artifact in CI and verify retrieval after deployment.
- Link the research archive, prior implementations and advanced tools from secondary navigation while preserving their version-pinned source paths.

## Validation recorded

- Both browser README questions passed in real Chromium using the existing browser runtime.
- A clean offline install from the locally built 313,318-byte native ZIP passed both README CLI questions. Wheel inspection found only the three runtime packages and distribution metadata.
- Documentation inventory, infrastructure checks, and changed workflow YAML and shell syntax checks passed locally.

## Limitations and blocked checks

- The evaluation archive still resides in the full repository. The independent downloadable package excludes the archive. Moving version-pinned inputs would require a migration of their workflows and references.
- The public URL is created by the first deployment of this change.

## Next steps

- Validate the frozen archive and the public download in the normal release workflow when the candidate is submitted.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
