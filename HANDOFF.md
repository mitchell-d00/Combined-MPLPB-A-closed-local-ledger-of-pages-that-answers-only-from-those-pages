# Repository handoff

Last reviewed: 2026-11-25.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `5bef945e401f96a6422bb8c468932d330b705fc4` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `7ea9b5288a462e6a02993c1489358513486a1d9237b6d063b494909cdb54f85d`.

## Betty report for Al

Run the Betty implementation step first, then the Al review step in a separate chat. Both inspect the repository and the public API manifest, confirm their step, then read the last Betty report on the newest PR by creation time. A specific PR link selects that PR. The maintainer pastes Al’s response and direction to Betty, who tests and updates that PR. Resume from the last applied state after a pause.

### Latest user update instructions

Implement Bubble and Wrap around the existing PR #103 reported-content proposal. Verify the current head and reconcile its report first. Preserve the existing 20 development inputs, ten primary targets, frozen scoring obligations, and unopened 24-case transfer packet. Bubble: reuse tools/study_sandbox.py. Stage only the approved native runtime, frozen worker, and public case inputs. Keep keys, scorer, generator, Git metadata, credentials, and host network outside the worker. Require MPLPB_REQUIRE_SANDBOX=1 python -m unittest tests.test_study_sandbox -v. Add a thin adapter; check parity on consumed cases, freeze before baseline/candidate comparison; fail closed on launch failures. Wrap: freeze 32 cases, four reporting mechanisms x two question purposes x four contexts. Preserve roles, polarity, conditions, source state and existing budgets. Patch the smallest shared operation; score every claim, including partials, against eligible exact witnesses. Preserve111 inventory,17 PE-02,96 consumed attribution,56 focused controls and older integrity tests, recording overlaps by hash. Freeze a committed ZIP before transfer once. Extend docs/TEST_INDEX.md and docs/results.json with stable IDs, PR origin, mechanism, rule, inputs, pins, command, raw output, score, budgets, custody and limits. Separate execution from semantics; append immutable records; audit duplicate IDs, links, seals, omitted attempts and planned-as-passed claims. Acceptance: ten primary targets, contrasting decisions, zero false support, valid preservation, separate transfer; retain unresolved misses and NOT_RUN. Full maintainer-supplied design is retained byte-for-byte in evaluation/bubble-wrap/2026-11-25/inputs-received/bubble-wrap-plan.json.

### Implemented scope

- Reconciled PR103 head5bef945 and preserved its original freeze and transfer seal.
- Added execution-only Bubble adapter using existing isolation machinery, separately frozen32 Wrap cases, complete-governor source-role scoring and indexed native/source-state/budget controls.
- No native reader changes at this baseline freeze.

### Validation recorded

- Required sandbox gate: restricted uid_map failure retained; approved host invocation passes all4 isolation tests with no direct fallback.
- Adapter parity123 consumed cases and final20 proposal cases pass; frozen before baseline/candidate comparison.
- Baseline256 isolated executions completed/scored;230 expected decisions pass,26 target misses,zero false-supported claim cases; all raw outcomes retained.
- Frozen16 native guards:13 pass,2fail,1 missing-new-module error. Preserved as baseline failures.
- Delivery observer path/classification errors retained separately; worker,adapter,scorer,key and baseline results unchanged.

### Limitations and blocked checks

- Candidate and transfer NOT_RUN at baseline freeze. Native semantic repair has not started.
- Private PE02 originals/raw receipts remain under original restrictions; public hashes and complete contract/discovery comparisons retain custody limits.
- Same operator prepared/saw templates and scored material. No transfer instances/key opened; isolation does not establish independence.
- Independent historical accuracy, semantic adjudication, preparation,blinding,outside-custodian scoring,native OOCC remain NOT_RUN.

### Next steps

- Implement smallest source-scoped report-content operation from frozen failures; retain every rejected candidate.
- Rerun identical development/preservation, commit and ZIP-freeze candidate, then run sealed transfer once without code changes afterward.
- Publish exact source/ZIP, raw scores and updated handoff/index; complete required release checks before any merge/deployment claim.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
