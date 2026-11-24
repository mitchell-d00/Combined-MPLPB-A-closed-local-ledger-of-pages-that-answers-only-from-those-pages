# Repository handoff

Last reviewed: 2026-11-24.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `b53b7103b5d4491bc1f7db4bae9f6f50d9cee35e` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `b3f0bfa38273315c81646f44e6f859c052bf24879218992d87514939bb9d02f3`.

## Latest user update instructions

Test it how often the new paths can interpret unfamiliar prose and prove relationships across documents. Call it scout

## Implemented scope

- Draw 12 FRUS historical documents from six new volumes after pinning the engine, and commit 24 questions and their source key before native execution.
- Compare native proof, matched passage discovery, two live graph passes, expert investigation, and a separate key-assisted quote probe.

## Validation recorded

- Verified 12 exact source fragments and the pre-run custody bundle. Reproduced outputs apart from regenerated WorkStore receipt IDs.
- Strict Ask completed 0/18 answerable questions and 0/6 cross-document relationships. All 6 missing-evidence controls withheld. The 48 graph passes preserved the native result.
- At 12 passages, native discovery found all anchors for 14/18 answerable questions and 3/6 relationship questions. The subsequent quote probe verified 22/24 anchors.
- Passed 41 focused tests and the documentation audit.

## Limitations and blocked checks

- The sample covers short English diplomatic records and was scored by one AI-assisted operator. No configured model ran.
- The full repository ZIP exceeds local extraction space. This pilot checks the current engine without changing it.

## Next steps

- Develop independently worded controls for comparing recommendations rather than wording and test verified scope warnings on partial outputs.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
