# Repository handoff

Last reviewed: 2026-11-25.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `629d08854b6075af2b8a4a7a224bc189a49feffa` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `50faf65734f1991bb7b0136f29ed96d1fdb59720af2069cd9295877d77583a7b`.

## Betty report for Al

Run the Betty implementation step first, then the Al review step in a separate chat. Both inspect the repository and the public API manifest, confirm their step, then read the last Betty report on the newest PR by creation time. A specific PR link selects that PR. The maintainer pastes Al’s response and direction to Betty, who tests and updates that PR. Resume from the last applied state after a pause.

### Latest user update instructions

Run Betty — local Cryptid test programme. Start from current main. Complete the following prompts in order, one series at a time. Continue through ordinary implementation choices without asking me to reconfirm this scope. Work in an isolated local branch/worktree. Local commits and source archives are authorized. Do not push, open or update remote PRs, merge, deploy, or modify remote main until Mitchell explicitly authorizes publication. Do not overwrite unrelated work or frozen evidence. STOP AT THIS PUBLICATION BOUNDARY. Tell Mitchell exactly what is ready and what remains blocked. Wait for his explicit instruction before pushing or merging.

### Implemented scope

- Established local Cryptid programme on isolated branch local/cryptid-programme from verified current remote main c01021c0b9983f9a607fbe782dea7ed5872d1f11
- Ordered scope: programme, documentary date roles, question wording, polarity/conditions/modality, identity/references, comparisons/corrections, multipart/document links, automatic source-linked representation, fixed-cap budgets, Bubblewrap controls, real-human onboarding preparation and final local ZIP review.

### Validation recorded

- Verified clean starting main and actual remote main SHA match c01021c0b9983f9a607fbe782dea7ed5872d1f11
- Required sandbox command: default nested namespaces BLOCKED two checks; host execution real Bubblewrap PASS4/4. Both transcripts retained.
- Frozen Mothman28 development executions completed on unchanged c01021c0:17 expected decisions pass,11positive misses,0false-supported claims. All five unchanged old date-role cases reproduced. Baseline/raw outputs, exact source hashes, harness/scorer/generator and sealed16case transfer retained before native edits.

### Limitations and blocked checks

- Reader series and final integration NOT_RUN at establishment.
- Same-operator preparation/scoring. Independent historical/semantic adjudication, independent preparation/blinding, outside-custodian scoring, native OOCC and human execution NOT_RUN.
- Prior handoff publication instructions are superseded by current LOCAL_ONLY boundary.

### Next steps

- Patch only evidenced shared date-role planning/proof gaps; rerun identical28 and preservation; commit ZIP before opening sealed transfer once.
- Run all series sequentially and finish a local committed-ZIP review package. No remote publication.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
