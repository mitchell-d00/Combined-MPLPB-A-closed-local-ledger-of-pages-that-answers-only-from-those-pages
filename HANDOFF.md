# Repository handoff

Last reviewed: 2026-11-25.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `065840d9e7109ed26642fb6c755a723a7b044113` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `790a81854272af4219ca02ae2b04d35a175d94b54195b30c8f1b3cc252010a5f`.

## Betty report for Al

Run the Betty implementation step first, then the Al review step in a separate chat. Both inspect the repository and the public API manifest, confirm their step, then read the last Betty report on the newest PR by creation time. A specific PR link selects that PR. The maintainer pastes Al’s response and direction to Betty, who tests and updates that PR. Resume from the last applied state after a pause.

### Latest user update instructions

Implement Bubble and Wrap around the existing PR #103 reported-content proposal.

Verify the current head and reconcile its report first. Preserve the existing 20 development inputs, ten primary targets, frozen scoring obligations, and unopened 24-case transfer packet.

Bubble: reuse `tools/study_sandbox.py`. Stage only the approved native runtime, frozen worker, and public case inputs. Keep keys, scorer, generator, Git metadata, credentials, and host network outside the worker.

Require:

```sh
MPLPB_REQUIRE_SANDBOX=1 python -m unittest tests.test_study_sandbox -v
```

Add a thin adapter for the proposal’s existing packet schema. Check its output parity on consumed cases, then freeze it before baseline/candidate comparison. Bubblewrap launch failure means blocked execution and a nonzero result; retain it separately from reader abstention.

Wrap: add a separately frozen 32-case development matrix: four reporting mechanisms × two question purposes × four contexts.

The mechanisms are affirmative report, reported denial, denial that reporting occurred, and conditional reporting. Ask both what the source attributes and whether independent actual authorship is established. Vary standalone context, a different document writer, unrelated quoted material, and eligible conflicting evidence.

Derive expectations from the requested actor, reporting layer, polarity, and conditions. Denials and quotations can support source-scoped answers.

Patch the smallest shared operation supported by these failures. Keep existing budgets. Score every claim, including partial claims, against exact eligible witnesses.

Preserve the 111 inventory cases, 17 PE-02 cases, 96 consumed attribution cases, focused controls, and applicable older integrity tests. Record overlapping cases by hash. Intended recoveries may change explicitly listed target abstentions; preserve all unaffected valid claims, refusals, conflicts, qualifications, missing obligations, and citations.

Freeze a committed ZIP candidate before running the unopened transfer packet once. Retain failures. Any transfer-informed repair consumes that packet.

Extend the existing `docs/TEST_INDEX.md` and `docs/results.json`. Give Bubble and Wrap stable family/case IDs. Link each test to its originating PR, failure mechanism, protected rule, frozen inputs, baseline/candidate pins, reproduction command, raw output, score, budgets, custody status, and remaining limitations.

Separate execution status from semantic outcome. Append immutable run records. Audit duplicate IDs, broken links, changed seals, omitted attempts, and planned tests presented as passed.

Acceptance requires the ten primary targets, correct contrasting decisions, zero false-supported claims, preserved valid earlier behavior, and separately reported transfer results. Publish unresolved misses and all `NOT_RUN` labels.

Latest maintainer updates:
Continue when you finish check tree make sure all pr are live and merged on main
We have a lot of open pr
Catch it all up then push everything merge to main

Latest maintainer instructions:
Run them all in sequence test , fix and then merge it all I’ll let you run until it’s finished next is pr 104 correct?
Mitchell will recruit and return results for the twelve-person onboarding trial.
Source-linked tag comparison: exact source/revision/hash coordinates, proposed tags independently checked natively; imported private cannot set access; preserve attribution, negation, conditions and date roles.

If it lost valid support or gained an unsupported claim, repair the reader. If it recovered a previously missed positive, verify the complete claim, qualifications, and citations before updating acceptance expectations. If execution or scoring failed, retain that separately from reader results.
Create a department-based navigation structure and map every existing component to its department. Start with documentation and entry points, preserving imports, commands, frozen evidence paths, and historical links. Update the Test Index to identify the responsible department. Move implementation files later in separately tested changes, with an old-path/new-path migration map.

Continue all authorized work in sequence, test/fix/merge; next newPR expected104. Mitchell recruits12first-time participants and returns their actual results.


### Implemented scope

- Merged PR103 with93/95/97 histories into main16948d5ec5901870c3e884f68e7bc1fffb6fa2b4 after exact2ab4b01head gates passed; allfour PRs report merged and main tree matches tested head. Pages deployment pending.
- Freeze source-linked proposal trial72development/24sealed transfer and baseline before native implementation. Retain exact uncommitted prototype and host scorer-reporting correction.
- Prepare seven department navigation pages and explicit component routing, preserving all implementation/import/command/evaluation/history paths. Native tag API not yet added at this preparation commit.
- Prepare compact onboarding materials with the exact small native wheel and five fixed synthetic tasks; no human observations yet.
- Add opt-in native source-linked proposal inspection using full ordinary native proof, explicit source pins, canonical/original containment and current eligibility; production answering remains unchanged.
- Complete seven department entry pages, component routing and Test Index family ownership. Root leads TryMPLPB→Departments→Evidence; contributor protocol preserved below first-use sections.
- Freeze two400KBnative onboarding ZIPs with identical wheel/collection/tasks/interface; only ENTRY documents differ. Helper verifies exact installed runtime and collection. Human executionNOT_RUN.
- Repair UI evidence-card selection after retained candidate browser failure; use native citation tuples instead of lexical ordering and await an actually opened source dialog. No native code changes after transfer.

### Validation recorded

- PR103 checked source7f6641d ZIPf5be70718a1454171005493eba452e8fbd0602f3195e5325f57dd268840f8162:280/280development/preservation and fresh24/24same-operator composition; first16/24failure retained.
- Exact2ab4b01 publication CI allgreen, including1,000-case readback:231/420complete,580/580refusals preserved,189positive misses; original v1failure and original labels/scorer retained.
- All PR93,95,97,103 report merged at16948d5; noopenPRs observed aftermerge. Verified main tree equals exact checked head and all old heads are ancestors.
- Source-tag baseline72isolated executions complete and raw72/72supported; tag API unavailable, semantic tag checksNOT_RUN. Frozen worker excludes keys/generator/scorer/Git/credentials/network.
- Uncommitted tag prototype72/72decisions,6valid66tamper,0wrongassignments,0recoveredanswers; raw contracts unchanged exceptfingerprints. Prototype source/raw hashes retained; fresh24still unopened.
- Native wheel70db08aec72861cc17fea8bc08b7eb6bc7986764e4adf47d0e04ead496253303 is400276bytes from checked7fsource. Isolated installed-wheel helper opens actual cited passage; fixed collection repeats byte-for-byte. These are software checks, not human observations.
- PR103 Pages45670095889completed successfully, public postdeployChromium plus a separate verified-TLS/SPKI observer pass; allsixcore module fingerprints match before/after full live UI,local-document andNPC/reload journeys.
- Source-tag15additional state/budget/ambiguity/mutation/original-containment guards pass; portable generator with explicit original17:31clock reproduces development manifest/key/seal byte-for-byte. Original generator and runner versions retained unchanged.
- Onboarding actualtwoZIPs extracted, installed-wheel helpers run under isolatedPython, allfive native contracts and opened citation identical. Frozen package parity plus scoring7arithmetic controls pass; zero human observations.
- Committed2af8ba8 ZIP17a3d15fe8ca2d7fffc27f949f621445692b6a053025a3939bc47bdaf2bf59ec matches24830files;72/72proposal,280/280preservation,24/24fresh proposal decisions,0wrong tags,0recoveredanswers.
- Full extracted native suite1834pass;52public controls,15software commands andWASMpass. BrowsercandidateFAIL retained:wrong lexical source card and stale-dialog assertion. FrozenJScontrols failbefore andpassafter correction;35Pythonbrowser/integritycontrolspass. Native packages byte-identical to transferfreeze; no rerun of the fresh packet.
- Corrected065840d deliveryZIP SHAafe52d43e335f5963b765d00c7ad373a6ec0fd6a5bb560c86a93d7d3a6bffb98matches27155trackedfiles, nativebytesexactlyequalonce-tested2af8ba8.15softwarecommands,58focusedtests,actualWASM,bothChromiumcontextsandactualnewsource-dialogchecksPASS.
- SourceTagfresh24/24(6valid18tamper),0wrongtags,0newanswers;raw24/24beforeandafter. Native2af8ba8full1834pass;280priorcontracts(including6partials)unchanged. FirstdeliverybrowserfailureandearlyZIPpreparationerrorretained.

### Limitations and blocked checks

- Zero reading-coverage gain from tag inspection; existingnative forms only. Same-operator templates visible, not independent preparation/blinding.
- Human12-person pilotNOT_RUN; frozen400KBarmZIPsandsoftwareparityarepreparationonly. Mitchell recruits and returns actualobservations.
- Independenthistoricalaccuracy,semanticadjudication,preparation/blinding,outside-custodianscoring,nativeOOCCremainNOT_RUN.
- Corrected deliverypassedlocalgates; exactpublication-headfullCI,104mergeanddeployedmainverificationpending.
- Originalsource-tagdeliveryrejectedforbrowserfailure;nativepackagesunchangedaftertransfer.Noheldpacket rerun.

### Next steps

- Pushfinal104evidencehead,currentPRreportwithexacttestedpins/checksumsandNOT_RUNlabels;requireall exact-headCIgatesbeforemerge.
- Mergemain,verifytree/sourcecardworkflow/sevenruntimefingerprintsandnoopenPRs;recordfinalreleaseinPR104/Actions.
- Mitchell administersfrozenpilotandreturnsrealobservations;do notfillmissingparticipantsorresults.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
