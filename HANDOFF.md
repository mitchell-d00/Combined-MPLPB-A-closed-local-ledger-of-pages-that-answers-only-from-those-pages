# Repository handoff

Last reviewed: 2026-11-26.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `ab8f73e83538d8e33e8d13df14c2f47b88054608` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `4552e65b0ee8270b66429be231e9ace77ef0019f5590b5549e9b716faed94121`.

## Betty report for Al

Run the Betty implementation step first, then the Al review step in a separate chat. Both inspect the repository and the public API manifest, confirm their step, then read the last Betty report on the newest PR by creation time. A specific PR link selects that PR. The maintainer pastes Al’s response and direction to Betty, who tests and updates that PR. Resume from the last applied state after a pause.

### Latest user update instructions

Betty — prioritize broader ordinary-language understanding. Work locally first. Create the next Cryptid series, “Bunyip,” if that name is unused. Before changing the reader, freeze development sources, questions, expected claims, qualifications, controls and baseline outputs. Preserve question arguments, negation, modality, attribution and requested relations through interpretation. Do not use entity-specific patches or infer missing facts. Audit every recovered answer against its source. Keep original failures and frozen scores. Mitchell has authorized incremental releases with verified gains and no regressions. Existing coverage misses alone do not require perfect scores before release. Once the gains are audited and required checks pass, publish the evidence, update the PR, merge through the normal protected workflow and verify deployment. Do not bypass required checks or request the same authorization again. Keep human onboarding execution NOT_RUN until Mitchell returns actual participant results.

### Implemented scope

- Local Bunyip branch from verified PR105headab8f73e; main remainsc01021c and no newer PR work exists. No native code changed at this baseline freeze.
- Frozen102development executions (51question/source obligations in two renderings) and42sealed transfer executions. Whole original question and source evidence remain authoritative.
- Incremental release criteria prospectively supersede the old requirement for perfect coverage; verified source-supported gains/no regressions/required software checks are mandatory. Original failures and scores remain unchanged.

### Validation recorded

- Both102case baselines completed in real fail-closed Bubblewrap before any native change. Main12/60positive completions; PR10516/60;42/42withhold controls on each. Originalscores50/102 and58/102 retained.
- Four main strict-key flags reflect an absent additive literal-polarity field. Separate source-scoped representation review retained; no old key/score changed.

### Limitations and blocked checks

- Native repair, candidate preservation, ZIP checks and fresh transfer NOT_RUN at this freeze.
- Same-operator preparation/scoring; independent historical/semantic/preparation/blinding/outside-custodian/nativeOOCC andhuman executionNOT_RUN.

### Next steps

- Repair shared interpretation/proof mechanism from reproduced failures; audit complete recovered claims and exact citations.
- Preserve main/candidate valid support and guards; freeze repaired ZIP then open sealed transfer once.
- Publish verified incremental gains, updatePR105, merge only through normal required checks and verify deployment/live fingerprints.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
