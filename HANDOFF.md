# Repository handoff

Last reviewed: 2026-11-25.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `16948d5ec5901870c3e884f68e7bc1fffb6fa2b4` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `53b83d0080020f63b67362fda613ef19071d6557c820d903a522cb9b2f062328`.

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

### Validation recorded

- PR103 checked source7f6641d ZIPf5be70718a1454171005493eba452e8fbd0602f3195e5325f57dd268840f8162:280/280development/preservation and fresh24/24same-operator composition; first16/24failure retained.
- Exact2ab4b01 publication CI allgreen, including1,000-case readback:231/420complete,580/580refusals preserved,189positive misses; original v1failure and original labels/scorer retained.
- All PR93,95,97,103 report merged at16948d5; noopenPRs observed aftermerge. Verified main tree equals exact checked head and all old heads are ancestors.
- Source-tag baseline72isolated executions complete and raw72/72supported; tag API unavailable, semantic tag checksNOT_RUN. Frozen worker excludes keys/generator/scorer/Git/credentials/network.
- Uncommitted tag prototype72/72decisions,6valid66tamper,0wrongassignments,0recoveredanswers; raw contracts unchanged exceptfingerprints. Prototype source/raw hashes retained; fresh24still unopened.
- Native wheel70db08aec72861cc17fea8bc08b7eb6bc7986764e4adf47d0e04ead496253303 is400276bytes from checked7fsource. Isolated installed-wheel helper opens actual cited passage; fixed collection repeats byte-for-byte. These are software checks, not human observations.

### Limitations and blocked checks

- Source-tag trial is proposal validation over already-supported native report forms; no broader reading or answer-coverage gain demonstrated.
- Independent historical accuracy,semantic adjudication,preparation/blinding,outside-custodian scoring,native OOCC remainNOT_RUN. Same operator designed templates and scored.
- Human onboarding executionNOT_RUN; Mitchell recruits real participants. Frozen entry versions, rubric and actual observations must remain distinct from software checks.
- PR103 main deployment/live verification pending; next tag candidate ZIP/fresh transfer and exact-head release gates pending.
- Department structure is navigation only; file moves require a separately tested old/new migration map.
- Original first transfer16/24failed, wider unit-counter candidate rejected, original scorer/gate failures retained; none relabeled as passes.

### Next steps

- Verify deployed main16948d5 with actual Chromium and core module hashes; update PR103 final report.
- Add/test opt-in native source-linked proposal checker, preserve all raw reader contracts, freeze committed ZIP and run fresh24once; do not treat zero answer recovery as coverage gain.
- Finish department navigation/Test Index ownership and freeze two onboarding arms for Mitchell; keep actual human outcomesNOT_RUN until returned.
- Open next newPR104, pass exact-head archive and regression gates, merge and verify live/main clean with no open PRs.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
