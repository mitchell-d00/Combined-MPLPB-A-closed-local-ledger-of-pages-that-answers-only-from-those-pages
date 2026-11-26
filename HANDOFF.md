# Repository handoff

Last reviewed: 2026-11-26.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `91dd6d0e02c56f60ecf47122bd0e9bf9e0ac8acb` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `b6ce7167ebeb532d1ff13b6ad1037b541fc1e5087d46b5063aa3bfe316916e72`.

## Betty report for Al

Run the Betty implementation step first, then the Al review step in a separate chat. Both inspect the repository and the public API manifest, confirm their step, then read the last Betty report on the newest PR by creation time. A specific PR link selects that PR. The maintainer pastes Al’s response and direction to Betty, who tests and updates that PR. Resume from the last applied state after a pause.

### Latest user update instructions

Betty — prioritize broader ordinary-language understanding. Work locally first. Create the next Cryptid series, “Bunyip,” if that name is unused. Before changing the reader, freeze development sources, questions, expected claims, qualifications, controls and baseline outputs. Preserve question arguments, negation, modality, attribution and requested relations through interpretation. Do not use entity-specific patches or infer missing facts. Audit every recovered answer against its source. Keep original failures and frozen scores. Mitchell has authorized incremental releases with verified gains and no regressions. Existing coverage misses alone do not require perfect scores before release. Once the gains are audited and required checks pass, publish the evidence, update the PR, merge through the normal protected workflow and verify deployment. Do not bypass required checks or request the same authorization again. Keep human onboarding execution NOT_RUN until Mitchell returns actual participant results.

### Implemented scope

- BunyipC2 source/results retained locally; C2rejected after14newgovernor controls expose10unsupportedcompletions. Existingprimarygain56/60 versus16PRbaseline andscope24/24remain documented. No publication yet.
- C2matchesall849oldPRcontracts. Four support differences against main are false compound authors formed from headers, not valid support losses.
- Sourcechecked assessment validates44oldadditionaloutputs and21metadata cases fromfrozen originals; oldstrict failuresunchanged. ProspectiveCIpolicy mayonlyacceptafter contract-preservation and execution-integrity checks.

### Validation recorded

- Both102case baselines completed in real fail-closed Bubblewrap before any native change. Main12/60positive completions; PR10516/60;42/42withhold controls on each. Originalscores50/102 and58/102 retained.
- Four main strict-key flags reflect an absent additive literal-polarity field. Separate source-scoped representation review retained; no old key/score changed.
- C1realhost102completed:98/102strict,56completions,0flags onprimarypacket. PostC1developmentWrap24:20/24,4unsupportedcompletecases caused by standaloneOnlyifscope. OriginalPRWrap16/24 has6unsupportedclaims and2positive misses. AlloriginalrawscoresandfailedC1retained.
- DefaultnamespaceC1launch102executionfailures,0readerexecutions; separatehostretrycompleted102. No unsandboxed fallback.
- C2core98/102,56/60completions,42withholds0falseflags;scope24/24. Governordevelopment14score4/14,10falseflags; retainandrejectC2.
- 849currentPRcontracts exactlyunchanged inC2; releasedmainreplaycomplete and4apparentsupportlosseschecked againstexactclaims: inventedauthorsfusedwithheaders. No lostvalidsupport identified.
- 57focused nativechecksPASS. Legacy65case sourceassessmentPASS afterretainedhost-audit correction; historical/independentsemantic NOT_RUN.

### Limitations and blocked checks

- C2rejected; C3governor repair, final cleanZIPsoftware checks and42freshtransfer remain NOT_RUN.
- Same-operator preparation/scoring; independent historical/semantic/preparation/blinding/outside-custodian/nativeOOCC andhuman executionNOT_RUN.

### Next steps

- Repair shared interpretation/proof mechanism from reproduced failures; audit complete recovered claims and exact citations.
- Preserve main/candidate valid support and guards; freeze repaired ZIP then open sealed transfer once.
- Publish verified incremental gains, updatePR105, merge only through normal required checks and verify deployment/live fingerprints.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
