# Repository handoff

Last reviewed: 2026-11-19.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `0b2c5c834a87262b1cc4853a30f88e3f9252c6a5` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `f8d6228f5681418ed6eef12e43ba68e39176e2594f40b8c0b1e6ca5a1175eada`.

## Latest user update instructions

Build original D% randomized prose tests with structural variation, binary answer/refuse expectations, E/F metrics and a frozen generator/key. Run current main before engine fixes. Keep identifying references out of new artifacts. The separate-window requirement is waived.

## Implemented scope

- Add generator, isolated worker and post-run scorer only; no native engine changes.
- Freeze generator and private key before a 1,240-case current-main baseline; retain all failures.

## Validation recorded

- 15 generator/scorer software tests passed, exit 0.
- Native runtime has no diff from main 6334e1b3a08db10984de637adbd5e5a6021b381c.
- Generator frozen at0b2c5c834a87262b1cc4853a30f88e3f9252c6a5;1,240 packets generated and key/seal hashes recorded before baseline execution.

## Limitations and blocked checks

- Baseline execution and extracted-source regression pending.
- Developer-authored fictional tests; independent semantic review NOT RUN.
- User instruction is sanitized to honor the requirement to omit identifying references. Private key stays outside the repository.

## Next steps

- Freeze committed generator, generate and seal a fresh batch before execution.
- Run all baseline cases without modifying MPLPB; preserve and report failures and costs.
- Run extracted-source regressions and documentation audit, retain evidence and prepare a new handoff.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
