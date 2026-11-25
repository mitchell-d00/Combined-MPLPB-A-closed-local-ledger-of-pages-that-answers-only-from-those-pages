# Repository handoff

Last reviewed: 2026-11-25.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `defb519185880480b07be024048403e1447e01cd` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `aade0c8acd729250b4e10dbe7f3b9dbb1a5d6a4da044bb50cf45f934284e231c`.

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


### Implemented scope

- Reconciled PR103 head5bef945 and preserved its original freeze and transfer seal.
- Added execution-only Bubble adapter using existing isolation machinery, separately frozen32 Wrap cases, complete-governor source-role scoring and indexed native/source-state/budget controls.
- No native reader changes at this baseline freeze.
- Add one native source-scoped report operation reusing existing action/policy checks, with separate writer/reporter/embedded actor, inner/outer negation and conditional status. No instruction or historical claim changes.
- Freeze nine byline/governor contrasts and expanded280 baseline before further native repair. Fresh24 composition instances/key remain unopened.
- Merge actual PR97/95 histories while retaining later FRUS reader/evidence and all byte-identical older implementation/evaluation files; retarget both PRs to main for unified tested integration.
- Integrate actual PR93 browser document workflow and local capture path, preserving new role APIs and frozen older integrity tests; final combined ZIP/browser gates remain pending.
- Add only the shared unpunctuated metadata boundary and retain a separate conditional fragment ending in a period. Do not change existing punctuated instruction unit counts.
- All93/95/97 head histories are ancestors of the consolidation branch; preserve later FRUS evidence and original integrity tests, integrate missing93 local-document UI/provenance.

### Validation recorded

- Required sandbox gate: restricted uid_map failure retained; approved host invocation passes all4 isolation tests with no direct fallback.
- Adapter parity123 consumed cases and final20 proposal cases pass; frozen before baseline/candidate comparison.
- Baseline256 isolated executions completed/scored;230 expected decisions pass,26 target misses,zero false-supported claim cases; all raw outcomes retained.
- Frozen16 native guards:13 pass,2fail,1 missing-new-module error. Preserved as baseline failures.
- Delivery observer path/classification errors retained separately; worker,adapter,scorer,key and baseline results unchanged.
- Amended v3 scorer: baseline230/256 to development256/256; ten primary source targets recovered; Wrap12source answers,4conflicts,16independent-authorship withholds. Zero final false-supported claim cases.
- All prior80claims preserved;30new source report claims have complete governor, typed roles, canonical and actual written-HTML byte witnesses. Six partials unchanged; all101unaffected inventory,96instruction and17PE02 complete contracts/discovery preserved.
- All169indexed native controls pass:56focused,92authority/integrity,16report guards,5accounting.
- Initial scorer26certificate rejections remain failed. A versioned projection auditor restores automatic H1 wrapper; v2 CLI import/logging failures retained; v3 frozen before exact unchanged-output rescoring. Keys,inputs,adapter and reader unchanged by correction.
- Committed204a7d ZIP SHA-256804161aec3d4286296413007874bd0b60f030589ceb72203dad5a524396e7ea2 has13700 matched extractedfiles; isolated extracted256/256 passes.
- Once-only first transfer16/24 versusbaseline12/24:4positive12withhold8miss0false support. AcceptanceFAIL; originalcandidateunchanged. All24 consumed, no relabeling.
- Fresh composition generator/seed/packet/key seals frozen before any continuation native edit. Exact instances/key remain unopened.
- Four openPRs93,95,97,103. Reconcile diverged histories, retain later reader/evidence and integrate genuinely missing local-document browser work before tested main merge.
- Continuation baseline280 isolated/scored:272pass8miss,0false-supported claim cases on that frozen packet set. Separately frozen9new byline/governor guards:6pass3fail, including one exposed false-supported conditional-fragment claim. Preserve that control failure; prior zero figures apply only to their stated frozen sets.
- FRUS history conflict resolution leaves all three native runtime packages byte-identical to the pre-merge candidate; older implementation/evidence content already matches current. PR93 browser feature remains to integrate.
- Expanded280 continuation:272/280 to280/280;97complete6partial6conflict171abstain122claims,0false-supported claim cases,0failed/notrun/unscored. All prior full contracts and counters preserved.
- Nine frozen byline/governor controls6/9to9/9; one prior false-supported conditional fragment eliminated. Existing16report guards pass. Wider candidate with4examined-unit counter changes retained as rejected; no key relabeling.
- Original93browser-bridge and integrity checks35pass plus UI script syntax/workflow checks pass. Native package differences from first candidate remain restricted to source_units and reported_content guard.

### Limitations and blocked checks

- Private PE02 originals/raw receipts remain under original restrictions; public hashes and complete contract/discovery comparisons retain custody limits.
- Same operator prepared/saw templates and scored material. No transfer instances/key opened; isolation does not establish independence.
- Independent historical accuracy, semantic adjudication, preparation,blinding,outside-custodian scoring,native OOCC remain NOT_RUN.
- Committed ZIP/extracted checks, once-only transfer, exact-head CI and deployment NOT_RUN at this development snapshot.
- 28non-target positive questions remain incomplete:4partials24misses, including FRESH05. Preservation pass is not full answer coverage.
- The initial frozen-scorer protocol did not pass. Accepted development figures use disclosed v3 projection/import correction; retain all earlier failures.
- First transfer acceptance failed; do not merge that candidate. Full native archive-suite completion unconfirmed after environment/session interruption; partial log retained.
- Fresh composition transfer remains unopened/unexecuted. Combined committed ZIP, full exact-head CI, merge and live verification pending at source freeze; do not claim initial transfer acceptance.

### Next steps

- Reconcile all four open PRs into one tested current tree, preserving later source/evidence.
- Retain first failed transfer as development. Repair the shared byline boundary after the fresh packet freeze; no caps or source/key changes.
- Test committed continuation ZIP, run fresh transfer once, finish exact-head CI, merge and verify deployed main and PR states.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
