# Repository handoff

Last reviewed: 2026-11-26.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `eeda87e03567482302f6fdd011a7d51f27bec9f4` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `1deb5c36bd8a839542c7d7b1759a553861346ff8de9f6af923bf6947a7c277e5`.

## Betty report for Al

Run the Betty implementation step first, then the Al review step in a separate chat. Both inspect the repository and the public API manifest, confirm their step, then read the last Betty report on the newest PR by creation time. A specific PR link selects that PR. The maintainer pastes Al’s response and direction to Betty, who tests and updates that PR. Resume from the last applied state after a pause.

### Latest user update instructions

Run the bounded C3 comparison within existing Cryptid → Bunyip → Round 2. Freeze the five C3-REPL-P replacement pairs before execution, then freeze paired fresh C3-REPL-R and X packets and run both pinned readers once without reader repairs. Report useful comparisons and keep replacement, formatting, and incident status separate. Preserve the old incomplete checks.

### Implemented scope

- Freeze 10 synthetic development replacements and examiner rules. Use the existing Cryptid isolated runner on the released and C3 runtime ZIPs. Retain raw public-eligible outcomes and startup logs separately.

### Validation recorded

- Development registry, key, inputs, scorer policy and both scoped runtime ZIP hashes are frozen before reader execution. No development or transfer result exists at this checkpoint.

### Limitations and blocked checks

- Original 17 preservation checks remain incomplete and the original 100 transfer cases NOT_RUN. Recovery remains closed. History publication incident stays open. No independent blinding, historical or semantic adjudication, outside-custodian scoring, native OOCC or human onboarding.

### Next steps

- Execute the 10-case development comparison in the existing hosted isolated runner. Then freeze the fresh paired R/X draws with unchanged runtime and evaluate without repairs.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
