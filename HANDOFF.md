# Repository handoff

Last reviewed: 2026-11-26.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `dcbf222605898d887d21a9ceb72ba63b83a838b9` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `e09355e164d81dfd56828b44b2dcf3e30d63032d518d5ca8eaaf26ea40a2ba61`.

## Betty report for Al

Run the Betty implementation step first, then the Al review step in a separate chat. Both inspect the repository and the public API manifest, confirm their step, then read the last Betty report on the newest PR by creation time. A specific PR link selects that PR. The maintainer pastes Al’s response and direction to Betty, who tests and updates that PR. Resume from the last applied state after a pause.

### Latest user update instructions

Run the bounded C3 comparison within existing Cryptid → Bunyip → Round 2. Freeze the five C3-REPL-P replacement pairs before execution, then freeze paired fresh C3-REPL-R and X packets and run both pinned readers once without reader repairs. Report useful comparisons and keep replacement, formatting, and incident status separate. Preserve the old incomplete checks.

### Implemented scope

- Retain the isolated 10-case replacement development comparison and freeze the two new 20-case replacement packets before fresh execution. Reader source remains unchanged.

### Validation recorded

- Both readers ran all ten development cases, retained five of five controls, supported one overlapping target and missed four. Zero unsupported completions or lost protected answers. Exact artifact SHA-256 1420fc5a9c68ea48a27f8df2082ed7b5c01896aeefbde6202edf5ee5383c6a48. Fresh keys and inputs are frozen in this checkpoint; no fresh execution result at freeze.

### Limitations and blocked checks

- Original 17 preservation checks remain incomplete and the original 100 transfer cases NOT_RUN. Recovery remains closed. History publication incident stays open. No independent blinding, historical or semantic adjudication, outside-custodian scoring, native OOCC or human onboarding.

### Next steps

- Run the same released and C3 runtime ZIPs once on both fresh packets without changes. Verify artifacts, score by family and unique original question, and retain any failed result.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
